# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PatientConsent(models.Model):
    _name = "patient.consent"
    _description = "Patient Consent"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "display_name"

    condition_id = fields.Many2one(
        "patient.condition", string="Condition", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="condition_id.partner_id", store=True, string="Patient")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    consent_type = fields.Selection(
        selection=[
            ("treatment", "Treatment Consent"),
            ("patch_test", "Patch Test Consent"),
            ("photo_release", "Photo Release"),
        ],
        required=True, default="treatment", tracking=True)
    date = fields.Date(default=fields.Date.context_today, tracking=True)
    signed = fields.Boolean(tracking=True)
    signature_method = fields.Char(
        string="Signed Via",
        help="e.g. 'In person, paper form' or 'Printed and countersigned'.")
    notes = fields.Text()

    @api.depends("partner_id.name", "consent_type", "date")
    def _compute_display_name(self):
        selection = dict(self._fields["consent_type"].selection)
        for consent in self:
            consent.display_name = "%s - %s (%s)" % (
                consent.partner_id.name or self.env._("Patient"),
                selection.get(consent.consent_type, ""),
                consent.date or self.env._("no date"),
            )

    def action_mark_signed(self):
        self.write({"date": fields.Date.context_today(self), "signed": True})
