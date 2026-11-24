# -*- coding: utf-8 -*-
{
    "name": "Paramedical Tattoo - My Day",
    "version": "19.0.1.0.0",
    "category": "Medical",
    "summary": "My Day sections for a practice: today's appointments, booking requests, "
               "patch tests to read, follow-ups to book",
    "description": """
Paramedical Tattoo - My Day
===========================
Adds a practice's day to My Day (the start screen):

* **Today's appointments** - a practitioner's own (everyone's, for staff who
  aren't practitioners), with Complete once one has started. Appointments are
  their own records, not calendar meetings, so My Day's calendar section never
  showed them.
* **Booking requests** - online requests waiting to be confirmed, with Confirm.
* **Patch tests to read** - pending results due today or overdue.
* **Follow-ups to book** - sessions whose recommended next session is due
  within two weeks, for patients with nothing booked yet.

Installs itself with My Day and Paramedical Tattoo - Appointments.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["my_day", "paramedic_appointment"],
    "auto_install": True,
    "installable": True,
}
