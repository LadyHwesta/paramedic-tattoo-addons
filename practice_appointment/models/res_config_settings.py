# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    practice_reminder_lead_days = fields.Integer(
        string="Appointment reminder lead time (days)",
        config_parameter="practice_appointment.reminder_lead_days", default=2)
    practice_booking_horizon_days = fields.Integer(
        string="Online booking horizon (days)",
        config_parameter="practice_appointment.booking_horizon_days", default=21,
        help="How many days ahead the client self-booking page shows open "
             "times for.")
