# -*- coding: utf-8 -*-
from datetime import timedelta

import pytz

from odoo import fields, models
from odoo.tools.intervals import Intervals

_ACTIVE_STATES = ("requested", "confirmed")


class ParamedicPractitioner(models.Model):
    _inherit = "paramedic.practitioner"

    service_ids = fields.Many2many(
        "paramedic.service", "paramedic_practitioner_service_rel",
        "practitioner_id", "service_id", string="Qualified Services",
        help="Leave empty to allow this practitioner to perform any "
             "service.")

    def _free_intervals(self, dt_from, dt_to):
        """Open work time between two naive (UTC) datetimes, minus this
        practitioner's existing active appointments. Returns an
        ``Intervals`` of naive UTC (start, stop, appointments) triples."""
        self.ensure_one()
        empty = Intervals([])
        if not self.resource_calendar_id or dt_from >= dt_to:
            return empty

        aware_from = pytz.UTC.localize(dt_from)
        aware_to = pytz.UTC.localize(dt_to)
        work = self.resource_calendar_id._work_intervals_batch(
            aware_from, aware_to)[False]

        busy_appointments = self.env["paramedic.appointment"].search([
            ("practitioner_id", "=", self.id),
            ("state", "in", _ACTIVE_STATES),
            ("start", "<", dt_to),
            ("stop", ">", dt_from),
        ])
        busy = Intervals([
            (pytz.UTC.localize(appt.start), pytz.UTC.localize(appt.stop), appt)
            for appt in busy_appointments
        ])

        free = work - busy
        return Intervals([
            (start.astimezone(pytz.UTC).replace(tzinfo=None),
             stop.astimezone(pytz.UTC).replace(tzinfo=None), recs)
            for start, stop, recs in free
        ])

    def _available_slots(self, service, dt_from, dt_to, limit=20):
        """Candidate appointment start times for ``service`` with this
        practitioner between two naive UTC datetimes, packed back-to-back
        (including the service's buffer) from the start of each open work
        period. Returns a list of naive UTC datetimes, earliest first."""
        self.ensure_one()
        slot_minutes = service.duration * 60 + service.buffer_minutes
        slot_length = timedelta(minutes=slot_minutes)
        slots = []
        for start, stop, _recs in self._free_intervals(dt_from, dt_to):
            cursor = start
            while cursor + slot_length <= stop and len(slots) < limit:
                slots.append(cursor)
                cursor += slot_length
            if len(slots) >= limit:
                break
        return slots
