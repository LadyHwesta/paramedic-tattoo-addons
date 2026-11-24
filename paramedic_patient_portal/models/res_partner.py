# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    clinical_note_ids = fields.One2many("patient.clinical.note", "partner_id",
                                        string="Clinical Notes")
    patient_photo_ids = fields.One2many("patient.photo", "partner_id", string="Photos")
    clinical_note_count = fields.Integer(compute="_compute_patient_portal_counts")
    marketing_photo_count = fields.Integer(compute="_compute_patient_portal_counts")

    @api.depends("clinical_note_ids", "patient_photo_ids.marketing_ok")
    def _compute_patient_portal_counts(self):
        for partner in self:
            partner.clinical_note_count = len(partner.clinical_note_ids)
            partner.marketing_photo_count = len(
                partner.patient_photo_ids.filtered("marketing_ok"))

    def action_view_clinical_notes(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "paramedic_patient_portal.action_patient_clinical_note")
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {"default_partner_id": self.id}
        return action

    def action_view_patient_photos(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "paramedic_patient_portal.action_patient_photo")
        action["domain"] = [("partner_id", "=", self.id)]
        return action
