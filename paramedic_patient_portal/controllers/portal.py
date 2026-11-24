# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PatientRecordsPortal(CustomerPortal):
    """My Records: a patient's shared notes and shared photos, and their
    marketing permission per photo. Everything is looked up by the signed-in
    patient, never by an id alone."""

    def _patient(self):
        return request.env.user.partner_id

    def _shared_notes(self):
        return request.env["patient.clinical.note"].sudo().search([
            ("partner_id", "=", self._patient().id), ("visibility", "=", "patient")])

    def _shared_photos(self):
        return request.env["patient.photo"].sudo().search([
            ("partner_id", "=", self._patient().id), ("shared_with_patient", "=", True)])

    def _my_photo(self, photo_id):
        photo = request.env["patient.photo"].sudo().browse(int(photo_id)).exists()
        if not photo or photo.partner_id != self._patient() or not photo.shared_with_patient:
            return None
        return photo

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "patient_record_count" in counters:
            values["patient_record_count"] = (
                len(self._shared_notes()) + len(self._shared_photos()))
        return values

    @http.route(["/my/records"], type="http", auth="user", website=True)
    def my_records(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "patient_records",
            "notes": self._shared_notes(),
            "photos": self._shared_photos(),
            "saved": kw.get("saved"),
        })
        return request.render("paramedic_patient_portal.portal_my_records", values)

    @http.route(["/my/records/photo/<int:photo_id>"], type="http", auth="user")
    def my_record_photo(self, photo_id, **kw):
        """The image, only to its own patient (session photos are private
        attachments)."""
        photo = self._my_photo(photo_id)
        if not photo:
            raise request.not_found()
        attachment = photo.attachment_id.sudo()
        return request.make_response(
            base64.b64decode(attachment.datas or b""),
            headers=[("Content-Type", attachment.mimetype or "image/jpeg"),
                     ("Cache-Control", "private, max-age=3600"),
                     ("X-Content-Type-Options", "nosniff")])

    @http.route(["/my/records/photo/<int:photo_id>/marketing"], type="http", auth="user",
                website=True, methods=["POST"])
    def my_record_photo_marketing(self, photo_id, allow=None, **kw):
        photo = self._my_photo(photo_id)
        if not photo:
            raise request.not_found()
        photo._portal_set_marketing(allow == "1")
        return request.redirect("/my/records?saved=1#photos")
