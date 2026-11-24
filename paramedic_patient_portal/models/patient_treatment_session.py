# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PatientTreatmentSession(models.Model):
    _inherit = "patient.treatment.session"

    photo_ids = fields.One2many("patient.photo", "session_id", string="Photo Sharing")
    clinical_note_ids = fields.One2many("patient.clinical.note", "session_id",
                                        string="Clinical Notes Entries")

    @api.model_create_multi
    def create(self, vals_list):
        sessions = super().create(vals_list)
        sessions._sync_patient_photos()
        return sessions

    def write(self, vals):
        result = super().write(vals)
        if {"before_photo_ids", "after_photo_ids"} & set(vals):
            self._sync_patient_photos()
        return result

    def _sync_patient_photos(self):
        """One patient.photo per before/after photo: added with the photo,
        removed with it."""
        Photo = self.env["patient.photo"].sudo()
        for session in self:
            wanted = {(a.id, "before") for a in session.before_photo_ids} | {
                (a.id, "after") for a in session.after_photo_ids}
            existing = {(p.attachment_id.id, p.kind): p for p in session.sudo().photo_ids}
            for key in wanted - set(existing):
                Photo.create({"session_id": session.id, "attachment_id": key[0],
                              "kind": key[1]})
            for key in set(existing) - wanted:
                existing[key].unlink()
