#!/usr/bin/env python3
"""Generate label pages for math-tools site."""

import os, re

# All tools grouped by source page
# Each entry: (tool_name, tool_href, [tags], source_page_href, source_page_label)

tools = [
    # === projects.html (Diff Eq) ===
    ("Direction Field", "slope.html", ["First-Order", "Slope Field"], "projects.html", "Diff Eq"),
    ("Phase Line Plot", "phaseline.html", ["First-Order", "Autonomous", "Stability"], "projects.html", "Diff Eq"),
    ("Mass-Spring-Damping Simulator", "massspring.html", ["Second-Order", "Oscillations", "Damping"], "projects.html", "Diff Eq"),
    ("Multiple Degree of Freedom Mass Spring", "massspring-horizontal.html", ["Systems", "Normal Modes", "Coupled"], "projects.html", "Diff Eq"),
    ("Damped Pendulum Simulator", "pendulum_simulator.html", ["Second-Order", "Nonlinear", "Pendulum"], "projects.html", "Diff Eq"),
    ("Elastic (Spring) Pendulum", "elastic_pendulum.html", ["Nonlinear", "Coupled", "Lagrangian"], "projects.html", "Diff Eq"),
    ("Coupled Pendula with Spring", "coupled.html", ["Coupled", "Normal Modes", "Beats"], "projects.html", "Diff Eq"),
    ("Forced Vibrations and Resonance", "forcing.html", ["Second-Order", "Forced", "Resonance"], "projects.html", "Diff Eq"),
    ("Fourier Series Approximation", "fourier.html", ["Series", "Periodic", "Approximation"], "projects.html", "Diff Eq"),
    ("Laplace Transform Visualizer", "laplace.html", ["Integral Transforms", "Convergence", "Shifting Theorems"], "projects.html", "Diff Eq"),
    ("Convolution Visualizer", "convolution.html", ["Integral Transforms", "Flip & Slide", "Heaviside"], "projects.html", "Diff Eq"),
    ("Linear Phase Portraits", "linearportrait.html", ["Systems", "Eigenvalues", "Phase Plane"], "projects.html", "Diff Eq"),
    ("Nonlinear Phase Portraits", "nonlinearphaseportraits.html", ["Nonlinear", "Nullclines", "Vector Field"], "projects.html", "Diff Eq"),
    ("Lotka-Volterra Model", "lotkavolterra.html", ["Systems", "Ecology", "Predator-Prey"], "projects.html", "Diff Eq"),
    ("Lotka-Volterra with Carrying Capacity", "lvcarrying.html", ["Systems", "Logistic", "Ecology"], "projects.html", "Diff Eq"),
    ("Lorenz System", "lorenzsystem.html", ["Chaos", "3D", "Attractor"], "projects.html", "Diff Eq"),
    ("Multi-Pendulum Simulator", "multi_pendulum.html", ["Chaos", "Lagrangian", "Pendulum"], "projects.html", "Diff Eq"),
    ("Particle in a Cubic Potential", "potential.html", ["Potential", "Phase Space", "Nonlinear"], "projects.html", "Diff Eq"),
    ("Particle in a Double Well Potential", "double_potential.html", ["Potential", "Bistability", "Symmetric"], "projects.html", "Diff Eq"),
    ("Newton's Law of Cooling", "cooling.html", ["First-Order", "Heat Transfer", "Exponential Decay"], "projects.html", "Diff Eq"),
    ("Bifurcation Diagram", "bifurcation.html", ["Discrete Dynamics", "Period-Doubling", "Feigenbaum", "Chaos"], "projects.html", "Diff Eq"),
    ("Pendulum Wave", "pendulum-wave.html", ["Pendulum", "Wave Patterns", "Emergent Behavior", "3D View"], "projects.html", "Diff Eq"),

    # === linear.html (Linear Algebra) ===
    ("Geometry of Linear Systems", "geometry2d.html", ["Visualization", "Foundations"], "linear.html", "Linear Algebra"),
    ("2D Matrix Transformation Visualizer", "transformations2d.html", ["Visualization", "Transformations"], "linear.html", "Linear Algebra"),
    ("2D SVD Visualization", "svd2d.html", ["Visualization", "Decomposition"], "linear.html", "Linear Algebra"),
    ("Coordinate Transform Visualizer", "changebasisviz.html", ["Visualization", "Transformations"], "linear.html", "Linear Algebra"),
    ("Matrix Product", "prod.html", ["Foundations", "Computation"], "linear.html", "Linear Algebra"),
    ("Determinant and Trace", "determinants.html", ["Foundations", "Computation"], "linear.html", "Linear Algebra"),
    ("Reduced Row Echelon Form Solver (RREF)", "rrefsolver.html", ["Foundations", "Row Reduction"], "linear.html", "Linear Algebra"),
    ("Matrix Inverse", "inversematrix.html", ["Foundations", "Computation"], "linear.html", "Linear Algebra"),
    ("Elementary Matrices", "elementary.html", ["Foundations", "Row Reduction"], "linear.html", "Linear Algebra"),
    ("Row Echelon Form Solver (REF)", "refsolver.html", ["Foundations", "Row Reduction"], "linear.html", "Linear Algebra"),
    ("Change of Coordinates (Transition Matrix)", "changebasis.html", ["Transformations", "Computation"], "linear.html", "Linear Algebra"),
    ("Similarity Transforms", "lineartransform.html", ["Transformations", "Computation"], "linear.html", "Linear Algebra"),
    ("Gram-Schmidt Orthogonalization", "gramschmidtorthogonal.html", ["Foundations", "Computation"], "linear.html", "Linear Algebra"),
    ("Matrix Diagonalization", "diag.html", ["Eigenvalues", "Decomposition"], "linear.html", "Linear Algebra"),
    ("Cholesky Factorization", "choleskyfactors.html", ["Decomposition", "Factorization"], "linear.html", "Linear Algebra"),
    ("Four Fundamental Subspaces", "ffs.html", ["Foundations", "Subspaces"], "linear.html", "Linear Algebra"),
    ("A = CR Factorization", "cr.html", ["Decomposition", "Factorization"], "linear.html", "Linear Algebra"),
    ("Magic Factorization", "magicfactors.html", ["Decomposition", "Factorization"], "linear.html", "Linear Algebra"),
    ("Linear Equation Solver", "linearequation.html", ["Foundations", "Row Reduction"], "linear.html", "Linear Algebra"),
    ("Matrix Inverse or Pseudo-Inverse", "generalizedinverse.html", ["Foundations", "Computation"], "linear.html", "Linear Algebra"),
    ("PA = LU Factorization", "lufactor.html", ["Decomposition", "Factorization"], "linear.html", "Linear Algebra"),
    ("QR Factorization", "qrfactor.html", ["Decomposition", "Factorization"], "linear.html", "Linear Algebra"),
    ("Least Squares Solver using QR Factorization", "leastsquaresqr.html", ["Least Squares", "Decomposition"], "linear.html", "Linear Algebra"),
    ("Least Squares Solver using Normal Equations", "leastsquaresnormaleqns.html", ["Least Squares", "Computation"], "linear.html", "Linear Algebra"),
    ("Least Squares Solver using SVD", "leastsquaressvd.html", ["Least Squares", "Decomposition"], "linear.html", "Linear Algebra"),
    ("Eigenvalues and Eigenvectors", "eigenvalues-eigenvectors.html", ["Eigenvalues", "Computation"], "linear.html", "Linear Algebra"),
    ("Singular Value Decomposition (SVD)", "svdcompute.html", ["Decomposition", "Factorization"], "linear.html", "Linear Algebra"),

    # === numerical.html (Numerical Methods) ===
    ("Bisection Method", "bisection.html", ["Root Finding", "Bracketing"], "numerical.html", "Numerical Methods"),
    ("Newton's Method Visualizer", "newton.html", ["Root Finding", "Iterative"], "numerical.html", "Numerical Methods"),
    ("Fixed Point Iteration", "cobweb.html", ["Root Finding", "Fixed Points", "Iterative"], "numerical.html", "Numerical Methods"),
    ("Polynomial Interpolation", "interpolation.html", ["Interpolation", "Polynomial"], "numerical.html", "Numerical Methods"),
    ("Polynomial Least Squares Data Fitting", "leastsquaresdata.html", ["Least Squares", "Data Fitting"], "numerical.html", "Numerical Methods"),
    ("Rational Function Least Squares Data Fitting", "leastsquaresrational.html", ["Least Squares", "Rational Function"], "numerical.html", "Numerical Methods"),
    ("Finite Difference Generator", "finitediff.html", ["Finite Differences", "Derivatives"], "numerical.html", "Numerical Methods"),

    # === optim.html (Linear Programming) ===
    ("Method of Corners (Graphical Method)", "corners.html", ["Graphical", "Feasible Region", "Optimization"], "optim.html", "Linear Programming"),

    # === pdftools.html (PDF Tools) ===
    ("PDF & Image Merger", "pdf_manager.html", ["Merge", "Images"], "pdftools.html", "PDF Tools"),
    ("PDF Organizer", "pdf_sort.html", ["Reorder", "Delete"], "pdftools.html", "PDF Tools"),
    ("PDF Darken", "pdf_dark.html", ["Enhance", "Scans"], "pdftools.html", "PDF Tools"),
    ("Office to PDF Viewer", "office2pdf.html", ["DOCX", "XLSX"], "pdftools.html", "PDF Tools"),
]

# Build label -> tools mapping
from collections import OrderedDict
label_tools = {}
for name, href, tags, source_href, source_label in tools:
    for tag in tags:
        if tag not in label_tools:
            label_tools[tag] = []
        label_tools[tag].append((name, href, source_href, source_label))

def slug(label):
    """Convert label to filename-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def generate_page(label, tool_list):
    n = len(tool_list)
    tool_cards = []
    for i, (name, href, source_href, source_label) in enumerate(tool_list, 1):
        tool_cards.append(f'''
        <article class="tool-card" aria-labelledby="card-{i}">
          <span class="card-num" aria-hidden="true">Tool {i} of {n}</span>
          <h2 id="card-{i}">{escape(name)}</h2>
          <p class="card-source">From <a href="../{source_href}">{escape(source_label)}</a></p>
          <a href="../{href}" class="card-link">Open Tool <span aria-hidden="true">&rarr;</span></a>
        </article>''')

    cards_html = '\n'.join(tool_cards)
    title = f'Tools tagged &ldquo;{escape(label)}&rdquo;'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="All interactive math tools tagged {escape(label)}.">
  <title>{escape(label)} — Label — Math Tools</title>

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-LEQE004C92"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-LEQE004C92');
  </script>

  <style>
    :root {{
      --bg-page: #f3f4f6;
      --bg-card: #ffffff;
      --bg-section: #f9fafb;
      --text-primary: #1f2937;
      --text-secondary: #4b5563;
      --text-muted: #6b7280;
      --border-color: #d1d5db;
      --border-focus: #3b82f6;
      --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
      --shadow-lg: 0 4px 6px rgba(0,0,0,0.1);
      --btn-primary-bg: #4338ca;
      --btn-primary-hover: #3730a3;
      --link-color: #4338ca;
      --link-hover: #3730a3;
      --skip-bg: #2563eb;
      --card-hover-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
      --tag-bg: #eef2ff;
      --tag-text: #3730a3;
      --tag-border: #c7d2fe;
    }}

    @media (prefers-contrast: more) {{
      :root {{
        --bg-page: #ffffff; --bg-card: #ffffff; --bg-section: #f0f0f0;
        --text-primary: #000000; --text-secondary: #000000; --text-muted: #333333;
        --border-color: #000000; --border-focus: #0000ff;
        --shadow: 0 0 0 2px #000; --shadow-lg: 0 0 0 3px #000;
        --btn-primary-bg: #0000cc; --btn-primary-hover: #000099;
        --link-color: #0000cc; --link-hover: #000099;
        --card-hover-shadow: 0 0 0 3px #000;
        --tag-bg: #e0e0ff; --tag-text: #000066; --tag-border: #000099;
      }}
    }}

    .high-contrast {{
      --bg-page: #ffffff; --bg-card: #ffffff; --bg-section: #f0f0f0;
      --text-primary: #000000; --text-secondary: #000000; --text-muted: #333333;
      --border-color: #000000; --border-focus: #0000ff;
      --shadow: 0 0 0 2px #000; --shadow-lg: 0 0 0 3px #000;
      --btn-primary-bg: #0000cc; --btn-primary-hover: #000099;
      --link-color: #0000cc; --link-hover: #000099;
      --card-hover-shadow: 0 0 0 3px #000;
      --tag-bg: #e0e0ff; --tag-text: #000066; --tag-border: #000099;
    }}

    .skip-link {{
      position: absolute; top: -100%; left: 50%; transform: translateX(-50%);
      background: var(--skip-bg); color: #fff; padding: 0.75rem 1.5rem;
      z-index: 1000; border-radius: 0 0 0.5rem 0.5rem; font-weight: 600; text-decoration: none;
    }}
    .skip-link:focus {{ top: 0; outline: 3px solid #000; outline-offset: 2px; }}

    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background-color: var(--bg-page); color: var(--text-primary);
      margin: 0; padding: 0; min-height: 100vh; line-height: 1.6;
    }}
    *:focus-visible {{ outline: 3px solid var(--border-focus); outline-offset: 2px; }}
    .sr-only {{
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
    }}

    .main-nav {{
      position: sticky; top: 0; left: 0; width: 100%; z-index: 20;
      background: var(--bg-card); box-shadow: var(--shadow);
    }}
    .nav-inner {{ max-width: 72rem; margin: 0 auto; padding: 0.5rem 1rem; }}
    .nav-list {{
      list-style: none; display: flex; justify-content: center; gap: 1rem;
      margin: 0; padding: 0; flex-wrap: wrap;
    }}
    .nav-list a {{
      color: var(--link-color); text-decoration: none; font-weight: 700;
      font-size: 1.15rem; padding: 0.25rem 0.5rem; border-radius: 0.25rem;
    }}
    .nav-list a:hover, .nav-list a:focus-visible {{ color: var(--link-hover); text-decoration: underline; }}
    .nav-list a[aria-current="page"] {{
      background: var(--tag-bg); border-bottom: 3px solid var(--link-color);
    }}

    .page-header {{
      text-align: center; max-width: 72rem; margin: 0 auto; padding: 2.5rem 1rem 1rem;
    }}
    .page-header h1 {{
      font-size: 2rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.5rem;
    }}
    .page-header .subtitle {{
      font-size: 1.1rem; color: var(--text-secondary); max-width: 48rem;
      margin: 0 auto 1.5rem; line-height: 1.7;
    }}
    .label-badge {{
      display: inline-block; font-size: 1rem; font-weight: 600;
      background: var(--tag-bg); color: var(--tag-text);
      border: 1px solid var(--tag-border);
      padding: 0.25rem 0.75rem; border-radius: 1rem; margin-bottom: 0.75rem;
    }}

    .card-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
      gap: 1.5rem; max-width: 72rem; margin: 0 auto; padding: 0 1rem 3rem;
    }}

    .tool-card {{
      background: var(--bg-card); border: 1px solid var(--border-color);
      border-radius: 0.75rem; box-shadow: var(--shadow); padding: 1.5rem;
      display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s;
    }}
    .tool-card:hover {{ transform: translateY(-4px); box-shadow: var(--card-hover-shadow); }}
    .tool-card h2 {{
      font-size: 1.25rem; font-weight: 700; color: var(--text-primary);
      margin: 0 0 0.5rem; line-height: 1.3;
    }}
    .card-num {{
      display: inline-block; font-size: 0.72rem; font-weight: 700;
      color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.3rem;
    }}
    .card-source {{
      color: var(--text-secondary); font-size: 0.9rem; margin: 0 0 1rem; flex-grow: 1;
    }}
    .card-source a {{ color: var(--link-color); font-weight: 600; }}
    .card-source a:hover {{ color: var(--link-hover); }}
    .tool-card .card-link {{
      display: inline-flex; align-items: center; justify-content: center;
      background: var(--btn-primary-bg); color: #fff;
      padding: 0.6rem 1.25rem; border-radius: 0.5rem;
      text-decoration: none; font-weight: 600; font-size: 0.95rem;
      min-height: 44px; min-width: 44px;
      transition: background-color 0.15s, transform 0.1s;
      align-self: flex-start;
    }}
    .tool-card .card-link:hover, .tool-card .card-link:focus-visible {{
      background: var(--btn-primary-hover); transform: translateY(-1px);
    }}
    .tool-card .card-link:active {{ transform: translateY(0); }}

    .contrast-toggle {{
      position: fixed; bottom: 1rem; right: 1rem; z-index: 20;
      background: var(--text-primary); color: var(--bg-card);
      border: 2px solid var(--border-color); border-radius: 50%;
      width: 48px; height: 48px; font-size: 1.25rem; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      box-shadow: var(--shadow-lg);
    }}
    .contrast-toggle:focus-visible {{ outline: 3px solid var(--border-focus); outline-offset: 2px; }}

    .site-footer {{
      max-width: 72rem; margin: 0 auto; border-top: 1px solid var(--border-color);
      padding: 1.5rem 1rem; text-align: center; color: var(--text-secondary);
      font-size: 0.85rem; line-height: 1.7;
    }}
    .site-footer a {{ color: var(--link-color); }}
    .site-footer a:hover {{ color: var(--link-hover); }}

    @media (max-width: 640px) {{
      .page-header h1 {{ font-size: 1.5rem; }}
      .page-header .subtitle {{ font-size: 1rem; }}
      .card-grid {{ grid-template-columns: 1fr; padding: 0 0.75rem 2rem; }}
      .tool-card {{ padding: 1.25rem; }}
      .nav-list {{ gap: 0.5rem; }}
      .nav-list a {{ font-size: 0.95rem; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .tool-card {{ transition: none; }}
      .tool-card:hover {{ transform: none; }}
      .tool-card .card-link {{ transition: none; }}
      .tool-card .card-link:hover {{ transform: none; }}
    }}
  </style>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <div id="liveRegion" class="sr-only" aria-live="polite" aria-atomic="true"></div>

  <nav class="main-nav" aria-label="Main navigation">
    <div class="nav-inner">
      <ul class="nav-list" role="list">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../teaching.html">Teaching</a></li>
        <li><a href="../projects.html">Diff Eq</a></li>
        <li><a href="../linear.html">Linear Algebra</a></li>
        <li><a href="../optim.html">Linear Programming</a></li>
        <li><a href="../numerical.html">Numerical Methods</a></li>
      </ul>
    </div>
  </nav>

  <main id="main-content">
    <header class="page-header">
      <span class="label-badge">{escape(label)}</span>
      <h1>{title}</h1>
      <p class="subtitle">{n} tool{"s" if n != 1 else ""} with this label.</p>
    </header>

    <section aria-label="Tools tagged {escape(label)}">
      <h2 class="sr-only">Tool List</h2>
      <div class="card-grid">{cards_html}
      </div>
    </section>
  </main>

  <footer class="site-footer" role="contentinfo">
    &copy; Shelvean Kapita. All code released under the MIT License.<br>
    <strong>Accessibility:</strong> This page is designed to meet
    <a href="https://www.w3.org/TR/WCAG21/">WCAG 2.1 AA</a> standards.
    If you encounter any accessibility issues, please contact
    <a href="mailto:kapita@tamu.edu">kapita@tamu.edu</a>.
  </footer>

  <button class="contrast-toggle" id="contrastToggle" aria-label="Toggle high-contrast mode" title="Toggle high-contrast mode" type="button">
    <span aria-hidden="true">&#9681;</span>
  </button>

  <script>
    function announce(msg) {{
      var el = document.getElementById('liveRegion');
      el.textContent = '';
      setTimeout(function() {{ el.textContent = msg; }}, 50);
    }}
    document.getElementById('contrastToggle').addEventListener('click', function() {{
      document.documentElement.classList.toggle('high-contrast');
      var on = document.documentElement.classList.contains('high-contrast');
      announce('High contrast mode ' + (on ? 'enabled' : 'disabled'));
    }});
  </script>
</body>
</html>'''


# Generate all label pages
outdir = '/home/user/math-tools/labels'
generated = []
for label, tool_list in sorted(label_tools.items()):
    filename = slug(label) + '.html'
    filepath = os.path.join(outdir, filename)
    html = generate_page(label, tool_list)
    with open(filepath, 'w') as f:
        f.write(html)
    generated.append((label, filename, len(tool_list)))
    print(f"  {filename:40s}  {label:25s}  ({len(tool_list)} tools)")

print(f"\nGenerated {len(generated)} label pages in {outdir}/")
