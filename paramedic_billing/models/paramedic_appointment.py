# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ParamedicAppointment(models.Model):
    _inherit = "paramedic.appointment"

    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True, copy=False)
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Payment")
    to_invoice = fields.Boolean(compute="_compute_to_invoice", search="_search_to_invoice")

    @api.depends("state", "invoice_id")
    def _compute_to_invoice(self):
        for appt in self:
            appt.to_invoice = appt.state == "completed" and not appt.invoice_id

    def _search_to_invoice(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise UserError(_("Unsupported search."))
        domain = [("state", "=", "completed"), ("invoice_id", "=", False)]
        return domain if (operator == "=") == value else ["!", "&", *domain]

    def action_create_invoice(self):
        invoices = self.env["account.move"]
        for appt in self:
            if appt.invoice_id:
                raise UserError(_("%s already has an invoice.", appt.display_name))
            if appt.state != "completed":
                raise UserError(_("Complete %s before invoicing it.", appt.display_name))
            product = appt.service_id.product_id
            if not product:
                raise UserError(_("Give the service %s a price first (Configuration, Services).",
                                  appt.service_id.name))
            day = fields.Date.context_today(self, appt.start)
            appt.invoice_id = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": appt.partner_id.id,
                "invoice_origin": appt.display_name,
                "invoice_line_ids": [(0, 0, {
                    "product_id": product.id,
                    "name": "%s, %s" % (appt.service_id.name, day.strftime("%b %d, %Y")),
                    "quantity": 1,
                })],
            })
            appt.message_post(body=_("Invoice %s created.", appt.invoice_id._get_html_link()))
            invoices |= appt.invoice_id
        return self._open_invoices(invoices)

    def action_view_invoice(self):
        return self._open_invoices(self.invoice_id)

    def _open_invoices(self, invoices):
        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) == 1:
            action.update(views=[(False, "form")], res_id=invoices.id)
        else:
            action["domain"] = [("id", "in", invoices.ids)]
        return action
