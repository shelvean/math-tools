"""Strogatz Fig. 9.4.2 -- the Lorenz map z_{n+1} vs z_n.

Successive local maxima of z(t) on the attractor lie almost perfectly on
a one-dimensional tent-like curve.  This is the empirical observation
that motivated Lorenz's geometric reduction of the attractor's dynamics
to a 1D map.
"""

import matplotlib.pyplot as plt

from _common import IC_SPARROW, integrate, successive_z_maxima

R = 28.0
T_END = 200.0
T_DISCARD = 20.0


def main() -> None:
    sol = integrate(R, IC_SPARROW, T_END, n_samples=200000)

    keep = sol.t >= T_DISCARD
    maxima = successive_z_maxima(sol.t[keep], sol.z[keep])
    z_n, z_np1 = maxima[:-1], maxima[1:]

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.scatter(z_n, z_np1, s=4, alpha=0.6)
    lo = min(z_n.min(), z_np1.min())
    hi = max(z_n.max(), z_np1.max())
    ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, label="z_{n+1} = z_n")
    ax.set_xlabel("z_n")
    ax.set_ylabel("z_{n+1}")
    ax.set_title(f"Lorenz return map, r = {R}, {len(z_n)} maxima")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_aspect("equal")

    fig.tight_layout()
    out = "lorenz_map.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
