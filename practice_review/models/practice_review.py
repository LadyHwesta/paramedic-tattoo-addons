# -*- coding: utf-8 -*-
import base64

from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

OPEN_STATES = ("submitted", "published")


class PracticeReview(models.Model):
    """A client's review of a practitioner. Written in the client portal,
    checked by staff, and only then published as a post in the practice's
    reviews blog (with comments off)."""
    _name = "practice.review"
    _description = "Practitioner Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    _rec_name = "title"

    partner_id = fields.Many2one(
        "res.partner", string="Client", required=True, index=True, ondelete="cascade",
        readonly=True)
    practitioner_id = fields.Many2one(
        "practice.practitioner", required=True, index=True, ondelete="cascade",
        readonly=True)
    rating = fields.Integer(required=True, readonly=True, tracking=True)
    stars = fields.Char(compute="_compute_stars")
    title = fields.Char(required=True, readonly=True)
    body = fields.Text(string="Review", required=True, readonly=True)
    display_name_public = fields.Char(
        string="Shown As", required=True, readonly=True,
        help="The name shown with the published review, as the client chose it.")
    photo_ids = fields.Many2many(
        "practice.photo", "practice_review_photo_rel", "review_id", "photo_id",
        string="Photos", readonly=True,
        help="Photos the client chose to show with their review. Only their own "
             "photos shared with them can be chosen.")
    state = fields.Selection(
        [("submitted", "To Review"), ("published", "Published"),
         ("rejected", "Not Published"), ("withdrawn", "Withdrawn by Client")],
        default="submitted", required=True, tracking=True, readonly=True)
    reject_reason = fields.Text(
        string="Reason", tracking=True,
        help="Shown to the client in their portal when a review isn't published.")
    moderated_by_id = fields.Many2one("res.users", readonly=True)
    moderated_date = fields.Datetime(readonly=True)
    blog_post_id = fields.Many2one("blog.post", readonly=True, copy=False, ondelete="set null")
    public_attachment_ids = fields.Many2many(
        "ir.attachment", "practice_review_public_attachment_rel", "review_id",
        "attachment_id", readonly=True, copy=False,
        help="Public copies of the chosen photos, made when the review is published "
             "and removed when it comes down.")

    _rating_range = models.Constraint(
        "CHECK(rating >= 1 AND rating <= 5)", "A rating is 1 to 5 stars.")

    @api.depends("rating")
    def _compute_stars(self):
        for review in self:
            review.stars = "★" * (review.rating or 0) + "☆" * (5 - (review.rating or 0))

    @api.constrains("photo_ids", "partner_id")
    def _check_photos_are_the_clients(self):
        for review in self:
            foreign = review.photo_ids.filtered(
                lambda p: p.partner_id != review.partner_id or not p.shared_with_client)
            if foreign:
                raise ValidationError(_(
                    "A review can only show the client's own photos shared with them."))

    # ------------------------------------------------------------------
    # Who may review whom
    # ------------------------------------------------------------------
    @api.model
    def _reviewable_practitioners(self, partner):
        """Practitioners the client has had a completed appointment with and
        hasn't already got a review waiting or published for."""
        done = self.env["practice.appointment"].sudo().search([
            ("partner_id", "=", partner.id), ("state", "=", "completed")]).practitioner_id
        open_reviews = self.sudo().search([
            ("partner_id", "=", partner.id), ("state", "in", OPEN_STATES)]).practitioner_id
        return done - open_reviews

    @api.model
    def _portal_submit(self, partner, practitioner, rating, title, body, shown_as, photos):
        """Create a review from the portal form, after checking everything the
        form could have been tampered with."""
        if practitioner not in self._reviewable_practitioners(partner):
            raise UserError(_("You can review a practitioner after a completed visit, once."))
        if not 1 <= rating <= 5:
            raise UserError(_("Choose 1 to 5 stars."))
        if not (title or "").strip() or not (body or "").strip():
            raise UserError(_("Give your review a title and a few words."))
        allowed = self.env["practice.photo"].sudo().search([
            ("partner_id", "=", partner.id), ("shared_with_client", "=", True)])
        if photos - allowed:
            raise UserError(_("You can only add your own photos."))
        review = self.sudo().create({
            "partner_id": partner.id, "practitioner_id": practitioner.id, "rating": rating,
            "title": title.strip()[:120], "body": body.strip()[:4000],
            "display_name_public": (shown_as or "").strip()[:60] or self._default_shown_as(partner),
            "photo_ids": [(6, 0, photos.ids)],
        })
        review._notify_moderator()
        return review

    @api.model
    def _default_shown_as(self, partner):
        """First name and last initial: enough to be real, not enough to find
        someone."""
        parts = (partner.name or "").split()
        if len(parts) >= 2:
            return "%s %s." % (parts[0], parts[-1][0])
        return parts[0] if parts else _("A client")

    def _notify_moderator(self):
        moderator = self.env.company.practice_review_moderator_id or self.env.ref(
            "base.user_admin", raise_if_not_found=False)
        for review in self:
            if moderator and moderator.active:
                review.activity_schedule(
                    "mail.mail_activity_data_todo", user_id=moderator.id,
                    summary=_("Review to check: %s", review.practitioner_id.display_name))

    # ------------------------------------------------------------------
    # Moderation
    # ------------------------------------------------------------------
    def action_publish(self):
        for review in self:
            if review.state not in ("submitted", "rejected"):
                raise UserError(_("Only a review waiting to be checked can be published."))
            blog = self.env["blog.blog"]._practice_review_blog()
            if not blog:
                raise UserError(_("Set a reviews blog first, in Settings › Practice Appointments."))
            post = self.env["blog.post"].sudo().create({
                "blog_id": blog.id,
                "name": review.title,
                "subtitle": "%s %s" % (review.stars, review.practitioner_id.display_name),
                "author_id": self.env.company.partner_id.id,
                "tag_ids": [(4, review._practitioner_tag(blog).id)],
                "content": "<p></p>",
            })
            review.public_attachment_ids = review._public_photo_copies(post)
            post.write({"content": review._post_html(), "is_published": True})
            review.write({
                "state": "published", "blog_post_id": post.id, "reject_reason": False,
                "moderated_by_id": self.env.user.id, "moderated_date": fields.Datetime.now(),
            })
            review.activity_unlink(["mail.mail_activity_data_todo"])

    def action_reject(self):
        for review in self:
            review._take_down()
            review.write({"state": "rejected", "moderated_by_id": self.env.user.id,
                          "moderated_date": fields.Datetime.now()})
            review.activity_unlink(["mail.mail_activity_data_todo"])

    def _portal_withdraw(self):
        for review in self:
            review._take_down()
            review.state = "withdrawn"
            review.activity_unlink(["mail.mail_activity_data_todo"])

    def _take_down(self):
        """Remove the published post and the public photo copies."""
        for review in self.sudo():
            if review.blog_post_id:
                review.blog_post_id.unlink()
            review.public_attachment_ids.unlink()

    def _practitioner_tag(self, blog):
        Tag = self.env["blog.tag"].sudo()
        name = self.practitioner_id.display_name
        return Tag.search([("name", "=", name)], limit=1) or Tag.create({"name": name})

    def _public_photo_copies(self, post):
        """Published reviews show copies of the chosen photos; the originals
        stay private session attachments."""
        copies = self.env["ir.attachment"]
        for photo in self.sudo().photo_ids:
            source = photo.attachment_id
            copies |= self.env["ir.attachment"].sudo().create({
                "name": "review-%s-%s" % (self.id, source.name or photo.id),
                "datas": source.datas, "mimetype": source.mimetype,
                "res_model": "blog.post", "res_id": post.id, "public": True,
            })
        return copies

    def _post_html(self):
        self.ensure_one()
        photos = Markup("").join(
            Markup('<div class="col-6 col-md-4 mb-3"><img src="/web/image/%s" class="img-fluid rounded" '
                   'alt="%s" loading="lazy"/></div>') % (a.id, _("Photo shared by %s", self.display_name_public))
            for a in self.public_attachment_ids)
        paragraphs = Markup("").join(
            Markup("<p>%s</p>") % line for line in self.body.splitlines() if line.strip())
        return (Markup('<section class="o_practice_review">'
                       '<p class="o_practice_review_stars fs-3 mb-2" aria-label="%s">%s</p>'
                       '<blockquote class="blockquote">%s</blockquote>'
                       '<p class="text-muted">%s</p>') % (
                    _("%s out of 5 stars", self.rating), self.stars, paragraphs,
                    _("%(name)s, about %(practitioner)s", name=self.display_name_public,
                      practitioner=self.practitioner_id.display_name))
                + (Markup('<div class="row">%s</div>') % photos if photos else Markup(""))
                + Markup("</section>"))
