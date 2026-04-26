"""Sensitive dependence on initial conditions (the "butterfly effect").

Two trajectories at r = 28, both starting from IC = (0, 1, 1.05) but with
the second offset by 1e-8 in x.  We plot |delta(t)| on a log scale; the
slope where sep is in the exponential-growth regime (after the initial
alignment transient, before saturation at attractor scale) estimates the
largest Lyapunov exponent.  Strogatz quotes lambda_max ~= 0.9 in
Section 9.3.

Tolerances are tightened to 1e-13 so the integrator can resolve
separations several orders of magnitude below the seed offset.
"""

import numpy as np
import matplotlib.pyplot as plt

from _common import IC_SPARROW, integrate

R = 28.0
T_END = 25.0
DELTA = 1e-8


def main() -> None:
    ic_a = IC_SPARROW
    ic_b = (IC_SPARROW[0] + DELTA, IC_SPARROW[1], IC_SPARROW[2])

    a = integrate(R, ic_a, T_END, n_samples=25000, rtol=1e-13, atol=1e-13)
    b = integrate(R, ic_b, T_END, n_samples=25000, rtol=1e-13, atol=1e-13)

    sep = np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
    sep = np.maximum(sep, 1e-18)

    # Fit window: skip the initial transient where the perturbation is
    # still aligning with the unstable manifold (sep oscillates near
    # DELTA), and stop before saturation at attractor scale.  For
    # DELTA = 1e-8 the clean exponential band sits roughly at t in [10, 22].
    growth_window = (a.t >= 10.0) & (a.t <= 22.0)
    slope, intercept = np.polyfit(a.t[growth_window], np.log(sep[growth_window]), 1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogy(a.t, sep, lw=0.7, label=f"|delta(t)|, initial offset {DELTA:.0e}")
    ax.semilogy(
        a.t[growth_window],
        np.exp(intercept + slope * a.t[growth_window]),
        "r--", lw=1.2, label=f"fit: slope = {slope:.3f}",
    )
    ax.set_xlabel("t")
    ax.set_ylabel("separation")
    ax.set_title(f"Sensitive dependence at r = {R}")
    ax.legend()
    ax.grid(alpha=0.3, which="both")

    fig.tight_layout()
    out = "sensitive_dependence.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}; estimated largest Lyapunov exponent ~= {slope:.3f}")


if __name__ == "__main__":
    main()
