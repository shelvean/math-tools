#!/usr/bin/env python3
"""Fold the site nav into a "Menu" button on narrow screens.

Every page carries its own copy of the top nav, in one of two markups:
most pages use a <nav> holding <ul class="nav-list">; the subject hubs
(projects, dynamical, linear, ...) use <div class="topbar"><nav class="nav">
with the links directly inside, next to a theme toggle. On a phone the
ten-plus links wrap to five or more lines, which buries the page under the
nav and, where the nav is sticky, keeps a quarter of the screen covered.

This injects one self-contained block just before </head> on every page
with either markup. At 700px and below it hides the links behind a toggle
button; tapping it opens them as a vertical list. Wider screens are
untouched. The links are only hidden once the script has added the
`nav-menu-js` class, so without JavaScript the full nav still shows, and
because the block sits in <head> the full nav never flashes on load.

The script is idempotent: previously-injected blocks are stripped and
re-written, so re-running after edits is safe.
"""
import os
import re
import glob

BASE = os.path.dirname(os.path.abspath(__file__))

START = '<!-- nav-menu:start -->'
END = '<!-- nav-menu:end -->'

# Markers that identify the site nav in each markup.
NAV_MARKERS = ('class="nav-list"', '<div class="topbar"><nav class="nav"')

BLOCK = START + """
<style>
.nav-menu-btn{display:none;}
@media (max-width:700px){
  .nav-menu-js .nav-menu-btn{display:inline-flex;align-items:center;gap:.5rem;
    min-height:44px;margin:0;padding:.4rem .8rem;cursor:pointer;
    border:1px solid currentColor;border-radius:.375rem;background:transparent;color:inherit;
    font:700 1rem/1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;}
  .nav-menu-js .nav-menu-btn:focus-visible{outline:3px solid #2563eb;outline-offset:2px;}
  .nav-menu-js nav .nav-list,.nav-menu-js .topbar>nav.nav{display:none;}
  .nav-menu-js .nav-open .nav-list,.nav-menu-js .topbar.nav-open>nav.nav{display:flex;
    flex-direction:column;align-items:stretch;gap:0;margin:.5rem 0 0;padding:0;
    max-height:calc(100vh - 5rem);overflow-y:auto;}
  .nav-menu-js .nav-open .nav-list a,.nav-menu-js .topbar.nav-open>nav.nav a{display:flex;
    align-items:center;min-height:44px;padding:.5rem .75rem;font-size:1rem;}
  .nav-menu-js .topbar{flex-wrap:wrap;align-items:center;}
  .nav-menu-js .topbar.nav-open>nav.nav{flex:1 0 100%;order:3;}
}
@media print{.nav-menu-btn{display:none!important;}}
</style>
<script>
(function () {
  var root = document.documentElement;
  root.classList.add('nav-menu-js');
  function init() {
    // panel: the element holding the links; host: the element that gets
    // .nav-open and also contains the button.
    var panel = document.querySelector('nav .nav-list'), host;
    if (panel) host = panel.closest('nav');
    else if ((panel = document.querySelector('.topbar > nav.nav'))) host = panel.parentNode;
    else { root.classList.remove('nav-menu-js'); return; }
    if (!panel.id) panel.id = 'site-nav-list';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-menu-btn';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', panel.id);
    btn.innerHTML = '<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24">' +
      '<path fill="currentColor" d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg><span>Menu</span>';
    // Match the button to the page's own link colour, and keep matching it
    // when a theme toggle or the system colour scheme changes that colour.
    var link = panel.querySelector('a');
    function syncColor() { if (link) btn.style.color = getComputedStyle(link).color; }
    function syncSoon() { syncColor(); setTimeout(syncColor, 350); }
    syncColor();
    if (window.MutationObserver) {
      var mo = new MutationObserver(syncSoon);
      mo.observe(root, {attributes: true});
      mo.observe(document.body, {attributes: true});
    }
    if (window.matchMedia) {
      var mq = matchMedia('(prefers-color-scheme: dark)');
      if (mq.addEventListener) mq.addEventListener('change', syncSoon);
    }
    panel.parentNode.insertBefore(btn, panel);
    function setOpen(open) {
      host.classList.toggle('nav-open', open);
      btn.setAttribute('aria-expanded', String(open));
    }
    btn.addEventListener('click', function () {
      syncColor();
      setOpen(btn.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && host.classList.contains('nav-open')) { setOpen(false); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (host.classList.contains('nav-open') && !host.contains(e.target)) setOpen(false);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
</script>
""" + END + '\n'


def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html
    html = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', html, flags=re.DOTALL)
    if any(m in html for m in NAV_MARKERS):
        if '</head>' not in html:
            print(f"  FAIL {os.path.basename(path)} (no </head>)")
            return None
        html = html.replace('</head>', BLOCK + '</head>', 1)
    if html == original:
        return 'unchanged'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return 'updated'


def main():
    counts = {'updated': 0, 'unchanged': 0}
    # labels/ pages come from generate_labels.py, which includes BLOCK itself;
    # patching them here keeps the committed copies in step without regenerating.
    paths = glob.glob(os.path.join(BASE, '*.html')) + glob.glob(os.path.join(BASE, 'labels', '*.html'))
    for path in sorted(paths):
        kind = process(path)
        if kind:
            counts[kind] += 1
    print(f"Done. {counts['updated']} pages updated, {counts['unchanged']} unchanged.")


if __name__ == '__main__':
    main()
