# Paramedical Tattoo - Patient Records

The clinical side of a paramedical/medical tattooing practice: patients,
practitioners, the conditions being treated, informed consent, pigment
patch tests, and treatment sessions.

## What it adds

### Patients

Extends the contact form with a **Patient** tab (staff-only, hidden
entirely from anyone without the Practitioner/Staff group): a
system-assigned patient number, date of birth, emergency contact,
referring provider, and the safety-relevant medical flags a practitioner
needs before a session - bleeding disorders, blood thinners, keloid
history, allergies, plus a free-text notes field for anything else.
Separately, a photo/marketing consent flag distinct from clinical
treatment consent. Insurance payer/member-ID fields exist but sit unused
and hidden unless filled in - there so a future move to billing insurance
doesn't need a schema change.

### Practitioners

`paramedic.practitioner` wraps a staff login, their working hours (an
Odoo `resource.calendar`, so time off is handled for free), a licence
number, and an NPI number (also unused today, same forward-compatibility
reasoning). Modelled as its own record from day one so a solo practice
can add a second practitioner later without any restructuring - the
appointment-scheduling module (planned) computes availability per
practitioner.

### Conditions, consent, patch tests, sessions

- **`patient.condition`** - what's being treated (areola restoration,
  scar camouflage, scalp micropigmentation, vitiligo, or free-text
  "other"), the area, onset date, and the practitioner responsible for
  continuity of care. Every consent, patch test, and session for that
  issue hangs off this record.
- **`patient.consent`** - one row per consent (treatment, patch test, or
  photo release), with a printable QWeb form (adapts its wording to the
  consent type) and an acceptance checkbox - no e-signature module
  required.
- **`patient.patch_test`** - pigment, lot number, application date, and
  a read date that defaults to 3 days later (edit if read sooner or
  later). A condition's `patch_test_clear` flag tracks whether its most
  recent test came back clear.
- **`patient.treatment.session`** - date, pigment/lot used, area,
  clinical notes, aftercare given, adverse reactions, before/after
  photos, and a recommended next-session date. Numbered automatically in
  date order within its condition.

## Data handling

Every model this module adds is staff-only - there is exactly one
security group (**Practitioner / Staff**) and no portal or public access
rows anywhere in `security/ir.model.access.csv`. A portal or unprivileged
internal user gets a plain access error, not an empty list, if they ever
try. See the repository README for the (non-)compliance note.

## Requirements

Odoo 19 Community, `contacts`, `resource`, `mail`. No extra Python
packages.

## Tests

`--test-tags=/paramedic_base` (14): patient-number assignment (once,
only for patients), condition/consent/patch-test/session computed
fields and defaults, session numbering, the consent PDF renders, and the
access-control boundary - a portal user and a plain internal user without
the staff group are both refused, a user with it is not.
