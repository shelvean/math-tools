"""Strogatz Section 9.3 setup -- stable fixed points C+/C- for 1 < r < r_H.

At r = 10 (well below the Hopf threshold r_H = 470/19 ~= 24.74) the two
nontrivial fixed points C+/- are stable spirals.  Both initial conditions
discussed in chat are integrated; each spirals into one of the fixed
points.
"""

import matplotlib.pyplot as plt
import numpy as np

from _common import IC_NEAR_ORIGIN, IC_SPARROW, fixed_points, integrate

R = 10.0
T_END = 30.0


def main() -> None:
    runs = [("(0, 1, 0)", IC_NEAR_ORIGIN), ("(0, 1, 1.05)", IC_SPARROW)]
    _, cplus, cminus = fixed_points(R)

    fig = plt.figure(figsize=(11, 5))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    axxz = fig.add_subplot(1, 2, 2)

    for label, ic in runs:
        sol = integrate(R, ic, T_END)
        ax3d.plot(sol.x, sol.y, sol.z, lw=0.5, label=f"IC {label}")
        axxz.plot(sol.x, sol.z, lw=0.5, label=f"IC {label}")
        final = np.array([sol.x[-1], sol.y[-1], sol.z[-1]])
        settled = "C+" if np.linalg.norm(final - cplus) < np.linalg.norm(final - cminus) else "C-"
        print(f"IC {label}: settled onto {settled}, |final - target| = "
              f"{min(np.linalg.norm(final - cplus), np.linalg.norm(final - cminus)):.2e}")

    for label, pt in [("C+", cplus), ("C-", cminus)]:
        ax3d.scatter(*pt, color="k", s=25)
        axxz.scatter(pt[0], pt[2], color="k", s=25, zorder=3)
        axxz.annotate(label, (pt[0], pt[2]), textcoords="offset points", xytext=(6, 4))

    ax3d.set_xlabel("x"); ax3d.set_ylabel("y"); ax3d.set_zlabel("z")
    ax3d.set_title(f"Stable spirals onto C+/-, r = {R}")
    ax3d.legend(fontsize=8)

    axxz.set_xlabel("x"); axxz.set_ylabel("z")
    axxz.set_title("xz projection")
    axxz.legend(fontsize=8)
    axxz.grid(alpha=0.3)

    fig.tight_layout()
    out = "stable_fixed_points.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
