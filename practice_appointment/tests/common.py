# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase


class PracticeAppointmentCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # A Monday 09:00-17:00 UTC-only working-hours calendar, so slot
        # math in tests doesn't depend on the server's configured tz.
        cls.calendar = cls.env["resource.calendar"].create({
            "name": "Test Mon 9-17 UTC",
            "tz": "UTC",
            "attendance_ids": [(0, 0, {
                "name": "Monday",
                "dayofweek": "0",
                "hour_from": 9.0,
                "hour_to": 17.0,
                "day_period": "full_day",
            })],
        })
        cls.staff_user = cls.env["res.users"].create({
            "name": "Test Practitioner", "login": "test_practitioner",
            "group_ids": [(6, 0, [
                cls.env.ref("practice_base.group_practice_staff").id,
                cls.env.ref("base.group_user").id,
            ])],
        })
        cls.practitioner = cls.env["practice.practitioner"].create({
            "user_id": cls.staff_user.id,
            "resource_calendar_id": cls.calendar.id,
        })
        cls.service = cls.env["practice.service"].create({
            "name": "Consultation", "duration": 1.0, "buffer_minutes": 0,
        })
        cls.client = cls.env["res.partner"].create({
            "name": "Pat Doe", "is_client": True,
        })

        # the next Monday at 00:00 UTC, so tests are stable regardless of
        # what day they happen to run on
        today = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0)
        cls.next_monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
