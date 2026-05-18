#!/usr/bin/env python3
"""Add a floating 'Feedback / Report a bug' button + in-page modal to every tool page.

The modal POSTs to the Web3Forms API. The visitor needs no account and
no mail client; submissions land in the email tied to your access key.

Setup (one-time, ~30 seconds)
-----------------------------
1. Open https://web3forms.com and enter your email address (kapita@tamu.edu).
2. They send a confirmation email containing a single access key (a UUID).
3. Paste the access key into ACCESS_KEY below.
4. Re-run:   python3 add_feedback.py

That's it. There's no dashboard to babysit; submissions arrive as emails.

Until ACCESS_KEY is filled in, the modal opens and looks correct, but
the Send button reports that it isn't wired up yet (instead of silently
swallowing submissions).

The script is idempotent: previously-injected blocks are stripped and
re-written, so it's safe to re-run after editing CONFIG or the HTML.
"""
import os
import re
import glob

BASE = '/home/user/math-tools'

# ============================================================================
# CONFIG -- paste your Web3Forms access key here (see docstring).
# ============================================================================
ACCESS_KEY = ''   # the UUID emailed to you by web3forms.com
# ============================================================================

# Hub / landing pages -- skip.
SKIP = {
    'index.html',
    'teaching.html',
    'projects.html',
    'linear.html',
    'optim.html',
    'numerical.html',
    'about.html',
    'pdftools.html',
}

CSS_START = '/* feedback-mark-css:start */'
CSS_END = '/* feedback-mark-css:end */'
HTML_START = '<!-- feedback-mark:start -->'
HTML_END = '<!-- feedback-mark:end -->'

FEEDBACK_CSS = f"""{CSS_START}
.fb-btn{{position:fixed;right:1rem;bottom:1rem;z-index:9999;
  display:inline-flex;align-items:center;gap:.4rem;
  padding:.55rem .85rem;border:0;border-radius:999px;cursor:pointer;
  background:#4338ca;color:#fff;font:600 .9rem/1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,.18);
  transition:transform .15s ease,background .15s ease,box-shadow .15s ease;}}
.fb-btn:hover,.fb-btn:focus-visible{{background:#3730a3;color:#fff;
  transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.22);text-decoration:none;}}
.fb-btn:focus-visible{{outline:3px solid #fff;outline-offset:2px;}}
.fb-btn svg{{flex-shrink:0;}}
@media(max-width:480px){{.fb-btn span{{display:none;}}
  .fb-btn{{padding:.6rem;border-radius:50%;}}}}
@media print{{.fb-btn,.fb-bd{{display:none!important;}}}}

.fb-bd{{position:fixed;inset:0;z-index:10000;background:rgba(15,23,42,.55);
  display:flex;align-items:center;justify-content:center;padding:1rem;
  opacity:0;pointer-events:none;transition:opacity .15s ease;
  font:400 1rem/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;}}
.fb-bd.fb-open{{opacity:1;pointer-events:auto;}}
.fb-dlg{{background:#fff;color:#111827;border-radius:.75rem;max-width:32rem;width:100%;
  box-shadow:0 20px 50px rgba(0,0,0,.3);transform:translateY(8px);
  transition:transform .15s ease;max-height:calc(100vh - 2rem);overflow:auto;}}
.fb-bd.fb-open .fb-dlg{{transform:translateY(0);}}
.fb-hd{{display:flex;align-items:center;justify-content:space-between;
  padding:1rem 1.25rem;border-bottom:1px solid #e5e7eb;}}
.fb-hd h2{{margin:0;font-size:1.1rem;font-weight:700;color:#111827;}}
.fb-x{{background:none;border:0;font-size:1.4rem;line-height:1;cursor:pointer;
  color:#6b7280;padding:.25rem .5rem;border-radius:.25rem;}}
.fb-x:hover,.fb-x:focus-visible{{color:#111827;background:#f3f4f6;}}
.fb-bd label{{display:block;font-weight:600;font-size:.9rem;margin:.85rem 0 .3rem;color:#374151;}}
.fb-bd label .fb-opt{{font-weight:400;color:#6b7280;}}
.fb-bd textarea,.fb-bd input[type=email]{{width:100%;font:inherit;color:#111827;
  padding:.55rem .65rem;border:1px solid #d1d5db;border-radius:.4rem;background:#fff;
  resize:vertical;}}
.fb-bd textarea:focus,.fb-bd input[type=email]:focus{{outline:0;border-color:#4338ca;
  box-shadow:0 0 0 3px rgba(67,56,202,.18);}}
.fb-bd textarea{{min-height:7rem;}}
.fb-body{{padding:0 1.25rem 1rem;}}
.fb-hp{{position:absolute;left:-9999px;width:1px;height:1px;opacity:0;}}
.fb-ft{{display:flex;justify-content:flex-end;gap:.5rem;
  padding:.85rem 1.25rem;border-top:1px solid #e5e7eb;background:#f9fafb;
  border-radius:0 0 .75rem .75rem;}}
.fb-ft button{{font:600 .9rem/1 inherit;padding:.55rem 1rem;border-radius:.4rem;
  cursor:pointer;border:1px solid transparent;}}
.fb-cancel{{background:#fff;color:#374151;border-color:#d1d5db;}}
.fb-cancel:hover{{background:#f3f4f6;}}
.fb-send{{background:#4338ca;color:#fff;}}
.fb-send:hover:not(:disabled){{background:#3730a3;}}
.fb-send:disabled{{opacity:.6;cursor:not-allowed;}}
.fb-msg{{padding:.6rem .75rem;border-radius:.4rem;font-size:.9rem;margin-top:.5rem;display:none;}}
.fb-msg.fb-err{{display:block;background:#fef2f2;color:#991b1b;border:1px solid #fecaca;}}
.fb-msg.fb-ok{{display:block;background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;}}
{CSS_END}
"""

FEEDBACK_HTML_TMPL = """{HTML_START}
<button type="button" id="fb-open" class="fb-btn" aria-label="Send feedback or report a bug">
  <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24">
    <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
  </svg>
  <span>Feedback</span>
</button>
<div class="fb-bd" id="fb-bd" role="dialog" aria-modal="true" aria-labelledby="fb-title" hidden>
  <div class="fb-dlg">
    <div class="fb-hd">
      <h2 id="fb-title">Feedback / report a bug</h2>
      <button type="button" class="fb-x" id="fb-x" aria-label="Close">&times;</button>
    </div>
    <form id="fb-form" class="fb-body" novalidate>
      <label for="fb-text">What happened, or what would you like to see improved?</label>
      <textarea id="fb-text" name="feedback" required aria-required="true"></textarea>
      <label for="fb-email">Email <span class="fb-opt">(optional, so we can reply)</span></label>
      <input id="fb-email" name="email" type="email" autocomplete="email">
      <input type="text" name="botcheck" class="fb-hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="fb-msg" id="fb-msg" role="status" aria-live="polite"></div>
    </form>
    <div class="fb-ft">
      <button type="button" class="fb-cancel" id="fb-cancel">Cancel</button>
      <button type="submit" form="fb-form" class="fb-send" id="fb-send">Send</button>
    </div>
  </div>
</div>
<script>
(function () {{
  var ACCESS_KEY = {access_key!r};
  var configured = !!ACCESS_KEY;

  var bd = document.getElementById('fb-bd');
  var openBtn = document.getElementById('fb-open');
  var closeBtn = document.getElementById('fb-x');
  var cancelBtn = document.getElementById('fb-cancel');
  var form = document.getElementById('fb-form');
  var textEl = document.getElementById('fb-text');
  var emailEl = document.getElementById('fb-email');
  var sendBtn = document.getElementById('fb-send');
  var msg = document.getElementById('fb-msg');
  var lastFocus = null;

  function showMsg(text, kind) {{
    msg.textContent = text;
    msg.className = 'fb-msg ' + (kind === 'ok' ? 'fb-ok' : 'fb-err');
  }}
  function clearMsg() {{ msg.textContent = ''; msg.className = 'fb-msg'; }}

  function open() {{
    lastFocus = document.activeElement;
    bd.hidden = false;
    requestAnimationFrame(function () {{ bd.classList.add('fb-open'); }});
    clearMsg();
    setTimeout(function () {{ textEl.focus(); }}, 50);
    document.addEventListener('keydown', onKey);
  }}
  function close() {{
    bd.classList.remove('fb-open');
    document.removeEventListener('keydown', onKey);
    setTimeout(function () {{
      bd.hidden = true;
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }}, 150);
  }}
  function onKey(e) {{
    if (e.key === 'Escape') {{ e.preventDefault(); close(); return; }}
    if (e.key === 'Tab') {{
      var f = bd.querySelectorAll('button,textarea,input:not(.fb-hp),[tabindex]:not([tabindex="-1"])');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) {{ e.preventDefault(); last.focus(); }}
      else if (!e.shiftKey && document.activeElement === last) {{ e.preventDefault(); first.focus(); }}
    }}
  }}

  openBtn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  cancelBtn.addEventListener('click', close);
  bd.addEventListener('click', function (e) {{ if (e.target === bd) close(); }});

  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    var text = textEl.value.trim();
    if (!text) {{ showMsg('Please enter some feedback.', 'err'); textEl.focus(); return; }}
    if (!configured) {{
      showMsg("Feedback isn't wired up yet \\u2014 the site owner needs to add an access key.", 'err');
      return;
    }}
    var page = (document.title || location.pathname).trim();
    var payload = {{
      access_key: ACCESS_KEY,
      subject: '[Feedback] ' + page,
      from_name: 'Math Tools feedback',
      page: page,
      url: location.href,
      feedback: text,
      email: emailEl.value.trim(),
      botcheck: form.botcheck.value
    }};
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending\\u2026';
    fetch('https://api.web3forms.com/submit', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json', 'Accept': 'application/json'}},
      body: JSON.stringify(payload)
    }})
      .then(function (r) {{ return r.json().catch(function () {{ return {{success: r.ok}}; }}); }})
      .then(function (data) {{
        if (data && data.success) {{
          showMsg('Thanks \\u2014 your feedback was sent.', 'ok');
          textEl.value = ''; emailEl.value = '';
          setTimeout(close, 1400);
        }} else {{
          showMsg((data && data.message) || "Sorry, that didn't go through. Try again later.", 'err');
        }}
      }})
      .catch(function () {{
        showMsg("Network error \\u2014 please try again.", 'err');
      }})
      .finally(function () {{
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
      }});
  }});
}})();
</script>
{HTML_END}
"""


def feedback_html():
    return FEEDBACK_HTML_TMPL.format(
        HTML_START=HTML_START,
        HTML_END=HTML_END,
        access_key=ACCESS_KEY,
    )


def strip_old(html):
    # Drop any prior feedback-mark CSS / HTML / legacy mailto block.
    html = re.sub(
        re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?',
        '',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        re.escape(HTML_START) + r'.*?' + re.escape(HTML_END) + r'\n?',
        '',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'\n?/\* ===== Feedback mark ===== \*/.*?@media print\{\.feedback-mark\{display:none;\}\}\n?',
        '',
        html,
        flags=re.DOTALL,
    )
    return html


def process(path):
    name = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = strip_old(html)

    if '</style>' in html:
        idx = html.rfind('</style>')
        html = html[:idx] + FEEDBACK_CSS + html[idx:]
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + FEEDBACK_CSS + '</style>\n</head>', 1)
    else:
        print(f"  FAIL {name} (no </head>)")
        return False

    block = feedback_html()
    if '</body>' in html:
        html = html.replace('</body>', block + '</body>', 1)
    else:
        html = html + '\n' + block

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


def main():
    count = 0
    skipped = 0
    for path in sorted(glob.glob(os.path.join(BASE, '*.html'))):
        name = os.path.basename(path)
        if name in SKIP:
            print(f"  SKIP {name} (hub page)")
            skipped += 1
            continue
        if process(path):
            count += 1
            print(f"  OK   {name}")

    print(f"\nDone. Updated {count} pages ({skipped} hubs skipped).")
    if not ACCESS_KEY:
        print(
            "\nNOTE: ACCESS_KEY is empty, so the modal will say 'Feedback isn't\n"
            "      wired up yet' on Send. Visit https://web3forms.com, enter your\n"
            "      email, copy the access key they send you, paste it into\n"
            "      ACCESS_KEY at the top of this script, and re-run.")


if __name__ == '__main__':
    main()
