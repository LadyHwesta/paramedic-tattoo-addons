# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .practice_types import local_when


class PracticeSession(models.Model):
    _name = "practice.session"
    _description = "Treatment Session"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "display_name"

    plan_id = fields.Many2one(
        "practice.plan", string="Treatment Plan", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="plan_id.partner_id", store=True, string="Client")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    practitioner_id = fields.Many2one(
        "practice.practitioner", string="Practitioner", tracking=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True, tracking=True)
    session_number = fields.Integer(
        compute="_compute_session_number", store=True,
        help="This session's position among the plan's sessions, in date "
             "order.")
    area_treated = fields.Char(string="Area / Focus")
    product_name = fields.Char(
        string="Products Used", tracking=True,
        help="Oils, remedies, pigments or anything else used on the client.")
    product_lot = fields.Char(string="Lot #", tracking=True)
    notes = fields.Text(string="Session Notes")
    aftercare_given = fields.Boolean(default=True)
    aftercare_notes = fields.Text()
    adverse_reaction = fields.Boolean(string="Reaction or Concern", tracking=True)
    adverse_reaction_notes = fields.Text(string="Reaction Notes")
    next_session_recommended_date = fields.Date(string="Next Session Recommended")

    before_photo_ids = fields.Many2many(
        "ir.attachment", "practice_session_before_photo_rel",
        "session_id", "attachment_id", string="Before Photos")
    after_photo_ids = fields.Many2many(
        "ir.attachment", "practice_session_after_photo_rel",
        "session_id", "attachment_id", string="After Photos")

    @api.depends("partner_id.name", "date")
    def _compute_display_name(self):
        for session in self:
            session.display_name = "%s - %s" % (
                session.partner_id.name or self.env._("Client"), local_when(self.env, session.date))

    @api.depends("plan_id.session_ids.date")
    def _compute_session_number(self):
        for plan in self.mapped("plan_id"):
            ordered = plan.session_ids.sorted("date")
            for index, session in enumerate(ordered, start=1):
                session.session_number = index
