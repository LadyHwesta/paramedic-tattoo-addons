# -*- coding: utf-8 -*-
from odoo import fields, models


class PracticePlan(models.Model):
    _inherit = "practice.plan"

    related_surgery_date = fields.Date(
        string="Related Surgery Date",
        help="For example the mastectomy date for an areola restoration.")
