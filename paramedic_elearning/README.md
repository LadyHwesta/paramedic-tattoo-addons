# eLearning: HB Ink Studio Training

A pure-data module: installing it drops two ready-built courses into
Odoo's **eLearning** app - nothing to author by hand.

## What's in it

- **Patient Records & Clinical Documentation** - bringing on a patient,
  the condition record, informed consent, patch testing, and documenting
  a treatment session.
- **Scheduling & Booking** - adding a practitioner and services (and the
  gates that protect a real session), booking an appointment yourself or
  confirming a portal request, and the patient's own online booking flow.

Each course ends with a 4-question quiz.

## Access

Both courses are gated (`visibility="members"`, `enroll="invite"`);
everyone in `paramedic_base.group_paramedic_staff` is auto-enrolled in
both via `enroll_group_ids`.

## Dependencies

Only `website_slides` + `paramedic_base` + `paramedic_appointment`.

Content is adapted from `docs/handbook.html`.
