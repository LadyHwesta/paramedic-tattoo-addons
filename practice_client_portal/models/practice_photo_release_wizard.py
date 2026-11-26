# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class ClientPhotoReleaseWizard(models.TransientModel):
    """Attach one signed photo release to several photos at once."""
    _name = "practice.photo.release.wizard"
    _description = "Attach a Signed Photo Release"

    photo_ids = fields.Many2many("practice.photo", string="Photos")
    partner_id = fields.Many2one("res.partner", string="Client", readonly=True)
    consent_id = fields.Many2one(
        "practice.consent", string="Signed Photo Release", required=True,
        domain="[('partner_id', '=', partner_id), ('consent_type', '=', 'photo_release'), "
               "('signed', '=', True)]")
    skipped_count = fields.Integer(compute="_compute_skipped_count")

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        photos = self.env["practice.photo"].browse(self.env.context.get("active_ids", []))
        clients = photos.partner_id
        if len(clients) > 1:
            raise UserError(self.env._(
                "Select one client's photos: a release covers only the client who signed it."))
        values.update({"photo_ids": [(6, 0, photos.ids)], "partner_id": clients.id})
        return values

    @api.depends("photo_ids")
    def _compute_skipped_count(self):
        for wizard in self:
            wizard.skipped_count = len(wizard.photo_ids.filtered(
                lambda p: p.withdrawn_by_client or p.marketing_source == "client"))

    def action_attach(self):
        self.ensure_one()
        self.photo_ids._attach_release(self.consent_id)
        return {"type": "ir.actions.act_window_close"}
