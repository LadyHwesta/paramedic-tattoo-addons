# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ParamedicPractitioner(models.Model):
    _name = "paramedic.practitioner"
    _description = "Practitioner"
    _inherit = ["mail.thread"]
    _rec_name = "display_name"

    user_id = fields.Many2one(
        "res.users", string="User", required=True, ondelete="restrict",
        tracking=True,
        help="The login this practitioner uses. Their name and photo come "
             "from this user's contact record.")
    partner_id = fields.Many2one(
        related="user_id.partner_id", string="Contact", store=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    resource_calendar_id = fields.Many2one(
        "resource.calendar", string="Working Hours", tracking=True,
        help="This practitioner's schedule - time off and holidays on this "
             "calendar are respected when computing open appointment slots.")
    license_number = fields.Char(
        string="Body Art / Cosmetology Licence #", tracking=True)
    npi_number = fields.Char(
        string="NPI Number",
        help="National Provider Identifier - not needed until/unless the "
             "practice bills insurance directly.")
    color = fields.Integer(string="Calendar Color")
    active = fields.Boolean(default=True, tracking=True)

    _user_uniq = models.Constraint(
        "unique(user_id)",
        "This user is already set up as a practitioner.",
    )

    @api.depends("partner_id.name")
    def _compute_display_name(self):
        for practitioner in self:
            practitioner.display_name = practitioner.partner_id.name or self.env._(
                "Practitioner")
