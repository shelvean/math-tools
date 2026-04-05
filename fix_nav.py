#!/usr/bin/env python3
"""Replace non-standard navs with the projects.html-style nav."""
import re, os

BASE = '/home/user/math-tools'

NAV_HTML = '''<nav class="main-nav" aria-label="Main navigation">
  <div class="nav-inner">
    <ul class="nav-list" role="list">
      <li><a href="index.html">Home</a></li>
      <li><a href="teaching.html">Teaching</a></li>
      <li><a href="projects.html">Diff Eq</a></li>
      <li><a href="linear.html">Linear Algebra</a></li>
      <li><a href="optim.html">Linear Programming</a></li>
      <li><a href="numerical.html">Numerical Methods</a></li>
    </ul>
  </div>
</nav>'''

NAV_CSS = """
/* ===== Site Nav ===== */
.main-nav{position:sticky;top:0;left:0;width:100%;z-index:1000;
  background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.1);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;}
.nav-inner{max-width:72rem;margin:0 auto;padding:.5rem 1rem;}
.nav-list{list-style:none;display:flex;justify-content:center;gap:1rem;margin:0;padding:0;flex-wrap:wrap;}
.nav-list a{color:#4338ca;text-decoration:none;font-weight:700;font-size:1.05rem;
  padding:.5rem .5rem;border-radius:.25rem;display:inline-flex;align-items:center;min-height:44px;}
.nav-list a:hover,.nav-list a:focus-visible{color:#3730a3;text-decoration:underline;}
@media(max-width:640px){.nav-list{gap:.4rem;}.nav-list a{font-size:.9rem;padding:.4rem .35rem;}}
"""

def has_main_nav(html):
    return 'class="main-nav"' in html

def add_css(html):
    if '</style>' in html:
        html = html.replace('</style>', NAV_CSS + '</style>', 1)
    else:
        html = html.replace('</head>', '<style>' + NAV_CSS + '</style>\n</head>', 1)
    return html

# Group 1: Tailwind nav-container pages
for page in ['changebasis.html', 'elementary.html', 'inversematrix.html', 'lineareqn.html']:
    path = os.path.join(BASE, page)
    if not os.path.exists(path):
        print(f"  SKIP {page}")
        continue
    with open(path, 'r') as f:
        html = f.read()
    if has_main_nav(html):
        print(f"  SKIP {page} (done)")
        continue
    html = re.sub(
        r'<(?:div|header)\s+class="nav-container[^"]*"[^>]*>\s*<nav[^>]*>.*?</nav>\s*</(?:div|header)>',
        NAV_HTML, html, count=1, flags=re.DOTALL
    )
    html = add_css(html)
    with open(path, 'w') as f:
        f.write(html)
    print(f"  OK   {page}")

# Group 2: changebasisviz, svd2d (div wrapper with Tailwind nav)
for page in ['changebasisviz.html', 'svd2d.html']:
    path = os.path.join(BASE, page)
    if not os.path.exists(path):
        print(f"  SKIP {page}")
        continue
    with open(path, 'r') as f:
        html = f.read()
    if has_main_nav(html):
        print(f"  SKIP {page} (done)")
        continue
    html = re.sub(
        r'<!-- Nav -->\s*<div[^>]*>\s*<nav[^>]*>.*?</nav>\s*</div>',
        NAV_HTML, html, count=1, flags=re.DOTALL
    )
    html = add_css(html)
    with open(path, 'w') as f:
        f.write(html)
    print(f"  OK   {page}")

# Group 3: slopev1 (Tailwind fixed nav)
for page in ['slopev1.html']:
    path = os.path.join(BASE, page)
    if not os.path.exists(path):
        print(f"  SKIP {page}")
        continue
    with open(path, 'r') as f:
        html = f.read()
    if has_main_nav(html):
        print(f"  SKIP {page} (done)")
        continue
    html = re.sub(
        r'<nav\s+class="fixed\s+top-0[^"]*"[^>]*>.*?</nav>',
        NAV_HTML, html, count=1, flags=re.DOTALL
    )
    html = add_css(html)
    with open(path, 'w') as f:
        f.write(html)
    print(f"  OK   {page}")

# Group 4: corners.html, corners_v1.html (header with embedded nav)
for page in ['corners.html', 'corners_v1.html']:
    path = os.path.join(BASE, page)
    if not os.path.exists(path):
        print(f"  SKIP {page}")
        continue
    with open(path, 'r') as f:
        html = f.read()
    if has_main_nav(html):
        print(f"  SKIP {page} (done)")
        continue
    # Replace entire header block that contains nav
    html = re.sub(
        r'<!-- Header with navigation -->\s*<header[^>]*>.*?</header>',
        NAV_HTML, html, count=1, flags=re.DOTALL
    )
    html = add_css(html)
    with open(path, 'w') as f:
        f.write(html)
    print(f"  OK   {page}")

# Group 5: pend.html
for page in ['pend.html']:
    path = os.path.join(BASE, page)
    if not os.path.exists(path):
        print(f"  SKIP {page}")
        continue
    with open(path, 'r') as f:
        html = f.read()
    if has_main_nav(html):
        print(f"  SKIP {page} (done)")
        continue
    html = re.sub(
        r'<nav\s+class="flex[^"]*"[^>]*>.*?</nav>',
        NAV_HTML, html, count=1, flags=re.DOTALL
    )
    html = add_css(html)
    with open(path, 'w') as f:
        f.write(html)
    print(f"  OK   {page}")

print("\nDone.")
