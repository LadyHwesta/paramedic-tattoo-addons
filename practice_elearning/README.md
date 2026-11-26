# eLearning: Practitioner Suite Training

Installing it puts two ready-built courses into Odoo's **eLearning** app:

- **Client Records**: bringing on a client and their health flags, the
  treatment plan, consent forms, pre-treatment tests, documenting a session.
- **Scheduling & Booking**: practitioners and services (and the checks a
  service can require first), booking an appointment or confirming an online
  request, and the client's own online booking.

Each course ends with a 4-question quiz. Members only, by invitation; everyone
in `practice_base.group_practice_staff` is enrolled.

## Changing a lesson

The lessons live in `tools/build_course_data.py`: edit there and run it from
the repository root to rebuild `data/slide_channel_data.xml`.

## Screenshots

The screenshots in this module and in the other Practitioner Suite course
modules come from a made-up practice, Riverbend Wellness:

1. Install the whole suite on a throwaway database and load the sample with
   `tools/sample_practice.py` in an `odoo-bin shell`.
2. Run Odoo on it and take the pictures with `tools/shoot.py` (headless
   Chrome; it writes each picture into the module that uses it).
