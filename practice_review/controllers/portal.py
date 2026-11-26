# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PracticeReviewPortal(CustomerPortal):
    """My Reviews: a client reviews the practitioners they've had a completed
    visit with. Everything is looked up from the signed-in client, never from
    an id alone, and runs as sudo with no portal access rules on the models."""

    def _client(self):
        return request.env.user.partner_id

    def _my_reviews(self):
        return request.env["practice.review"].sudo().search([("partner_id", "=", self._client().id)])

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "practice_review_count" in counters:
            Review = request.env["practice.review"]
            values["practice_review_count"] = (
                len(self._my_reviews()) + len(Review._reviewable_practitioners(self._client())))
        return values

    @http.route(["/my/reviews"], type="http", auth="user", website=True)
    def my_reviews(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "practice_reviews",
            "reviews": self._my_reviews(),
            "practitioners": request.env["practice.review"]._reviewable_practitioners(self._client()),
            "sent": kw.get("sent"), "withdrawn": kw.get("withdrawn"),
        })
        return request.render("practice_review.portal_my_reviews", values)

    @http.route(["/my/reviews/new/<int:practitioner_id>"], type="http", auth="user", website=True,
                methods=["GET", "POST"])
    def my_review_new(self, practitioner_id, **post):
        partner = self._client()
        Review = request.env["practice.review"]
        practitioner = request.env["practice.practitioner"].sudo().browse(practitioner_id).exists()
        if not practitioner or practitioner not in Review._reviewable_practitioners(partner):
            return request.redirect("/my/reviews")
        photos = request.env["practice.photo"].sudo().search([
            ("partner_id", "=", partner.id), ("shared_with_client", "=", True)])
        error = None
        if request.httprequest.method == "POST":
            chosen = photos.filtered(
                lambda p: str(p.id) in request.httprequest.form.getlist("photo_ids"))
            if chosen and not post.get("photo_consent"):
                error = "To include photos, tick the box saying they may be shown with your review."
            else:
                try:
                    rating = int(post.get("rating") or 0)
                    Review._portal_submit(partner, practitioner, rating, post.get("title"),
                                          post.get("body"), post.get("shown_as"), chosen)
                    return request.redirect("/my/reviews?sent=1")
                except (UserError, ValueError) as exc:
                    error = str(exc.args[0]) if exc.args else str(exc)
        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "practice_reviews",
            "practitioner": practitioner, "photos": photos, "error": error, "post": post,
            "shown_as_default": Review._default_shown_as(partner),
        })
        return request.render("practice_review.portal_review_form", values)

    @http.route(["/my/reviews/<int:review_id>/withdraw"], type="http", auth="user", website=True,
                methods=["POST"])
    def my_review_withdraw(self, review_id, **kw):
        review = self._my_reviews().filtered(lambda r: r.id == review_id)
        if review and review.state in ("submitted", "published"):
            review._portal_withdraw()
        return request.redirect("/my/reviews?withdrawn=1")
