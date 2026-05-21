#!/usr/bin/env python3
"""Add a "Cite this tool" disclosure block with three tabs — APA 7,
MLA 9, and BibTeX (@online) — to every tool page. Each citation is
auto-customized using the page's <h1> as the title and its filename as
the URL slug.

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
AUTHOR_LAST = 'Kapita'
AUTHOR_FIRST = 'Shelvean'
AUTHOR_INITIAL = 'S.'
PUBLISHER = 'Math Tools'
YEAR = '2026'

# Hub/landing/personal/utility pages — citations don't apply.
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
.cite-box{{max-width:44rem;margin:.75rem auto;border:1px solid #d1d5db;
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
.cite-tabs{{display:flex;gap:.1rem;border-bottom:1px solid #e5e7eb;margin-bottom:.15rem;}}
.cite-tab{{appearance:none;background:transparent;border:0;
  border-bottom:2px solid transparent;padding:.45rem .85rem;
  font:600 .8rem/1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  color:#6b7280;cursor:pointer;
  transition:color .15s ease,border-color .15s ease;}}
.cite-tab:hover{{color:#374151;}}
.cite-tab[aria-selected="true"]{{color:#4338ca;border-bottom-color:#4338ca;}}
.cite-tab:focus-visible{{outline:2px solid #4338ca;outline-offset:1px;
  border-radius:.2rem 0 0 0;}}
.cite-text{{margin:0;padding:.55rem .7rem;background:#f3f4f6;
  border:1px solid #e5e7eb;border-radius:.3rem;
  font:.825rem/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color:#111827;white-space:pre-wrap;word-break:break-word;
  user-select:text;}}
.cite-pane[hidden]{{display:none;}}
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
    <div class="cite-tabs" role="tablist" aria-label="Citation format">
      <button type="button" class="cite-tab" role="tab" aria-selected="true"
              aria-controls="cite-pane-apa" id="cite-tab-apa">APA</button>
      <button type="button" class="cite-tab" role="tab" aria-selected="false"
              aria-controls="cite-pane-mla" id="cite-tab-mla" tabindex="-1">MLA</button>
      <button type="button" class="cite-tab" role="tab" aria-selected="false"
              aria-controls="cite-pane-bib" id="cite-tab-bib" tabindex="-1">BibTeX</button>
    </div>
    <pre class="cite-text cite-pane" id="cite-pane-apa" role="tabpanel"
         aria-labelledby="cite-tab-apa">{apa}</pre>
    <pre class="cite-text cite-pane" id="cite-pane-mla" role="tabpanel"
         aria-labelledby="cite-tab-mla" hidden>{mla}</pre>
    <pre class="cite-text cite-pane" id="cite-pane-bib" role="tabpanel"
         aria-labelledby="cite-tab-bib" hidden>{bib}</pre>
    <button type="button" class="cite-copy" data-cite-copy
            aria-label="Copy active citation to clipboard">Copy citation</button>
  </div>
</details>
<script>
(function(){{
  /* Tab switching with arrow-key navigation, scoped per cite-box. */
  document.querySelectorAll('.cite-box').forEach(function(box){{
    var tabs  = Array.prototype.slice.call(box.querySelectorAll('.cite-tab'));
    var panes = box.querySelectorAll('.cite-pane');
    function activate(tab){{
      var target = tab.getAttribute('aria-controls');
      tabs.forEach(function(t){{
        var on = (t === tab);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.setAttribute('tabindex', on ? '0' : '-1');
      }});
      panes.forEach(function(p){{
        if (p.id === target) p.removeAttribute('hidden');
        else p.setAttribute('hidden', '');
      }});
    }}
    tabs.forEach(function(tab, i){{
      tab.addEventListener('click', function(){{ activate(tab); }});
      tab.addEventListener('keydown', function(e){{
        if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight' &&
            e.key !== 'Home' && e.key !== 'End') return;
        e.preventDefault();
        var next = i;
        if (e.key === 'ArrowRight') next = (i + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') next = 0;
        else if (e.key === 'End') next = tabs.length - 1;
        tabs[next].focus(); activate(tabs[next]);
      }});
    }});
  }});

  /* Copy the text of the currently-visible pane. */
  document.querySelectorAll('[data-cite-copy]').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      var box = btn.closest('.cite-box');
      if (!box) return;
      var pane = box.querySelector('.cite-pane:not([hidden])');
      if (!pane) return;
      var text = (pane.textContent || '').trim();
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
    """Strip nested HTML, decode common entities, unwrap inline MathJax,
    collapse whitespace."""
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'<[^>]+>', '', s)
    s = (s.replace('&mdash;', '—').replace('&ndash;', '–')
           .replace('&amp;', '&').replace('&nbsp;', ' ')
           .replace('&quot;', '"').replace('&#39;', "'")
           .replace('&lt;', '<').replace('&gt;', '>'))
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


def bibtex_escape(s):
    """Escape characters that BibTeX/LaTeX would otherwise misinterpret."""
    out = []
    for ch in s:
        if ch == '\\':
            out.append('\\textbackslash{}')
        elif ch in '&%$#_{}':
            out.append('\\' + ch)
        elif ch == '~':
            out.append('\\textasciitilde{}')
        elif ch == '^':
            out.append('\\textasciicircum{}')
        else:
            out.append(ch)
    return ''.join(out)


def html_escape(s):
    """Escape for safe insertion into <pre> innerHTML."""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def bib_key(filename):
    stem = filename.replace('.html', '').lower()
    return AUTHOR_LAST.lower() + YEAR + re.sub(r'[^a-z0-9]', '', stem)


def build_citations(title, filename):
    url = SITE_URL + filename
    mla_url = url.replace('https://', '').replace('http://', '')

    apa = f'{AUTHOR_LAST}, {AUTHOR_INITIAL} ({YEAR}). {title}. {PUBLISHER}. {url}'
    mla = (f'{AUTHOR_LAST}, {AUTHOR_FIRST}. "{title}." '
           f'{PUBLISHER}, {YEAR}, {mla_url}.')
    bib = (
        f'@online{{{bib_key(filename)},\n'
        f'  author       = {{{AUTHOR_FIRST} {AUTHOR_LAST}}},\n'
        f'  title        = {{{{{bibtex_escape(title)}}}}},\n'
        f'  year         = {{{YEAR}}},\n'
        f'  organization = {{{PUBLISHER}}},\n'
        f'  url          = {{{url}}}\n'
        f'}}'
    )
    return html_escape(apa), html_escape(mla), html_escape(bib)


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
    apa, mla, bib = build_citations(title, name)

    if '</style>' in html:
        idx = html.rfind('</style>')
        html = html[:idx] + CITE_CSS + html[idx:]
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + CITE_CSS + '</style>\n</head>', 1)
    else:
        return ('FAIL', name, title, None)

    block = CITE_HTML_TMPL.format(
        start=HTML_START, end=HTML_END,
        apa=apa, mla=mla, bib=bib,
    )
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
            print(f'  OK   {name:42s} -> "{title}"')
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
