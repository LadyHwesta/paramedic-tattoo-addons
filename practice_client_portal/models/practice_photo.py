# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

_MARKETING_FIELDS = {"marketing_ok", "marketing_source", "marketing_date", "withdrawn_by_client"}


class ClientPhoto(models.Model):
    """A session photo, as the client and marketing see it: shared with the
    client or not, and whether it may be used in marketing, by whose
    permission and since when. The image itself stays the session's private
    attachment."""
    _name = "practice.photo"
    _description = "Client Photo"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "name"

    session_id = fields.Many2one(
        "practice.session", string="Session", required=True, index=True,
        ondelete="cascade")
    partner_id = fields.Many2one(
        related="session_id.partner_id", store=True, string="Client", index=True)
    date = fields.Datetime(related="session_id.date", store=True)
    attachment_id = fields.Many2one(
        "ir.attachment", required=True, ondelete="cascade", index=True)
    name = fields.Char(related="attachment_id.name")
    image = fields.Binary(related="attachment_id.datas", string="Image")
    kind = fields.Selection([("before", "Before"), ("after", "After")], required=True)
    shared_with_client = fields.Boolean(
        string="Shared with Client", tracking=True,
        help="Shown in the client's portal, where they can also allow its use in "
             "marketing.")

    marketing_ok = fields.Boolean(
        string="OK for Marketing", readonly=True, tracking=True,
        help="Set only by the client in their portal, or by attaching their signed "
             "photo release here.")
    marketing_source = fields.Selection(
        [("client", "Client, in their portal"), ("signed_form", "Signed photo release")],
        string="Permission From", readonly=True, tracking=True)
    marketing_date = fields.Datetime(string="Permission Since", readonly=True)
    marketing_consent_id = fields.Many2one(
        "practice.consent", string="Signed Photo Release", tracking=True,
        domain="[('partner_id', '=', partner_id), ('consent_type', '=', 'photo_release'), "
               "('signed', '=', True)]",
        help="Attach the client's signed photo release to record their permission.")
    marketing_label = fields.Char(compute="_compute_marketing_label", string="Marketing")
    withdrawn_by_client = fields.Boolean(
        readonly=True, copy=False,
        help="The client withdrew permission for this photo in their portal. A release "
             "covering all their photos doesn't override that; only they can allow it again.")

    _attachment_uniq = models.Constraint(
        "unique(session_id, attachment_id)", "This photo is already listed for the session.")

    @api.depends("marketing_ok", "marketing_source", "marketing_date")
    def _compute_marketing_label(self):
        for photo in self:
            if not photo.marketing_ok:
                photo.marketing_label = self.env._("No marketing permission")
                continue
            source = dict(self._fields["marketing_source"].selection).get(
                photo.marketing_source, "")
            day = format_date(self.env, fields.Datetime.context_timestamp(
                photo, photo.marketing_date).date()) if photo.marketing_date else ""
            photo.marketing_label = self.env._(
                "Marketing OK (%(who)s, %(date)s)", who=source, date=day)

    def write(self, vals):
        if _MARKETING_FIELDS & set(vals) and not self.env.context.get("practice_photo_marketing"):
            raise UserError(self.env._(
                "Marketing permission comes only from the client, in their portal, or from "
                "their signed photo release attached to the photo."))
        if "marketing_consent_id" in vals and not self.env.context.get("practice_photo_marketing"):
            consent = self.env["practice.consent"].browse(vals["marketing_consent_id"])
            if consent:
                self._attach_release(consent)
                vals = {k: v for k, v in vals.items() if k != "marketing_consent_id"}
            else:
                self._release_withdrawn()
                vals = {k: v for k, v in vals.items() if k != "marketing_consent_id"}
            if not vals:
                return True
        return super().write(vals)

    def _attach_release(self, consent):
        """Marketing permission from a signed photo release (one photo, several
        selected, or all of a client's photos). Photos the client withdrew in
        their portal, and ones the client allowed themselves, are left as they
        are."""
        valid = consent._is_valid_photo_release()
        for photo in self.with_context(practice_photo_marketing=True):
            if photo.partner_id != consent.partner_id:
                raise UserError(self.env._(
                    "%(release)s is another client's release.", release=consent.display_name))
            if photo.marketing_source == "client" or photo.withdrawn_by_client:
                continue
            values = {"marketing_consent_id": consent.id}
            if valid and not photo.marketing_ok:
                values.update({"marketing_ok": True, "marketing_source": "signed_form",
                               "marketing_date": fields.Datetime.now()})
            if photo.marketing_consent_id != consent or values.keys() - {"marketing_consent_id"}:
                photo.write(values)
                if valid:
                    photo.message_post(body=self.env._(
                        "Marketing permission from the signed release %(release)s.",
                        release=consent.display_name))

    def _release_withdrawn(self):
        """The release these photos relied on is gone, unsigned or no longer
        covers them: permission that came from it ends."""
        for photo in self.with_context(practice_photo_marketing=True):
            if photo.marketing_source == "signed_form":
                photo.write({"marketing_ok": False, "marketing_source": False,
                             "marketing_date": False, "marketing_consent_id": False})
                photo.message_post(body=self.env._(
                    "Marketing permission ended: the signed release no longer covers this photo."))
            elif photo.marketing_consent_id:
                photo.write({"marketing_consent_id": False})

    def _portal_set_marketing(self, allow):
        """The client's own choice, from their portal."""
        self.ensure_one()
        if allow == self.marketing_ok and (self.marketing_source == "client" or not allow):
            return
        self.with_context(practice_photo_marketing=True).write({
            "marketing_ok": allow,
            "marketing_source": "client" if allow else False,
            "marketing_date": fields.Datetime.now() if allow else False,
            "marketing_consent_id": False,
            "withdrawn_by_client": not allow,
        })
        self.message_post(body=self.env._(
            "The client allowed this photo's use in marketing, in their portal.") if allow
            else self.env._("The client withdrew permission to use this photo in marketing, "
                            "in their portal."))

    @api.model_create_multi
    def create(self, vals_list):
        photos = super().create(vals_list)
        # A signed release covering all the client's photos covers new ones too.
        for photo in photos:
            releases = self.env["practice.consent"].search([
                ("partner_id", "=", photo.partner_id.id), ("consent_type", "=", "photo_release"),
                ("signed", "=", True), ("covers_all_photos", "=", True)], limit=1)
            if releases:
                photo._attach_release(releases)
        return photos

    def _image_url(self):
        self.ensure_one()
        return f"/web/image/ir.attachment/{self.attachment_id.id}/datas"
