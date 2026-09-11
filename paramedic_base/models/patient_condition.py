# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PatientCondition(models.Model):
    _name = "patient.condition"
    _description = "Patient Condition"
    _inherit = ["mail.thread"]
    _order = "onset_date desc, id desc"
    _rec_name = "display_name"

    partner_id = fields.Many2one(
        "res.partner", string="Patient", required=True, ondelete="cascade",
        domain=[("is_patient", "=", True)], index=True, tracking=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    condition_type = fields.Selection(
        selection=[
            ("areola_restoration", "Areola Restoration"),
            ("scar_camouflage", "Scar Camouflage"),
            ("scalp_micropigmentation", "Scalp Micropigmentation"),
            ("vitiligo", "Vitiligo Repigmentation"),
            ("other", "Other"),
        ],
        required=True, tracking=True)
    condition_type_other = fields.Char(string="Other Condition")
    area = fields.Char(string="Area / Location", tracking=True)
    onset_date = fields.Date(
        string="Onset / Diagnosis Date",
        help="When the underlying condition began or was diagnosed.")
    related_surgery_date = fields.Date(
        string="Related Surgery Date",
        help="e.g. the mastectomy date for an areola restoration.")
    referring_notes = fields.Text()
    practitioner_id = fields.Many2one(
        "paramedic.practitioner", string="Primary Practitioner", tracking=True,
        help="Kept consistent across a patient's treatment for continuity "
             "of care.")
    state = fields.Selection(
        selection=[
            ("draft", "Intake"),
            ("active", "In Treatment"),
            ("completed", "Completed"),
            ("discontinued", "Discontinued"),
        ],
        default="draft", required=True, tracking=True)
    active = fields.Boolean(default=True)

    consent_ids = fields.One2many(
        "patient.consent", "condition_id", string="Consents")
    patch_test_ids = fields.One2many(
        "patient.patch_test", "condition_id", string="Patch Tests")
    session_ids = fields.One2many(
        "patient.treatment.session", "condition_id", string="Sessions")
    session_count = fields.Integer(compute="_compute_session_count")
    latest_patch_test_id = fields.Many2one(
        "patient.patch_test", compute="_compute_latest_patch_test")
    patch_test_clear = fields.Boolean(
        string="Patch Test Clear", compute="_compute_latest_patch_test",
        store=True,
        help="True once the most recent patch test for this condition came "
             "back clear.")

    @api.depends("partner_id.name", "condition_type", "condition_type_other")
    def _compute_display_name(self):
        selection = dict(self._fields["condition_type"].selection)
        for condition in self:
            label = (
                condition.condition_type_other
                if condition.condition_type == "other"
                else selection.get(condition.condition_type, "")
            )
            condition.display_name = "%s - %s" % (
                condition.partner_id.name or self.env._("Patient"), label)

    @api.depends("session_ids")
    def _compute_session_count(self):
        for condition in self:
            condition.session_count = len(condition.session_ids)

    @api.depends("patch_test_ids.result", "patch_test_ids.application_date")
    def _compute_latest_patch_test(self):
        for condition in self:
            latest = condition.patch_test_ids.sorted(
                lambda t: t.application_date or fields.Date.today())[-1:]
            condition.latest_patch_test_id = latest
            condition.patch_test_clear = bool(latest and latest.result == "clear")

    def action_view_sessions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Sessions - %s", self.display_name),
            "res_model": "patient.treatment.session",
            "view_mode": "list,form",
            "domain": [("condition_id", "=", self.id)],
            "context": {
                "default_condition_id": self.id,
                "default_partner_id": self.partner_id.id,
                "default_practitioner_id": self.practitioner_id.id,
            },
        }
