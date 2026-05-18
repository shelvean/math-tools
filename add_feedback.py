#!/usr/bin/env python3
"""Add a floating 'Feedback / Report a bug' button to every tool page.

Skips hub/landing pages that aren't interactive tools (index, teaching,
projects, linear, optim, numerical, about, pdftools).

The button is a fixed-position pill at the bottom-right corner. The
subject of the mailto: link is filled in at load time from the page
title, so feedback emails identify the tool automatically.
"""
import os
import re
import glob

BASE = '/home/user/math-tools'
FEEDBACK_EMAIL = 'kapita@tamu.edu'

# Hub / landing pages — not tools, so skip.
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

FEEDBACK_CSS = """
/* ===== Feedback mark ===== */
.feedback-mark{position:fixed;right:1rem;bottom:1rem;z-index:9999;
  display:inline-flex;align-items:center;gap:.4rem;
  padding:.55rem .85rem;border-radius:999px;
  background:#4338ca;color:#fff;font:600 .9rem/1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,.18);
  transition:transform .15s ease,background .15s ease,box-shadow .15s ease;}
.feedback-mark:hover,.feedback-mark:focus-visible{background:#3730a3;color:#fff;
  transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.22);text-decoration:none;}
.feedback-mark:focus-visible{outline:3px solid #fff;outline-offset:2px;}
.feedback-mark svg{flex-shrink:0;}
@media(max-width:480px){.feedback-mark span{display:none;}
  .feedback-mark{padding:.6rem;border-radius:50%;}}
@media print{.feedback-mark{display:none;}}
"""

FEEDBACK_HTML = f"""<!-- feedback-mark:start -->
<a id="feedback-mark" class="feedback-mark"
   href="mailto:{FEEDBACK_EMAIL}?subject=Feedback%20on%20a%20math%20tool"
   aria-label="Send feedback or report a bug about this page">
  <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24">
    <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
  </svg>
  <span>Feedback</span>
</a>
<script>
(function () {{
  var a = document.getElementById('feedback-mark');
  if (!a) return;
  var page = (document.title || location.pathname).trim();
  a.href = 'mailto:{FEEDBACK_EMAIL}'
    + '?subject=' + encodeURIComponent('[Feedback] ' + page)
    + '&body=' + encodeURIComponent(
        'Page: ' + location.href + '\\n\\n'
        + 'What happened / what would you like to see improved?\\n\\n'
      );
}})();
</script>
<!-- feedback-mark:end -->
"""

START_MARK = '<!-- feedback-mark:start -->'
END_MARK = '<!-- feedback-mark:end -->'


def process(path):
    name = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove any prior block so re-running the script is idempotent.
    if START_MARK in html and END_MARK in html:
        html = re.sub(
            re.escape(START_MARK) + r'.*?' + re.escape(END_MARK) + r'\n?',
            '',
            html,
            flags=re.DOTALL,
        )

    # Inject CSS before the last </style>, or wrap one before </head>.
    if '.feedback-mark{' not in html:
        if '</style>' in html:
            idx = html.rfind('</style>')
            html = html[:idx] + FEEDBACK_CSS + html[idx:]
        elif '</head>' in html:
            html = html.replace(
                '</head>',
                '<style>' + FEEDBACK_CSS + '</style>\n</head>',
                1,
            )
        else:
            print(f"  FAIL {name} (no </head>)")
            return False

    # Inject the link+script right before </body>.
    if '</body>' in html:
        html = html.replace('</body>', FEEDBACK_HTML + '</body>', 1)
    else:
        html = html + '\n' + FEEDBACK_HTML

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
    print(f"\nDone. Added feedback button to {count} pages ({skipped} hubs skipped).")


if __name__ == '__main__':
    main()
