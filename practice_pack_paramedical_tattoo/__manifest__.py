# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - Paramedical Tattoo Pack",
    "version": "19.0.1.0.0",
    "category": "Services",
    "summary": "Sets the Practitioner Suite up for a paramedical tattoo practice: "
               "treatment types, pigment patch tests, health flags and consent wording",
    "description": """
Practitioner Suite - Paramedical Tattoo Pack
============================================

Everything specific to paramedical and medical tattooing, on top of the
general Practitioner Suite:

* **Treatment types**: areola restoration, scar camouflage, scalp
  micropigmentation and vitiligo repigmentation.
* **Pigment patch test**, read after 3 days.
* **Health flags**: bleeding disorder, blood thinners, keloid history.
* **Consent forms**: treatment and patch test wording for tattooing.
* **Extra fields**: the related surgery date on a treatment plan (for
  example a mastectomy) and the numbing agent used in a session.

All of it is ordinary data the practice can edit afterwards.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_base"],
    "data": [
        "data/practice_pack_data.xml",
        "views/practice_views.xml",
    ],
    "installable": True,
}
