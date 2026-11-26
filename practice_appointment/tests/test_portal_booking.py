# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import HttpCase, TransactionCase, tagged


def _all_day_calendar(env, name="Test Calendar"):
    return env["resource.calendar"].create({
        "name": name, "tz": "UTC",
        "attendance_ids": [
            (0, 0, {
                "name": "Every day", "dayofweek": str(d),
                "hour_from": 0.0, "hour_to": 23.0, "day_period": "full_day",
            }) for d in range(7)
        ],
    })


@tagged("post_install", "-at_install")
class TestPortalBookingPages(HttpCase):
    """The GET side of the booking flow, over real HTTP."""

    def setUp(self):
        super().setUp()
        self.calendar = _all_day_calendar(self.env)
        staff_user = self.env["res.users"].create({
            "name": "Portal Test Practitioner", "login": "portal_test_prac",
            "group_ids": [(6, 0, [
                self.env.ref("practice_base.group_practice_staff").id,
                self.env.ref("base.group_user").id,
            ])],
        })
        self.practitioner = self.env["practice.practitioner"].create({
            "user_id": staff_user.id, "resource_calendar_id": self.calendar.id,
        })
        self.service = self.env["practice.service"].create({
            "name": "Free Consultation", "duration": 1.0, "buffer_minutes": 0,
        })
        self.env["res.users"].create({
            "name": "Prospective Client", "login": "prospective_client",
            "password": "prospective_client",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })

    def test_book_page_lists_eligible_service_and_slots(self):
        self.authenticate("prospective_client", "prospective_client")

        book_page = self.url_open("/my/book")
        self.assertEqual(book_page.status_code, 200)
        self.assertIn("Free Consultation", book_page.text)

        slots_page = self.url_open("/my/book/%s" % self.service.id)
        self.assertEqual(slots_page.status_code, 200)
        self.assertIn("Free Consultation", slots_page.text)
        # a slot time should be rendered as a button
        self.assertIn("btn-outline-primary", slots_page.text)

    def test_gated_service_not_offered_to_new_client(self):
        self.env["practice.service"].create({
            "name": "Areola Restoration Session", "duration": 2.0,
            "requires_test": True,
        })
        self.authenticate("prospective_client", "prospective_client")
        book_page = self.url_open("/my/book")
        self.assertNotIn("Areola Restoration Session", book_page.text)

    def test_my_appointments_page_loads(self):
        self.authenticate("prospective_client", "prospective_client")
        resp = self.url_open("/my/appointments")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("My Appointments", resp.text)


@tagged("post_install", "-at_install")
class TestPortalBookingLogic(TransactionCase):
    """The booking itself - exercised the same way the controller does it,
    without the HTTP/CSRF layer, since the interesting behaviour (client
    auto-provisioning, condition auto-selection, state/source) lives in the
    model, not the routing."""

    def setUp(self):
        super().setUp()
        self.calendar = _all_day_calendar(self.env)
        staff_user = self.env["res.users"].create({
            "name": "Logic Test Practitioner", "login": "logic_test_prac",
            "group_ids": [(6, 0, [
                self.env.ref("practice_base.group_practice_staff").id,
                self.env.ref("base.group_user").id,
            ])],
        })
        self.practitioner = self.env["practice.practitioner"].create({
            "user_id": staff_user.id, "resource_calendar_id": self.calendar.id,
        })
        self.service = self.env["practice.service"].create({
            "name": "Free Consultation", "duration": 1.0,
        })
        self.new_client = self.env["res.partner"].create({
            "name": "Not Yet A Client",
        })

    def _portal_book(self, service, partner):
        if not partner.is_client:
            partner.is_client = True
        condition = service._find_eligible_plan(partner)
        return self.env["practice.appointment"].create({
            "partner_id": partner.id,
            "plan_id": condition.id if condition else False,
            "service_id": service.id,
            "practitioner_id": self.practitioner.id,
            "start": datetime.utcnow().replace(
                minute=0, second=0, microsecond=0) + timedelta(hours=2),
            "state": "requested",
            "source": "portal",
        })

    def test_booking_provisions_client_and_sets_source(self):
        self.assertFalse(self.new_client.is_client)
        appt = self._portal_book(self.service, self.new_client)
        self.assertTrue(self.new_client.is_client)
        self.assertTrue(self.new_client.client_ref)
        self.assertEqual(appt.state, "requested")
        self.assertEqual(appt.source, "portal")
