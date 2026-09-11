# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo.tests import tagged

from .common import ParamedicAppointmentCommon


@tagged("post_install", "-at_install")
class TestAvailability(ParamedicAppointmentCommon):
    def test_free_intervals_match_working_hours(self):
        window_start = self.next_monday
        window_end = self.next_monday + timedelta(days=7)
        free = self.practitioner._free_intervals(window_start, window_end)
        intervals = list(free)
        self.assertEqual(len(intervals), 1)
        start, stop, _recs = intervals[0]
        self.assertEqual(start, self.next_monday + timedelta(hours=9))
        self.assertEqual(stop, self.next_monday + timedelta(hours=17))

    def test_no_calendar_means_no_slots(self):
        self.practitioner.resource_calendar_id = False
        slots = self.practitioner._available_slots(
            self.service, self.next_monday, self.next_monday + timedelta(days=7))
        self.assertEqual(slots, [])

    def test_slots_are_back_to_back_with_no_buffer(self):
        slots = self.practitioner._available_slots(
            self.service, self.next_monday, self.next_monday + timedelta(days=1))
        expected = [
            self.next_monday + timedelta(hours=9 + h) for h in range(8)]
        self.assertEqual(slots, expected)

    def test_slots_respect_buffer_time(self):
        long_service = self.env["paramedic.service"].create({
            "name": "Long Session", "duration": 2.0, "buffer_minutes": 30,
        })
        slots = self.practitioner._available_slots(
            long_service, self.next_monday, self.next_monday + timedelta(days=1))
        expected = [
            self.next_monday + timedelta(hours=9),
            self.next_monday + timedelta(hours=11, minutes=30),
            self.next_monday + timedelta(hours=14),
        ]
        self.assertEqual(slots, expected)

    def test_slots_exclude_existing_appointment(self):
        nine = self.next_monday + timedelta(hours=9)
        self.env["paramedic.appointment"].create({
            "partner_id": self.patient.id,
            "service_id": self.service.id,
            "practitioner_id": self.practitioner.id,
            "start": nine,
            "state": "confirmed",
        })
        slots = self.practitioner._available_slots(
            self.service, self.next_monday, self.next_monday + timedelta(days=1))
        self.assertNotIn(nine, slots)
        self.assertIn(self.next_monday + timedelta(hours=10), slots)
        self.assertEqual(len(slots), 7)

    def test_cancelled_appointment_does_not_block_slot(self):
        nine = self.next_monday + timedelta(hours=9)
        appt = self.env["paramedic.appointment"].create({
            "partner_id": self.patient.id,
            "service_id": self.service.id,
            "practitioner_id": self.practitioner.id,
            "start": nine,
            "state": "confirmed",
        })
        appt.action_cancel()
        slots = self.practitioner._available_slots(
            self.service, self.next_monday, self.next_monday + timedelta(days=1))
        self.assertIn(nine, slots)
