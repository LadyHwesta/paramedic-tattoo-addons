# -*- coding: utf-8 -*-
{
    "name": "eLearning: Notes and Photo Permissions",
    "version": "19.0.2.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: internal and shared client notes, sharing photos, "
               "and clients' permission to use photos in marketing",
    "description": """
eLearning: Notes and Photo Permissions
======================================

One short course (Odoo's eLearning app), ready on install, with a quiz, for
practitioners and staff using the client portal: writing internal and shared
client notes, sharing photos with a client, and how permission to use a
photo in marketing is given, shown and withdrawn. Members only, by invitation,
for Practitioner Suite staff. Installs itself with the client portal and the
other Practitioner Suite courses.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_elearning", "practice_client_portal"],
    "data": ["data/slide_channel_data.xml"],
    "auto_install": True,
    "installable": True,
}
