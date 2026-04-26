"""Strogatz Fig. 9.5.2 -- transient chaos at r = 21.

Below the Hopf bifurcation at r_H = 470/19 ~= 24.74 the fixed points C+
and C- are still linearly stable, but a chaotic invariant set already
exists in phase space.  Trajectories wander chaotically for a while and
then collapse onto one of C+ or C-.  Here IC = (0, 1, 0).
"""

import matplotlib.pyplot as plt
import numpy as np

from _common import IC_NEAR_ORIGIN, fixed_points, integrate

R = 21.0
T_END = 60.0


def main() -> None:
    sol = integrate(R, IC_NEAR_ORIGIN, T_END, n_samples=40000)
    _, cplus, cminus = fixed_points(R)

    fig = plt.figure(figsize=(11, 5))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    axt = fig.add_subplot(1, 2, 2)

    ax3d.plot(sol.x, sol.y, sol.z, lw=0.4)
    ax3d.scatter(*cplus, color="k"); ax3d.scatter(*cminus, color="k")
    ax3d.set_xlabel("x"); ax3d.set_ylabel("y"); ax3d.set_zlabel("z")
    ax3d.set_title(f"Trajectory, r = {R}, IC = {IC_NEAR_ORIGIN}")

    axt.plot(sol.t, sol.x, lw=0.6)
    for name, pt in [("C+", cplus), ("C-", cminus)]:
        axt.axhline(pt[0], ls="--", color="k", alpha=0.5)
        axt.text(T_END * 1.005, pt[0], name, va="center")
    axt.set_xlabel("t"); axt.set_ylabel("x")
    axt.set_title("x(t) -- chaotic transient settling onto C+ or C-")
    axt.grid(alpha=0.3)

    final = np.array([sol.x[-1], sol.y[-1], sol.z[-1]])
    settled_to = "C+" if np.linalg.norm(final - cplus) < np.linalg.norm(final - cminus) else "C-"

    fig.tight_layout()
    out = "transient_chaos.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}; trajectory settled onto {settled_to}")


if __name__ == "__main__":
    main()
