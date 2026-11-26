# -*- coding: utf-8 -*-
{
    "name": "eLearning: Billing Clients",
    "version": "19.0.2.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: pricing services, invoicing visits, taking payment, who still owes",
    "description": """
eLearning: Billing Clients
===========================

One short course (Odoo's eLearning app), ready on install, with a quiz, for
whoever bills clients: pricing services, invoicing a completed visit in one
click, taking payment at the desk, and finding visits not yet billed or still
owed. Members only, by invitation, for invoicing users.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_elearning", "practice_billing"],
    "data": ["data/slide_channel_data.xml"],
    "installable": True,
}
