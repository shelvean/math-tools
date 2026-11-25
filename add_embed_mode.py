#!/usr/bin/env python3
"""Give every tool page the ?embed=1 view, for iframing into Pressbooks.

Opening a tool with ?embed=1 (e.g. slope.html?embed=1) shows only the tool:
the site navigation, back links, title block, intro and About panel, cite
box, footer and feedback button are hidden. The page title stays in the
document for screen readers. Without the parameter nothing changes.

The block is the one introduced on the ten book pages in #783 (slope,
phaseline, linearportrait, convolution, taylorseries,
eigenvalues-eigenvectors, massspring, cooling, pendulum_simulator,
forcing); this script copies it to every other tool page so all tools embed the
same way. The only addition to the #783 block is `div.main-nav`, the
wrapper around the site nav on matrixvectorviz and transformations2d. It goes just before </head>, after the nav-menu
block, between embed-mode:start and embed-mode:end comments.

In the frame the page is laid out for the frame's height. The tool no longer
stretches to fill it (the pages set min-height: 100vh on the body, which left
a large blank area under a tool shorter than its frame), the contrast button
sits directly under the tool instead of at the bottom corner of the frame, and
anything taller than the frame scrolls inside it instead of being cut off.

Embed mode is opt-in rather than triggered by "am I inside an iframe?",
because desktop-preview.html iframes the normal pages and must keep
showing them as they are.

Targets: every page with a "Cite this tool" box, plus every tool linked
from catalog.html; catalog.html itself is excluded.

Idempotent: an existing block is stripped and rewritten, so re-running is
safe and leaves already-correct pages byte-for-byte unchanged.
"""
import os
import re
import glob

BASE = os.path.dirname(os.path.abspath(__file__))

START = '<!-- embed-mode:start -->'
END = '<!-- embed-mode:end -->'

BLOCK = """<!-- embed-mode:start -->
<script>
/* Embed view. Add ?embed=1 to the address to show only the tool. */
(function () {
  var v = new URLSearchParams(location.search).get('embed');
  if (v !== null && v !== '0' && v !== 'false') document.documentElement.classList.add('embed');
})();
</script>
<style>
html.embed .skip, html.embed .skip-link,
html.embed nav.nav, html.embed nav.main-nav, html.embed div.main-nav,
html.embed .back-links, html.embed .back-link,
html.embed #fb-open, html.embed #fb-bd,
html.embed main > .subtitle, html.embed header[role="banner"] > p, html.embed main > nav.related,
html.embed main > div.info-panel:first-of-type:not([id]),
html.embed details.cite-box, html.embed aside.footnotes, html.embed footer { display: none !important; }
html.embed main > h1, html.embed header[role="banner"] > h1 { position: absolute !important; width: 1px !important; height: 1px !important; margin: -1px !important; padding: 0 !important; overflow: hidden !important; clip: rect(0 0 0 0) !important; border: 0 !important; white-space: nowrap !important; }
html.embed a[id^="fnref"] { display: none !important; }
html.embed header[role="banner"] { margin: 0 !important; padding: 0 !important; }
html.embed main.card { max-width: none !important; margin: 0 auto !important; padding: 8px 10px !important; border: 0 !important; border-radius: 0 !important; box-shadow: none !important; }
html.embed { height: 100% !important; overflow: hidden !important; }
html.embed body { height: 100% !important; min-height: 0 !important; overflow-y: auto !important; }
html.embed .contrast-toggle, html.embed .ctoggle, html.embed .hctog { position: static !important; margin: 8px 10px 10px auto !important; }
</style>
<!-- embed-mode:end -->
"""

BLOCK_RE = re.compile(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', re.S)


def targets():
    names = set()
    for path in glob.glob(os.path.join(BASE, '*.html')):
        with open(path, encoding='utf-8') as fh:
            if 'cite-mark:start' in fh.read():
                names.add(os.path.basename(path))
    with open(os.path.join(BASE, 'catalog.html'), encoding='utf-8') as fh:
        names.update(re.findall(r'class="tool-name" href="([^"#?]+\.html)"', fh.read()))
    names.discard('catalog.html')
    return sorted(n for n in names if os.path.exists(os.path.join(BASE, n)))


def main():
    changed = 0
    names = targets()
    for name in names:
        path = os.path.join(BASE, name)
        with open(path, encoding='utf-8') as fh:
            html = fh.read()
        new = BLOCK_RE.sub('', html)
        idx = new.lower().find('</head>')
        if idx < 0:
            print('  skip (no </head>):', name)
            continue
        new = new[:idx] + BLOCK + new[idx:]
        if new != html:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new)
            changed += 1
    print('embed mode: %d tool pages, %d updated' % (len(names), changed))


if __name__ == '__main__':
    main()
