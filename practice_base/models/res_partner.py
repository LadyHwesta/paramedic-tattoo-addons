# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_client = fields.Boolean(string="Is a Client")
    client_ref = fields.Char(
        string="Client #", copy=False, readonly=True,
        help="Assigned automatically the first time this contact is marked "
             "as a client.")
    date_of_birth = fields.Date(string="Date of Birth")
    emergency_contact_name = fields.Char()
    emergency_contact_phone = fields.Char()

    # --- Referral (kept simple - free text; graduate to a linked contact
    # if referrals become common enough to want reporting on them) -------
    referring_provider_name = fields.Char(string="Referring Provider")
    referring_provider_contact = fields.Char(string="Referring Provider Phone/Email")

    # --- What a practitioner must know before treating -------------------
    health_flag_ids = fields.Many2many(
        "practice.health.flag", "practice_partner_health_flag_rel",
        "partner_id", "flag_id", string="Health Flags",
        help="Things to check before every treatment. Each practice keeps its "
             "own list in Configuration.")
    has_allergies = fields.Boolean(string="Known Allergies")
    allergy_notes = fields.Text(string="Allergy Details")
    relevant_medical_notes = fields.Text(
        string="Other Health Notes",
        help="Anything else a practitioner should know before treating this "
             "client (medications, injuries, prior reactions...).")

    # --- Consent to use photos for purposes beyond the clinical record,
    # e.g. a portfolio - distinct from the per-procedure treatment consent
    # tracked on practice.consent. --------------------------------------
    photo_marketing_consent = fields.Boolean(
        string="OK to Use Photos for Marketing/Portfolio")

    # --- Insurance placeholder - unused today, kept so a future move to
    # billing insurance doesn't require a schema change. -----------------
    insurance_payer_name = fields.Char(string="Insurance Payer")
    insurance_member_id = fields.Char(string="Insurance Member ID")

    plan_ids = fields.One2many(
        "practice.plan", "partner_id", string="Treatment Plans")
    plan_count = fields.Integer(compute="_compute_plan_count")

    @api.depends("plan_ids")
    def _compute_plan_count(self):
        for partner in self:
            partner.plan_count = len(partner.plan_ids)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners.filtered(
            lambda p: p.is_client and not p.client_ref
        )._assign_client_ref()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if vals.get("is_client"):
            self.filtered(
                lambda p: p.is_client and not p.client_ref
            )._assign_client_ref()
        return res

    def _assign_client_ref(self):
        for partner in self:
            partner.client_ref = self.env["ir.sequence"].next_by_code(
                "practice.client.ref")

    def action_view_plans(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Treatment Plans - %s", self.name),
            "res_model": "practice.plan",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
