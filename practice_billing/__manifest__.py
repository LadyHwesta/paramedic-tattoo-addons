# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - Billing",
    "version": "19.0.2.0.0",
    "category": "Services",
    "summary": "A price on each service, and an invoice from a completed appointment in one click",
    "description": """
Practitioner Suite - Billing
============================

* **Services have a price.** Each service is billed as a service product,
  created for you the first time you give the service a price.
* **Create Invoice** on a completed appointment makes the client's invoice
  for that service and links it back, so the appointment shows whether it's
  been paid.
* **To Invoice** filter: completed appointments that haven't been billed yet.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_appointment", "account"],
    "data": [
        "views/practice_billing_views.xml",
    ],
    "auto_install": True,
    "installable": True,
}
