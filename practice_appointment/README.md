# Practitioner Suite - Appointments

Service types, practitioner scheduling, and client self-booking, built
on top of `practice_base`.

Odoo Community has no self-service booking app - the "Appointments" app
is Enterprise-only, and OCA has no equivalent repository either. This
builds one on the pieces that *are* in Community: `resource.calendar`
(the same working-hours/time-off engine that powers HR and
manufacturing) for availability, and a bespoke booking model for
everything else.

## What it adds

### Services

`practice.service` - a name, duration, buffer time blocked after it
(cleanup/prep before the next client), which practitioners are
qualified to perform it (leave empty for "any practitioner"), whether
it's offered for online self-booking, and two requirement checks: **requires
a clear pre-treatment test** and/or **requires a signed treatment consent**. A
service can also be flagged to **create a treatment session** on
completion - use this for treatment sessions, leave it off for
consultations.

### Appointments

`practice.appointment` links a client, practitioner, service, and
(when the service is gated) the `practice.plan` it's for. Three
things are checked on save, all skippable with `skip_appointment_checks`
in context for a back-office correction:

- **No overlap** - a practitioner can't be double-booked; the blocked
  window is the service's duration *plus* its buffer.
- **Practitioner qualification** - if a service names specific
  practitioners, only they can be assigned to it.
- **The requirement check** - a service requiring a pre-treatment test or treatment
  consent refuses to book without a treatment plan on file that satisfies it.

Completing an appointment for a session-type service creates the linked
`practice.session` automatically, pre-filled with the
practitioner, date, and area from the treatment plan - the practitioner fills
in the session detail (products, photos, notes) afterward.

### Availability

Computed per practitioner from their own `resource.calendar` (so time
off is free) minus their existing active appointments, packed
back-to-back including each service's buffer. No separate scheduling
engine or synced calendar to keep consistent with reality.

### Client self-booking

`/my/book` lists the services currently open to a client online: those
marked bookable, and - for a gated service - only if the client already
has a treatment plan on file that satisfies the gate. A brand-new client
therefore only ever sees ungated services (typically a consultation)
until a practitioner has assessed them and opened a treatment plan; anything
requiring a pre-treatment test or consent is booked by staff once that's in
place. Picking a service shows real open times for the next few weeks;
picking a time requests it (`state = requested`) for staff to confirm.
`/my/appointments` lists a client's own upcoming and past visits, with a
self-cancel option outside a 24-hour window.

None of this touches `practice.plan`, `practice.consent`,
`practice.test`, or `practice.session` directly from the
portal layer - the booking controller runs as an administrator
internally and only ever reads/writes the client's own appointment
records, the same "nothing client is portal-reachable" posture as
`practice_base`.

## Settings

Settings → Practitioner Suite Appointments: reminder lead time (default 2 days
before an appointment) and the online booking window (default 21 days
ahead).

## Requirements

Odoo 19 Community, `practice_base`, `portal`. No extra Python packages.

## Tests

`--test-tags=/practice_appointment` (20): availability math against a
real `resource.calendar` (working hours, buffer time, existing/cancelled
appointments), the overlap/qualification/gating constraints and their
bypass, completing a session creates the treatment session, and the
portal booking flow (pages render, a gated service isn't offered to a
new client, booking provisions the client record and sets
`state`/`source` correctly).
