# Paramedical Tattoo - Appointments

Service types, practitioner scheduling, and patient self-booking, built
on top of `paramedic_base`.

Odoo Community has no self-service booking app - the "Appointments" app
is Enterprise-only, and OCA has no equivalent repository either. This
builds one on the pieces that *are* in Community: `resource.calendar`
(the same working-hours/time-off engine that powers HR and
manufacturing) for availability, and a bespoke booking model for
everything else.

## What it adds

### Services

`paramedic.service` - a name, duration, buffer time blocked after it
(cleanup/prep before the next patient), which practitioners are
qualified to perform it (leave empty for "any practitioner"), whether
it's offered for online self-booking, and two clinical gates: **requires
a clear patch test** and/or **requires a signed treatment consent**. A
service can also be flagged to **create a treatment session** on
completion - use this for real ink sessions, leave it off for
consultations.

### Appointments

`paramedic.appointment` links a patient, practitioner, service, and
(when the service is gated) the `patient.condition` it's for. Three
things are checked on save, all skippable with `skip_appointment_checks`
in context for a back-office correction:

- **No overlap** - a practitioner can't be double-booked; the blocked
  window is the service's duration *plus* its buffer.
- **Practitioner qualification** - if a service names specific
  practitioners, only they can be assigned to it.
- **The clinical gate** - a service requiring a patch test or treatment
  consent refuses to book without a condition on file that satisfies it.

Completing an appointment for a session-type service creates the linked
`patient.treatment.session` automatically, pre-filled with the
practitioner, date, and area from the condition - the practitioner fills
in the clinical detail (pigment, photos, notes) afterward.

### Availability

Computed per practitioner from their own `resource.calendar` (so time
off is free) minus their existing active appointments, packed
back-to-back including each service's buffer. No separate scheduling
engine or synced calendar to keep consistent with reality.

### Patient self-booking

`/my/book` lists the services currently open to a patient online: those
marked bookable, and - for a gated service - only if the patient already
has a condition on file that satisfies the gate. A brand-new patient
therefore only ever sees ungated services (typically a consultation)
until a practitioner has assessed them and opened a condition; anything
requiring a patch test or consent is booked by staff once that's in
place. Picking a service shows real open times for the next few weeks;
picking a time requests it (`state = requested`) for staff to confirm.
`/my/appointments` lists a patient's own upcoming and past visits, with a
self-cancel option outside a 24-hour window.

None of this touches `patient.condition`, `patient.consent`,
`patient.patch_test`, or `patient.treatment.session` directly from the
portal layer - the booking controller runs as an administrator
internally and only ever reads/writes the patient's own appointment
records, the same "nothing clinical is portal-reachable" posture as
`paramedic_base`.

## Settings

Settings → Paramedical Appointments: reminder lead time (default 2 days
before an appointment) and the online booking window (default 21 days
ahead).

## Requirements

Odoo 19 Community, `paramedic_base`, `portal`. No extra Python packages.

## Tests

`--test-tags=/paramedic_appointment` (20): availability math against a
real `resource.calendar` (working hours, buffer time, existing/cancelled
appointments), the overlap/qualification/gating constraints and their
bypass, completing a session creates the treatment session, and the
portal booking flow (pages render, a gated service isn't offered to a
new patient, booking provisions the patient record and sets
`state`/`source` correctly).
