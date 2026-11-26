"""Builds the Client Reviews course from the content below.

Run from the repository root after changing a lesson:

    python3 practice_elearning_review/tools/build_course_data.py
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





def ul(*items):
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

M = 'practice_elearning_review'

REVIEWS = ('channel_reviews', "Client Reviews",
    "How clients review their practitioner, checking each review before it goes online, and what clients stay in charge of.",
    'practice_base.group_practice_staff', [
    ("From visit to website", [
        ("How a client writes a review", ''.join([
            p("After a <strong>completed</strong> appointment, the client can review the practitioner who treated "
              "them from <strong>My Reviews</strong> in their portal: 1 to 5 stars, a title, a few words, and how "
              "their name is shown (first name and last initial, unless they change it)."),
            p("They can add any of their own photos you've shared with them, ticking that those photos may be "
              "shown with the review."),
            shot(M, 'portal_review_form.png', "The review form in the client portal",
                 "a client reviewing their practitioner, with one of their photos."),
            callout('fa-user-check', "Only real clients", "A review needs a completed visit with that "
                    "practitioner, and a client has one review per practitioner at a time."),
        ])),
        ("Checking and publishing", ''.join([
            p("Every review waits in " + path("Practice", "Reviews") + ", and whoever checks reviews gets a "
              "to-do. Set who that is in " + path("Settings", "Practice Appointments", "Reviews checked by") +
              "."),
            shot(M, 'review_backend.png', "A review waiting to be checked", "a review to check, with the "
                 "photo the client chose."),
            ul("<strong>Publish</strong> puts it on the <strong>Client Reviews</strong> blog, tagged with the "
               "practitioner, with copies of the chosen photos. Comments are off on reviews.",
               "<strong>Don't Publish</strong> keeps it off the website. Add a short note if you like: the "
               "client sees it in their portal."),
            shot(M, 'review_published.png', "A published review on the blog", "the published review."),
            callout('fa-undo', "The client stays in charge", "A client can withdraw their review at any time: the "
                    "post and its photo copies come down. The original photos stay private in their records."),
        ])),
    ]),
], [
    ("Who can review a practitioner?",
     ["A client after a completed visit with them", "Anyone visiting the website", "Any portal user",
      "Only staff"], 0),
    ("A client sends a review. When does it appear on the website?",
     ["Straight away", "Once someone clicks Publish", "After 24 hours", "Never"], 1),
    ("Can website visitors comment on a published review?",
     ["No, comments are off on reviews", "Yes, like any blog post", "Only signed-in clients",
      "Only the practitioner"], 0),
    ("A client withdraws a published review. What happens to the photos they chose?",
     ["The public copies come down; the originals stay private in their records", "They stay on the blog",
      "They're deleted from the client's records", "They're shared on the practice's other pages"], 0),
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
    write(M, [REVIEWS])
