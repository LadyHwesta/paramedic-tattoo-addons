# -*- coding: utf-8 -*-
{
    "name": "eLearning: Notes and Photo Permissions",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: internal and shared clinical notes, sharing photos, "
               "and patients' permission to use photos in marketing",
    "description": """
eLearning: Notes and Photo Permissions
======================================

One short course (Odoo's eLearning app), ready on install, with a quiz, for
practitioners and staff using the patient portal: writing internal and shared
clinical notes, sharing photos with a patient, and how permission to use a
photo in marketing is given, shown and withdrawn. Members only, by invitation,
for Paramedical Tattoo staff. Installs itself with the patient portal and the
other Paramedical courses.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["paramedic_elearning", "paramedic_patient_portal"],
    "data": ["data/slide_channel_data.xml"],
    "auto_install": True,
    "installable": True,
}
