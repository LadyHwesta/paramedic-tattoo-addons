# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    paramedic_reminder_lead_days = fields.Integer(
        string="Appointment reminder lead time (days)",
        config_parameter="paramedic_appointment.reminder_lead_days", default=2)
    paramedic_booking_horizon_days = fields.Integer(
        string="Online booking horizon (days)",
        config_parameter="paramedic_appointment.booking_horizon_days", default=21,
        help="How many days ahead the patient self-booking page shows open "
             "times for.")
