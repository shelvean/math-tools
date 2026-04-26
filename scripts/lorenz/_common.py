"""Shared Lorenz-system helpers used by every example in this directory.

Reproduces figures from Strogatz, *Nonlinear Dynamics and Chaos* (2nd ed.),
Chapter 9.  All examples integrate

    x' = sigma (y - x)
    y' = r x - y - x z
    z' = x y - b z

with sigma = 10, b = 8/3 held fixed; only r varies between examples.

Integration uses scipy's RK45 (Dormand-Prince 5(4) embedded pair) with
rtol = atol = 1e-9 -- the value Strogatz cites in Section 9.3 as the
threshold below which the attractor is visibly distorted.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

SIGMA = 10.0
B = 8.0 / 3.0

R_PITCHFORK = 1.0
R_HOPF = SIGMA * (SIGMA + B + 3.0) / (SIGMA - B - 1.0)  # 470/19 ~= 24.7368

IC_NEAR_ORIGIN = (0.0, 1.0, 0.0)
IC_SPARROW = (0.0, 1.0, 1.05)


@dataclass(frozen=True)
class LorenzSolution:
    t: np.ndarray
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    r: float
    sigma: float
    b: float
    ic: tuple[float, float, float]


def rhs(t: float, state: np.ndarray, sigma: float, r: float, b: float) -> np.ndarray:
    x, y, z = state
    return np.array([sigma * (y - x), r * x - y - x * z, x * y - b * z])


def fixed_points(r: float, b: float = B) -> tuple[np.ndarray, np.ndarray | None, np.ndarray | None]:
    origin = np.zeros(3)
    if r <= 1.0:
        return origin, None, None
    s = np.sqrt(b * (r - 1.0))
    cplus = np.array([s, s, r - 1.0])
    cminus = np.array([-s, -s, r - 1.0])
    return origin, cplus, cminus


def integrate(
    r: float,
    ic: tuple[float, float, float],
    t_end: float,
    *,
    sigma: float = SIGMA,
    b: float = B,
    n_samples: int = 20000,
    rtol: float = 1e-9,
    atol: float = 1e-9,
    t_start: float = 0.0,
) -> LorenzSolution:
    """Integrate with Dormand-Prince 5(4) on a dense uniform output grid."""
    t_eval = np.linspace(t_start, t_end, n_samples)
    sol = solve_ivp(
        rhs,
        (t_start, t_end),
        ic,
        method="RK45",
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        args=(sigma, r, b),
    )
    if not sol.success:
        raise RuntimeError(f"integration failed: {sol.message}")
    return LorenzSolution(
        t=sol.t, x=sol.y[0], y=sol.y[1], z=sol.y[2],
        r=r, sigma=sigma, b=b, ic=tuple(ic),
    )


def successive_z_maxima(t: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Local maxima of z(t) by finite difference -- used for the Lorenz map."""
    interior = np.arange(1, len(z) - 1)
    is_max = (z[interior] > z[interior - 1]) & (z[interior] > z[interior + 1])
    return z[interior][is_max]
