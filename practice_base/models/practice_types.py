# -*- coding: utf-8 -*-
import pytz

from odoo import fields, models


def local_when(env, value):
    """A datetime as the practice reads it: in the company's time zone (its
    contact's), else the user's, as "Dec 2, 9:00 AM"."""
    if not value:
        return env._("no date")
    tz = pytz.timezone(env.company.partner_id.tz or env.user.tz or "UTC")
    local = pytz.utc.localize(value).astimezone(tz)
    return local.strftime("%b %-d, %-I:%M %p")


CONSENT_KINDS = [
    ("treatment", "Treatment Consent"),
    ("test", "Pre-treatment Test Consent"),
    ("photo_release", "Photo Release"),
]


class PracticePlanType(models.Model):
    """What a practice treats: massage for back pain, a sleep remedy, a
    strength program, areola restoration... Each practice keeps its own
    list."""
    _name = "practice.plan.type"
    _description = "Treatment Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(translate=True)
    active = fields.Boolean(default=True)


class PracticeTestType(models.Model):
    """A check done before treatment starts: a skin patch test for an oil,
    herb or pigment, a fitness assessment... and how long until it's read."""
    _name = "practice.test.type"
    _description = "Pre-treatment Test Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    read_after_days = fields.Integer(
        string="Read After (days)", default=0,
        help="How many days after the test its result is read. 0 means the "
             "result is known straight away.")
    active = fields.Boolean(default=True)


class PracticeHealthFlag(models.Model):
    """Something a practitioner must know before treating a client, such as
    blood thinners or pregnancy. Each practice keeps its own list."""
    _name = "practice.health.flag"
    _description = "Health Flag"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(translate=True)
    color = fields.Integer()
    active = fields.Boolean(default=True)


class PracticeConsentForm(models.Model):
    """The wording a client agrees to. The suite ships plain forms; a
    practice edits them or adds its own, and the first active form of a
    kind is used for new consents."""
    _name = "practice.consent.form"
    _description = "Consent Form"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    kind = fields.Selection(CONSENT_KINDS, required=True, default="treatment")
    sequence = fields.Integer(default=10)
    body = fields.Html(required=True, translate=True, sanitize=True)
    active = fields.Boolean(default=True)
