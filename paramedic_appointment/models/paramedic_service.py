# -*- coding: utf-8 -*-
from odoo import fields, models


class ParamedicService(models.Model):
    _name = "paramedic.service"
    _description = "Service Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    duration = fields.Float(
        string="Duration (hours)", required=True, default=1.0)
    buffer_minutes = fields.Integer(
        string="Buffer After (minutes)", default=15,
        help="Cleanup/prep time blocked on the practitioner's schedule "
             "after this service, before the next appointment can start.")
    requires_patch_test = fields.Boolean(
        string="Requires a Clear Patch Test",
        help="Can only be booked against a condition with a clear patch "
             "test on file.")
    requires_treatment_consent = fields.Boolean(
        string="Requires Signed Treatment Consent",
        help="Can only be booked against a condition with a signed "
             "treatment consent on file.")
    creates_treatment_session = fields.Boolean(
        string="Creates a Treatment Session",
        help="Completing an appointment for this service creates the "
             "linked patient.treatment.session record automatically. Leave "
             "off for consultations and other non-treatment services.")
    bookable_online = fields.Boolean(
        string="Bookable Online", default=True,
        help="Offered on the patient self-booking page. Turn off for "
             "services that always need an in-person assessment first - "
             "gated services (patch test / consent required) are never "
             "offered online regardless of this flag unless the patient "
             "already has a condition on file that satisfies them.")
    practitioner_ids = fields.Many2many(
        "paramedic.practitioner", "paramedic_practitioner_service_rel",
        "service_id", "practitioner_id", string="Qualified Practitioners",
        help="Leave empty to allow any practitioner to perform this "
             "service.")
    active = fields.Boolean(default=True)

    _duration_positive = models.Constraint(
        "CHECK(duration > 0)", "Duration must be positive.")
    _buffer_not_negative = models.Constraint(
        "CHECK(buffer_minutes >= 0)", "Buffer time can't be negative.")

    def _qualified_practitioners(self):
        self.ensure_one()
        return self.practitioner_ids or self.env["paramedic.practitioner"].search([])

    def _find_eligible_condition(self, partner):
        """A condition of ``partner`` that satisfies this service's
        requirements, or an empty recordset if none does (or none is
        required)."""
        self.ensure_one()
        if not (self.requires_patch_test or self.requires_treatment_consent):
            return self.env["patient.condition"]
        for condition in partner.condition_ids.filtered(
                lambda c: c.state != "discontinued"):
            if self.requires_patch_test and not condition.patch_test_clear:
                continue
            if self.requires_treatment_consent:
                signed = condition.consent_ids.filtered(
                    lambda c: c.consent_type == "treatment" and c.signed)
                if not signed:
                    continue
            return condition
        return self.env["patient.condition"]

    def _bookable_online_for(self, partner):
        """Whether ``partner`` can currently self-book this service."""
        self.ensure_one()
        if not self.active or not self.bookable_online:
            return False
        if not (self.requires_patch_test or self.requires_treatment_consent):
            return True
        return bool(self._find_eligible_condition(partner))
