#!/usr/bin/env python3
"""Inject a lightweight usage-tracking snippet into the interactive tools.

The snippet auto-instruments common interactions (button clicks, <select>
changes, file uploads) and reports them to Google Analytics via custom
events, using event delegation so it never conflicts with a page's own
listeners. It is guarded so a missing/blocked gtag can never break a tool.

Only interactive tools are touched. Static/landing/hub pages and the
auto-generated label pages are excluded. Re-running is a no-op for files
that already contain the snippet.
"""

import glob
import os
import re

# Static/landing/hub/content pages — these are navigation or content, not tools.
EXCLUDE = {
    "about.html", "cv.html", "index.html", "teaching.html", "projects.html",
    "dynamical.html", "linear.html", "numerical.html", "businessmath.html",
    "pdftools.html", "statesdata.html", "tipe-cycles-boucles.html",
    # this injector itself is not HTML, but guard against stray names
}

START = "<!-- usage-tracking:start -->"
END = "<!-- usage-tracking:end -->"

SNIPPET = """<!-- usage-tracking:start -->
<script>
/* Lightweight usage tracking: auto-instruments common interactions and sends
   custom events to Google Analytics. Guarded so a missing/blocked gtag never
   breaks the tool, and delegated so it never conflicts with the page's own
   listeners. */
(function () {
  function trackEvent(name, params) {
    try { if (typeof gtag === 'function') gtag('event', name, params || {}); } catch (e) {}
  }
  function labelFor(el) {
    var t = el.getAttribute('aria-label') || el.id ||
            (el.value && el.type !== 'text' ? el.value : '') ||
            (el.textContent || '').replace(/\\s+/g, ' ').trim() ||
            el.name || el.type || 'unknown';
    return String(t).slice(0, 64);
  }
  document.addEventListener('click', function (e) {
    if (!e.target || !e.target.closest) return;
    var el = e.target.closest('button,[role="button"],a.btn,input[type="button"],input[type="submit"],[data-track]');
    if (!el) return;
    trackEvent('ui_click', { event_category: 'interaction', event_label: labelFor(el) });
  }, true);
  document.addEventListener('change', function (e) {
    var el = e.target;
    if (!el || !el.matches) return;
    if (el.matches('select')) {
      trackEvent('select_change', { event_category: 'interaction', event_label: el.id || labelFor(el), option: String(el.value).slice(0, 64) });
    } else if (el.matches('input[type="file"]')) {
      trackEvent('file_upload', { event_category: 'interaction', event_label: el.id || labelFor(el) });
    }
  }, true);
})();
</script>
<!-- usage-tracking:end -->
"""


def has_gtag(html):
    return "googletagmanager.com/gtag/js" in html


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    changed, skipped_present, skipped_other = [], [], []

    for path in sorted(glob.glob(os.path.join(root, "*.html"))):
        name = os.path.basename(path)
        if name in EXCLUDE:
            skipped_other.append((name, "excluded (static/hub page)"))
            continue
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        if not has_gtag(html):
            skipped_other.append((name, "no gtag config"))
            continue
        if START in html:
            skipped_present.append(name)
            continue
        m = re.search(r"</body>", html, re.IGNORECASE)
        if not m:
            skipped_other.append((name, "no </body>"))
            continue
        idx = m.start()
        new_html = html[:idx] + SNIPPET + html[idx:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        changed.append(name)

    print("Injected snippet into %d tool(s):" % len(changed))
    for n in changed:
        print("  +", n)
    if skipped_present:
        print("\nAlready had snippet (%d):" % len(skipped_present))
        for n in skipped_present:
            print("  =", n)
    if skipped_other:
        print("\nSkipped (%d):" % len(skipped_other))
        for n, why in skipped_other:
            print("  -", n, "->", why)


if __name__ == "__main__":
    main()
