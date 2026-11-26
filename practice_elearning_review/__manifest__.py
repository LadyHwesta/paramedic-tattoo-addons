# -*- coding: utf-8 -*-
{
    "name": "eLearning: Client Reviews",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: how clients review their practitioner, checking each review, "
               "and what gets published",
    "description": """
eLearning: Client Reviews
=========================

A short course (Odoo's eLearning app) for whoever checks reviews: how a
client writes one after a completed visit, checking and publishing it to
the Client Reviews blog (comments off), not publishing one, and a client
withdrawing their review. Installs itself with the Practitioner Suite
courses and Reviews.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_elearning", "practice_review"],
    "data": ["data/slide_channel_data.xml"],
    "auto_install": True,
    "installable": True,
}
