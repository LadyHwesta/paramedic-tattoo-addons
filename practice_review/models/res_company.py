# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    practice_review_moderator_id = fields.Many2one(
        "res.users", string="Reviews Checked By",
        help="Gets a to-do for every new review. Leave empty for the administrator.")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    practice_review_moderator_id = fields.Many2one(
        related="company_id.practice_review_moderator_id", readonly=False)
