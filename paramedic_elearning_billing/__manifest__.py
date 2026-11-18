# -*- coding: utf-8 -*-
{
    "name": "eLearning: Billing Patients",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: pricing services, invoicing visits, taking payment, who still owes",
    "description": """
eLearning: Billing Patients
===========================

One short course (Odoo's eLearning app), ready on install, with a quiz, for
whoever bills patients: pricing services, invoicing a completed visit in one
click, taking payment at the desk, and finding visits not yet billed or still
owed. Members only, by invitation, for invoicing users.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["paramedic_elearning", "paramedic_billing"],
    "data": ["data/slide_channel_data.xml"],
    "installable": True,
}
