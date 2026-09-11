# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPatientRecords(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_user = cls.env["res.users"].create({
            "name": "Staff Practitioner", "login": "staff_practitioner",
            "group_ids": [(6, 0, [
                cls.env.ref("paramedic_base.group_paramedic_staff").id,
                cls.env.ref("base.group_user").id,
            ])],
        })
        cls.practitioner = cls.env["paramedic.practitioner"].create({
            "user_id": cls.staff_user.id,
        })
        cls.patient = cls.env["res.partner"].create({
            "name": "Pat Doe", "is_patient": True,
        })

    def test_patient_ref_assigned_once(self):
        self.assertTrue(self.patient.patient_ref)
        self.assertTrue(self.patient.patient_ref.startswith("PT"))
        first_ref = self.patient.patient_ref
        # re-saving is_patient=True again must not reassign the number
        self.patient.is_patient = True
        self.assertEqual(self.patient.patient_ref, first_ref)

    def test_patient_ref_not_assigned_to_non_patients(self):
        other = self.env["res.partner"].create({"name": "Not A Patient"})
        self.assertFalse(other.patient_ref)

    def test_practitioner_display_name(self):
        self.assertEqual(self.practitioner.display_name, "Staff Practitioner")

    def test_condition_display_name_and_default_state(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id,
            "condition_type": "areola_restoration",
            "practitioner_id": self.practitioner.id,
        })
        self.assertEqual(condition.state, "draft")
        self.assertIn("Pat Doe", condition.display_name)
        self.assertIn("Areola Restoration", condition.display_name)

    def test_condition_other_type_uses_free_text(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id,
            "condition_type": "other",
            "condition_type_other": "Stretch Mark Camouflage",
        })
        self.assertIn("Stretch Mark Camouflage", condition.display_name)

    def test_patch_test_read_date_defaults_to_three_days(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
        })
        test = self.env["patient.patch_test"].create({
            "condition_id": condition.id,
            "pigment_name": "Custom Blend #4",
            "application_date": date(2026, 1, 1),
        })
        self.assertEqual(test.read_date, date(2026, 1, 4))
        # once set, editing application_date doesn't silently move it
        test.application_date = date(2026, 1, 2)
        self.assertEqual(test.read_date, date(2026, 1, 4))

    def test_condition_patch_test_clear_tracks_latest_result(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
        })
        self.assertFalse(condition.patch_test_clear)
        first = self.env["patient.patch_test"].create({
            "condition_id": condition.id, "pigment_name": "Batch A",
            "application_date": date(2026, 1, 1), "result": "reaction",
        })
        self.assertFalse(condition.patch_test_clear)
        self.env["patient.patch_test"].create({
            "condition_id": condition.id, "pigment_name": "Batch B",
            "application_date": date(2026, 2, 1), "result": "clear",
        })
        self.assertTrue(condition.patch_test_clear)
        self.assertEqual(condition.latest_patch_test_id.pigment_name, "Batch B")
        self.assertNotEqual(condition.latest_patch_test_id, first)

    def test_session_numbering_in_date_order(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "scar_camouflage",
        })
        today = date.today()
        second = self.env["patient.treatment.session"].create({
            "condition_id": condition.id,
            "date": today + timedelta(days=30),
        })
        first = self.env["patient.treatment.session"].create({
            "condition_id": condition.id,
            "date": today,
        })
        self.assertEqual(first.session_number, 1)
        self.assertEqual(second.session_number, 2)

    def test_consent_mark_signed(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
        })
        consent = self.env["patient.consent"].create({
            "condition_id": condition.id, "consent_type": "treatment",
        })
        self.assertFalse(consent.signed)
        consent.action_mark_signed()
        self.assertTrue(consent.signed)

    def test_consent_report_renders(self):
        condition = self.env["patient.condition"].create({
            "partner_id": self.patient.id, "condition_type": "vitiligo",
        })
        consent = self.env["patient.consent"].create({
            "condition_id": condition.id, "consent_type": "patch_test",
        })
        report = self.env.ref("paramedic_base.action_report_patient_consent")
        html, content_type = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, consent.ids)
        self.assertEqual(content_type, "html")
        self.assertIn(b"Pat Doe", html)
        self.assertIn(b"Patch Test Consent", html)
