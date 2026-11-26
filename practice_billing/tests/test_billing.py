# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.practice_appointment.tests.common import PracticeAppointmentCommon


@tagged("post_install", "-at_install")
class TestBilling(PracticeAppointmentCommon):

    def _appointment(self, state="completed"):
        return self.env["practice.appointment"].create({
            "partner_id": self.client.id, "service_id": self.service.id,
            "practitioner_id": self.practitioner.id,
            "start": self.next_monday + timedelta(hours=10), "state": state,
        })

    def test_a_price_creates_the_service_product(self):
        self.assertFalse(self.service.product_id)
        self.service.list_price = 250
        product = self.service.product_id
        self.assertEqual((product.name, product.type, product.lst_price), (self.service.name, "service", 250))
        self.assertFalse(product.purchase_ok)
        self.service.list_price = 275
        self.assertEqual(self.service.product_id, product)
        self.assertEqual(product.lst_price, 275)

    def test_completed_appointment_becomes_an_invoice(self):
        self.service.list_price = 250
        appt = self._appointment()
        self.assertTrue(appt.to_invoice)
        self.assertIn(appt, self.env["practice.appointment"].search([("to_invoice", "=", True)]))
        action = appt.action_create_invoice()
        invoice = appt.invoice_id
        self.assertEqual(action["res_id"], invoice.id)
        self.assertEqual(invoice.partner_id, self.client)
        self.assertEqual(invoice.amount_untaxed, 250)
        self.assertIn(self.service.name, invoice.invoice_line_ids.name)
        self.assertFalse(appt.to_invoice)
        self.assertNotIn(appt, self.env["practice.appointment"].search([("to_invoice", "=", True)]))
        self.assertFalse(invoice.invoice_date)  # dated when it's confirmed
        invoice.action_post()
        self.assertEqual(invoice.invoice_date, fields.Date.context_today(invoice))
        self.assertEqual(appt.payment_state, "not_paid")

    def test_only_completed_and_priced_and_once(self):
        appt = self._appointment()
        with self.assertRaisesRegex(UserError, "price"):
            appt.action_create_invoice()
        self.service.list_price = 100
        upcoming = self._appointment(state="confirmed")
        upcoming.start = self.next_monday + timedelta(hours=13)
        with self.assertRaisesRegex(UserError, "Complete"):
            upcoming.action_create_invoice()
        appt.action_create_invoice()
        with self.assertRaisesRegex(UserError, "already"):
            appt.action_create_invoice()
