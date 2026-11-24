# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestParamedicMyDay(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        staff = "base.group_user,paramedic_base.group_paramedic_staff"
        cls.artist = new_test_user(cls.env, "avery.stone", groups=staff, tz="UTC", name="Avery Stone")
        cls.other = new_test_user(cls.env, "sam.lee", groups=staff, tz="UTC", name="Sam Lee")
        cls.desk = new_test_user(cls.env, "kim.tran", groups=staff, tz="UTC", name="Kim Tran")
        cls.outsider = new_test_user(cls.env, "pat.sales", groups="base.group_user", tz="UTC")
        Practitioner = cls.env["paramedic.practitioner"]
        cls.p_artist = Practitioner.create({"user_id": cls.artist.id})
        cls.p_other = Practitioner.create({"user_id": cls.other.id})
        cls.service = cls.env["paramedic.service"].create({"name": "Consultation", "duration": 0.5})
        cls.dana = cls.env["res.partner"].create({"name": "Dana Whitfield", "is_patient": True})
        cls.marisol = cls.env["res.partner"].create({"name": "Marisol Ortega", "is_patient": True})
        cls.today = fields.Date.context_today(cls.env["my.day"].with_user(cls.artist))
        cls.Appt = cls.env["paramedic.appointment"].with_context(skip_appointment_checks=True)

    def _day(self, user):
        return self.env["my.day"].with_user(user).get_day()

    def _section(self, user, key):
        return next((s for s in self._day(user)["sections"] if s["key"] == key), None)

    def _appt(self, who, prac, hours_from_now, state="confirmed"):
        return self.Appt.create({"partner_id": who.id, "service_id": self.service.id,
                                 "practitioner_id": prac.id, "state": state,
                                 "start": fields.Datetime.now() + timedelta(hours=hours_from_now)})

    def test_sections_sit_where_they_should(self):
        keys = [(s["column"], s["key"]) for s in self._day(self.artist)["sections"]]
        self.assertIn(("plan", "appointments"), keys)
        self.assertIn(("attention", "booking_requests"), keys)
        schedule = keys.index(("plan", "schedule"))
        self.assertEqual(keys[schedule + 1], ("plan", "appointments"))

    def test_a_practitioner_sees_their_own_appointments_today(self):
        mine = self._appt(self.dana, self.p_artist, 0)
        self._appt(self.marisol, self.p_other, 0)
        self._appt(self.marisol, self.p_artist, 72)
        section = self._section(self.artist, "appointments")
        self.assertEqual([i["id"] for i in section["items"]], [mine.id])
        self.assertEqual(section["items"][0]["name"], "Dana Whitfield")

    def test_staff_who_dont_practise_see_the_whole_book(self):
        self._appt(self.dana, self.p_artist, 0)
        self._appt(self.marisol, self.p_other, 0)
        section = self._section(self.desk, "appointments")
        self.assertEqual(len(section["items"]), 2)
        self.assertTrue(any("Avery Stone" in i["meta"] for i in section["items"]))

    def test_a_started_appointment_can_be_completed(self):
        self._appt(self.dana, self.p_artist, -0.1)
        item = self._section(self.artist, "appointments")["items"][0]
        self.assertEqual(item["buttons"][0]["method"], "action_complete")

    def test_booking_requests_wait_with_a_confirm_button(self):
        request = self._appt(self.dana, self.p_artist, 48, state="requested")
        section = self._section(self.desk, "booking_requests")
        self.assertEqual(section["count"], 1)
        item = section["items"][0]
        self.assertEqual(item["id"], request.id)
        self.assertEqual(item["buttons"][0]["method"], "action_confirm")

    def test_patch_tests_due_or_overdue(self):
        condition = self.env["patient.condition"].create(
            {"partner_id": self.dana.id, "condition_type": "areola_restoration"})
        PatchTest = self.env["patient.patch_test"]
        due = PatchTest.create({"condition_id": condition.id, "pigment_name": "Warm Rose 2",
                                "application_date": self.today - timedelta(days=4)})
        PatchTest.create({"condition_id": condition.id, "pigment_name": "Later",
                          "application_date": self.today})
        PatchTest.create({"condition_id": condition.id, "pigment_name": "Read",
                          "application_date": self.today - timedelta(days=5), "result": "clear"})
        section = self._section(self.artist, "patch_tests")
        self.assertEqual([i["id"] for i in section["items"]], [due.id])
        self.assertTrue(section["items"][0]["overdue"])

    def test_follow_ups_only_for_patients_with_nothing_booked(self):
        Session = self.env["patient.treatment.session"]
        for who in (self.dana, self.marisol):
            condition = self.env["patient.condition"].create(
                {"partner_id": who.id, "condition_type": "scar_camouflage"})
            Session.create({"condition_id": condition.id,
                            "date": fields.Datetime.now() - timedelta(days=30),
                            "next_session_recommended_date": self.today + timedelta(days=3)})
        self._appt(self.marisol, self.p_artist, 96)  # Marisol is already booked
        names = [i["name"] for i in self._section(self.artist, "follow_ups")["items"]]
        self.assertEqual(names, ["Dana Whitfield"])

    def test_people_outside_the_practice_dont_see_it(self):
        keys = {s["key"] for s in self._day(self.outsider)["sections"]}
        self.assertFalse({"appointments", "booking_requests", "patch_tests", "follow_ups"} & keys)
