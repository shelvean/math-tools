#!/usr/bin/env python3
"""Generate embed.html: copy-and-paste iframe codes for Pressbooks.

Reads the "Mathematical Tools" sections of catalog.html (section headings,
tool names, links and descriptions) and writes embed.html, a page listing
every tool with a ready-made embed snippet:

    <iframe src=".../tool.html?embed=1" ...></iframe>
    <p><a href=".../tool.html">Open <name> in a new tab</a></p>

?embed=1 switches the tool into embed mode (see add_embed_mode.py). The
plain link underneath is the fallback for formats that cannot run
interactive content (PDF and print exports) and for platforms that strip
iframes.

Re-run after editing catalog.html, then run add_nav_menu.py so the new
page gets the phone Menu button like every other page.
"""
import os
import re
import html

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://shelvean.github.io/math-tools/'


def parse_catalog():
    src = open(os.path.join(BASE, 'catalog.html'), encoding='utf-8').read()
    # Only the "Mathematical Tools" group: it ends where the next group starts.
    start = src.index('id="grp-mathematical-tools"')
    nxt = src.find('class="cat-grouphd"', start + 40)
    group = src[start:nxt if nxt > 0 else len(src)]
    sections = []
    for m in re.finditer(r'<h3 id="([^"]+)" class="cat-subhd">(.*?)</h3>(.*?)</ol>', group, re.S):
        sec_id, title_html, body = m.groups()
        title = re.sub(r'<span class="cat-count">.*?</span>', '', title_html)
        title = html.unescape(re.sub(r'<.*?>', '', title)).strip()
        tools = []
        for t in re.finditer(r'<a class="tool-name" href="([^"]+)">(.*?)</a>\s*'
                             r'<span class="tool-desc">(.*?)</span>', body, re.S):
            href, name, desc = t.groups()
            if not os.path.exists(os.path.join(BASE, href)):
                continue
            tools.append({'href': href,
                          'name': html.unescape(re.sub(r'<.*?>', '', name)).strip(),
                          'desc': desc.strip()})
        if tools:
            sections.append({'id': sec_id.replace('sec-', ''), 'title': title, 'tools': tools})
    return sections


HEAD = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#1d4ed8">
  <meta name="color-scheme" content="light">
  <title>Embed Math Tools in Pressbooks</title>
  <meta name="description" content="Copy-and-paste iframe embed codes for every Math Tools simulation, ready for Pressbooks chapters and other open textbooks.">
  <meta name="author" content="Shelvean Kapita">
  <link rel="canonical" href="https://shelvean.github.io/math-tools/embed.html">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Math Tools - Shelvean Kapita">
  <meta property="og:title" content="Embed Math Tools in Pressbooks">
  <meta property="og:description" content="Copy-and-paste iframe embed codes for every Math Tools simulation, ready for Pressbooks chapters and other open textbooks.">
  <meta property="og:url" content="https://shelvean.github.io/math-tools/embed.html">
  <meta property="og:image" content="https://shelvean.github.io/math-tools/android-chrome-192x192.png">
  <meta name="twitter:card" content="summary">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-LEQE004C92"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-LEQE004C92');</script>

  <script>
    window.MathJax = {
      tex: {inlineMath:[['$','$'],['\\(','\\)']],displayMath:[['$$','$$'],['\\[','\\]']]},
      options: { enableAssistiveMml: true, skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }
    };
  </script>
  <script src="vendor/mathjax@3.2.2/es5/tex-chtml.js" async></script>

  <style>
:root{
  --bg:#f0f2f5;--card:#fff;--sect:#f8f9fb;
  --info:#eff6ff;--inf-b:#1d4ed8;--inf-hd:#1e3a8a;
  --txt:#111827;--txt2:#374151;--muted:#4b5563;
  --bdr:#6b7280;--bdr2:#d1d5db;--focus:#1d4ed8;
  --blue:#1d4ed8;--bl2:#1e3a8a;--green:#15803d;
  --r:.5rem;--r2:.75rem;--link:#1e40af;
}
*,*::before,*::after{box-sizing:border-box;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  background:var(--bg);color:var(--txt);margin:0;min-height:100vh;line-height:1.6;}
*:focus-visible{outline:3px solid var(--focus);outline-offset:2px;border-radius:2px;}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
  clip:rect(0,0,0,0);white-space:nowrap;border:0;}
.skip{position:absolute;top:-100%;left:50%;transform:translateX(-50%);background:var(--blue);
  color:#fff;padding:.75rem 1.5rem;z-index:1000;border-radius:0 0 var(--r) var(--r);
  font-weight:700;text-decoration:none;}
.skip:focus{top:0;}

.nav{position:sticky;top:0;left:0;width:100%;z-index:100;background:var(--card);
  border-bottom:2px solid var(--bdr);box-shadow:0 1px 3px rgba(0,0,0,.10);}
.nav-in{max-width:72rem;margin:0 auto;padding:.45rem 1rem;}
.nav-list{list-style:none;display:flex;justify-content:center;gap:.75rem;margin:0;padding:0;flex-wrap:wrap;}
.nav-list a{color:var(--link);text-decoration:none;font-weight:700;font-size:1rem;
  padding:.625rem .5rem;border-radius:.3rem;display:inline-flex;align-items:center;min-height:44px;}
.nav-list a:hover,.nav-list a:focus-visible{text-decoration:underline;}
.back-link{display:flex;width:fit-content;align-items:center;gap:6px;font-size:.85rem;font-weight:500;
  color:#4338ca;text-decoration:none;margin:.5rem auto;}
.back-link:hover{color:#3730a3;}

.card{background:var(--card);padding:1.1rem 1.25rem;border-radius:var(--r2);
  max-width:960px;width:calc(100% - 2rem);margin:1rem auto 1.5rem;}
h1{font-size:1.75rem;font-weight:800;text-align:center;margin:0 0 .2rem;letter-spacing:-.02em;}
.subtitle{font-size:.9375rem;color:var(--txt2);text-align:center;margin:0 0 1.1rem;}

.how{background:var(--info);border:2px solid var(--inf-b);border-radius:var(--r);
  padding:.85rem 1.1rem;margin-bottom:1rem;}
.how h2{font-size:1rem;color:var(--inf-hd);margin:0 0 .4rem;}
.how ol{margin:0 0 .5rem 1.25rem;padding:0;}
.how li,.how p{font-size:.9375rem;color:var(--txt2);margin:.2rem 0;}
.how code{font-size:.85em;background:rgba(29,78,216,.08);padding:.05rem .3rem;border-radius:.25rem;}

.cbar{display:flex;flex-wrap:wrap;align-items:flex-end;gap:.75rem;margin-bottom:1rem;
  background:var(--sect);border:2px solid var(--bdr2);border-radius:var(--r);padding:.6rem .75rem;}
.cfield{display:flex;flex-direction:column;gap:.18rem;}
.cfield.grow{flex:1;min-width:12rem;}
.clbl{font-size:.8125rem;font-weight:700;color:var(--txt2);}
.cfield input[type=search],.cfield select{min-height:40px;padding:.2rem .5rem;font-size:.9rem;
  font-weight:600;border:2px solid var(--bdr);border-radius:.375rem;background:var(--card);color:var(--txt);width:100%;}
.cchk{display:flex;align-items:center;gap:.4rem;font-size:.875rem;font-weight:600;color:var(--txt2);
  min-height:40px;}
.cchk input{width:1.1rem;height:1.1rem;}

.sect{margin:1.25rem 0 .5rem;}
.sect h2{font-size:1.15rem;margin:0 0 .5rem;padding-bottom:.25rem;border-bottom:2px solid var(--bdr2);}
.tool{border:2px solid var(--bdr2);border-radius:var(--r);background:var(--card);
  padding:.7rem .85rem;margin-bottom:.6rem;}
.tool h3{font-size:1rem;margin:0 0 .15rem;}
.tool h3 a{color:var(--link);}
.tool .desc{font-size:.875rem;color:var(--txt2);margin:0 0 .5rem;}
.tool pre{margin:0 0 .5rem;padding:.5rem .65rem;background:#f3f4f6;border:1px solid #e5e7eb;
  border-radius:.35rem;font:.78rem/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  white-space:pre-wrap;word-break:break-all;color:#111827;}
.acts{display:flex;flex-wrap:wrap;gap:.4rem;}
.btn{display:inline-flex;align-items:center;gap:.35rem;min-height:40px;padding:.35rem .85rem;
  border-radius:.45rem;font-size:.875rem;font-weight:700;cursor:pointer;text-decoration:none;
  border:2px solid var(--blue);background:var(--card);color:var(--blue);}
.btn:hover{background:var(--info);}
.btn-go{background:var(--blue);color:#fff;}
.btn-go:hover{background:var(--bl2);}
.btn.ok{background:#ecfdf5;color:var(--green);border-color:var(--green);}
.preview{margin-top:.6rem;border:2px dashed var(--bdr2);border-radius:var(--r);overflow:hidden;}
.preview iframe{display:block;width:100%;border:0;background:#fff;}
.empty{display:none;text-align:center;color:var(--muted);padding:1rem;}

.footer{margin-top:1.25rem;border-top:2px solid var(--bdr2);padding-top:1rem;
  text-align:center;color:var(--txt2);font-size:.875rem;}
.footer a{color:var(--link);}
  </style>
</head>
"""

BODY_TOP = r"""<body>
<a href="#main" class="skip">Skip to main content</a>
<div id="live" class="sr-only" aria-live="polite" aria-atomic="true"></div>

<nav class="nav" aria-label="Main navigation">
  <div class="nav-in">
    <ul class="nav-list" role="list">
      <li><a href="index.html">Home</a></li>
      <li><a href="about.html">About</a></li>
      <li><a href="catalog.html">Catalog</a></li>
      <li><a href="teaching.html">Teaching</a></li>
      <li><a href="projects.html">Differential Equations</a></li>
      <li><a href="dynamical.html">Dynamical Systems</a></li>
      <li><a href="linear.html">Linear Algebra</a></li>
      <li><a href="optim.html">Optimization</a></li>
      <li><a href="numerical.html">Numerical Methods</a></li>
      <li><a href="calculus.html">Calculus</a></li>
      <li><a href="businessmath.html">Business Math</a></li>
    </ul>
  </div>
</nav>

<a href="catalog.html" class="back-link" aria-label="Back to the catalog">&larr; Back to the Catalog</a>

<main id="main" class="card">
  <h1>Embed Math Tools in Pressbooks</h1>
  <p class="subtitle">Every simulation below can be placed inside a Pressbooks chapter, or any web page that accepts an
    <code>&lt;iframe&gt;</code>. Readers then use the live tool without leaving the book.</p>

  <section class="how" aria-labelledby="how-hd">
    <h2 id="how-hd">How to embed a tool</h2>
    <ol>
      <li>Find the tool below and press <strong>Copy embed code</strong>.</li>
      <li>In the Pressbooks chapter editor, switch from the <strong>Visual</strong> tab to the <strong>Text</strong> (HTML) tab.</li>
      <li>Paste the code where the tool should appear, then save and view the chapter.</li>
    </ol>
    <p>The embedded version shows only the tool. This site's menus, the tool's title and introduction, the footer and
      the feedback button are hidden. The code also adds an ordinary link under the frame. PDF and print exports
      cannot run interactive content, so readers of those versions still get a working link.</p>
    <p>If Pressbooks removes the <code>&lt;iframe&gt;</code> when you save, your Pressbooks network may only accept embeds
      from approved sites. Ask your network administrator to allow <code>shelvean.github.io</code>.</p>
    <p>Any tool can also be embedded by hand: add <code>?embed=1</code> to its address, e.g.
      <code>https://shelvean.github.io/math-tools/pendulum_simulator.html?embed=1</code>.</p>
  </section>

  <div class="cbar" role="group" aria-label="Embed options">
    <div class="cfield grow">
      <label class="clbl" for="q">Search tools</label>
      <input type="search" id="q" placeholder="e.g. pendulum, eigenvalues, Newton" autocomplete="off">
    </div>
    <div class="cfield">
      <label class="clbl" for="height">Frame height</label>
      <select id="height">
        <option value="600">600 px - short</option>
        <option value="800">800 px</option>
        <option value="1000" selected>1000 px - default</option>
        <option value="1200">1200 px</option>
        <option value="1500">1500 px - tall</option>
      </select>
    </div>
    <label class="cchk"><input type="checkbox" id="fallback" checked> Include link below the frame</label>
  </div>
  <p id="count" class="sr-only" aria-live="polite"></p>
"""

BODY_BOTTOM = r"""
  <p class="empty" id="empty">No tools match your search.</p>

  <footer class="footer" role="contentinfo">
    <p>&copy; 2026 Shelvean Kapita - Department of Mathematics, Texas A&amp;M University. Educational content licensed under
      <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; source code under the
      <a href="https://opensource.org/licenses/MIT">MIT License</a>. </p>
  </footer>
</main>

<script>
(function () {
  var SITE = 'https://shelvean.github.io/math-tools/';
  var heightSel = document.getElementById('height');
  var fallback = document.getElementById('fallback');
  var q = document.getElementById('q');

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function snippet(tool) {
    var href = tool.getAttribute('data-href'), name = tool.getAttribute('data-name');
    var code = '<iframe src="' + SITE + href + '?embed=1" title="' + esc(name) + ' (interactive tool)" ' +
      'width="100%" height="' + heightSel.value + '" frameborder="0" loading="lazy" allowfullscreen></iframe>';
    if (fallback.checked) {
      code += '\n<p><a href="' + SITE + href + '" target="_blank" rel="noopener">Open the ' + esc(name) +
        ' in a new tab</a></p>';
    }
    return code;
  }
  var tools = Array.prototype.slice.call(document.querySelectorAll('.tool'));
  function refresh() {
    tools.forEach(function (tool) {
      tool.querySelector('pre code').textContent = snippet(tool);
      var frame = tool.querySelector('.preview iframe');
      if (frame) frame.height = heightSel.value;
    });
  }
  heightSel.addEventListener('change', refresh);
  fallback.addEventListener('change', refresh);
  refresh();

  function copyText(text, done) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { legacy(text, done); });
    } else legacy(text, done);
  }
  function legacy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); done(); } catch (e) {}
    document.body.removeChild(ta);
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('button[data-act]') : null;
    if (!btn) return;
    var tool = btn.closest('.tool');
    if (btn.getAttribute('data-act') === 'copy') {
      copyText(snippet(tool), function () {
        btn.textContent = 'Copied!'; btn.classList.add('ok');
        document.getElementById('live').textContent = 'Embed code for ' + tool.getAttribute('data-name') + ' copied.';
        setTimeout(function () { btn.textContent = 'Copy embed code'; btn.classList.remove('ok'); }, 1600);
      });
    } else {
      var box = tool.querySelector('.preview');
      var open = btn.getAttribute('aria-expanded') === 'true';
      if (open) { box.innerHTML = ''; box.hidden = true; }
      else {
        var f = document.createElement('iframe');
        f.src = tool.getAttribute('data-href') + '?embed=1';
        f.title = 'Preview of the embedded ' + tool.getAttribute('data-name');
        f.height = heightSel.value; f.loading = 'lazy';
        box.appendChild(f); box.hidden = false;
      }
      btn.setAttribute('aria-expanded', String(!open));
      btn.textContent = open ? 'Preview' : 'Hide preview';
    }
  });

  q.addEventListener('input', function () {
    var terms = q.value.toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
    tools.forEach(function (tool) {
      var hay = (tool.getAttribute('data-name') + ' ' + tool.getAttribute('data-href') + ' ' +
                 tool.querySelector('.desc').textContent).toLowerCase();
      var ok = terms.every(function (t) { return hay.indexOf(t) >= 0; });
      tool.hidden = !ok; if (ok) shown++;
    });
    document.querySelectorAll('.sect').forEach(function (s) {
      s.hidden = !s.querySelector('.tool:not([hidden])');
    });
    document.getElementById('empty').style.display = shown ? 'none' : 'block';
    document.getElementById('count').textContent = shown + ' tools shown.';
  });
})();
</script>
</body>
</html>
"""


def render(sections):
    out = [HEAD, BODY_TOP]
    for s in sections:
        out.append('\n  <section class="sect" aria-labelledby="s-%s">\n    <h2 id="s-%s">%s</h2>\n'
                   % (s['id'], s['id'], html.escape(s['title'])))
        for t in s['tools']:
            name = html.escape(t['name'], quote=True)
            out.append(
                '    <article class="tool" data-href="%(href)s" data-name="%(name)s">\n'
                '      <h3><a href="%(href)s">%(name)s</a></h3>\n'
                '      <p class="desc">%(desc)s</p>\n'
                '      <pre aria-label="Embed code for %(name)s"><code></code></pre>\n'
                '      <div class="acts">\n'
                '        <button type="button" class="btn btn-go" data-act="copy">Copy embed code</button>\n'
                '        <button type="button" class="btn" data-act="preview" aria-expanded="false">Preview</button>\n'
                '        <a class="btn" href="%(href)s?embed=1" target="_blank" rel="noopener">Open embedded view &#8599;</a>\n'
                '      </div>\n'
                '      <div class="preview" hidden></div>\n'
                '    </article>\n' % {'href': html.escape(t['href'], quote=True), 'name': name, 'desc': t['desc']})
        out.append('  </section>\n')
    out.append(BODY_BOTTOM)
    return ''.join(out)


def main():
    sections = parse_catalog()
    with open(os.path.join(BASE, 'embed.html'), 'w', encoding='utf-8') as fh:
        fh.write(render(sections))
    print('embed.html: %d sections, %d tools' % (len(sections), sum(len(s['tools']) for s in sections)))


if __name__ == '__main__':
    main()
