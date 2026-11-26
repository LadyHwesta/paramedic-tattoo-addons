"""Takes the Practitioner Suite course screenshots from a running sample database.

1. Build the sample (see sample_practice.py) and run Odoo on it, for example
   on http://localhost:8077 with --db-filter=^practicecourse$.
2. Run with a Python that has websocket-client (Odoo's own venv does):

       python3 practice_elearning/tools/shoot.py http://localhost:8077

It drives headless Google Chrome over the DevTools protocol, as the admin
(Jordan Ellis), then as the client Rosa Delgado, then logged out, and writes
each picture into the course module that uses it.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8077'
PORT = 9333


class Tab:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60)
        self.n = 0

    def call(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': method, 'params': params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('id') == self.n:
                if 'error' in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get('result', {})

    def js(self, expr):
        r = self.call('Runtime.evaluate', expression=expr, awaitPromise=True, returnByValue=True)
        return r.get('result', {}).get('value')

    def go(self, url, settle=2.5):
        self.call('Page.navigate', url=url)
        self.wait('document.readyState === "complete"')
        time.sleep(settle)

    def wait(self, cond, timeout=20):
        end = time.time() + timeout
        while time.time() < end:
            if self.js(f'!!({cond})'):
                return True
            time.sleep(0.3)
        raise TimeoutError(cond)

    def click_text(self, text, selector='*', settle=1.5):
        """Real mouse click on the smallest visible element containing the text."""
        box = self.js(f'''(() => {{
            const want = {json.dumps(text)};
            const els = [...document.querySelectorAll({json.dumps(selector)})].filter(e =>
                e.offsetParent !== null && e.textContent.trim().includes(want));
            els.sort((a, b) => a.textContent.length - b.textContent.length);
            if (!els.length) return null;
            els[0].scrollIntoView({{block: 'center'}});
            const r = els[0].getBoundingClientRect();
            return [r.x + r.width / 2, r.y + r.height / 2];
        }})()''')
        if not box:
            raise LookupError(f'nothing visible says {text!r}')
        x, y = box
        for kind in ('mouseMoved', 'mousePressed', 'mouseReleased'):
            self.call('Input.dispatchMouseEvent', type=kind, x=x, y=y, button='left', clickCount=1)
        time.sleep(settle)

    def type_into(self, selector, text, settle=1.5):
        self.js(f"document.querySelector({json.dumps(selector)}).focus()")
        self.call('Input.insertText', text=text)
        self.call('Input.dispatchKeyEvent', type='keyDown', key='Enter', code='Enter', windowsVirtualKeyCode=13)
        self.call('Input.dispatchKeyEvent', type='keyUp', key='Enter', code='Enter', windowsVirtualKeyCode=13)
        time.sleep(settle)

    def shot(self, *targets):
        """Save the screen as module/image, for each 'module/image.png' given."""
        data = base64.b64decode(self.call('Page.captureScreenshot', format='png')['data'])
        for target in targets:
            module, name = target.split('/')
            with open(os.path.join(REPO, module, 'static', 'img', name), 'wb') as f:
                f.write(data)
            print('wrote', target)

    def login(self, login, password):
        self.go(f'{BASE}/web/session/logout', settle=1.5)
        self.go(f'{BASE}/web/login')
        self.js(f'''document.querySelector('#login').value={json.dumps(login)};
                  document.querySelector('#password').value={json.dumps(password)};
                  document.querySelector('form.oe_login_form').submit();''')
        time.sleep(3)


def main():
    profile = tempfile.mkdtemp()
    chrome = subprocess.Popen([CHROME, '--headless=new', f'--remote-debugging-port={PORT}', f'--user-data-dir={profile}',
                               '--window-size=1280,800', '--hide-scrollbars', 'about:blank'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                pages = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json'))
                ws = next(p['webSocketDebuggerUrl'] for p in pages if p['type'] == 'page')
                break
            except Exception:
                time.sleep(0.2)
        tab = Tab(ws)
        tab.call('Page.enable')
        tab.call('Emulation.setDeviceMetricsOverride', width=1280, height=800, deviceScaleFactor=1, mobile=False)
        tab.login('admin', 'admin')
        for step in SHOTS:
            step(tab)
    finally:
        chrome.terminate()




def act(xmlid, rec=None):
    return f'{BASE}/odoo/action-{xmlid}' + (f'/{rec}' if rec else '')


IDS = {}


def lookup(tab):
    def one(model, domain):
        return tab.js(f'''fetch('/web/dataset/call_kw/' + {json.dumps(model)} + '/search', {{method: 'POST',
            headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{jsonrpc: '2.0', method: 'call',
            params: {{model: {json.dumps(model)}, method: 'search', args: [{json.dumps(domain)}], kwargs: {{limit: 1}}}}}})}})
            .then(r => r.json()).then(j => (j.result || [])[0])''')
    IDS['rosa'] = one('res.partner', [['name', '=', 'Rosa Delgado']])
    IDS['plan'] = one('practice.plan', [['partner_id.name', '=', 'Rosa Delgado']])
    IDS['massage'] = one('practice.service', [['name', '=', 'Massage, 60 minutes']])
    IDS['upcoming'] = one('practice.appointment', [['state', '=', 'confirmed']])
    IDS['to_bill'] = one('practice.appointment', [['state', '=', 'completed'], ['invoice_id', '=', False]])
    IDS['draft'] = one('account.move', [['move_type', '=', 'out_invoice'], ['state', '=', 'draft']])
    IDS['posted'] = one('account.move', [['move_type', '=', 'out_invoice'], ['state', '=', 'posted'],
                                         ['payment_state', '=', 'not_paid']])
    IDS['note'] = one('practice.note', [['visibility', '=', 'client']])
    IDS['review'] = one('practice.review', [['state', '=', 'submitted']])
    IDS['priya'] = one('practice.practitioner', [['user_id.login', '=', 'priya']])
    IDS['post'] = tab.js('''fetch('/web/dataset/call_kw/practice.review/search_read', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body: JSON.stringify({jsonrpc: '2.0', method: 'call',
        params: {model: 'practice.review', method: 'search_read', args: [[['state', '=', 'published']], ['blog_post_id']],
        kwargs: {limit: 1}}})}).then(r => r.json()).then(j => j.result[0].blog_post_id[0])''')
    IDS['post_url'] = tab.js(f'''fetch('/web/dataset/call_kw/blog.post/read', {{method: 'POST',
        headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{jsonrpc: '2.0', method: 'call',
        params: {{model: 'blog.post', method: 'read', args: [[{IDS['post']}], ['website_url']], kwargs: {{}}}}}})}})
        .then(r => r.json()).then(j => j.result[0].website_url)''')
    print('ids', IDS)


def s_records(tab):
    tab.go(act('practice_base.action_client', IDS['rosa']))
    tab.click_text('Client', '.nav-link')
    tab.js("[...document.querySelectorAll('.o_form_sheet .o_horizontal_separator, .o_form_sheet .o_form_label')]"
           ".find(e => e.textContent.trim().toUpperCase() === 'BEFORE TREATING').scrollIntoView({block: 'center'})")
    time.sleep(1)
    tab.shot('practice_elearning/client_form.png')
    tab.go(act('practice_base.action_practice_plan', IDS['plan']))
    tab.shot('practice_elearning/plan_form.png')


def s_scheduling(tab):
    tab.go(act('practice_appointment.action_practice_service', IDS['massage']))
    tab.shot('practice_elearning/service_form.png', 'practice_elearning_billing/service_price.png')
    tab.go(act('practice_appointment.action_practice_appointment', IDS['upcoming']))
    tab.shot('practice_elearning/appointment_new.png')


def s_billing(tab):
    tab.go(act('practice_appointment.action_practice_appointment', IDS['to_bill']))
    tab.shot('practice_elearning_billing/appointment_invoice.png')
    tab.go(act('account.action_move_out_invoice_type', IDS['draft']))
    tab.shot('practice_elearning_billing/invoice_draft.png')
    tab.go(act('account.action_move_out_invoice_type', IDS['posted']))
    tab.click_text('Pay', 'button', settle=2.5)
    tab.shot('practice_elearning_billing/register_payment.png')
    tab.go(act('practice_appointment.action_practice_appointment'))
    tab.click_text('', '.o_switch_view.o_list', settle=2)
    tab.js("document.querySelector('.o_searchview_facet .o_facet_remove')?.click()")
    time.sleep(2)
    tab.shot('practice_elearning_billing/appointments_billing.png')


def s_portal_staff(tab):
    tab.go(act('practice_client_portal.action_practice_note', IDS['note']))
    tab.shot('practice_elearning_client_portal/note_form.png')
    tab.go(act('practice_client_portal.action_practice_photo'))
    tab.shot('practice_elearning_client_portal/photos.png')
    tab.go(act('practice_review.action_practice_review', IDS['review']))
    tab.shot('practice_elearning_review/review_backend.png')


def s_as_client(tab):
    tab.login('rosa', 'rosa')
    tab.go(f'{BASE}/my/records', settle=3)
    tab.shot('practice_elearning_client_portal/my_records.png')
    tab.go(f"{BASE}/my/reviews/new/{IDS['priya']}", settle=3)
    tab.js("document.querySelector('#rating_5').checked = true;"
           "document.querySelector('#review_title').value = 'Calm, kind and practical';"
           "document.querySelector('#review_body').value = 'Priya explained every herb and checked in after a week.';"
           "document.querySelector('input[name=photo_ids]').checked = true;"
           "document.querySelector('#photo_consent').checked = true;")
    tab.call('Emulation.setDeviceMetricsOverride', width=1280, height=1240, deviceScaleFactor=1, mobile=False)
    time.sleep(1)
    tab.shot('practice_elearning_review/portal_review_form.png')
    tab.call('Emulation.setDeviceMetricsOverride', width=1280, height=800, deviceScaleFactor=1, mobile=False)


def s_public(tab):
    tab.go(f'{BASE}/web/session/logout', settle=1.5)
    tab.go(BASE + IDS['post_url'], settle=3)
    tab.shot('practice_elearning_review/review_published.png')


SHOTS = [lookup, s_records, s_scheduling, s_billing, s_portal_staff, s_as_client, s_public]

if __name__ == '__main__':
    main()
