#!/usr/bin/env python3
"""Add a "Cite this tool" disclosure block with a copy-to-clipboard
button to every tool page. Each citation is auto-customized using the
page's <h1> as the title and its filename as the URL slug. The format
is APA 7th edition for a web tool — universal, single-line, and
copy-paste friendly.

The block is placed immediately before the page's <footer> (the
natural "metadata about this page" location), so it sits with the
copyright/license info without competing with the tool's main UI.

Idempotent: previously-injected blocks are stripped and re-written, so
re-running after edits is safe.
"""
import os
import re
import glob

BASE = '/home/user/math-tools'
SITE_URL = 'https://shelvean.github.io/math-tools/'
AUTHOR = 'Kapita, S.'
PUBLISHER = 'Math Tools'
YEAR = '2026'

# Hub/landing/personal pages — they aggregate tools rather than being
# tools themselves, so a citation block doesn't add value.
SKIP_PAGES = {
    'index.html', 'about.html', 'cv.html',
    'teaching.html', 'projects.html', 'linear.html',
    'optim.html', 'numerical.html', 'dynamical.html',
    'businessmath.html', 'pdftools.html', 'desktop-preview.html',
    'ttlc2026.html', 'statesdata.html', 'epl.html', 'timer.html',
}

CSS_START = '/* cite-mark-css:start */'
CSS_END = '/* cite-mark-css:end */'
HTML_START = '<!-- cite-mark:start -->'
HTML_END = '<!-- cite-mark:end -->'

CITE_CSS = f"""{CSS_START}
.cite-box{{max-width:42rem;margin:.75rem auto;border:1px solid #d1d5db;
  border-radius:.4rem;background:#f9fafb;font-size:.85rem;text-align:left;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;}}
.cite-box[open]{{background:#fff;}}
.cite-summary{{cursor:pointer;font-weight:600;color:#374151;
  padding:.5rem .75rem;user-select:none;list-style:none;
  display:flex;align-items:center;gap:.4rem;}}
.cite-summary::-webkit-details-marker{{display:none;}}
.cite-summary::before{{content:"\\25B8";font-size:.75rem;color:#6b7280;
  transition:transform .15s ease;display:inline-block;}}
.cite-box[open] .cite-summary::before{{transform:rotate(90deg);}}
.cite-summary:hover{{color:#111827;}}
.cite-summary:focus-visible{{outline:2px solid #4338ca;outline-offset:1px;
  border-radius:.3rem;}}
.cite-content{{padding:.15rem .75rem .75rem;display:flex;flex-direction:column;gap:.5rem;}}
.cite-text{{margin:0;padding:.55rem .7rem;background:#f3f4f6;
  border:1px solid #e5e7eb;border-radius:.3rem;
  font:.825rem/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color:#111827;white-space:pre-wrap;word-break:break-word;
  user-select:text;}}
.cite-copy{{align-self:flex-start;padding:.4rem .85rem;border:1px solid #d1d5db;
  border-radius:.35rem;background:#fff;color:#374151;
  font:600 .8rem/1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  cursor:pointer;transition:background .15s ease,color .15s ease,border-color .15s ease;}}
.cite-copy:hover{{background:#f3f4f6;color:#111827;}}
.cite-copy:focus-visible{{outline:2px solid #4338ca;outline-offset:1px;}}
.cite-copy.cite-ok{{background:#ecfdf5;color:#166534;border-color:#bbf7d0;}}
@media print{{.cite-box{{display:none;}}}}
{CSS_END}
"""

CITE_HTML_TMPL = """{start}
<details class="cite-box">
  <summary class="cite-summary">Cite this tool</summary>
  <div class="cite-content">
    <p class="sr-only" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">APA 7th edition citation. Click the button below to copy to your clipboard, or select and copy the text manually.</p>
    <pre class="cite-text">{citation}</pre>
    <button type="button" class="cite-copy" data-cite-copy aria-label="Copy citation to clipboard">Copy citation</button>
  </div>
</details>
<script>
(function(){{
  var btns = document.querySelectorAll('[data-cite-copy]');
  btns.forEach(function(btn){{
    btn.addEventListener('click', function(){{
      var box = btn.closest('.cite-box');
      if (!box) return;
      var pre = box.querySelector('.cite-text');
      var text = (pre.textContent || '').trim();
      function showOk(){{
        var orig = btn.getAttribute('data-orig') || btn.textContent;
        btn.setAttribute('data-orig', orig);
        btn.textContent = 'Copied!';
        btn.classList.add('cite-ok');
        setTimeout(function(){{
          btn.textContent = orig;
          btn.classList.remove('cite-ok');
        }}, 1600);
      }}
      function fallback(){{
        try{{
          var ta = document.createElement('textarea');
          ta.value = text; ta.setAttribute('readonly', '');
          ta.style.position = 'fixed'; ta.style.opacity = '0';
          document.body.appendChild(ta); ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          showOk();
        }} catch(e) {{
          var orig = btn.getAttribute('data-orig') || btn.textContent;
          btn.setAttribute('data-orig', orig);
          btn.textContent = 'Press Ctrl+C';
          setTimeout(function(){{ btn.textContent = orig; }}, 1800);
        }}
      }}
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(showOk, fallback);
      }} else {{
        fallback();
      }}
    }});
  }});
}})();
</script>
{end}
"""


def clean(s):
    """Strip nested HTML, decode common entities, collapse whitespace,
    and unwrap inline MathJax delimiters so the citation reads as plain text."""
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'<[^>]+>', '', s)
    s = (s.replace('&mdash;', '—').replace('&ndash;', '–')
           .replace('&amp;', '&').replace('&nbsp;', ' ')
           .replace('&quot;', '"').replace('&#39;', "'")
           .replace('&lt;', '<').replace('&gt;', '>'))
    # Unwrap inline MathJax: \(x\) -> x, $$x$$/$x$ kept (rare in titles).
    s = re.sub(r'\\\(\s*(.*?)\s*\\\)', r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def extract_title(html):
    """Prefer first <h1>; fall back to <title> with site suffix stripped."""
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, flags=re.DOTALL | re.IGNORECASE)
    if m:
        title = clean(m.group(1))
        if title:
            return title
    m = re.search(r'<title[^>]*>(.*?)</title>', html, flags=re.DOTALL | re.IGNORECASE)
    if m:
        text = clean(m.group(1))
        for sep in (' — ', ' – ', ' | ', ' - '):
            if sep in text:
                text = text.split(sep)[0].strip()
                break
        return text
    return 'Untitled'


def build_citation(title, filename):
    """APA 7th edition for a web tool: Author. (Year). Title [descriptor]. Site. URL"""
    url = SITE_URL + filename
    return f'{AUTHOR} ({YEAR}). {title} [Web tool]. {PUBLISHER}. {url}'


def strip_old(html):
    html = re.sub(
        re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?',
        '', html, flags=re.DOTALL,
    )
    html = re.sub(
        re.escape(HTML_START) + r'.*?' + re.escape(HTML_END) + r'\n?',
        '', html, flags=re.DOTALL,
    )
    return html


def inject_block(html, block):
    """Place immediately BEFORE <footer (any class). Falls back to before
    </main>, then before </body>."""
    m = re.search(r'<footer\b', html)
    if m:
        return html[:m.start()] + block + html[m.start():], 'footer'
    m = re.search(r'</main\b', html, flags=re.IGNORECASE)
    if m:
        return html[:m.start()] + block + html[m.start():], 'main-end'
    if '</body>' in html:
        return html.replace('</body>', block + '</body>', 1), 'body-end'
    return html + '\n' + block, 'appended'


def process(path):
    name = os.path.basename(path)
    if name in SKIP_PAGES:
        return ('SKIP', name, None, None)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = strip_old(html)
    title = extract_title(html)
    citation = build_citation(title, name)

    if '</style>' in html:
        idx = html.rfind('</style>')
        html = html[:idx] + CITE_CSS + html[idx:]
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + CITE_CSS + '</style>\n</head>', 1)
    else:
        return ('FAIL', name, title, None)

    block = CITE_HTML_TMPL.format(start=HTML_START, end=HTML_END, citation=citation)
    html, where = inject_block(html, block)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return ('OK', name, title, where)


def main():
    counts = {'OK': 0, 'SKIP': 0, 'FAIL': 0}
    for path in sorted(glob.glob(os.path.join(BASE, '*.html'))):
        status, name, title, where = process(path)
        counts[status] += 1
        if status == 'OK':
            print(f'  OK   {name:42s} -> "{title}" @ {where}')
        elif status == 'SKIP':
            print(f'  SKIP {name}')
        else:
            print(f'  FAIL {name}')
    print(
        f"\nDone. {counts['OK']} citation blocks injected, "
        f"{counts['SKIP']} hubs/personal pages skipped, "
        f"{counts['FAIL']} failed."
    )


if __name__ == '__main__':
    main()
