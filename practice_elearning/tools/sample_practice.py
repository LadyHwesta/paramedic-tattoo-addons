"""Sample practice for the course screenshots. Run in an odoo-bin shell on a
throwaway database with the whole Practitioner Suite installed (generic
chart, website):

    odoo-bin shell -d practicecourse < practice_elearning/tools/sample_practice.py

Riverbend Wellness: a massage therapist (the admin, Jordan Ellis) and an
herbalist (Priya Nair). Clients with treatment plans, a signed consent, a
clear skin patch test, sessions with photos, invoices, a shared note and two
reviews (one waiting to be checked, one published). All made up.
"""
import base64
import io
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont

from odoo import fields


def picture(label, top, bottom):
    """A plain placeholder photo: a soft gradient with a label."""
    img = Image.new("RGB", (640, 480))
    draw = ImageDraw.Draw(img)
    for y in range(480):
        t = y / 479
        draw.line([(0, y), (640, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
    draw.text((96, 400), label, fill=(255, 255, 255), font=font)  # inside the square crop
    out = io.BytesIO()
    img.save(out, "PNG")
    return base64.b64encode(out.getvalue())


env = env(context=dict(env.context, tz="America/Los_Angeles"))
company = env["res.company"].browse(1)
company.write({"name": "Riverbend Wellness", "country_id": env.ref("base.us").id})
company.partner_id.tz = "America/Los_Angeles"

admin = env.ref("base.user_admin")
admin.write({"name": "Jordan Ellis", "tz": "America/Los_Angeles"})
staff_groups = [env.ref("base.group_user").id, env.ref("practice_base.group_practice_staff").id]
Users = env["res.users"]
priya = Users.search([("login", "=", "priya")]) or Users.create({
    "name": "Priya Nair", "login": "priya", "password": "priya", "tz": "America/Los_Angeles",
    "group_ids": [(6, 0, staff_groups)]})
portal = env.ref("base.group_portal").id
rosa_user = Users.search([("login", "=", "rosa")]) or Users.create({
    "name": "Rosa Delgado", "login": "rosa", "password": "rosa", "email": "rosa@example.com",
    "group_ids": [(6, 0, [portal])]})
marcus_user = Users.search([("login", "=", "marcus")]) or Users.create({
    "name": "Marcus Webb", "login": "marcus", "password": "marcus", "email": "marcus@example.com",
    "group_ids": [(6, 0, [portal])]})

Practitioner = env["practice.practitioner"]
jordan_p = Practitioner.search([("user_id", "=", admin.id)]) or Practitioner.create({
    "user_id": admin.id, "license_number": "LMT 48213"})
priya_p = Practitioner.search([("user_id", "=", priya.id)]) or Practitioner.create({
    "user_id": priya.id, "license_number": "RH (AHG) 1187"})

PlanType = env["practice.plan.type"]
back = PlanType.search([("name", "=", "Deep tissue for back pain")]) or PlanType.create(
    {"name": "Deep tissue for back pain", "sequence": 10})
sleep = PlanType.search([("name", "=", "Sleep support")]) or PlanType.create(
    {"name": "Sleep support", "sequence": 20})
patch = env.ref("practice_base.test_type_skin_patch")
Flag = env["practice.health.flag"]
flags = {}
for name, color in (("Pregnant", 3), ("Blood thinners", 1), ("Recent injury", 2)):
    flags[name] = Flag.search([("name", "=", name)]) or Flag.create({"name": name, "color": color})

Service = env["practice.service"]
def service(name, hours, price, **kw):
    s = Service.search([("name", "=", name)]) or Service.create(dict({"name": name, "duration": hours}, **kw))
    s.list_price = price
    return s

consult = service("Consultation, 30 minutes", 0.5, 40, bookable_online=True)
massage = service("Massage, 60 minutes", 1.0, 95, bookable_online=True, requires_test=True,
                  requires_treatment_consent=True, creates_treatment_session=True,
                  practitioner_ids=[(6, 0, jordan_p.ids)])
herbal = service("Herbal consultation, 45 minutes", 0.75, 70, bookable_online=True,
                 practitioner_ids=[(6, 0, priya_p.ids)])

rosa = rosa_user.partner_id
rosa.write({"is_client": True, "phone": "(707) 555-0142", "date_of_birth": "1984-06-12",
            "emergency_contact_name": "Luis Delgado", "emergency_contact_phone": "(707) 555-0178",
            "health_flag_ids": [(6, 0, flags["Recent injury"].ids)], "has_allergies": True,
            "allergy_notes": "Lavender oil (rash)."})
marcus = marcus_user.partner_id
marcus.write({"is_client": True, "health_flag_ids": [(6, 0, flags["Blood thinners"].ids)]})

Plan = env["practice.plan"]
rosa_plan = Plan.search([("partner_id", "=", rosa.id), ("plan_type_id", "=", back.id)]) or Plan.create({
    "partner_id": rosa.id, "plan_type_id": back.id, "area": "Lower back", "state": "active",
    "practitioner_id": jordan_p.id, "start_date": fields.Date.today() - timedelta(days=30),
    "background": "Desk job; pain after a fall in September. Goal: sleep through the night without pain."})
if not rosa_plan.consent_ids:
    env["practice.consent"].create({"plan_id": rosa_plan.id, "consent_type": "treatment", "signed": True,
                                    "signature_method": "In person, paper form"})
    env["practice.consent"].create({"plan_id": rosa_plan.id, "consent_type": "photo_release", "signed": True,
                                    "signature_method": "In person, paper form"})
if not rosa_plan.test_ids:
    env["practice.test"].create({"plan_id": rosa_plan.id, "test_type_id": patch.id,
                                 "product_name": "Arnica massage oil", "product_lot": "AR-2291",
                                 "test_date": fields.Date.today() - timedelta(days=28), "result": "clear"})
marcus_plan = Plan.search([("partner_id", "=", marcus.id)]) or Plan.create({
    "partner_id": marcus.id, "plan_type_id": sleep.id, "area": "Falling asleep", "state": "active",
    "practitioner_id": priya_p.id})

Appt = env["practice.appointment"].with_context(skip_appointment_checks=True)
now = datetime.now().replace(minute=0, second=0, microsecond=0)
def appt(partner, plan, svc, who, days, hour, state):
    start = (now + timedelta(days=days)).replace(hour=hour)
    found = Appt.search([("partner_id", "=", partner.id), ("service_id", "=", svc.id), ("start", "=", start)])
    return found or Appt.create({"partner_id": partner.id, "plan_id": plan.id, "service_id": svc.id,
                                 "practitioner_id": who.id, "start": start, "state": state})

first = appt(rosa, rosa_plan, massage, jordan_p, -21, 17, "confirmed")
second = appt(rosa, rosa_plan, massage, jordan_p, -7, 17, "confirmed")
herbal_visit = appt(rosa, rosa_plan, herbal, priya_p, -5, 18, "completed")
marcus_visit = appt(marcus, marcus_plan, herbal, priya_p, -10, 19, "completed")
marcus_massage = appt(marcus, marcus_plan, consult, jordan_p, -12, 16, "completed")
appt(rosa, rosa_plan, massage, jordan_p, 7, 17, "confirmed")
appt(marcus, marcus_plan, consult, jordan_p, 3, 16, "requested")
for visit in (first, second):
    if visit.state != "completed":
        visit.action_complete()

photos = [
    ("before.png", picture("Before, first session", (196, 160, 140), (120, 92, 80)), "before", first),
    ("after.png", picture("After, second session", (214, 182, 160), (150, 118, 100)), "after", second),
]
for name, data, kind, visit in photos:
    session = visit.session_id
    if session and not session.photo_ids:
        att = env["ir.attachment"].create({"name": name, "datas": data, "mimetype": "image/png"})
        session.write({"%s_photo_ids" % kind: [(4, att.id)], "product_name": "Arnica massage oil",
                       "product_lot": "AR-2291", "area_treated": "Lower back",
                       "notes": "Tension through the left side; eased by the end.",
                       "next_session_recommended_date": fields.Date.today() + timedelta(days=7)})
for photo in env["practice.photo"].search([("partner_id", "=", rosa.id)]):
    photo.shared_with_client = True
after = env["practice.photo"].search([("partner_id", "=", rosa.id), ("kind", "=", "after")], limit=1)
if after and not after.marketing_ok:
    after.with_user(rosa_user).sudo()._portal_set_marketing(True)

Note = env["practice.note"]
if not Note.search([("partner_id", "=", rosa.id)]):
    Note.create({"partner_id": rosa.id, "title": "Two-week check-in", "session_id": second.session_id.id,
                 "body": "<p>Moving more freely. Keep up the stretches twice a day, and use heat, not ice.</p>",
                 "author_id": admin.id, "visibility": "client"})

# Billing: the first visit invoiced and paid, the second invoiced (draft), Marcus's still to bill.
if not first.invoice_id:
    first.action_create_invoice()
    first.invoice_id.action_post()
    env["account.payment.register"].with_context(active_model="account.move",
                                                  active_ids=first.invoice_id.ids).create({})._create_payments()
if not second.invoice_id:
    second.action_create_invoice()
if not herbal_visit.invoice_id:
    herbal_visit.action_create_invoice()
    herbal_visit.invoice_id.action_post()

# Reviews: Marcus's published, Rosa's for Jordan waiting to be checked (Priya still reviewable).
Review = env["practice.review"]
if not Review.search([]):
    published = Review._portal_submit(marcus, priya_p, 5, "Finally sleeping",
                                      "Priya listened, explained every herb, and checked in after a week. "
                                      "I'm sleeping through most nights now.", "", env["practice.photo"])
    published.action_publish()
    Review._portal_submit(rosa, jordan_p, 5, "My back thanks you",
                          "Two sessions in and I can sit through a workday again. Jordan explains what "
                          "they're doing and why.", "", after)

env.cr.commit()
print("SAMPLE READY", "rosa", rosa.id, "plan", rosa_plan.id, "massage", massage.id,
      "upcoming", Appt.search([("state", "=", "confirmed"), ("start", ">", fields.Datetime.now())], limit=1).id)
