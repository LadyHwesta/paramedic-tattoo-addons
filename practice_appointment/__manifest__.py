# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - Appointments",
    "version": "19.0.2.0.0",
    "category": "Services",
    "summary": "Service types, practitioner scheduling, and client "
               "self-booking for a practice that treats clients",
    "description": """
Practitioner Suite - Appointments
===================================

Odoo Community has no self-service booking app (the "Appointments" app is
Enterprise-only), so this builds one on top of the ``resource`` module -
the same working-hours/time-off engine that powers HR and manufacturing.

* **Services** - a name, a duration, buffer time after it, which
  practitioners are qualified to perform it, whether it's offered for
  online self-booking, and whether it requires a clear pre-treatment test
  and/or a signed treatment consent on file before it can be booked at all.
* **Appointments** - client, practitioner, service, and (when the
  service is gated) the treatment plan it's for. Overlap,
  practitioner qualification, and the test/consent gate are all
  enforced on save, skippable with ``skip_appointment_checks`` in context
  for a back-office correction.
* **Availability** - computed per practitioner from their own
  ``resource.calendar`` (time off included for free) minus their existing
  appointments - no separate scheduling engine to keep in sync.
* **Client self-booking** - a portal page listing the services open to
  online booking, real open slots for the next few weeks, one click to
  request a time. Requests land as ``requested`` for staff to confirm.
* Completing a session-type appointment can create the linked
  ``practice.session`` record automatically, so the client's
  history and the calendar are one connected system.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_base", "portal"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/mail_template_data.xml",
        "views/practice_service_views.xml",
        "views/practice_practitioner_views.xml",
        "views/practice_appointment_views.xml",
        "views/portal_templates.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
}
