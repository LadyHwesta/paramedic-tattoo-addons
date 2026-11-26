# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .practice_types import CONSENT_KINDS


class PracticeConsent(models.Model):
    _name = "practice.consent"
    _description = "Client Consent"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "display_name"

    plan_id = fields.Many2one(
        "practice.plan", string="Treatment Plan", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="plan_id.partner_id", store=True, string="Client")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    consent_type = fields.Selection(
        CONSENT_KINDS, required=True, default="treatment", tracking=True)
    form_id = fields.Many2one(
        "practice.consent.form", string="Form", tracking=True,
        compute="_compute_form_id", store=True, readonly=False,
        domain="[('kind', '=', consent_type)]",
        help="The wording the client agrees to. Defaults to the first active "
             "form of this kind.")
    date = fields.Date(default=fields.Date.context_today, tracking=True)
    signed = fields.Boolean(tracking=True)
    signature_method = fields.Char(
        string="Signed Via",
        help="e.g. 'In person, paper form' or 'Printed and countersigned'.")
    notes = fields.Text()

    @api.depends("consent_type")
    def _compute_form_id(self):
        Form = self.env["practice.consent.form"]
        for consent in self:
            if consent.form_id.kind != consent.consent_type:
                consent.form_id = Form.search([("kind", "=", consent.consent_type)], limit=1)

    @api.depends("partner_id.name", "consent_type", "date")
    def _compute_display_name(self):
        selection = dict(self._fields["consent_type"].selection)
        for consent in self:
            consent.display_name = "%s - %s (%s)" % (
                consent.partner_id.name or self.env._("Client"),
                selection.get(consent.consent_type, ""),
                consent.date or self.env._("no date"),
            )

    def action_mark_signed(self):
        self.write({"date": fields.Date.context_today(self), "signed": True})
