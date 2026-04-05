#!/usr/bin/env python3
"""Add standard navigation bar to pages that don't have one."""
import re, os

BASE = '/home/user/math-tools'

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

NAV_HTML = """<nav class="main-nav" aria-label="Main navigation">
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
</nav>
"""

PAGES_WITHOUT_NAV = [
    'cooling.html',
    'cv.html',
    'nonlinear.html',
    'office2pdf.html',
    'pdf_dark.html',
    'pdf_manager.html',
    'pdf_sort.html',
    'plotfunction.html',
    'timer.html',
    'gradecalc.html',
    'epl.html',
    'mathjs.html',
]

for page in PAGES_WITHOUT_NAV:
    path = os.path.join(BASE, page)
    if not os.path.exists(path):
        print(f"  SKIP {page} (not found)")
        continue

    with open(path, 'r') as f:
        html = f.read()

    # Skip if already has nav
    if 'class="main-nav"' in html or 'class="nav"' in html:
        print(f"  SKIP {page} (already has nav)")
        continue

    # 1. Inject CSS: before </style> if exists, otherwise before </head>
    if '</style>' in html:
        html = html.replace('</style>', NAV_CSS + '</style>', 1)
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + NAV_CSS + '</style>\n</head>', 1)

    # 2. Inject nav HTML right after <body...>
    body_match = re.search(r'<body[^>]*>', html)
    if body_match:
        insert_pos = body_match.end()
        html = html[:insert_pos] + '\n' + NAV_HTML + html[insert_pos:]

    with open(path, 'w') as f:
        f.write(html)
    print(f"  OK   {page}")

print("\nDone.")
