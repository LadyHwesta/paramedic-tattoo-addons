"""Builds the Billing Clients course's data file from the content below.

Run from the repository root after changing a lesson:

    python3 practice_elearning_billing/tools/build_course_data.py

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



M = 'practice_elearning_billing'

# course: (xmlid, name, description, enroll group xmlid, [sections], quiz)

BILLING = ('channel_billing', "Billing Clients",
    "Price your services, invoice each visit in one click, take payment at the desk, and see who still owes.",
    'account.group_account_invoice', [
    ("Prices and invoices", [
        ("Pricing your services", ''.join([
            p("Each service has a <strong>Price</strong>. Set it in " + path("Practice", "Configuration",
              "Services") + ": the first time you give a service a price, it gets a product of its own "
              "(<strong>Billed As</strong>) that its invoices use."),
            shot(M, 'service_price.png', "A service with its price", "a 60-minute massage at $95."),
            p("Change the price on the service whenever your fees change; invoices already sent keep the "
              "price they were made with."),
            callout('fa-percent', "Check the tax", "A new service takes your company's default sales tax. If your "
                    "services aren't taxable, open the product from <strong>Billed As</strong> and clear its "
                    "<strong>Sales Taxes</strong>. Ask your accountant if you're not sure.", 'warning'),
        ])),
        ("Invoicing a visit", ''.join([
            p("When the visit is done, mark the appointment " + path("Complete") + ". A <strong>Create "
              "Invoice</strong> button appears."),
            shot(M, 'appointment_invoice.png', "A completed appointment with a Create Invoice button",
                 "a completed appointment, ready to invoice."),
            p("It makes the client's invoice for that service, with the visit's date on the line, and opens it. "
              "Add anything else from the visit, such as aftercare products, then " + path("Confirm") + "."),
            shot(M, 'invoice_draft.png', "A draft invoice for the session",
                 "the draft invoice: the client, the session and its price."),
            p("To bill several visits at once, tick them in the appointments list and click "
              "<strong>Create Invoices</strong>: each gets its own invoice."),
        ])),
    ]),
    ("Getting paid", [
        ("Taking payment at the desk", ''.join([
            p("On a confirmed invoice, " + path("Pay") + " records a payment: pick the journal (Bank for a card "
              "or check, Cash for cash), check the amount and date, and " + path("Create Payment") + ". The "
              "invoice and its appointment show <strong>Paid</strong>."),
            shot(M, 'register_payment.png', "The Pay dialog on an invoice", "recording an $80.50 payment."),
            p("To email the invoice instead, use " + path("Send") + ": the client gets a link to view it and, "
              "if you take card payments online, to pay it."),
        ])),
        ("Who still owes, and what's not billed", ''.join([
            p("The appointments list has a <strong>Payment</strong> column: paid, not paid or partly paid. The "
              "<strong>To Invoice</strong> filter lists completed visits that haven't been billed yet."),
            shot(M, 'appointments_billing.png', "The appointments list with a Payment column",
                 "a paid visit, two still owed, and a consultation not yet billed."),
            p("Overdue invoices are chased by email automatically (" + path("Accounting", "Configuration",
              "Payment Reminders") + "). The bank, reconciliation and reports are in the course "
              "<strong>Getting Paid and Keeping the Books</strong>."),
            callout('fa-info-circle', "Insurance", "Invoices go to the client. The insurance payer and member ID "
                    "on the client's record are for your reference; insurance claims aren't filed from here."),
        ])),
    ]),
], [
    ("When does an appointment get a Create Invoice button?",
     ["Once it's marked Complete", "As soon as it's booked", "When the client pays", "Never, invoices are typed by hand"], 0),
    ("You raise the price of a session. What happens to invoices already sent?",
     ["They keep the price they were made with", "They change to the new price", "They're cancelled",
      "They're sent again"], 0),
    ("A client pays cash at the desk. How do you record it?",
     ["Pay on the invoice, with the Cash journal", "Mark the appointment Completed", "Delete the invoice",
      "Nothing, cash isn't recorded"], 0),
    ("Where do you find visits that haven't been billed yet?",
     ["The To Invoice filter on the appointments list", "The client's treatment plans", "Payment Reminders",
      "The services list"], 0),
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
        f.write('<?xml version="1.0" encoding="utf-8" ?>\n<!-- Built by practice_elearning_billing/tools/'
                'build_course_data.py: edit there and rebuild. -->\n<odoo noupdate="1">\n\n' + body + '</odoo>\n')
    print(target)


if __name__ == '__main__':
    write(M, [BILLING])
