# -*- coding: utf-8 -*-
import base64

from odoo import SUPERUSER_ID, api
from odoo.tools import file_open

COVERS = {
    "channel_patient_portal": "cover_patient_portal.png",
}


def migrate(cr, version):
    """Courses now have their own cover pictures. Course data loads as
    noupdate, so set the picture here, and only where a course has none
    (never replace a picture someone chose)."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, image in COVERS.items():
        channel = env.ref(f"paramedic_elearning_patient_portal.{xmlid}", raise_if_not_found=False)
        if channel and not channel.image_1920:
            with file_open(f"paramedic_elearning_patient_portal/static/img/{image}", "rb") as f:
                channel.image_1920 = base64.b64encode(f.read())
