# -*- coding: utf-8 -*-
import base64
import re
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import HttpCase, tagged

# A 1x1 PNG.
PNG = base64.b64encode(bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d"
    "49444154789c6360000002000154a24f5d0000000049454e44ae426082"))


@tagged("post_install", "-at_install")
class TestPracticeReview(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        portal = cls.env.ref("base.group_portal")
        cls.client_user = cls.env["res.users"].create({
            "name": "Rosa Delgado", "login": "rosa_review", "password": "rosa_review_pw12",
            "email": "rosa@example.com", "group_ids": [(6, 0, [portal.id])]})
        cls.client = cls.client_user.partner_id
        cls.client.is_client = True
        staff = cls.env["res.users"].create({
            "name": "Morgan Reyes", "login": "morgan_review",
            "group_ids": [(6, 0, [cls.env.ref("base.group_user").id,
                                  cls.env.ref("practice_base.group_practice_staff").id])]})
        cls.practitioner = cls.env["practice.practitioner"].create({"user_id": staff.id})
        other = cls.env["res.users"].create({
            "name": "Sam Lee", "login": "sam_review",
            "group_ids": [(6, 0, [cls.env.ref("base.group_user").id])]})
        cls.other_practitioner = cls.env["practice.practitioner"].create({"user_id": other.id})
        cls.service = cls.env["practice.service"].create({"name": "Massage, 60 minutes", "duration": 1.0})
        cls.plan = cls.env["practice.plan"].create({"partner_id": cls.client.id})
        cls.appointment = cls.env["practice.appointment"].with_context(skip_appointment_checks=True).create({
            "partner_id": cls.client.id, "plan_id": cls.plan.id, "service_id": cls.service.id,
            "practitioner_id": cls.practitioner.id,
            "start": fields.Datetime.now() - timedelta(days=3), "state": "completed"})
        after = cls.env["ir.attachment"].create({"name": "after.png", "datas": PNG, "mimetype": "image/png"})
        hidden = cls.env["ir.attachment"].create({"name": "hidden.png", "datas": PNG, "mimetype": "image/png"})
        session = cls.env["practice.session"].create({
            "plan_id": cls.plan.id, "after_photo_ids": [(6, 0, [after.id, hidden.id])]})
        cls.shared_photo = session.photo_ids.filtered(lambda p: p.attachment_id == after)
        cls.shared_photo.shared_with_client = True
        cls.private_photo = session.photo_ids.filtered(lambda p: p.attachment_id == hidden)
        cls.Review = cls.env["practice.review"]

    def _submit(self, photos=None, practitioner=None, rating=5):
        return self.Review._portal_submit(
            self.client, practitioner or self.practitioner, rating, "Back pain gone",
            "Two sessions and I can sleep again.", "", photos or self.env["practice.photo"])

    def test_only_practitioners_with_a_completed_visit_can_be_reviewed(self):
        self.assertEqual(self.Review._reviewable_practitioners(self.client), self.practitioner)
        with self.assertRaises(UserError):
            self._submit(practitioner=self.other_practitioner)

    def test_one_open_review_per_practitioner(self):
        self._submit()
        self.assertFalse(self.Review._reviewable_practitioners(self.client))
        with self.assertRaises(UserError):
            self._submit()

    def test_a_new_review_waits_for_staff_with_a_to_do(self):
        review = self._submit()
        self.assertEqual(review.state, "submitted")
        self.assertFalse(review.blog_post_id)
        self.assertTrue(review.activity_ids)
        self.assertEqual(review.display_name_public, "Rosa D.")

    def test_stars_are_one_to_five(self):
        with self.assertRaises(UserError):
            self._submit(rating=6)

    def test_only_the_clients_own_shared_photos(self):
        with self.assertRaises(UserError):
            self._submit(photos=self.private_photo)

    def test_publishing_puts_it_on_the_reviews_blog_with_photo_copies(self):
        review = self._submit(photos=self.shared_photo)
        review.action_publish()
        post = review.blog_post_id
        self.assertEqual(review.state, "published")
        self.assertTrue(post.is_published)
        self.assertEqual(post.blog_id, self.env.ref("practice_review.blog_client_reviews"))
        self.assertIn(self.practitioner.display_name, post.tag_ids.mapped("name"))
        self.assertIn("★★★★★", post.content)
        self.assertNotIn("Delgado", post.content)
        copy = review.public_attachment_ids
        self.assertTrue(copy.public)
        self.assertNotEqual(copy, self.shared_photo.attachment_id)
        self.assertFalse(self.shared_photo.attachment_id.public)
        self.assertIn("/web/image/%s" % copy.id, post.content)

    def test_withdrawing_takes_the_post_and_photo_copies_down(self):
        review = self._submit(photos=self.shared_photo)
        review.action_publish()
        post, copies = review.blog_post_id, review.public_attachment_ids
        review._portal_withdraw()
        self.assertEqual(review.state, "withdrawn")
        self.assertFalse(post.exists())
        self.assertFalse(copies.exists())
        self.assertEqual(self.Review._reviewable_practitioners(self.client), self.practitioner)

    def test_not_publishing_keeps_it_off_the_website(self):
        review = self._submit()
        review.reject_reason = "It names another client."
        review.action_reject()
        self.assertEqual(review.state, "rejected")
        self.assertFalse(review.blog_post_id)

    def test_comments_are_refused_on_review_posts(self):
        review = self._submit()
        review.action_publish()
        post = review.blog_post_id.with_user(self.client_user)
        with self.assertRaises(AccessError):
            post.message_post(body="Nice!", message_type="comment")

    def test_portal_form_sends_a_review(self):
        self.authenticate("rosa_review", "rosa_review_pw12")
        page = self.url_open("/my/reviews")
        self.assertIn("Review Morgan Reyes", page.text)
        form = self.url_open("/my/reviews/new/%s" % self.practitioner.id)
        self.assertEqual(form.status_code, 200)
        token = re.search(r'name="csrf_token" value="([^"]+)"', form.text).group(1)
        response = self.url_open("/my/reviews/new/%s" % self.practitioner.id, data={
            "csrf_token": token, "rating": "4", "title": "Calm and kind",
            "body": "Felt listened to.", "shown_as": "R.D.",
            "photo_ids": str(self.shared_photo.id), "photo_consent": "1"})
        self.assertIn("/my/reviews", response.url)
        review = self.Review.search([("partner_id", "=", self.client.id)])
        self.assertEqual((review.rating, review.display_name_public), (4, "R.D."))
        self.assertEqual(review.photo_ids, self.shared_photo)

    def test_portal_refuses_a_practitioner_without_a_visit(self):
        self.authenticate("rosa_review", "rosa_review_pw12")
        response = self.url_open("/my/reviews/new/%s" % self.other_practitioner.id)
        self.assertTrue(response.url.endswith("/my/reviews"))

    def test_no_comment_box_on_reviews_even_with_comments_on(self):
        self.env.ref("website_blog.opt_blog_post_comment").active = True
        review = self._submit()
        review.action_publish()
        news = self.env["blog.blog"].create({"name": "News"})
        ordinary = self.env["blog.post"].create({"blog_id": news.id, "name": "Open late on Fridays",
                                                 "is_published": True})
        self.assertNotIn('id="o_wblog_post_comments"', self.url_open(review.blog_post_id.website_url).text)
        self.assertIn('id="o_wblog_post_comments"', self.url_open(ordinary.website_url).text)
