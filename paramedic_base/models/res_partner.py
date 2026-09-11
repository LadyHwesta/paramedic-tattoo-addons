# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_patient = fields.Boolean(string="Is a Patient")
    patient_ref = fields.Char(
        string="Patient #", copy=False, readonly=True,
        help="Assigned automatically the first time this contact is marked "
             "as a patient.")
    date_of_birth = fields.Date(string="Date of Birth")
    emergency_contact_name = fields.Char()
    emergency_contact_phone = fields.Char()

    # --- Referral (kept simple - free text; graduate to a linked contact
    # if referrals become common enough to want reporting on them) -------
    referring_provider_name = fields.Char(string="Referring Provider")
    referring_provider_contact = fields.Char(string="Referring Provider Phone/Email")

    # --- Safety-relevant medical history ---------------------------------
    has_bleeding_disorder = fields.Boolean(string="Bleeding Disorder")
    takes_blood_thinners = fields.Boolean(string="Takes Blood Thinners")
    has_keloid_history = fields.Boolean(string="History of Keloid Scarring")
    has_allergies = fields.Boolean(string="Known Allergies")
    allergy_notes = fields.Text(string="Allergy Details")
    relevant_medical_notes = fields.Text(
        string="Other Relevant Medical Notes",
        help="Anything else a practitioner should know before treating this "
             "patient (medications, skin conditions, prior reactions...).")

    # --- Consent to use photos for purposes beyond the clinical record,
    # e.g. a portfolio - distinct from the per-procedure treatment consent
    # tracked on patient.consent. --------------------------------------
    photo_marketing_consent = fields.Boolean(
        string="OK to Use Photos for Marketing/Portfolio")

    # --- Insurance placeholder - unused today, kept so a future move to
    # billing insurance doesn't require a schema change. -----------------
    insurance_payer_name = fields.Char(string="Insurance Payer")
    insurance_member_id = fields.Char(string="Insurance Member ID")

    condition_ids = fields.One2many(
        "patient.condition", "partner_id", string="Conditions")
    condition_count = fields.Integer(compute="_compute_condition_count")

    @api.depends("condition_ids")
    def _compute_condition_count(self):
        for partner in self:
            partner.condition_count = len(partner.condition_ids)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners.filtered(
            lambda p: p.is_patient and not p.patient_ref
        )._assign_patient_ref()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if vals.get("is_patient"):
            self.filtered(
                lambda p: p.is_patient and not p.patient_ref
            )._assign_patient_ref()
        return res

    def _assign_patient_ref(self):
        for partner in self:
            partner.patient_ref = self.env["ir.sequence"].next_by_code(
                "patient.ref")

    def action_view_conditions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Conditions - %s", self.name),
            "res_model": "patient.condition",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
