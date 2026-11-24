# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.tools import format_date, format_time

from odoo.addons.my_day.models.my_day import LIMIT

FOLLOW_UP_DAYS = 14


class MyDay(models.AbstractModel):
    _inherit = "my.day"

    @api.model
    def _my_day_sections(self):
        sections = super()._my_day_sections()
        plan = [s for s in sections if s[0] == "plan"]
        attention = [s for s in sections if s[0] != "plan"]
        # Appointments right under the calendar; the practice's queues first on the right.
        at = next((i + 1 for i, s in enumerate(plan) if s[1] == "schedule"), 0)
        plan[at:at] = [("plan", "appointments")]
        return plan + [("attention", "booking_requests"), ("attention", "patch_tests"),
                       ("attention", "follow_ups")] + attention

    def _my_day_practitioner(self):
        Practitioner = self._my_day_model("paramedic.practitioner")
        if Practitioner is None:
            return None
        return Practitioner.search([("user_id", "=", self.env.uid)], limit=1)

    def _my_day_section_appointments(self, today):
        Appointment = self._my_day_model("paramedic.appointment")
        if Appointment is None:
            return None
        start, end = self._my_day_bounds(today)
        domain = [("start", ">=", start), ("start", "<", end),
                  ("state", "in", ("requested", "confirmed", "completed"))]
        practitioner = self._my_day_practitioner()
        if practitioner:  # a practitioner sees their own book; others the whole practice's
            domain.append(("practitioner_id", "=", practitioner.id))
        appointments = Appointment.search(domain, order="start")
        tz = self._my_day_tz().zone
        now = fields.Datetime.now()
        items = []
        for appt in appointments:
            meta = appt.service_id.name or ""
            if not practitioner and appt.practitioner_id:
                meta = f"{meta} · {appt.practitioner_id.display_name}"
            if appt.state == "requested":
                meta = _("%s · not confirmed yet", meta)
            elif appt.state == "completed":
                meta = _("%s · done", meta)
            buttons = []
            if appt.state == "confirmed" and appt.start <= now:
                buttons.append(self._my_day_button(
                    _("Complete"), "fa-check", "paramedic.appointment", "action_complete",
                    after="reload", style="success"))
            items.append(self._my_day_item(
                appt, name=appt.partner_id.name,
                when=format_time(self.env, appt.start, tz=tz, time_format="short"),
                meta=meta, now=appt.start <= now <= (appt.stop or appt.start),
                buttons=buttons))
        return {
            "title": _("Today's appointments"), "icon": "fa-user-md", "count": len(items),
            "items": items, "empty": _("No appointments today."),
            "more": self._my_day_more(
                _("All appointments"), "paramedic.appointment",
                [("practitioner_id", "=", practitioner.id)] if practitioner else [],
                _("Appointments")),
        }

    def _my_day_section_booking_requests(self, today):
        Appointment = self._my_day_model("paramedic.appointment")
        if Appointment is None:
            return None
        domain = [("state", "=", "requested"), ("start", ">=", fields.Datetime.now())]
        requests = Appointment.search(domain, order="start", limit=LIMIT)
        tz = self._my_day_tz().zone
        items = [self._my_day_item(
            appt, name=appt.partner_id.name,
            meta=" · ".join(filter(None, [appt.service_id.name, appt.practitioner_id.display_name])),
            when=format_date(self.env, appt.start.date(), date_format="d MMM") + " "
            + format_time(self.env, appt.start, tz=tz, time_format="short"),
            buttons=[self._my_day_button(_("Confirm"), "fa-check", "paramedic.appointment",
                                         "action_confirm", after="remove", style="success")])
            for appt in requests]
        return {
            "title": _("Booking requests"), "icon": "fa-inbox", "count": Appointment.search_count(domain),
            "items": items, "empty": _("No requests waiting."),
            "more": self._my_day_more(_("All requests"), "paramedic.appointment", domain,
                                      _("Booking Requests")),
        }

    def _my_day_section_patch_tests(self, today):
        PatchTest = self._my_day_model("patient.patch_test")
        if PatchTest is None:
            return None
        domain = [("result", "=", "pending"), ("read_date", "<=", today)]
        tests = PatchTest.search(domain, order="read_date", limit=LIMIT)
        items = [self._my_day_item(
            test, name=test.partner_id.name, meta=test.pigment_name or "",
            when=_("Today") if test.read_date == today
            else format_date(self.env, test.read_date, date_format="d MMM"),
            overdue=test.read_date < today) for test in tests]
        return {
            "title": _("Patch tests to read"), "icon": "fa-eyedropper",
            "count": PatchTest.search_count(domain), "items": items,
            "empty": _("No patch tests to read."),
            "more": self._my_day_more(_("All pending patch tests"), "patient.patch_test",
                                      [("result", "=", "pending")], _("Patch Tests")),
        }

    def _my_day_section_follow_ups(self, today):
        Session = self._my_day_model("patient.treatment.session")
        Appointment = self._my_day_model("paramedic.appointment")
        if Session is None or Appointment is None:
            return None
        horizon = today + timedelta(days=FOLLOW_UP_DAYS)
        sessions = Session.search([("next_session_recommended_date", "!=", False),
                                   ("next_session_recommended_date", "<=", horizon)],
                                  order="next_session_recommended_date")
        booked = set(Appointment.search([
            ("partner_id", "in", sessions.partner_id.ids), ("start", ">=", fields.Datetime.now()),
            ("state", "in", ("requested", "confirmed"))]).partner_id.ids)
        # The latest session per patient decides; patients already booked are fine.
        latest = {}
        for session in sessions.sorted("date"):
            latest[session.partner_id.id] = session
        due = [s for pid, s in latest.items() if pid not in booked
               and s == Session.search([("partner_id", "=", pid)], order="date desc", limit=1)]
        due.sort(key=lambda s: s.next_session_recommended_date)
        items = [self._my_day_item(
            s, name=s.partner_id.name,
            meta=dict(s.condition_id._fields["condition_type"].selection).get(
                s.condition_id.condition_type, ""),
            when=format_date(self.env, s.next_session_recommended_date, date_format="d MMM"),
            overdue=s.next_session_recommended_date < today) for s in due[:LIMIT]]
        return {
            "title": _("Follow-ups to book"), "icon": "fa-calendar-plus-o", "count": len(due),
            "items": items, "empty": _("Every patient due back has a booking."),
            "more": self._my_day_more(
                _("All sessions due back"), "patient.treatment.session",
                [("next_session_recommended_date", "<=", fields.Date.to_string(horizon))],
                _("Sessions Due Back")),
        }
