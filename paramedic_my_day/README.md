# Paramedical Tattoo - My Day

Adds a practice's day to My Day (`my_day`, in LadyHwesta/odoo-addons). Before
this, a practitioner's My Day showed nothing about their patients: appointments
are `paramedic.appointment` records, not calendar meetings. Auto-installs with
`my_day` + `paramedic_appointment`.

| Section | Column | Shows | Button |
|---|---|---|---|
| Today's appointments | Plan (under the calendar) | A practitioner's own today; staff who aren't practitioners see the whole book, with who each is with | Complete, once started |
| Booking requests | Attention | Online requests (`requested`) still ahead | Confirm |
| Patch tests to read | Attention | Pending results with a read date today or earlier (overdue in red) | |
| Follow-ups to book | Attention | Patients whose latest session recommends a next one within 14 days, with nothing booked | |

Each section uses the user's own access rights: people outside the practice
(no Paramedical staff group) don't see them.

8 tests.
