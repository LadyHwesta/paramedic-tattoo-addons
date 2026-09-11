# -*- coding: utf-8 -*-
from datetime import timedelta
from urllib.parse import urlencode

from odoo import fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_ACTIVE_STATES = ("requested", "confirmed")


class ParamedicAppointmentPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "paramedic_appointment_count" in counters:
            partner = request.env.user.partner_id
            values["paramedic_appointment_count"] = request.env[
                "paramedic.appointment"].sudo().search_count([
                    ("partner_id", "=", partner.id),
                    ("state", "in", _ACTIVE_STATES),
                    ("start", ">=", fields.Datetime.now()),
                ])
        return values

    @staticmethod
    def _booking_horizon_days():
        param = request.env["ir.config_parameter"].sudo().get_param(
            "paramedic_appointment.booking_horizon_days", "21")
        try:
            return max(int(param), 1)
        except (TypeError, ValueError):
            return 21

    def _redirect(self, path, message=None, ok=True):
        if message:
            path += "?" + urlencode(
                {"appt_msg": message, "appt_ok": "1" if ok else "0"})
        return request.redirect(path)

    # ------------------------------------------------------------------
    @http.route(["/my/appointments"], type="http", auth="user", website=True)
    def my_appointments(self, **kw):
        partner = request.env.user.partner_id
        Appointment = request.env["paramedic.appointment"].sudo()
        now = fields.Datetime.now()
        upcoming = Appointment.search([
            ("partner_id", "=", partner.id),
            ("state", "in", _ACTIVE_STATES),
            ("start", ">=", now),
        ], order="start")
        past = Appointment.search([
            ("partner_id", "=", partner.id),
            ("start", "<", now),
        ], order="start desc", limit=50)
        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "paramedic_appointments",
            "upcoming": upcoming,
            "past": past,
            "now": now,
        })
        return request.render(
            "paramedic_appointment.portal_my_appointments", values)

    @http.route(["/my/appointment/<int:appointment_id>/cancel"], type="http",
                auth="user", website=True, methods=["POST"])
    def my_appointment_cancel(self, appointment_id, **post):
        partner = request.env.user.partner_id
        appointment = request.env["paramedic.appointment"].sudo().browse(
            appointment_id).exists()
        if not appointment or appointment.partner_id != partner:
            return request.not_found()
        if not appointment._portal_can_cancel():
            return self._redirect(
                "/my/appointments",
                "That appointment can no longer be cancelled online - "
                "please call the studio.", ok=False)
        appointment.action_cancel()
        return self._redirect("/my/appointments", "Appointment cancelled.")

    # ------------------------------------------------------------------
    @http.route(["/my/book"], type="http", auth="user", website=True)
    def my_book(self, **kw):
        partner = request.env.user.partner_id
        services = request.env["paramedic.service"].sudo().search([])
        eligible = services.filtered(
            lambda s: s._bookable_online_for(partner))
        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "paramedic_book",
            "services": eligible,
        })
        return request.render("paramedic_appointment.portal_book_service", values)

    @http.route(["/my/book/<int:service_id>"], type="http", auth="user",
                website=True)
    def my_book_service(self, service_id, **kw):
        partner = request.env.user.partner_id
        service = request.env["paramedic.service"].sudo().browse(
            service_id).exists()
        if not service or not service._bookable_online_for(partner):
            return request.not_found()

        now = fields.Datetime.now()
        horizon = now + timedelta(days=self._booking_horizon_days())
        practitioners = service._qualified_practitioners()
        slots_by_practitioner = []
        for practitioner in practitioners:
            raw_slots = practitioner._available_slots(service, now, horizon)
            slots = [
                (fields.Datetime.to_string(slot),
                 fields.Datetime.context_timestamp(request.env.user, slot)
                 .strftime("%a %b %d, %I:%M %p"))
                for slot in raw_slots
            ]
            if slots:
                slots_by_practitioner.append((practitioner, slots))

        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "paramedic_book",
            "service": service,
            "slots_by_practitioner": slots_by_practitioner,
        })
        return request.render("paramedic_appointment.portal_book_slots", values)

    @http.route(["/my/book/<int:service_id>/confirm"], type="http",
                auth="user", website=True, methods=["POST"])
    def my_book_confirm(self, service_id, **post):
        partner = request.env.user.partner_id
        service = request.env["paramedic.service"].sudo().browse(
            service_id).exists()
        practitioner = request.env["paramedic.practitioner"].sudo().browse(
            int(post.get("practitioner_id", 0))).exists()
        start = fields.Datetime.to_datetime(post.get("start"))
        if not (service and practitioner and start):
            return request.not_found()

        if not partner.is_patient:
            partner.sudo().is_patient = True
        condition = service._find_eligible_condition(partner)

        try:
            request.env["paramedic.appointment"].sudo().create({
                "partner_id": partner.id,
                "condition_id": condition.id if condition else False,
                "service_id": service.id,
                "practitioner_id": practitioner.id,
                "start": start,
                "state": "requested",
                "source": "portal",
            })
        except (UserError, ValidationError) as exc:
            return self._redirect(
                "/my/book/%s" % service_id, exc.args[0], ok=False)
        return self._redirect(
            "/my/appointments",
            "Request sent - we'll confirm your %s appointment shortly."
            % service.name)
