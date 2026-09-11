# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PatientTreatmentSession(models.Model):
    _name = "patient.treatment.session"
    _description = "Treatment Session"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "display_name"

    condition_id = fields.Many2one(
        "patient.condition", string="Condition", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="condition_id.partner_id", store=True, string="Patient")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    practitioner_id = fields.Many2one(
        "paramedic.practitioner", string="Practitioner", tracking=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True, tracking=True)
    session_number = fields.Integer(
        compute="_compute_session_number", store=True,
        help="This session's position among the condition's sessions, in "
             "date order.")
    area_treated = fields.Char()
    pigment_name = fields.Char(tracking=True)
    pigment_lot = fields.Char(string="Pigment Lot #", tracking=True)
    numbing_agent = fields.Char()
    notes = fields.Text(string="Clinical Notes")
    aftercare_given = fields.Boolean(default=True)
    aftercare_notes = fields.Text()
    adverse_reaction = fields.Boolean(tracking=True)
    adverse_reaction_notes = fields.Text()
    next_session_recommended_date = fields.Date()

    before_photo_ids = fields.Many2many(
        "ir.attachment", "patient_session_before_photo_rel",
        "session_id", "attachment_id", string="Before Photos")
    after_photo_ids = fields.Many2many(
        "ir.attachment", "patient_session_after_photo_rel",
        "session_id", "attachment_id", string="After Photos")

    @api.depends("partner_id.name", "date")
    def _compute_display_name(self):
        for session in self:
            session.display_name = "%s - %s" % (
                session.partner_id.name or self.env._("Patient"),
                session.date or self.env._("no date"),
            )

    @api.depends("condition_id.session_ids.date")
    def _compute_session_number(self):
        for condition in self.mapped("condition_id"):
            ordered = condition.session_ids.sorted("date")
            for index, session in enumerate(ordered, start=1):
                session.session_number = index
