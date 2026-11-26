# -*- coding: utf-8 -*-
from odoo import fields, models


class PracticeSession(models.Model):
    _inherit = "practice.session"

    numbing_agent = fields.Char()
