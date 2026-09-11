# -*- coding: utf-8 -*-
{
    "name": "Paramedical Tattoo - Appointments",
    "version": "19.0.1.0.0",
    "category": "Medical",
    "summary": "Service types, practitioner scheduling, and patient "
               "self-booking for a paramedical/medical tattooing practice",
    "description": """
Paramedical Tattoo - Appointments
===================================

Odoo Community has no self-service booking app (the "Appointments" app is
Enterprise-only), so this builds one on top of the ``resource`` module -
the same working-hours/time-off engine that powers HR and manufacturing.

* **Services** - a name, a duration, buffer time after it, which
  practitioners are qualified to perform it, whether it's offered for
  online self-booking, and whether it requires a clear patch test and/or
  a signed treatment consent on file before it can be booked at all.
* **Appointments** - patient, practitioner, service, and (when the
  service is clinically gated) the condition it's for. Overlap,
  practitioner qualification, and the patch-test/consent gate are all
  enforced on save, skippable with ``skip_appointment_checks`` in context
  for a back-office correction.
* **Availability** - computed per practitioner from their own
  ``resource.calendar`` (time off included for free) minus their existing
  appointments - no separate scheduling engine to keep in sync.
* **Patient self-booking** - a portal page listing the services open to
  online booking, real open slots for the next few weeks, one click to
  request a time. Requests land as ``requested`` for staff to confirm.
* Completing a session-type appointment can create the linked
  ``patient.treatment.session`` record automatically, so the clinical
  history and the calendar are one connected system.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["paramedic_base", "portal"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/mail_template_data.xml",
        "views/paramedic_service_views.xml",
        "views/paramedic_practitioner_views.xml",
        "views/paramedic_appointment_views.xml",
        "views/portal_templates.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
}
