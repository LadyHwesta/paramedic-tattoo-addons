"""Builds the Notes and Photo Permissions course's data file from the content below.

Run from the repository root after changing a lesson:

    python3 practice_elearning_client_portal/tools/build_course_data.py

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



M = 'practice_elearning_client_portal'

# course: (xmlid, name, description, enroll group xmlid, [sections], quiz)

PORTAL = ('channel_client_portal', "Notes and Photo Permissions",
    "Write notes that stay internal or that your client sees, share photos with them, and know "
    "which photos you may use in marketing.",
    'practice_base.group_practice_staff', [
    ("Client notes", [
        ("Internal or shared with the client", ''.join([
            p("Write a note from a session's <strong>Notes</strong> tab, the <strong>Notes</strong> "
              "button on the client, or " + path("Practice", "Records", "Client Notes") +
              ". Give it a title, write the note, and choose who sees it at the top:"),
            flow(('fa-lock', "Internal: staff only (the default)"),
                 ('fa-user', "Shared with client: in their portal")),
            shot(M, 'note_form.png', "A note shared with the client",
                 "a two-week check-in, shared with the client."),
            p("A shared note appears under <strong>My Records</strong> in the client's portal. "
              "They get an email saying there's an update, with a link to sign in. The note itself "
              "never goes by email, because email isn't private."),
            callout('fa-comment-o', "Write shared notes for the client",
                    "Plain words, as you'd say it to them: what you saw, and what they should do next. "
                    "Keep your own shorthand and plans for an internal note."),
            callout('fa-exclamation-triangle', "Shared means shared",
                    "Switching a note back to Internal hides it from the portal, but the client may "
                    "already have read it. Check before you share.", 'warning'),
        ])),
    ]),
    ("Photos and marketing permission", [
        ("Sharing photos with the client", ''.join([
            p("Before and after photos stay staff-only until you share them. On the session, open "
              "the <strong>Sharing &amp; Marketing</strong> tab and tick <strong>Shared with "
              "Client</strong> on each photo they should see."),
            shot(M, 'my_records.png', "A client's My Records page",
                 "what the client sees: your shared update, and their shared photos."),
            callout('fa-key', "The client needs a portal login",
                    "If they don't have one yet, open their contact and use "
                    "<strong>Grant portal access</strong> (in the gear menu). They get an email to set "
                    "their password."),
        ])),
        ("Permission to use a photo in marketing", ''.join([
            p("A photo may be used on your website, portfolio or social media only with the "
              "client's permission, and every photo shows whether you have it:"),
            flow(('fa-user', "The client ticks it in their portal"),
                 ('fa-file-text-o', "Or you attach their signed photo release")),
            shot(M, 'photos.png', "Photos with their marketing permission",
                 "the green badge says who gave permission, and since when."),
            p("Nobody else can tick it: staff record permission only from a signed "
              "<strong>Photo Release</strong> consent, and one release goes a long way:"),
            flow(('fa-check-square-o', "Covers All Photos ticked: every photo, now and later"),
                 ('fa-files-o', "Or select photos, then Attach Signed Release")),
            p("Tick <strong>Covers All Photos</strong> on the release when it covers everything "
              "from their treatment: each new photo is covered as you add it. For a release that "
              "covers only some photos, select them in " + path("Practice", "Records",
              "Photos") + ", then " + path("Actions", "Attach Signed Release") + ". To find photos "
              "you may use, filter <strong>OK for Marketing</strong>."),
            callout('fa-undo', "When a client withdraws it",
                    "The badge goes and the change is logged on the photo. A release doesn't override "
                    "the client: only they can allow that photo again. Stop using it, and take it "
                    "down where you can. If the release itself is withdrawn, every photo it covered "
                    "loses its permission.", 'warning'),
            callout('fa-info-circle', "The old checkbox",
                    "The client's single \"OK to use photos\" checkbox is replaced by this permission "
                    "per photo, so each one has its own proof."),
        ])),
    ]),
], [
    ("You write a note. Who can see it if you don't change anything?",
     ["Only staff", "The client, in their portal", "Everyone with the link", "Nobody until it's signed"], 0),
    ("What does the client's email say when you share a note?",
     ["That there's an update, with a link to sign in", "The whole note", "The note's title and first line",
      "Nothing: no email is sent"], 0),
    ("Which photos does a client see in their portal?",
     ["Only the ones you tick Shared with Client", "All their photos", "Only after photos",
      "None: photos stay in the office"], 0),
    ("A client signed a release covering everything from their treatment. What do you do?",
     ["Tick Covers All Photos on the release", "Tick OK for Marketing on each photo",
      "Attach the release to each photo one by one, forever", "Nothing: staff can't record it"], 0),
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
        f.write('<?xml version="1.0" encoding="utf-8" ?>\n<!-- Built by practice_elearning_client_portal/tools/'
                'build_course_data.py: edit there and rebuild. -->\n<odoo noupdate="1">\n\n' + body + '</odoo>\n')
    print(target)


if __name__ == '__main__':
    write(M, [PORTAL])
