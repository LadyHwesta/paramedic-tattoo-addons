# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_ACTIVE_STATES = ("requested", "confirmed")


class ParamedicAppointment(models.Model):
    _name = "paramedic.appointment"
    _description = "Appointment"
    _inherit = ["mail.thread"]
    _order = "start"
    _rec_name = "display_name"

    partner_id = fields.Many2one(
        "res.partner", string="Patient", required=True,
        domain=[("is_patient", "=", True)], ondelete="cascade", tracking=True)
    condition_id = fields.Many2one(
        "patient.condition", string="Condition",
        domain="[('partner_id', '=', partner_id)]", tracking=True)
    service_id = fields.Many2one(
        "paramedic.service", string="Service", required=True, tracking=True)
    practitioner_id = fields.Many2one(
        "paramedic.practitioner", string="Practitioner", required=True,
        tracking=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    start = fields.Datetime(required=True, tracking=True)
    stop = fields.Datetime(compute="_compute_stop", store=True)
    duration_display = fields.Float(
        string="Duration (h)", related="service_id.duration")
    state = fields.Selection(
        selection=[
            ("requested", "Requested"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
            ("no_show", "No-show"),
        ],
        default="confirmed", required=True, tracking=True)
    source = fields.Selection(
        selection=[("backoffice", "Back office"), ("portal", "Website")],
        default="backoffice", readonly=True)
    notes = fields.Text()
    session_id = fields.Many2one(
        "patient.treatment.session", string="Treatment Session",
        readonly=True, copy=False)
    reminder_sent = fields.Boolean(default=False, copy=False, readonly=True)

    _stop_after_start = models.Constraint(
        "CHECK (stop > start)", "An appointment must end after it starts.")

    @api.depends("start", "service_id.duration", "service_id.buffer_minutes")
    def _compute_stop(self):
        for appt in self:
            if appt.start and appt.service_id:
                minutes = (
                    appt.service_id.duration * 60 + appt.service_id.buffer_minutes)
                appt.stop = appt.start + timedelta(minutes=minutes)
            else:
                appt.stop = appt.start

    @api.depends("partner_id.name", "service_id.name", "start")
    def _compute_display_name(self):
        for appt in self:
            appt.display_name = "%s - %s (%s)" % (
                appt.partner_id.name or self.env._("Patient"),
                appt.service_id.name or "", appt.start or "")

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    @api.constrains("practitioner_id", "start", "stop", "state")
    def _check_no_overlap(self):
        if self.env.context.get("skip_appointment_checks"):
            return
        for appt in self:
            if appt.state not in _ACTIVE_STATES:
                continue
            overlap = self.search_count([
                ("id", "!=", appt.id),
                ("practitioner_id", "=", appt.practitioner_id.id),
                ("state", "in", _ACTIVE_STATES),
                ("start", "<", appt.stop),
                ("stop", ">", appt.start),
            ])
            if overlap:
                raise ValidationError(_(
                    "%(practitioner)s already has an appointment that "
                    "overlaps %(start)s.",
                    practitioner=appt.practitioner_id.display_name,
                    start=appt.start))

    @api.constrains("practitioner_id", "service_id")
    def _check_practitioner_qualified(self):
        if self.env.context.get("skip_appointment_checks"):
            return
        for appt in self:
            qualified = appt.service_id.practitioner_ids
            if qualified and appt.practitioner_id not in qualified:
                raise ValidationError(_(
                    "%(practitioner)s isn't set up to perform %(service)s.",
                    practitioner=appt.practitioner_id.display_name,
                    service=appt.service_id.name))

    @api.constrains("service_id", "condition_id", "state")
    def _check_service_requirements(self):
        if self.env.context.get("skip_appointment_checks"):
            return
        for appt in self:
            if appt.state not in _ACTIVE_STATES:
                continue
            errors = appt._service_requirement_errors()
            if errors:
                raise ValidationError(_(
                    "%(service)s requires %(missing)s.",
                    service=appt.service_id.name, missing="; ".join(errors)))

    def _service_requirement_errors(self):
        self.ensure_one()
        service = self.service_id
        if not (service.requires_patch_test or service.requires_treatment_consent):
            return []
        if not self.condition_id:
            return [_("a condition on file to check against")]
        errors = []
        if service.requires_patch_test and not self.condition_id.patch_test_clear:
            errors.append(_("a clear patch test on file for this condition"))
        if service.requires_treatment_consent:
            signed = self.condition_id.consent_ids.filtered(
                lambda c: c.consent_type == "treatment" and c.signed)
            if not signed:
                errors.append(_(
                    "a signed treatment consent on file for this condition"))
        return errors

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_confirm(self):
        self.write({"state": "confirmed"})
        template = self.env.ref(
            "paramedic_appointment.mail_template_appointment_confirmed",
            raise_if_not_found=False)
        if template:
            for appt in self:
                template.send_mail(appt.id, force_send=False)

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_no_show(self):
        self.write({"state": "no_show"})

    def action_complete(self):
        for appt in self:
            appt.state = "completed"
            if appt.service_id.creates_treatment_session and not appt.session_id:
                if not appt.condition_id:
                    raise UserError(_(
                        "Set a condition on this appointment before "
                        "completing it - the treatment session needs one."))
                session = self.env["patient.treatment.session"].create({
                    "condition_id": appt.condition_id.id,
                    "practitioner_id": appt.practitioner_id.id,
                    "date": appt.start,
                    "area_treated": appt.condition_id.area,
                })
                appt.session_id = session

    def action_view_session(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "patient.treatment.session",
            "res_id": self.session_id.id,
            "view_mode": "form",
        }

    # ------------------------------------------------------------------
    # Portal booking
    # ------------------------------------------------------------------
    def _portal_can_cancel(self):
        self.ensure_one()
        return (
            self.state in _ACTIVE_STATES
            and self.start > fields.Datetime.now() + timedelta(hours=24)
        )

    @api.model
    def _cron_send_reminders(self):
        lead_days = self._reminder_lead_days()
        now = fields.Datetime.now()
        due = self.search([
            ("state", "=", "confirmed"),
            ("reminder_sent", "=", False),
            ("start", ">=", now),
            ("start", "<=", now + timedelta(days=lead_days)),
        ])
        template = self.env.ref(
            "paramedic_appointment.mail_template_appointment_reminder",
            raise_if_not_found=False)
        if not template or not due:
            return
        for appt in due:
            template.send_mail(appt.id, force_send=False)
        due.write({"reminder_sent": True})

    @api.model
    def _reminder_lead_days(self):
        param = self.env["ir.config_parameter"].sudo().get_param(
            "paramedic_appointment.reminder_lead_days", "2")
        try:
            return max(int(param), 0)
        except (TypeError, ValueError):
            return 2
