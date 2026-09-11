# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import ParamedicAppointmentCommon


@tagged("post_install", "-at_install")
class TestParamedicAppointment(ParamedicAppointmentCommon):
    def _appt(self, **kw):
        vals = {
            "partner_id": self.patient.id,
            "service_id": self.service.id,
            "practitioner_id": self.practitioner.id,
            "start": self.next_monday + timedelta(hours=9),
            "state": "confirmed",
        }
        vals.update(kw)
        return self.env["paramedic.appointment"].create(vals)

    def test_stop_computed_from_service_duration(self):
        appt = self._appt()
        self.assertEqual(appt.stop, appt.start + timedelta(hours=1))

    def test_overlap_blocked(self):
        self._appt()
        with self.assertRaises(ValidationError):
            self._appt(start=self.next_monday + timedelta(hours=9, minutes=30))

    def test_back_to_back_is_not_an_overlap(self):
        self._appt()
        second = self._appt(start=self.next_monday + timedelta(hours=10))
        self.assertTrue(second)

    def test_skip_checks_bypasses_overlap(self):
        self._appt()
        second = self.env["paramedic.appointment"].with_context(
            skip_appointment_checks=True).create({
                "partner_id": self.patient.id,
                "service_id": self.service.id,
                "practitioner_id": self.practitioner.id,
                "start": self.next_monday + timedelta(hours=9),
                "state": "confirmed",
            })
        self.assertTrue(second)

    def test_unqualified_practitioner_blocked(self):
        other_service = self.env["paramedic.service"].create({
            "name": "Specialist Only", "duration": 1.0,
        })
        # explicitly restrict to a *different* practitioner than self.practitioner
        other_user = self.env["res.users"].create({
            "name": "Other Practitioner", "login": "other_practitioner",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
        })
        other = self.env["paramedic.practitioner"].create({
            "user_id": other_user.id})
        other_service.practitioner_ids = [(6, 0, [other.id])]
        with self.assertRaises(ValidationError):
            self._appt(service_id=other_service.id)

    def test_gated_service_requires_condition(self):
        gated = self.env["paramedic.service"].create({
            "name": "Session 1", "duration": 1.0,
            "requires_patch_test": True,
        })
        with self.assertRaises(ValidationError):
            self._appt(service_id=gated.id)

    def test_gated_service_requires_clear_patch_test(self):
        gated = self.env["paramedic.service"].create({
            "name": "Session 1", "duration": 1.0,
            "requires_patch_test": True,
        })
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
        })
        with self.assertRaises(ValidationError):
            self._appt(service_id=gated.id, condition_id=condition.id)

        self.env["patient.patch_test"].create({
            "condition_id": condition.id, "pigment_name": "Batch A",
            "result": "clear",
        })
        appt = self._appt(service_id=gated.id, condition_id=condition.id)
        self.assertTrue(appt)

    def test_gated_service_requires_signed_consent(self):
        gated = self.env["paramedic.service"].create({
            "name": "Session 1", "duration": 1.0,
            "requires_treatment_consent": True,
        })
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
        })
        with self.assertRaises(ValidationError):
            self._appt(service_id=gated.id, condition_id=condition.id)

        consent = self.env["patient.consent"].create({
            "condition_id": condition.id, "consent_type": "treatment",
        })
        consent.action_mark_signed()
        appt = self._appt(service_id=gated.id, condition_id=condition.id)
        self.assertTrue(appt)

    def test_complete_creates_treatment_session(self):
        session_service = self.env["paramedic.service"].create({
            "name": "Ink Session", "duration": 1.0,
            "creates_treatment_session": True,
        })
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
            "area": "Left hand",
        })
        appt = self._appt(service_id=session_service.id, condition_id=condition.id)
        self.assertFalse(appt.session_id)
        appt.action_complete()
        self.assertEqual(appt.state, "completed")
        self.assertTrue(appt.session_id)
        self.assertEqual(appt.session_id.condition_id, condition)
        self.assertEqual(appt.session_id.area_treated, "Left hand")

    def test_confirm_sends_email(self):
        appt = self._appt(state="requested")
        appt.action_confirm()
        self.assertEqual(appt.state, "confirmed")
