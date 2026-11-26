# -*- coding: utf-8 -*-
{
    "name": "Practitioner Suite - Reviews",
    "version": "19.0.1.0.0",
    "category": "Services",
    "summary": "Clients review their practitioner in the portal; staff check each review "
               "before it's published to a reviews blog with comments off",
    "description": """
Practitioner Suite - Reviews
============================

* **Only real clients:** a client can review a practitioner once they've had a
  completed appointment with them, from **My Reviews** in their portal.
* **Stars, words and photos:** 1 to 5 stars, a title, the review, the name to
  show (first name and last initial unless they change it), and any of their
  own shared photos they choose, with their permission to show them.
* **Checked before it's public:** every review waits under Practice › Reviews,
  with a to-do for whoever checks reviews. **Publish** puts it on the Client
  Reviews blog, tagged with the practitioner; **Don't Publish** keeps it off,
  with an optional note the client sees.
* **Comments off:** review posts never show a comment box, and comments sent
  to them anyway are refused.
* **The client stays in charge:** withdrawing a review takes the post and its
  public photo copies down. The photos themselves stay private session
  records; only copies are published.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/practitioner-addons",
    "depends": ["practice_appointment", "practice_client_portal", "website_blog"],
    "data": [
        "security/ir.model.access.csv",
        "data/blog_data.xml",
        "views/practice_review_views.xml",
        "views/portal_templates.xml",
        "views/blog_templates.xml",
    ],
    "installable": True,
}
