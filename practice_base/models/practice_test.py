# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class PracticeTest(models.Model):
    """A check before treatment starts, such as a skin patch test or a
    fitness assessment, with the product and lot used and its result."""
    _name = "practice.test"
    _description = "Pre-treatment Test"
    _inherit = ["mail.thread"]
    _order = "test_date desc, id desc"
    _rec_name = "display_name"

    plan_id = fields.Many2one(
        "practice.plan", string="Treatment Plan", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="plan_id.partner_id", store=True, string="Client")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    test_type_id = fields.Many2one(
        "practice.test.type", string="Test", required=True, tracking=True,
        ondelete="restrict",
        default=lambda self: self.env["practice.test.type"].search([], limit=1))
    product_name = fields.Char(
        string="Product Tested", tracking=True,
        help="The oil, herb, pigment or product tested, if any.")
    product_lot = fields.Char(string="Lot #", tracking=True)
    test_date = fields.Date(
        string="Done On", default=fields.Date.context_today, required=True,
        tracking=True)
    read_date = fields.Date(
        compute="_compute_read_date", store=True, readonly=False,
        string="Read On",
        help="From the test type's waiting time; change it if it's read sooner "
             "or later.")
    result = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("clear", "Clear"),
            ("reaction", "Reaction / Concern"),
        ],
        default="pending", required=True, tracking=True)
    result_notes = fields.Text()

    @api.depends("partner_id.name", "test_type_id.name", "product_name", "test_date")
    def _compute_display_name(self):
        for test in self:
            what = " - ".join(filter(None, [test.test_type_id.name, test.product_name]))
            test.display_name = "%s - %s (%s)" % (
                test.partner_id.name or self.env._("Client"), what,
                test.test_date or self.env._("no date"))

    @api.depends("test_date", "test_type_id.read_after_days")
    def _compute_read_date(self):
        for test in self:
            if test.test_date and not test.read_date:
                test.read_date = test.test_date + timedelta(
                    days=test.test_type_id.read_after_days or 0)

    def action_mark_clear(self):
        self.write({"result": "clear"})

    def action_mark_reaction(self):
        self.write({"result": "reaction"})
