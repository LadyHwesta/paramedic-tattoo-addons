# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PatientClinicalNote(models.Model):
    _name = "patient.clinical.note"
    _description = "Clinical Note"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "title"

    partner_id = fields.Many2one(
        "res.partner", string="Patient", required=True, index=True, ondelete="cascade",
        domain=[("is_patient", "=", True)], tracking=True)
    condition_id = fields.Many2one(
        "patient.condition", string="Condition", ondelete="set null",
        domain="[('partner_id', '=', partner_id)]")
    session_id = fields.Many2one(
        "patient.treatment.session", string="Session", ondelete="set null",
        domain="[('partner_id', '=', partner_id)]")
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    author_id = fields.Many2one(
        "res.users", string="Written by", default=lambda self: self.env.user, required=True)
    title = fields.Char(required=True)
    body = fields.Html(string="Note", sanitize=True)
    visibility = fields.Selection(
        [("internal", "Internal"), ("patient", "Shared with patient")],
        default="internal", required=True, tracking=True,
        help="Internal notes are for staff only. Shared notes also appear in the "
             "patient's portal, and the patient is emailed that there's an update "
             "(never the note itself).")
    shared_on = fields.Datetime(readonly=True, copy=False)

    @api.constrains("partner_id", "session_id", "condition_id")
    def _check_same_patient(self):
        for note in self:
            for record in (note.session_id, note.condition_id):
                if record and record.partner_id != note.partner_id:
                    raise ValidationError(self.env._(
                        "A note's session and condition must be the same patient's."))

    @api.model_create_multi
    def create(self, vals_list):
        notes = super().create(vals_list)
        notes.filtered(lambda n: n.visibility == "patient")._on_shared()
        return notes

    def write(self, vals):
        newly_shared = self.filtered(lambda n: n.visibility != "patient") \
            if vals.get("visibility") == "patient" else self.browse()
        result = super().write(vals)
        newly_shared._on_shared()
        return result

    def _on_shared(self):
        """Shared with the patient: note when, and tell them there's an update."""
        template = self.env.ref(
            "paramedic_patient_portal.mail_template_note_shared", raise_if_not_found=False)
        for note in self:
            note.shared_on = fields.Datetime.now()
            if template and note.partner_id.email:
                template.sudo().send_mail(note.id, force_send=False)

    def _portal_url(self):
        return "/my/records"
