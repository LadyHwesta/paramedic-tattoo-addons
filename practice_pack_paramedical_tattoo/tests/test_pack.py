# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParamedicalTattooPack(TransactionCase):

    def test_new_records_default_to_the_tattoo_setup(self):
        client = self.env["res.partner"].create({"name": "Grace Hill", "is_client": True})
        plan = self.env["practice.plan"].create({
            "partner_id": client.id, "related_surgery_date": date(2025, 3, 1)})
        self.assertEqual(plan.plan_type_id, self.env.ref(
            "practice_pack_paramedical_tattoo.plan_type_areola_restoration"))
        test = self.env["practice.test"].create({
            "plan_id": plan.id, "product_name": "Areola Blend 2", "test_date": date(2026, 1, 1)})
        self.assertEqual(test.read_date, date(2026, 1, 4))
        consent = self.env["practice.consent"].create({"plan_id": plan.id, "consent_type": "treatment"})
        self.assertIn("pigment into the skin", consent.form_id.body)

    def test_health_flags_are_tags_on_the_client(self):
        flag = self.env.ref("practice_pack_paramedical_tattoo.health_flag_keloid")
        client = self.env["res.partner"].create({
            "name": "Grace Hill", "is_client": True, "health_flag_ids": [(4, flag.id)]})
        self.assertIn("keloid", client.health_flag_ids.name)

    def test_session_records_the_numbing_agent(self):
        client = self.env["res.partner"].create({"name": "Grace Hill", "is_client": True})
        plan = self.env["practice.plan"].create({"partner_id": client.id})
        session = self.env["practice.session"].create({"plan_id": plan.id, "numbing_agent": "Lidocaine 4%"})
        self.assertEqual(session.numbing_agent, "Lidocaine 4%")
