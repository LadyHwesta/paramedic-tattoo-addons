# -*- coding: utf-8 -*-
{
    "name": "eLearning: Practitioner Suite Training",
    "version": "19.0.2.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning courses: client records, and scheduling and booking",
    "description": """
eLearning: Practitioner Suite Training
======================================

Two short courses (Odoo's eLearning app) for running a practice day to day:

* **Client Records**: bringing on a client and their health flags, the
  treatment plan, consent forms, pre-treatment tests, documenting a session.
* **Scheduling & Booking**: practitioners and services, the checks a service
  can require first, booking and confirming appointments, the client's own
  online booking.

Install it and both courses appear in eLearning, ready to assign.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["website_slides", "website_slides_publication_digest", "practice_base", "practice_appointment"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "practice_elearning/static/src/scss/course_content.scss",
        ],
    },
    "application": False,
}
