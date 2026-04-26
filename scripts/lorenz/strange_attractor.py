"""Strogatz Fig. 9.3.3 / 9.4.1 -- the canonical Lorenz strange attractor.

r = 28, sigma = 10, b = 8/3.  Two trajectories from the two initial
conditions discussed:
  - (0, 1, 0)        the textbook "near origin" start
  - (0, 1, 1.05)     Sparrow's classic IC

A long transient (t in [0, 5]) is integrated and discarded so the plotted
arc lies on the attractor itself rather than on the approach to it.
"""

import matplotlib.pyplot as plt

from _common import IC_NEAR_ORIGIN, IC_SPARROW, fixed_points, integrate

R = 28.0
T_END = 50.0
T_DISCARD = 5.0


def main() -> None:
    runs = [("(0, 1, 0)", IC_NEAR_ORIGIN), ("(0, 1, 1.05)", IC_SPARROW)]
    _, cplus, cminus = fixed_points(R)

    fig = plt.figure(figsize=(11, 5))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    axxz = fig.add_subplot(1, 2, 2)

    for label, ic in runs:
        sol = integrate(R, ic, T_END)
        keep = sol.t >= T_DISCARD
        ax3d.plot(sol.x[keep], sol.y[keep], sol.z[keep], lw=0.4, label=f"IC {label}")
        axxz.plot(sol.x[keep], sol.z[keep], lw=0.3, label=f"IC {label}")

    for label, pt, color in [("C+", cplus, "k"), ("C-", cminus, "k")]:
        ax3d.scatter(*pt, color=color, s=20)
        axxz.scatter(pt[0], pt[2], color=color, s=20, zorder=3)
        axxz.annotate(label, (pt[0], pt[2]), textcoords="offset points", xytext=(6, 4))

    ax3d.set_xlabel("x"); ax3d.set_ylabel("y"); ax3d.set_zlabel("z")
    ax3d.set_title(f"Lorenz attractor, r = {R}")
    ax3d.legend(loc="upper left", fontsize=8)

    axxz.set_xlabel("x"); axxz.set_ylabel("z")
    axxz.set_title("xz projection")
    axxz.legend(loc="lower right", fontsize=8)
    axxz.grid(alpha=0.3)

    fig.tight_layout()
    out = "strange_attractor.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
