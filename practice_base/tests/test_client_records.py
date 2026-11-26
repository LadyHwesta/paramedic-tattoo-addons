# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestClientRecords(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_user = cls.env["res.users"].create({
            "name": "Staff Practitioner", "login": "staff_practitioner",
            "group_ids": [(6, 0, [
                cls.env.ref("practice_base.group_practice_staff").id,
                cls.env.ref("base.group_user").id,
            ])],
        })
        cls.practitioner = cls.env["practice.practitioner"].create({
            "user_id": cls.staff_user.id,
        })
        cls.client = cls.env["res.partner"].create({
            "name": "Pat Doe", "is_client": True,
        })

    def test_client_ref_assigned_once(self):
        self.assertTrue(self.client.client_ref)
        self.assertTrue(self.client.client_ref.startswith("CL"))
        first_ref = self.client.client_ref
        # re-saving is_client=True again must not reassign the number
        self.client.is_client = True
        self.assertEqual(self.client.client_ref, first_ref)

    def test_client_ref_not_assigned_to_non_clients(self):
        other = self.env["res.partner"].create({"name": "Not A Client"})
        self.assertFalse(other.client_ref)

    def test_practitioner_display_name(self):
        self.assertEqual(self.practitioner.display_name, "Staff Practitioner")

    def test_condition_display_name_and_default_state(self):
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id,
            "practitioner_id": self.practitioner.id,
            "plan_type_id": self.env.ref("practice_base.plan_type_general").id,
        })
        self.assertEqual(condition.state, "draft")
        self.assertIn("Pat Doe", condition.display_name)
        self.assertIn("General treatment", condition.display_name)

    def test_plan_uses_the_practice_own_treatment_types(self):
        sleep = self.env["practice.plan.type"].create({"name": "Sleep support"})
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id, "plan_type_id": sleep.id, "area": "Insomnia",
        })
        self.assertIn("Sleep support (Insomnia)", condition.display_name)

    def test_read_date_follows_the_test_type(self):
        quick = self.env["practice.test.type"].create({"name": "Fitness assessment"})
        plan = self.env["practice.plan"].create({"partner_id": self.client.id})
        test = self.env["practice.test"].create({
            "plan_id": plan.id, "test_type_id": quick.id, "test_date": date(2026, 1, 1)})
        self.assertEqual(test.read_date, date(2026, 1, 1))

    def test_consent_gets_the_form_of_its_kind(self):
        plan = self.env["practice.plan"].create({"partner_id": self.client.id})
        consent = self.env["practice.consent"].create({"plan_id": plan.id, "consent_type": "photo_release"})
        self.assertEqual(consent.form_id, self.env.ref("practice_base.consent_form_photo_release"))
        consent.consent_type = "test"
        self.assertEqual(consent.form_id.kind, "test")

    def test_patch_test_read_date_defaults_to_the_type_days(self):
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id,
        })
        test = self.env["practice.test"].create({
            "plan_id": condition.id,
            "product_name": "Custom Blend #4",
            "test_type_id": self.env.ref("practice_base.test_type_skin_patch").id,
            "test_date": date(2026, 1, 1),
        })
        self.assertEqual(test.read_date, date(2026, 1, 3))
        # once set, editing test_date doesn't silently move it
        test.test_date = date(2026, 1, 2)
        self.assertEqual(test.read_date, date(2026, 1, 3))

    def test_condition_test_clear_tracks_latest_result(self):
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id,
        })
        self.assertFalse(condition.test_clear)
        first = self.env["practice.test"].create({
            "plan_id": condition.id, "product_name": "Batch A",
            "test_date": date(2026, 1, 1), "result": "reaction",
        })
        self.assertFalse(condition.test_clear)
        self.env["practice.test"].create({
            "plan_id": condition.id, "product_name": "Batch B",
            "test_date": date(2026, 2, 1), "result": "clear",
        })
        self.assertTrue(condition.test_clear)
        self.assertEqual(condition.latest_test_id.product_name, "Batch B")
        self.assertNotEqual(condition.latest_test_id, first)

    def test_session_numbering_in_date_order(self):
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id,
        })
        today = date.today()
        second = self.env["practice.session"].create({
            "plan_id": condition.id,
            "date": today + timedelta(days=30),
        })
        first = self.env["practice.session"].create({
            "plan_id": condition.id,
            "date": today,
        })
        self.assertEqual(first.session_number, 1)
        self.assertEqual(second.session_number, 2)

    def test_consent_mark_signed(self):
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id,
        })
        consent = self.env["practice.consent"].create({
            "plan_id": condition.id, "consent_type": "treatment",
        })
        self.assertFalse(consent.signed)
        consent.action_mark_signed()
        self.assertTrue(consent.signed)

    def test_consent_report_renders(self):
        condition = self.env["practice.plan"].create({
            "partner_id": self.client.id,
        })
        consent = self.env["practice.consent"].create({
            "plan_id": condition.id, "consent_type": "test",
            "form_id": self.env.ref("practice_base.consent_form_test").id,
        })
        report = self.env.ref("practice_base.action_report_practice_consent")
        html, content_type = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, consent.ids)
        self.assertEqual(content_type, "html")
        self.assertIn(b"Pat Doe", html)
        self.assertIn(b"Pre-treatment Test Consent", html)
        self.assertIn(b"look for a reaction", html)
