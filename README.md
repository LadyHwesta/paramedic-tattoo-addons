# Paramedical Tattoo Addons

Odoo 19 **Community** modules for paramedical / medical tattooing
practices — areola restoration, scar camouflage, scalp micropigmentation,
vitiligo repigmentation, and similar work — covering patient records and
appointment scheduling.

Built for one practitioner's studio, but designed from the start to grow
to several practitioners without a rebuild, since Odoo's own self-service
booking app (Appointments) is Enterprise-only and there's no Community
equivalent.

## Modules

- `paramedic_base` — patients (extends `res.partner`), practitioners,
  the condition being treated, informed consent, pigment patch tests, and
  treatment sessions with before/after photos. Locked down to staff;
  nothing here is ever reachable through a portal or public view.
- `paramedic_appointment` — service types with duration and required
  prerequisites (e.g. "needs a completed patch test"), practitioner
  working hours via Odoo's `resource` module, and a portal booking page
  so a patient can request an open slot without a phone call.

## A note on patient data

This is health-adjacent data, handled accordingly regardless of which
specific privacy law applies to a given practice: patient and treatment
records are staff-only, changes are tracked, and photos are stored as
ordinary private attachments (no third-party service, no public URL).
None of that is a substitute for checking with your state's cosmetology /
body-art board or a healthcare attorney about what recordkeeping and
consent rules apply to your practice specifically — this repo doesn't
attempt to certify compliance with any regulation, it just tries not to
make the technical side harder than it has to be.

## Testing

[`testing/`](testing/) is a self-contained local Odoo 19 + Postgres
instance — see [`testing/README.md`](testing/README.md).

## Compatibility

Targets **Odoo 19.0**, tracked on `main` (mirrored to a `19.0` branch).

## License

LGPL-3 — see [`LICENSE`](LICENSE).
