# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PracticePlan(models.Model):
    """One thing a client is being treated for, and the thread every
    consent, pre-treatment test and session for it hangs off."""
    _name = "practice.plan"
    _description = "Treatment Plan"
    _inherit = ["mail.thread"]
    _order = "start_date desc, id desc"
    _rec_name = "display_name"

    partner_id = fields.Many2one(
        "res.partner", string="Client", required=True, ondelete="cascade",
        domain=[("is_client", "=", True)], index=True, tracking=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    plan_type_id = fields.Many2one(
        "practice.plan.type", string="Treatment", required=True, tracking=True,
        ondelete="restrict",
        default=lambda self: self.env["practice.plan.type"].search([], limit=1))
    area = fields.Char(string="Area / Focus", tracking=True,
                       help="Where on the body, or what the work focuses on.")
    start_date = fields.Date(string="Started", default=fields.Date.context_today)
    background = fields.Text(
        help="What led the client here: history, goals, anything from a "
             "referring provider.")
    practitioner_id = fields.Many2one(
        "practice.practitioner", string="Primary Practitioner", tracking=True,
        help="Kept the same across the plan for continuity.")
    state = fields.Selection(
        selection=[
            ("draft", "Intake"),
            ("active", "In Treatment"),
            ("completed", "Completed"),
            ("discontinued", "Discontinued"),
        ],
        default="draft", required=True, tracking=True)
    active = fields.Boolean(default=True)

    consent_ids = fields.One2many("practice.consent", "plan_id", string="Consents")
    test_ids = fields.One2many("practice.test", "plan_id", string="Pre-treatment Tests")
    session_ids = fields.One2many("practice.session", "plan_id", string="Sessions")
    session_count = fields.Integer(compute="_compute_session_count")
    latest_test_id = fields.Many2one("practice.test", compute="_compute_latest_test")
    test_clear = fields.Boolean(
        string="Test Clear", compute="_compute_test_clear", store=True,
        help="True once the most recent pre-treatment test for this plan came "
             "back clear.")

    @api.depends("partner_id.name", "plan_type_id.name", "area")
    def _compute_display_name(self):
        for plan in self:
            label = plan.plan_type_id.name or ""
            if plan.area:
                label = "%s (%s)" % (label, plan.area)
            plan.display_name = "%s - %s" % (
                plan.partner_id.name or self.env._("Client"), label)

    @api.depends("session_ids")
    def _compute_session_count(self):
        for plan in self:
            plan.session_count = len(plan.session_ids)

    def _latest_test(self):
        self.ensure_one()
        return self.test_ids.sorted(lambda t: t.test_date or fields.Date.today())[-1:]

    @api.depends("test_ids.result", "test_ids.test_date")
    def _compute_latest_test(self):
        for plan in self:
            plan.latest_test_id = plan._latest_test()

    @api.depends("test_ids.result", "test_ids.test_date")
    def _compute_test_clear(self):
        for plan in self:
            latest = plan._latest_test()
            plan.test_clear = bool(latest and latest.result == "clear")

    def action_view_sessions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Sessions - %s", self.display_name),
            "res_model": "practice.session",
            "view_mode": "list,form",
            "domain": [("plan_id", "=", self.id)],
            "context": {
                "default_plan_id": self.id,
                "default_partner_id": self.partner_id.id,
                "default_practitioner_id": self.practitioner_id.id,
            },
        }
