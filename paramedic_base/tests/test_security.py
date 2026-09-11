# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParamedicSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({
            "name": "Confidential Patient", "is_patient": True,
        })
        cls.condition = cls.env["patient.condition"].create({
            "partner_id": cls.patient.id, "condition_type": "vitiligo",
        })
        cls.session = cls.env["patient.treatment.session"].create({
            "condition_id": cls.condition.id,
        })
        cls.portal_user = cls.env["res.users"].create({
            "name": "Portal Visitor", "login": "portal_visitor",
            "group_ids": [(6, 0, [cls.env.ref("base.group_portal").id])],
        })
        cls.plain_internal_user = cls.env["res.users"].create({
            "name": "Front Desk (no clinical access)", "login": "front_desk",
            "group_ids": [(6, 0, [cls.env.ref("base.group_user").id])],
        })

    def test_portal_user_cannot_read_conditions(self):
        with self.assertRaises(AccessError):
            self.env["patient.condition"].with_user(
                self.portal_user).search([])

    def test_portal_user_cannot_read_sessions(self):
        with self.assertRaises(AccessError):
            self.env["patient.treatment.session"].with_user(
                self.portal_user).browse(self.session.id).date

    def test_internal_user_without_group_cannot_read_conditions(self):
        with self.assertRaises(AccessError):
            self.env["patient.condition"].with_user(
                self.plain_internal_user).search([])

    def test_staff_group_can_read_conditions(self):
        staff = self.env["res.users"].create({
            "name": "Cleared Staff", "login": "cleared_staff",
            "group_ids": [(6, 0, [
                self.env.ref("base.group_user").id,
                self.env.ref("paramedic_base.group_paramedic_staff").id,
            ])],
        })
        found = self.env["patient.condition"].with_user(staff).search(
            [("id", "=", self.condition.id)])
        self.assertEqual(found, self.condition)
