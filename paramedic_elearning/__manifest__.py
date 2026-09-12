# -*- coding: utf-8 -*-
{
    "name": "eLearning: HB Ink Studio Training",
    "version": "19.0.1.1.0",
    "category": "Website/eLearning",
    "summary": "eLearning courses: patient records/clinical documentation and scheduling",
    "description": """
eLearning: HB Ink Studio Training
====================================

Two short, self-contained eLearning courses (Odoo's *eLearning* app) for
running HB Ink Studio day to day:

* **Patient Records & Clinical Documentation** - bringing on a patient,
  the condition record, informed consent, patch testing, documenting a
  treatment session.
* **Scheduling & Booking** - setting up a practitioner and services,
  booking an appointment, confirming a portal request, the patient's own
  online booking flow.

Install this module and both courses appear in eLearning already built -
nothing to author by hand.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["website_slides", "paramedic_base", "paramedic_appointment"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "paramedic_elearning/static/src/scss/course_content.scss",
        ],
    },
    "application": False,
}
