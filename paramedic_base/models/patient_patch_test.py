# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class PatientPatchTest(models.Model):
    _name = "patient.patch_test"
    _description = "Pigment Patch Test"
    _inherit = ["mail.thread"]
    _order = "application_date desc, id desc"
    _rec_name = "display_name"

    condition_id = fields.Many2one(
        "patient.condition", string="Condition", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="condition_id.partner_id", store=True, string="Patient")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    pigment_name = fields.Char(required=True, tracking=True)
    pigment_lot = fields.Char(string="Pigment Lot #", tracking=True)
    application_date = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    read_date = fields.Date(
        compute="_compute_read_date", store=True, readonly=False,
        string="Read On",
        help="Defaults to 3 days after application; adjust if read sooner "
             "or later.")
    result = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("clear", "Clear"),
            ("reaction", "Reaction"),
        ],
        default="pending", required=True, tracking=True)
    reaction_notes = fields.Text()

    @api.depends("partner_id.name", "pigment_name", "application_date")
    def _compute_display_name(self):
        for test in self:
            test.display_name = "%s - %s (%s)" % (
                test.partner_id.name or self.env._("Patient"),
                test.pigment_name or "",
                test.application_date or self.env._("no date"),
            )

    @api.depends("application_date")
    def _compute_read_date(self):
        for test in self:
            if test.application_date and not test.read_date:
                test.read_date = test.application_date + timedelta(days=3)

    def action_mark_clear(self):
        self.write({"result": "clear"})

    def action_mark_reaction(self):
        self.write({"result": "reaction"})
