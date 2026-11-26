# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - Client Records",
    "version": "19.0.2.0.0",
    "category": "Services",
    "summary": "Clients, practitioners, treatment plans, consents, pre-treatment "
               "tests and session notes for any practice that treats clients",
    "description": """
Practitioner Suite - Client Records
===================================

The records side of a practice that treats clients one to one: massage,
herbalism, personal training, paramedical tattooing and the like.

* **Clients**: a contact with a client number, date of birth, emergency
  contact, referring provider, allergies, and the practice's own **health
  flags** to check before treating (blood thinners, pregnancy...).
* **Practitioners**: who treats, their working hours and licence or
  certification. A solo practice can add a second practitioner later
  without changing anything.
* **Treatment plans**: what a client is being treated for (from the
  practice's own list of treatment types), where or what it focuses on,
  and by whom. Every consent, test and session for it hangs off the plan.
* **Consents**: treatment, pre-treatment test and photo release, each
  printed from an editable consent form, signed and recorded.
* **Pre-treatment tests**: the practice's own checks (a skin patch test, a
  fitness assessment), with the product and lot tested, when it's read, and
  the result.
* **Sessions**: date, products and lot used, notes, aftercare, reactions,
  before and after photos, and when to come back.

Client records are staff-only: nothing this module adds is reachable from a
portal or public page. Practice-specific setups come as packs, such as
``practice_pack_paramedical_tattoo``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["contacts", "resource", "mail"],
    "data": [
        "security/practice_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/practice_type_data.xml",
        "data/practice_consent_form_data.xml",
        "report/practice_consent_report.xml",
        "views/practice_types_views.xml",
        "views/res_partner_views.xml",
        "views/practice_practitioner_views.xml",
        "views/practice_plan_views.xml",
        "views/practice_consent_views.xml",
        "views/practice_test_views.xml",
        "views/practice_session_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
}
