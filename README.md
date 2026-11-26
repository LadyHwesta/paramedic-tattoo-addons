# Practitioner Suite

Odoo 19 **Community** modules for any practice that treats clients one to
one: massage therapists, herbalists, personal trainers, paramedical tattoo
artists and the like. Client records, consent, scheduling and online
booking, a client portal, billing, and client reviews.

Built so a solo practitioner can start alone and add practitioners later
without a rebuild. Odoo's own self-service booking app (Appointments) is
Enterprise-only, so booking is built here on Odoo's `resource` module.

## Modules

- `practice_base`: clients (on `res.partner`) with the practice's own
  **health flags**, practitioners, **treatment plans** (from the practice's
  own list of treatment types), consents printed from editable **consent
  forms**, **pre-treatment tests** (the practice's own test types and waiting
  times), and sessions with before and after photos. Staff-only: nothing is
  reachable from a portal or public page.
- `practice_appointment`: services with a duration, buffer time and the
  checks they need first (a clear test, a signed consent), practitioners'
  working hours via Odoo's `resource` module, and a portal booking page so a
  client can request an open time without a phone call.
- `practice_billing`: a price on each service and an invoice from a
  completed appointment in one click.
- `practice_client_portal`: notes marked **Internal** or **Shared with
  client**, photos shared with the client, and the client's own permission
  to use each photo in marketing. Adds **My Records** to the portal.
- `practice_review`: clients review the practitioner who treated them, with
  stars, words and their own photos; staff check every review before it's
  published to a **Client Reviews** blog with comments off.
- `practice_my_day`: the practice's day in My Day (`odoo-addons/my_day`):
  today's appointments, booking requests, tests to read and clients due back.
- `practice_pack_paramedical_tattoo`: sets the suite up for a paramedical
  tattoo practice (treatment types, pigment patch test, health flags, consent
  wording, surgery date and numbing agent).
- `practice_elearning`, `practice_elearning_billing`,
  `practice_elearning_client_portal`, `practice_elearning_review`: short,
  ready-built courses in Odoo's eLearning app, with quizzes and screenshots.
  Each course module has a `tools/build_course_data.py`; the screenshots come
  from `practice_elearning/tools/sample_practice.py` and `shoot.py`.

## A note on client data

Client records can hold health information, so they're handled carefully
whatever privacy law applies to a given practice: records are staff-only
unless a practitioner shares a note or photo with that client, changes are
tracked, and photos are private attachments served only to their own client
(published reviews show copies the client chose). None of this replaces
checking with your licensing board or an attorney about the recordkeeping
and consent rules for your kind of practice; this repo doesn't certify
compliance with any regulation.

## Testing

[`testing/`](testing/) is a self-contained local Odoo 19 + Postgres
instance: see [`testing/README.md`](testing/README.md).

## Compatibility

Targets **Odoo 19.0**, tracked on `main` (mirrored to a `19.0` branch).

## License

LGPL-3: see [`LICENSE`](LICENSE).
