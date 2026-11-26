# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class BlogBlog(models.Model):
    _inherit = "blog.blog"

    is_practice_review_blog = fields.Boolean(
        string="Client Reviews Blog",
        help="Published practitioner reviews go here, and nobody can comment on "
             "its posts.")

    @api.model
    def _practice_review_blog(self):
        return self.sudo().search([("is_practice_review_blog", "=", True)], limit=1)


class BlogPost(models.Model):
    _inherit = "blog.post"

    is_practice_review = fields.Boolean(related="blog_id.is_practice_review_blog")

    def message_post(self, **kwargs):
        # Reviews have comments off, even if the website allows comments on its
        # other blogs: the comment box is hidden, and this refuses one sent anyway.
        if (kwargs.get("message_type", "notification") == "comment"
                and not self.env.user._is_internal()
                and any(self.sudo().mapped("blog_id.is_practice_review_blog"))):
            raise AccessError(_("Comments are turned off on reviews."))
        return super().message_post(**kwargs)
