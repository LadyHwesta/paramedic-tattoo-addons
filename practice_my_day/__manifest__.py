# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - My Day",
    "version": "19.0.2.0.0",
    "category": "Services",
    "summary": "My Day sections for a practice: today's appointments, booking requests, "
               "tests to read, follow-ups to book",
    "description": """
Practitioner Suite - My Day
===========================
Adds a practice's day to My Day (the start screen):

* **Today's appointments** - a practitioner's own (everyone's, for staff who
  aren't practitioners), with Complete once one has started. Appointments are
  their own records, not calendar meetings, so My Day's calendar section never
  showed them.
* **Booking requests** - online requests waiting to be confirmed, with Confirm.
* **Tests to read** - pending pre-treatment test results due today or overdue.
* **Follow-ups to book** - sessions whose recommended next session is due
  within two weeks, for clients with nothing booked yet.

Installs itself with My Day and Practitioner Suite - Appointments.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["my_day", "practice_appointment"],
    "auto_install": True,
    "installable": True,
}
