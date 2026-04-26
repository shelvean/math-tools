"""Strogatz Fig. 9.3.1 / 9.3.2 -- aperiodic time series at r = 28.

Plots x(t), y(t), z(t) for the chaotic regime starting from Sparrow's IC.
y(t) is the panel that most closely matches Strogatz's Fig. 9.3.2; z(t)
shows the irregular spiking that the Lorenz return map (see lorenz_map.py)
collapses onto a one-dimensional curve.
"""

import matplotlib.pyplot as plt

from _common import IC_SPARROW, integrate

R = 28.0
T_END = 50.0


def main() -> None:
    sol = integrate(R, IC_SPARROW, T_END)

    fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    for ax, series, name in zip(axes, (sol.x, sol.y, sol.z), ("x", "y", "z")):
        ax.plot(sol.t, series, lw=0.6)
        ax.set_ylabel(name)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("t")
    axes[0].set_title(f"Lorenz time series, r = {R}, IC = {IC_SPARROW}")

    fig.tight_layout()
    out = "time_series.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
