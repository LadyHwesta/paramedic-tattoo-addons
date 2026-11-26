# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ClientConsent(models.Model):
    _inherit = "practice.consent"

    covers_all_photos = fields.Boolean(
        string="Covers All Photos", tracking=True,
        help="This signed release covers all of the client's photos, including ones "
             "taken later: each gets marketing permission without attaching the release "
             "photo by photo. A photo the client withdraws in their portal stays "
             "withdrawn.")
    photo_ids = fields.One2many("practice.photo", "marketing_consent_id",
                                string="Photos Covered")
    photo_count = fields.Integer(compute="_compute_photo_count")

    @api.depends("photo_ids")
    def _compute_photo_count(self):
        for consent in self:
            consent.photo_count = len(consent.photo_ids)

    def _is_valid_photo_release(self):
        self.ensure_one()
        return self.consent_type == "photo_release" and self.signed

    @api.model_create_multi
    def create(self, vals_list):
        consents = super().create(vals_list)
        consents._apply_to_all_photos()
        return consents

    def write(self, vals):
        result = super().write(vals)
        if {"signed", "consent_type", "covers_all_photos"} & set(vals):
            # No longer a valid release: the photos it covered lose permission.
            for consent in self.filtered(lambda c: not c._is_valid_photo_release()):
                consent.photo_ids._release_withdrawn()
            self.filtered(lambda c: c._is_valid_photo_release() and not c.covers_all_photos
                          and "covers_all_photos" in vals).photo_ids._release_withdrawn()
            # Newly valid: photos it was already attached to gain permission.
            for consent in self.filtered(lambda c: c._is_valid_photo_release()):
                consent.photo_ids._attach_release(consent)
            self._apply_to_all_photos()
        return result

    def unlink(self):
        self.photo_ids._release_withdrawn()
        return super().unlink()

    def _apply_to_all_photos(self):
        for consent in self.filtered(
                lambda c: c._is_valid_photo_release() and c.covers_all_photos):
            photos = self.env["practice.photo"].search([("partner_id", "=", consent.partner_id.id)])
            photos._attach_release(consent)

    def action_view_covered_photos(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "practice_client_portal.action_practice_photo")
        action["domain"] = [("marketing_consent_id", "=", self.id)]
        return action
