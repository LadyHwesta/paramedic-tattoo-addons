"""Builds the Client Records and Scheduling & Booking courses from the content below.

Run from the repository root after changing a lesson:

    python3 practice_elearning/tools/build_course_data.py

Keep lessons in step with the screens: when a menu or button is renamed,
change it here and rebuild.
"""
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---- lesson building blocks (classes styled by course_content.scss) ----

def p(text):
    return f'<p>{text}</p>'


def path(*steps):
    return '<span class="oe-path">' + ' › '.join(escape(s) for s in steps) + '</span>'


def callout(icon, label, text, kind=''):
    cls = f'oe-callout oe-callout-{kind}' if kind else 'oe-callout'
    return (f'<div class="{cls}"><span class="oe-callout-icon"><i class="fa {icon}" /></span>'
            f'<div><span class="oe-callout-label">{escape(label)}</span><p>{text}</p></div></div>')


def shot(module, image, alt, caption):
    return (f'<div class="oe-diagram"><img src="/{module}/static/img/{image}" alt="{escape(alt)}" class="img-fluid" />'
            f'<p class="oe-diagram-caption"><span class="oe-diagram-caption-tag">Screenshot</span>{caption}</p></div>')


def flow(*steps):
    parts = []
    for i, (icon, text) in enumerate(steps):
        if i:
            parts.append('<span class="oe-flow-arrow"><i class="fa fa-long-arrow-right" /></span>')
        parts.append(f'<div class="oe-flow-step"><span class="oe-flow-step-icon"><i class="fa {icon}" /></span>'
                     f'{escape(text)}</div>')
    return '<div class="oe-diagram"><div class="oe-flow">' + ''.join(parts) + '</div></div>'



M = 'practice_elearning'

# course: (xmlid, name, description, enroll group xmlid, [sections], quiz)

RECORDS = ('channel_records', "Client Records",
    "Bring on a client, open a treatment plan, record consent and pre-treatment tests, and document each session.",
    'practice_base.group_practice_staff', [
    ("Clients and treatment plans", [
        ("Bringing on a client", ''.join([
            p("Someone becomes a client the moment you tick <strong>Is a Client</strong>, whether they booked "
              "online or you're entering them after a consultation. Open " + path("Practice", "Clients", "New") +
              ", or find them under Contacts and tick the box: a <strong>Client #</strong> is assigned "
              "automatically."),
            p("On the <strong>Client</strong> tab, fill in date of birth, emergency contact and referring provider. "
              "Under <strong>Before Treating</strong>, add the <strong>Health Flags</strong> that apply and any "
              "allergies, so every practitioner sees them before a session."),
            shot(M, 'client_form.png', "A client's record with health flags", "a client's Client tab, with a "
                 "health flag and an allergy recorded."),
            callout('fa-flag', "Your own health flags", "Each practice keeps its own list in " +
                    path("Practice", "Configuration", "Health Flags") + ": for example Pregnant, Blood thinners or "
                    "Recent injury."),
            callout('fa-globe', "Requested online?", "A client who requests an appointment on your website is "
                    "flagged and numbered automatically too. Fill in their health details at the first visit."),
        ])),
        ("The treatment plan", ''.join([
            p("Everything that follows, consent, pre-treatment tests and sessions, hangs off a <strong>treatment "
              "plan</strong>: one per thing you're treating the client for. Choose the <strong>Treatment</strong> "
              "from your practice's list, add the <strong>Area / Focus</strong>, and set yourself as "
              "<strong>Primary Practitioner</strong>."),
            flow(('fa-inbox', "Intake"), ('fa-heartbeat', "In Treatment"), ('fa-check', "Completed")),
            p("Move the plan's status as you start, and again when it's done (or Discontinued)."),
            shot(M, 'plan_form.png', "A treatment plan", "a treatment plan, with the tabs the rest of this "
                 "course uses."),
            callout('fa-list', "Your own treatments", "Set up what your practice treats in " +
                    path("Practice", "Configuration", "Treatment Types") + ": \"Deep tissue for back pain\", "
                    "\"Sleep support\", \"Strength program\"... Rename the starting \"General treatment\" to suit."),
        ])),
    ]),
    ("Consent and pre-treatment tests", [
        ("Consent", ''.join([
            p("One record per consent: treatment, pre-treatment test or photo release. Add a row on the plan's "
              "<strong>Consents</strong> tab; the <strong>Form</strong> fills in with your wording for that kind."),
            p("Print it from the record's " + path("Print") + " menu, have the client sign, then click "
              "<strong>Mark Signed</strong>."),
            callout('fa-pencil', "Your own wording", "Edit the forms, or add your own, in " +
                    path("Practice", "Configuration", "Consent Forms") + ". The first form of each kind is used "
                    "for new consents."),
            callout('fa-camera', "Photos are separate", "A photo release is its own consent: a client can say yes "
                    "to treatment and no to photos. A printed but unsigned consent doesn't count."),
        ])),
        ("Pre-treatment tests", ''.join([
            p("A check before treatment starts, such as a skin patch test for an oil or remedy, or a fitness "
              "assessment. Add a row on the plan's <strong>Pre-treatment Tests</strong> tab: the test, what was "
              "tested and its lot number, and the date. <strong>Read On</strong> fills in from the test type's "
              "waiting time."),
            flow(('fa-eyedropper', "Done today"), ('fa-clock-o', "Read on the date"),
                 ('fa-check-circle', "Clear, or Reaction / Concern")),
            p("Record the result with notes when you check it. Tests to read show on My Day."),
            callout('fa-refresh', "Only the latest counts", "A new clear test replaces an old one. Set up your "
                    "tests and their waiting times in " + path("Practice", "Configuration",
                    "Pre-treatment Test Types") + "."),
        ])),
    ]),
    ("Documenting a session", [
        ("Documenting a session", ''.join([
            p("A session is created for you when you complete an appointment, or you can add one on the plan's "
              "<strong>Sessions</strong> tab. Record the products used and their lot numbers, the area or focus, "
              "your session notes, and whether aftercare was given."),
            p("Add before and after photos; sessions on a plan are numbered in date order, so progress is easy to "
              "follow. Set <strong>Next Session Recommended</strong> and My Day reminds you to book it."),
            callout('fa-exclamation-triangle', "If something went wrong", "Tick <strong>Reaction or "
                    "Concern</strong> and describe it.", 'warning'),
        ])),
    ]),
], [
    ("A pre-treatment test came back clear two months ago, and a new one just came back clear too. Which one counts?",
     ["The most recent one", "The oldest one", "Both, averaged", "Neither: a plan needs three clear tests"], 0),
    ("A client signs the treatment consent but not the photo release. Can you use their photos in your marketing?",
     ["Yes, treatment consent covers everything", "No, the photo release is a separate consent",
      "Only for some treatments", "Only if the test was clear"], 1),
    ("What does every consent, test and session attach to?",
     ["The treatment plan", "The appointment", "The practitioner", "Nothing, they're independent"], 0),
    ("Where do you add the health flags your practice checks before treating?",
     ["Practice › Configuration › Health Flags", "In each appointment", "On the invoice", "They can't be changed"], 0),
])

SCHEDULING = ('channel_scheduling', "Scheduling & Booking",
    "Set up practitioners and services, book appointments, confirm online requests, and let clients book themselves.",
    'practice_base.group_practice_staff', [
    ("One-time setup", [
        ("Adding yourself as a practitioner", ''.join([
            p("Open " + path("Practice", "Configuration", "Practitioners", "New") + " and set <strong>User</strong> "
              "to your own login. Click into <strong>Working Hours</strong> to set the days and times you work: "
              "the booking page uses them to know when you're free, and time off you add there is respected."),
            p("Add your licence or certification number while you're there."),
            callout('fa-key', "One thing to know", "Creating or editing a Working Hours calendar needs Administrator "
                    "access. Adding a practitioner later who isn't an Administrator? Set their hours up for them "
                    "the first time."),
        ])),
        ("Your services, and the checks that come first", ''.join([
            p("In " + path("Practice", "Configuration", "Services") + ", add one row per thing you offer, with its "
              "<strong>Duration</strong> and a <strong>Buffer After</strong> for cleanup or notes. Tick "
              "<strong>Bookable Online</strong> for anything a client may request themselves, often just a "
              "consultation or a first visit."),
            p("A service can require a <strong>clear pre-treatment test</strong> and a <strong>signed treatment "
              "consent</strong> before it can be booked, and can <strong>create a session</strong> record when "
              "it's completed."),
            shot(M, 'service_form.png', "A service with its requirements", "a treatment session that needs a "
                 "clear test and signed consent first."),
            callout('fa-shield', "What the requirements do", "A service with requirements can't be booked, by you "
                    "or online, against a treatment plan until the plan meets them. Nothing gets booked ahead of "
                    "the safety step."),
        ])),
    ]),
    ("Booking appointments", [
        ("Booking one yourself, and confirming a request", ''.join([
            p("<strong>Booking it yourself:</strong> " + path("Practice", "Appointments", "New") + ": pick the "
              "client, the service and, for a service with requirements, the treatment plan it's for. The end "
              "time comes from the service's duration and buffer, and you can't double-book yourself."),
            shot(M, 'appointment_new.png', "A new appointment", "booking an appointment."),
            p("<strong>Confirming a web request:</strong> open " + path("Practice", "Records",
              "Needs Confirmation") + ", check it and click <strong>Confirm</strong>: the client gets a "
              "confirmation email."),
            flow(('fa-user-times', "No-show"), ('fa-ban', "Cancel"), ('fa-check', "Complete")),
            p("Complete creates the linked session record for you, ready for your notes."),
        ])),
        ("The client's own online booking", ''.join([
            flow(('fa-list', "Pick a service"), ('fa-calendar', "Real open times"),
                 ('fa-inbox', "Lands in Needs Confirmation")),
            p("A client only ever sees services marked <strong>Bookable Online</strong>."),
            callout('fa-lock', "Services with requirements stay hidden until they're met", "They only show once "
                    "the client has a treatment plan that meets them. A brand-new client sees a consultation, not "
                    "a treatment, until you've seen them and opened a plan. Nothing from their records is shown "
                    "online."),
            p("Clients can cancel their own upcoming appointment, but only more than 24 hours ahead."),
        ])),
    ]),
], [
    ("A brand-new client with no treatment plan opens the booking page. What can they book?",
     ["Only a consultation (or another service without requirements)", "Any treatment",
      "Nothing until staff create an account", "A test only"], 0),
    ("Who can create or edit a practitioner's Working Hours?",
     ["Any staff member", "Only an Administrator", "Only that practitioner", "Clients, from their portal"], 1),
    ("How close to an appointment can a client still cancel it online?",
     ["Any time before it starts", "More than 24 hours ahead; closer than that, they call",
      "Never", "Only staff can cancel"], 1),
    ("Completing an appointment for a service that creates a session does what?",
     ["Nothing extra", "Creates the linked session record, ready for your notes",
      "Sends the client their photos", "Closes the treatment plan"], 1),
])


# ---- writing the data ----

def course_xml(module, course, quiz):
    xmlid, name, description, group, sections = course
    out = [f'''    <record id="{xmlid}" model="slide.channel">
        <field name="name">{escape(name)}</field>
        <field name="image_1920" type="base64" file="{module}/static/img/cover_{xmlid.removeprefix('channel_')}.png" />
        <field name="channel_type">training</field>
        <field name="description" type="html"><p>{escape(description)}</p></field>
        <field name="visibility">members</field>
        <field name="enroll">invite</field>
        <field name="is_published" eval="True" />
        <field name="enroll_group_ids" eval="[(6, 0, [ref('{group}')])]" />
    </record>
''']
    seq = 0
    for s_index, (section, lessons) in enumerate(sections, 1):
        seq += 10
        out.append(f'''    <record id="{xmlid}_s{s_index}" model="slide.slide">
        <field name="channel_id" ref="{xmlid}" />
        <field name="is_published" eval="True" />
        <field name="name">{escape(section)}</field>
        <field name="is_category" eval="True" />
        <field name="sequence">{seq}</field>
    </record>
''')
        for l_index, (lesson, html) in enumerate(lessons, 1):
            seq += 1
            out.append(f'''    <record id="{xmlid}_s{s_index}_l{l_index}" model="slide.slide">
        <field name="channel_id" ref="{xmlid}" />
        <field name="is_published" eval="True" />
        <field name="name">{escape(lesson)}</field>
        <field name="slide_category">article</field>
        <field name="sequence">{seq}</field>
        <field name="html_content" type="html"><div class="oe-course-content">{html}</div></field>
    </record>
''')
    out.append(f'''    <record id="{xmlid}_quiz" model="slide.slide">
        <field name="channel_id" ref="{xmlid}" />
        <field name="is_published" eval="True" />
        <field name="name">Check what you've learned</field>
        <field name="slide_category">quiz</field>
        <field name="sequence">{seq + 50}</field>
    </record>
''')
    for q_index, (question, answers, right) in enumerate(quiz, 1):
        out.append(f'''    <record id="{xmlid}_q{q_index}" model="slide.question">
        <field name="slide_id" ref="{xmlid}_quiz" />
        <field name="sequence">{q_index}</field>
        <field name="question">{escape(question)}</field>
    </record>
''')
        for a_index, answer in enumerate(answers, 1):
            out.append(f'''    <record id="{xmlid}_q{q_index}_a{a_index}" model="slide.answer">
        <field name="question_id" ref="{xmlid}_q{q_index}" />
        <field name="sequence">{a_index}</field>
        <field name="text_value">{escape(answer)}</field>
        <field name="is_correct" eval="{a_index - 1 == right}" />
    </record>
''')
    return ''.join(out)


def write(module, courses):
    body = ''.join(course_xml(module, course[:5], course[5]) for course in courses)
    target = os.path.join(ROOT, module, 'data', 'slide_channel_data.xml')
    with open(target, 'w') as f:
        f.write('<?xml version="1.0" encoding="utf-8" ?>\n<!-- Built by ' + module + '/tools/'
                'build_course_data.py: edit there and rebuild. -->\n<odoo noupdate="1">\n\n' + body + '</odoo>\n')
    print(target)


if __name__ == '__main__':
    write(M, [RECORDS, SCHEDULING])
