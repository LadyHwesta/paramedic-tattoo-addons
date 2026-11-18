# -*- coding: utf-8 -*-
{
    "name": "Paramedical Tattoo - Billing",
    "version": "19.0.1.0.0",
    "category": "Medical",
    "summary": "A price on each service, and an invoice from a completed appointment in one click",
    "description": """
Paramedical Tattoo - Billing
============================

* **Services have a price.** Each service is billed as a service product,
  created for you the first time you give the service a price.
* **Create Invoice** on a completed appointment makes the patient's invoice
  for that service and links it back, so the appointment shows whether it's
  been paid.
* **To Invoice** filter: completed appointments that haven't been billed yet.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/paramedic-tattoo-addons",
    "depends": ["paramedic_appointment", "account"],
    "data": [
        "views/paramedic_billing_views.xml",
    ],
    "auto_install": True,
    "installable": True,
}
