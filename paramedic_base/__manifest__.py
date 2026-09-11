# -*- coding: utf-8 -*-
{
    "name": "Paramedical Tattoo - Patient Records",
    "version": "19.0.1.0.0",
    "category": "Medical",
    "summary": "Patients, practitioners, treated conditions, informed "
               "consent, pigment patch tests, and treatment sessions for a "
               "paramedical/medical tattooing practice",
    "description": """
Paramedical Tattoo - Patient Records
=====================================

The clinical side of running a paramedical tattooing practice - areola
restoration, scar camouflage, scalp micropigmentation, vitiligo
repigmentation, and similar work.

* **Patients** - a person on ``res.partner`` with a patient number,
  date of birth, emergency contact, referring provider, and the
  safety-relevant medical flags a practitioner needs before touching a
  needle to skin (bleeding disorders, blood thinners, keloid history,
  allergies).
* **Practitioners** - who's treating, their working hours, licence and
  (for later, if the practice ever bills insurance) NPI number. Modelled
  as its own record from the start so a solo practice can add a second
  practitioner later without restructuring anything.
* **Conditions** - what's being treated, on which area, since when, and
  by whom - the thread every consent, patch test, and session for that
  issue hangs off of.
* **Informed consent** - one record per consent (treatment, photo
  release, patch test), with a printable form and an acceptance
  checkbox.
* **Patch tests** - pigment, lot number, application date, the 48-72h
  read date, and the result. A documented safety step before first ink.
* **Treatment sessions** - date, pigment and lot used, area, notes,
  aftercare given, adverse reactions, before/after photos, and the
  practitioner's recommendation for the next session.

Patient and clinical data is staff-only throughout - nothing this module
adds is ever reachable from a portal or public view. See this repo's
README for a note on regulatory scope.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["contacts", "resource", "mail"],
    "data": [
        "security/paramedic_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "report/patient_consent_report.xml",
        "views/res_partner_views.xml",
        "views/paramedic_practitioner_views.xml",
        "views/patient_condition_views.xml",
        "views/patient_consent_views.xml",
        "views/patient_patch_test_views.xml",
        "views/patient_treatment_session_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
}
