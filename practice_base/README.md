# Practitioner Suite - Client Records

The records side of a practice that treats clients one to one: clients,
practitioners, treatment plans, consent, pre-treatment tests and sessions.

## What it adds

### Clients

A **Client** tab on the contact form (staff-only): a client number
(`CL00001`), date of birth, emergency contact, referring provider, the
practice's own **health flags** (tags such as Pregnant or Blood thinners,
kept in Configuration), allergies, and other health notes. Insurance payer
and member ID fields stay hidden unless filled in.

### Practitioners

`practice.practitioner` wraps a staff login, their working hours (an Odoo
`resource.calendar`, so time off is handled for free), a licence or
certification number, and an NPI number for practices that may bill
insurance one day. Its own record from day one, so a solo practice can add
a second practitioner later without restructuring.

### Treatment plans, consent, tests, sessions

- **`practice.plan`**: what's being treated (a **treatment type** from the
  practice's own list), the area or focus, when it started, the background,
  and the primary practitioner. Every consent, test and session hangs off it.
- **`practice.consent`**: one record per consent (treatment, pre-treatment
  test or photo release), printed from an editable **consent form**
  (`practice.consent.form`; the first active form of a kind is used) with an
  acceptance checkbox. No e-signature module needed.
- **`practice.test`**: a **pre-treatment test** of one of the practice's
  **test types**, the product and lot tested, the date, and a read date from
  the type's waiting time. A plan's `test_clear` follows its latest test.
- **`practice.session`**: date, products and lot used, area, notes,
  aftercare, reactions, before and after photos, and a recommended next
  session. Numbered in date order within its plan.

A new database gets one starting treatment type ("General treatment"), one
test type ("Skin patch test", read after 2 days) and plain consent wording,
all editable. Packs such as `practice_pack_paramedical_tattoo` add a
practice's own setup.

## Data handling

Every model here is staff-only: one security group (**Practitioner /
Staff**) and no portal or public access rows. A portal user, or an internal
user without the group, gets an access error.

## Requirements

Odoo 19 Community: `contacts`, `resource`, `mail`.

## Tests

`--test-tags=/practice_base`: client numbers, plan, consent, test and
session defaults and computed fields, the practice's own types, consent
forms, session numbering, the consent PDF, and the access boundary.
