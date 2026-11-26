# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PracticeNote(models.Model):
    _name = "practice.note"
    _description = "Client Note"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "title"

    partner_id = fields.Many2one(
        "res.partner", string="Client", required=True, index=True, ondelete="cascade",
        domain=[("is_client", "=", True)], tracking=True)
    plan_id = fields.Many2one(
        "practice.plan", string="Treatment Plan", ondelete="set null",
        domain="[('partner_id', '=', partner_id)]")
    session_id = fields.Many2one(
        "practice.session", string="Session", ondelete="set null",
        domain="[('partner_id', '=', partner_id)]")
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    author_id = fields.Many2one(
        "res.users", string="Written by", default=lambda self: self.env.user, required=True)
    title = fields.Char(required=True)
    body = fields.Html(string="Note", sanitize=True)
    visibility = fields.Selection(
        [("internal", "Internal"), ("client", "Shared with client")],
        default="internal", required=True, tracking=True,
        help="Internal notes are for staff only. Shared notes also appear in the "
             "client's portal, and the client is emailed that there's an update "
             "(never the note itself).")
    shared_on = fields.Datetime(readonly=True, copy=False)

    @api.constrains("partner_id", "session_id", "plan_id")
    def _check_same_client(self):
        for note in self:
            for record in (note.session_id, note.plan_id):
                if record and record.partner_id != note.partner_id:
                    raise ValidationError(self.env._(
                        "A note's session and treatment plan must be the same client's."))

    @api.model_create_multi
    def create(self, vals_list):
        notes = super().create(vals_list)
        notes.filtered(lambda n: n.visibility == "client")._on_shared()
        return notes

    def write(self, vals):
        newly_shared = self.filtered(lambda n: n.visibility != "client") \
            if vals.get("visibility") == "client" else self.browse()
        result = super().write(vals)
        newly_shared._on_shared()
        return result

    def _on_shared(self):
        """Shared with the client: note when, and tell them there's an update."""
        template = self.env.ref(
            "practice_client_portal.mail_template_note_shared", raise_if_not_found=False)
        for note in self:
            note.shared_on = fields.Datetime.now()
            if template and note.partner_id.email:
                template.sudo().send_mail(note.id, force_send=False)

    def _portal_url(self):
        return "/my/records"
