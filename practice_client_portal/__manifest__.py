# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - Client Portal",
    "version": "19.0.2.0.0",
    "category": "Services",
    "summary": "Client notes marked internal or shared with the client, and client-controlled "
               "permission to use their photos in marketing",
    "description": """
Practitioner Suite - Client Portal
===================================
A portal for a practice's clients, like a health record's patient portal:

* **Client notes**, each marked **Internal** (the default: staff only) or
  **Shared with client**. A shared note appears in the client's portal, and
  they get an email saying there's an update, with a link to sign in. The
  note itself never goes by email.
* **Photos the client sees:** staff tick which session photos to share; only
  those appear in the client's portal.
* **Marketing permission per photo:** the client ticks "OK to use in
  marketing" on a shared photo, and can untick it any time. Staff can record
  it only by attaching a signed photo release. Every photo shows whether it
  may be used, by whose permission and since when, and a filter lists the
  ones that may.

Notes and photos stay staff-only in the back office; the portal shows a
client only their own shared notes and photos, served privately.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_base", "portal"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/practice_note_views.xml",
        "views/practice_photo_views.xml",
        "views/practice_photo_release_wizard_views.xml",
        "views/practice_session_views.xml",
        "views/res_partner_views.xml",
        "views/portal_templates.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
