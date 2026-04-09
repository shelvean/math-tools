#!/usr/bin/env python3
"""Add 'Back to [Category]' link to all tool pages that don't have one."""
import re, os

BASE = '/home/user/math-tools'

# Map: tool filename -> (parent_href, parent_label)
TOOL_MAP = {
    # Diff Eq tools -> projects.html
    'slope.html': ('projects.html', 'Differential Equations'),
    'phaseline.html': ('projects.html', 'Differential Equations'),
    'massspring.html': ('projects.html', 'Differential Equations'),
    'massspring-horizontal.html': ('projects.html', 'Differential Equations'),
    'pendulum_simulator.html': ('projects.html', 'Differential Equations'),
    'elastic_pendulum.html': ('projects.html', 'Differential Equations'),
    'coupled.html': ('projects.html', 'Differential Equations'),
    'forcing.html': ('projects.html', 'Differential Equations'),
    'fourier.html': ('projects.html', 'Differential Equations'),
    'laplace.html': ('projects.html', 'Differential Equations'),
    'convolution.html': ('projects.html', 'Differential Equations'),
    'linearportrait.html': ('projects.html', 'Differential Equations'),
    'nonlinearphaseportraits.html': ('projects.html', 'Differential Equations'),
    'lotkavolterra.html': ('projects.html', 'Differential Equations'),
    'lvcarrying.html': ('projects.html', 'Differential Equations'),
    'lorenzsystem.html': ('projects.html', 'Differential Equations'),
    'multi_pendulum.html': ('projects.html', 'Differential Equations'),
    'potential.html': ('projects.html', 'Differential Equations'),
    'double_potential.html': ('projects.html', 'Differential Equations'),
    'cooling.html': ('projects.html', 'Differential Equations'),
    'bifurcation.html': ('projects.html', 'Differential Equations'),
    'pendulum_wave.html': ('projects.html', 'Differential Equations'),
    'pend.html': ('projects.html', 'Differential Equations'),
    'slopev1.html': ('projects.html', 'Differential Equations'),

    # Linear Algebra tools -> linear.html
    'geometry2d.html': ('linear.html', 'Linear Algebra'),
    'transformations2d.html': ('linear.html', 'Linear Algebra'),
    'svd2d.html': ('linear.html', 'Linear Algebra'),
    'changebasisviz.html': ('linear.html', 'Linear Algebra'),
    'prod.html': ('linear.html', 'Linear Algebra'),
    'determinants.html': ('linear.html', 'Linear Algebra'),
    'rrefsolver.html': ('linear.html', 'Linear Algebra'),
    'inversematrix.html': ('linear.html', 'Linear Algebra'),
    'elementary.html': ('linear.html', 'Linear Algebra'),
    'refsolver.html': ('linear.html', 'Linear Algebra'),
    'changebasis.html': ('linear.html', 'Linear Algebra'),
    'lineartransform.html': ('linear.html', 'Linear Algebra'),
    'gramschmidtorthogonal.html': ('linear.html', 'Linear Algebra'),
    'diag.html': ('linear.html', 'Linear Algebra'),
    'choleskyfactors.html': ('linear.html', 'Linear Algebra'),
    'ffs.html': ('linear.html', 'Linear Algebra'),
    'cr.html': ('linear.html', 'Linear Algebra'),
    'magicfactors.html': ('linear.html', 'Linear Algebra'),
    'linearequation.html': ('linear.html', 'Linear Algebra'),
    'lineareqn.html': ('linear.html', 'Linear Algebra'),
    'generalizedinverse.html': ('linear.html', 'Linear Algebra'),
    'lufactor.html': ('linear.html', 'Linear Algebra'),
    'qrfactor.html': ('linear.html', 'Linear Algebra'),
    'leastsquaresqr.html': ('linear.html', 'Linear Algebra'),
    'leastsquaresnormaleqns.html': ('linear.html', 'Linear Algebra'),
    'leastsquaressvd.html': ('linear.html', 'Linear Algebra'),
    'eigenvalues-eigenvectors.html': ('linear.html', 'Linear Algebra'),
    'svdcompute.html': ('linear.html', 'Linear Algebra'),
    'rref.html': ('linear.html', 'Linear Algebra'),
    'nonlinear.html': ('linear.html', 'Linear Algebra'),
    'epl.html': ('linear.html', 'Linear Algebra'),

    # Numerical Methods tools -> numerical.html
    'bisection.html': ('numerical.html', 'Numerical Methods'),
    'newton.html': ('numerical.html', 'Numerical Methods'),
    'cobweb.html': ('numerical.html', 'Numerical Methods'),
    'interpolation.html': ('numerical.html', 'Numerical Methods'),
    'leastsquaresdata.html': ('numerical.html', 'Numerical Methods'),
    'leastsquaresrational.html': ('numerical.html', 'Numerical Methods'),
    'finitediff.html': ('numerical.html', 'Numerical Methods'),
    'plotfunction.html': ('numerical.html', 'Numerical Methods'),

    # Linear Programming tools -> optim.html
    'corners.html': ('optim.html', 'Linear Programming'),
    'corners_v1.html': ('optim.html', 'Linear Programming'),

    # PDF tools -> pdftools.html
    'pdf_manager.html': ('pdftools.html', 'PDF Tools'),
    'pdf_sort.html': ('pdftools.html', 'PDF Tools'),
    'pdf_dark.html': ('pdftools.html', 'PDF Tools'),
    'office2pdf.html': ('pdftools.html', 'PDF Tools'),
}

# CSS for back link (self-contained)
BACK_CSS = """
/* ===== Back link ===== */
.back-link{display:inline-flex;align-items:center;gap:6px;font-size:.85rem;font-weight:500;
  color:#4338ca;text-decoration:none;margin:0.5rem 0 0.5rem 1rem;transition:transform .2s;}
.back-link:hover{transform:translateX(-3px);color:#3730a3;}
"""

count = 0
for filename, (parent_href, parent_label) in TOOL_MAP.items():
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        print(f"  SKIP {filename} (not found)")
        continue

    with open(path, 'r') as f:
        html = f.read()

    # Skip if already has a back-link
    if 'class="back-link"' in html:
        print(f"  SKIP {filename} (already has back link)")
        continue

    back_html = f'<a href="{parent_href}" class="back-link" aria-label="Back to {parent_label}">&larr; Back to {parent_label}</a>\n'

    # Strategy: insert after the closing </nav> tag
    nav_end = html.find('</nav>')
    if nav_end >= 0:
        insert_pos = nav_end + len('</nav>')
        # Skip any whitespace
        while insert_pos < len(html) and html[insert_pos] in '\n\r':
            insert_pos += 1
        html = html[:insert_pos] + '\n' + back_html + html[insert_pos:]
    else:
        # Fallback: insert after <body>
        body_match = re.search(r'<body[^>]*>', html)
        if body_match:
            insert_pos = body_match.end()
            html = html[:insert_pos] + '\n' + back_html + html[insert_pos:]
        else:
            print(f"  FAIL {filename} (no nav or body tag)")
            continue

    # Add CSS if not present
    if 'back-link' not in html.split('</nav>')[0] or True:  # CSS might be needed
        if '</style>' in html:
            # Add before last </style>
            idx = html.rfind('</style>')
            html = html[:idx] + BACK_CSS + html[idx:]
        else:
            html = html.replace('</head>', '<style>' + BACK_CSS + '</style>\n</head>', 1)

    with open(path, 'w') as f:
        f.write(html)
    count += 1
    print(f"  OK   {filename} -> {parent_label}")

print(f"\nDone. Added back links to {count} pages.")
