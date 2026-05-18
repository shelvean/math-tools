#!/usr/bin/env python3
"""Add a feedback button + in-page modal to every tool page, and add
a highlighted inline "Leave feedback" link on every major hub page.

Tool pages get a floating bottom-right pill. Major hubs get an inline
highlighted button placed right after the page's subtitle, since their
clean layouts don't need a floating element competing for attention.

The modal POSTs to the Web3Forms API, so the visitor needs no account
and no mail client; submissions land in the email tied to ACCESS_KEY.

Setup (one-time, ~30 seconds)
-----------------------------
1. Open https://web3forms.com and enter your email.
2. Confirm via the email they send; copy the access key (a UUID).
3. Paste it into ACCESS_KEY below.
4. Re-run:   python3 add_feedback.py

The script is idempotent: previously-injected blocks are stripped and
re-written, so re-running after edits is safe.
"""
import os
import re
import glob

BASE = '/home/user/math-tools'

# ============================================================================
# CONFIG
# ============================================================================
ACCESS_KEY = '1b02c5d6-09a9-4536-93f4-a01e0459e743'
# ============================================================================

# Hubs / landing pages: get the modal + inline CTA, but NOT the floating button
# (their layouts are cleaner without it; the inline link is the entry point).
HUB_PAGES = {
    'index.html',
    'teaching.html',
    'projects.html',
    'linear.html',
    'optim.html',
    'numerical.html',
    'about.html',
    'pdftools.html',
}

# Pages that receive an inline highlighted "Leave feedback" link, placed
# immediately after the listed anchor text. The anchor must be unique within
# the page (or just appear first in the natural subtitle/intro spot).
INLINE_CTA_ANCHORS = {
    'index.html':     'All processing happens client-side.',
    'linear.html':    'Matrix operations, geometric transformations, decompositions, and least squares.',
    'numerical.html': 'Root-finding, interpolation, least-squares data fitting, and finite differences.',
    'optim.html':     'Graphical methods for two-variable problems &mdash; feasible regions, corner points, and the method of corners.',
    'projects.html':  'First-order ODEs, oscillations, integral transforms, and phase-plane analysis.',
    'dynamical.html': 'Continuous and discrete dynamics, bifurcations, chaos, and physical oscillators.',
    'teaching.html':  'A record of courses taught across institutions, spanning differential equations, linear algebra, numerical methods, calculus, and PDEs.',
    'pdftools.html':  'no files are uploaded to any server.',
}

CSS_START = '/* feedback-mark-css:start */'
CSS_END = '/* feedback-mark-css:end */'
HTML_START = '<!-- feedback-mark:start -->'
HTML_END = '<!-- feedback-mark:end -->'
CTA_START = '<!-- fb-cta:start -->'
CTA_END = '<!-- fb-cta:end -->'

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
@media print{{.fb-btn,.fb-bd,.fb-link{{display:none!important;}}}}

.fb-link{{display:inline;font:inherit;font-weight:700;color:#4338ca;
  background:#eef2ff;padding:.05rem .5rem;border-radius:.3rem;
  border:1px solid #c7d2fe;cursor:pointer;text-decoration:none;
  vertical-align:baseline;line-height:inherit;}}
.fb-link:hover,.fb-link:focus-visible{{background:#e0e7ff;color:#3730a3;
  border-color:#a5b4fc;text-decoration:underline;}}
.fb-link:focus-visible{{outline:2px solid #4338ca;outline-offset:1px;}}

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

# Floating button (omitted on hubs).
FB_BUTTON_HTML = """<button type="button" id="fb-open" class="fb-btn" aria-label="Send feedback or report a bug">
  <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24">
    <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
  </svg>
  <span>Feedback</span>
</button>
"""

# Modal + JS (always injected).
FB_MODAL_TMPL = """<div class="fb-bd" id="fb-bd" role="dialog" aria-modal="true" aria-labelledby="fb-title" hidden>
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
  if (!bd) return;
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

  function open(e) {{
    if (e && e.preventDefault) e.preventDefault();
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

  Array.prototype.forEach.call(
    document.querySelectorAll('#fb-open, [data-fb-open]'),
    function (t) {{ t.addEventListener('click', open); }}
  );
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
"""

INLINE_CTA = (
    f' {CTA_START}'
    "We'd love to hear what you think. "
    '<button type="button" class="fb-link" data-fb-open>Leave feedback</button>.'
    f'{CTA_END}'
)


def feedback_block(with_button):
    parts = [HTML_START + '\n']
    if with_button:
        parts.append(FB_BUTTON_HTML)
    parts.append(FB_MODAL_TMPL.format(access_key=ACCESS_KEY))
    parts.append(HTML_END + '\n')
    return ''.join(parts)


def strip_old(html):
    html = re.sub(
        re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?',
        '', html, flags=re.DOTALL,
    )
    html = re.sub(
        re.escape(HTML_START) + r'.*?' + re.escape(HTML_END) + r'\n?',
        '', html, flags=re.DOTALL,
    )
    # strip prior inline CTA (with any leading space we added)
    html = re.sub(
        r' ?' + re.escape(CTA_START) + r'.*?' + re.escape(CTA_END),
        '', html, flags=re.DOTALL,
    )
    # legacy v1 mailto block
    html = re.sub(
        r'\n?/\* ===== Feedback mark ===== \*/.*?@media print\{\.feedback-mark\{display:none;\}\}\n?',
        '', html, flags=re.DOTALL,
    )
    return html


def inject_inline_cta(html, anchor):
    if anchor not in html:
        return html, False
    return html.replace(anchor, anchor + INLINE_CTA, 1), True


def process(path):
    name = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = strip_old(html)

    # CSS
    if '</style>' in html:
        idx = html.rfind('</style>')
        html = html[:idx] + FEEDBACK_CSS + html[idx:]
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + FEEDBACK_CSS + '</style>\n</head>', 1)
    else:
        print(f"  FAIL {name} (no </head>)")
        return None

    # Button + modal
    with_button = name not in HUB_PAGES
    block = feedback_block(with_button)
    if '</body>' in html:
        html = html.replace('</body>', block + '</body>', 1)
    else:
        html += '\n' + block

    # Inline CTA
    cta_added = False
    if name in INLINE_CTA_ANCHORS:
        html, cta_added = inject_inline_cta(html, INLINE_CTA_ANCHORS[name])

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return ('hub' if not with_button else 'tool',
            'cta' if cta_added else None)


def main():
    counts = {'tool': 0, 'hub': 0, 'cta': 0, 'missed_cta': 0}
    for path in sorted(glob.glob(os.path.join(BASE, '*.html'))):
        name = os.path.basename(path)
        result = process(path)
        if result is None:
            continue
        kind, cta = result
        counts[kind] += 1
        if name in INLINE_CTA_ANCHORS:
            if cta:
                counts['cta'] += 1
            else:
                counts['missed_cta'] += 1
                print(f"  WARN {name}: anchor not found for inline CTA")
        marker = ' +CTA' if cta else ''
        print(f"  OK   {name} ({'hub, no button' if kind == 'hub' else 'tool, with button'}){marker}")

    print(
        f"\nDone. {counts['tool']} tool pages with floating button, "
        f"{counts['hub']} hub pages without button, "
        f"{counts['cta']} inline CTAs injected"
        + (f", {counts['missed_cta']} anchors missing" if counts['missed_cta'] else '')
        + '.'
    )
    if not ACCESS_KEY:
        print(
            "\nNOTE: ACCESS_KEY is empty. Visit https://web3forms.com, enter your\n"
            "      email, paste the access key here, and re-run.")


if __name__ == '__main__':
    main()
