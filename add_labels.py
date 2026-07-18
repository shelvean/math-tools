#!/usr/bin/env python3
"""Add new labels to tool cards across all hub pages, then regenerate label pages."""
import re, os

def slug(label):
    label = label.replace('&amp;', '&')
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')

def tag_html(label):
    s = slug(label)
    esc = label.replace('&', '&amp;')
    return f'<a href="labels/{s}.html" class="tag">{esc}</a>'

def add_tags_after(html, existing_tag_text, new_labels, filepath):
    """Find a card-tags div containing existing_tag_text and append new tag links."""
    # Find the card-tags div that contains the existing_tag_text
    pattern = re.compile(
        r'(<div class="card-tags"[^>]*>)(.*?' + re.escape(existing_tag_text) + r'.*?)(</div>)',
        re.DOTALL
    )
    m = pattern.search(html)
    if not m:
        print(f"  WARNING: Could not find '{existing_tag_text}' in {filepath}")
        return html

    opening = m.group(1)
    content = m.group(2)
    closing = m.group(3)

    # Build new tag links
    new_tags = ''
    for label in new_labels:
        t = tag_html(label)
        if t not in content:  # Don't add duplicates
            # Check if content ends with newline/whitespace pattern
            if '\n' in content:
                new_tags += '\n            ' + t
            else:
                new_tags += t

    replacement = opening + content + new_tags + closing
    html = html[:m.start()] + replacement + html[m.end():]
    return html

# ============================================================
# PROJECTS.HTML — Differential Equations
# ============================================================
projects_additions = [
    # (unique text to find the right card-tags div, [new labels to add])
    # 1. Direction Field — add Vector Field, Visualization
    ("Slope Field", ["Vector Field", "Visualization"]),
    # 2. Phase Line Plot — add Fixed Points
    ("Autonomous", ["Fixed Points"]),
    # 3. Mass-Spring-Damping — add Phase Plane
    ("Damping</a>", ["Phase Plane"]),
    # 4. Multiple DOF Mass Spring — add Oscillations, Second-Order
    ("Normal Modes", ["Oscillations", "Second-Order"]),
    # 5. Damped Pendulum — add Damping, Phase Plane
    ('>Nonlinear</a><a href="labels/pendulum.html"', ["Damping", "Phase Plane"]),
    # 6. Elastic Pendulum — add Pendulum, Resonance
    ("Lagrangian</a>", ["Pendulum", "Resonance"]),
    # 7. Coupled Pendula — add Pendulum
    ("Beats</a>", ["Pendulum"]),
    # 8. Forced Vibrations — add Oscillations, Damping
    ("Resonance</a>", ["Oscillations", "Damping"]),
    # 9. Fourier Series — add Convergence
    ("Approximation</a>", ["Convergence"]),
    # 10. Linear Phase Portraits — add Stability, Vector Field
    ("Phase Plane</a>", ["Stability", "Vector Field"]),
    # 11. Nonlinear Phase Portraits — add Systems, Phase Plane, Autonomous, Fixed Points, Stability
    ("Nullclines", ["Systems", "Phase Plane", "Autonomous", "Fixed Points", "Stability"]),
    # 12. Lotka-Volterra — add Nonlinear, Phase Plane
    ("Predator-Prey</a>", ["Nonlinear", "Phase Plane"]),
    # 13. LV + Carrying Capacity — add Nonlinear, Predator-Prey, Stability
    ("Logistic", ["Nonlinear", "Predator-Prey", "Stability"]),
    # 14. Lorenz System — add Systems, Nonlinear
    ("Attractor</a>", ["Systems", "Nonlinear"]),
    # 15. Multi-Pendulum — add Nonlinear
    ('>Chaos</a><a href="labels/lagrangian.html"', ["Nonlinear"]),
    # 16. Cubic Potential — add Second-Order
    ('>Potential</a><a href="labels/phase-space.html"', ["Second-Order"]),
    # 17. Double Well Potential — add Nonlinear, Phase Space, Second-Order
    ("Bistability", ["Nonlinear", "Phase Space", "Second-Order"]),
    # 18. Newton's Cooling — add Autonomous
    ("Exponential Decay</a>", ["Autonomous"]),
    # 19. Bifurcation — add Stability, Nonlinear
    ("Feigenbaum", ["Stability", "Nonlinear"]),
    # 20. Pendulum Phase Array — add Oscillations
    ("Emergent Behavior", ["Oscillations"]),
]

# ============================================================
# LINEAR.HTML — Linear Algebra
# ============================================================
linear_additions = [
    # 2. 2D Matrix Transform — add Decomposition
    ('>Visualization</a>\n            <a href="labels/transformations.html" class="tag">Transformations</a>', ["Decomposition"]),
    # 3. 2D SVD — add Factorization
    ('>Visualization</a>\n            <a href="labels/decomposition.html"', ["Factorization"]),
    # 6. Determinant and Trace — add Eigenvalues
    ("card-determinants", ["Eigenvalues"]),
    # 7. RREF — add Computation
    ("card-rrefsolver", ["Computation"]),
    # 8. Matrix Inverse — add Row Reduction
    ("card-inversematrix", ["Row Reduction"]),
    # 10. REF — add Computation
    ("card-refsolver", ["Computation"]),
    # 12. Similarity Transforms — add Eigenvalues
    ("card-lineartransform", ["Eigenvalues"]),
    # 14. Diagonalization — add Factorization
    ("card-diag", ["Factorization"]),
    # 16. Four Fundamental Subspaces — add Row Reduction
    ("card-ffs", ["Row Reduction"]),
    # 19. Linear Equation Solver — add Computation
    ("card-lineareq", ["Computation"]),
    # 20. Pseudo-Inverse — add Least Squares
    ("card-geninverse", ["Least Squares"]),
    # 21. LU — add Row Reduction
    ("card-lu", ["Row Reduction"]),
    # 23. LS via QR — add Factorization
    ("card-lsqr", ["Factorization"]),
    # 25. LS via SVD — add Factorization
    ("card-lssvd", ["Factorization"]),
    # 26. Eigenvalues — add Foundations
    ("card-eigen", ["Foundations"]),
]

# ============================================================
# NUMERICAL.HTML — Numerical Methods
# ============================================================
numerical_additions = [
    # 1. Bisection — add Convergence
    ("Bracketing", ["Convergence"]),
    # 2. Newton's Method — add Convergence
    ('>Root Finding</a>\n            <a href="labels/iterative.html" class="tag">Iterative</a>', ["Convergence"]),
    # 3. Fixed Point Iteration — add Convergence, Discrete Dynamics, Chaos
    ("Fixed Points", ["Convergence", "Discrete Dynamics", "Chaos"]),
    # 4. Polynomial Interpolation — add Approximation
    ('>Polynomial</a>', ["Approximation"]),
    # 5. Polynomial LS Data Fitting — add Polynomial, Approximation
    ('>Data Fitting</a>', ["Polynomial", "Approximation"]),
    # 6. Rational Function LS — add Data Fitting, Approximation
    ("Rational Function</a>", ["Data Fitting", "Approximation"]),
    # 7. Finite Differences — add Approximation
    ("Derivatives</a>", ["Approximation"]),
]

# ============================================================
# OPTIM.HTML — Linear Programming
# ============================================================
optim_additions = [
    # 1. Method of Corners — add Visualization
    ("Optimization</a>", ["Visualization"]),
]

def process_file_simple(filepath, additions):
    """For linear.html, use aria-labelledby IDs to find the right card."""
    with open(filepath, 'r') as f:
        html = f.read()

    for marker, new_labels in additions:
        if marker.startswith('card-'):
            # Find by card ID — locate the card-tags div within this article
            # Find the article with this labelledby, then find its card-tags div
            art_pattern = re.compile(
                r'(aria-labelledby="' + re.escape(marker) + r'".*?<div class="card-tags"[^>]*>)(.*?)(</div>)',
                re.DOTALL
            )
            m = art_pattern.search(html)
            if not m:
                print(f"  WARNING: Could not find card '{marker}' in {filepath}")
                continue
            content = m.group(2)
            new_tags = ''
            for label in new_labels:
                t = '\n            ' + tag_html(label)
                if tag_html(label) not in content:
                    new_tags += t
            html = html[:m.start()] + m.group(1) + content + new_tags + '\n          ' + m.group(3) + html[m.end():]
        else:
            html = add_tags_after(html, marker, new_labels, filepath)

    with open(filepath, 'w') as f:
        f.write(html)
    print(f"Updated {filepath}")

def process_file(filepath, additions):
    with open(filepath, 'r') as f:
        html = f.read()

    for marker, new_labels in additions:
        html = add_tags_after(html, marker, new_labels, filepath)

    with open(filepath, 'w') as f:
        f.write(html)
    print(f"Updated {filepath}")

base = '/home/user/math-tools'

process_file(os.path.join(base, 'projects.html'), projects_additions)
process_file_simple(os.path.join(base, 'linear.html'), linear_additions)
process_file(os.path.join(base, 'numerical.html'), numerical_additions)
process_file(os.path.join(base, 'optim.html'), optim_additions)

print("\nDone adding labels to hub pages.")
