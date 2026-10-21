#!/usr/bin/env python3
"""Generate the two asymptotic-theory figures and the comparison table.

Outputs (into ``program/outputs``):

    figures/fig13_asymptotics.{pdf,png}   series vs computed Nusselt number
    figures/fig14_pressure_law.{pdf,png}  closed-form vs computed pressure drop
    tables/table_asymptotics.tex          analytic vs finite-element comparison

The finite-element points are read from ``outputs/data``; the analytical curves
are computed here from the parameters, so every plotted point is reproducible.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
from scipy.special import hyp2f1

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from hff import asymptotics, config  # noqa: E402
from hff.figures import COL, STYLE  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "data"
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"


def save(fig, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=400)
    plt.close(fig)
    print("wrote", name)


def main() -> int:
    plt.rcParams.update(STYLE)
    cfg = config.load("params/baseline.json")
    H0 = cfg["geometry"]["H0"]
    L = cfg["geometry"]["L"]
    coupled = json.loads((DATA / "coupled_baseline.json").read_text())
    a_data = json.loads((DATA / "asymptotics.json").read_text())

    x = np.array(coupled["x"])
    w = np.array(coupled["w"])
    Nu = np.array(coupled["Nu"])
    xg = np.array(a_data["graetz"]["x"]) if "x" in a_data["graetz"] else None
    # the profile is stored in the run output, not in asymptotics.json
    prof = np.loadtxt(DATA / "asymptotics_graetz_profile.csv", delimiter=",", skiprows=1)
    xg, Nug = prof[:, 0], prof[:, 1]

    # ---------------------------------------------------------------- figure 13
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.5))
    ax = axes[0]
    ax.plot(xg * 1e3, Nug, "-", color=COL["blue"],
            label="Graetz series, straight passage")
    ax.plot(x[:-1] * 1e3, Nu, "o", ms=2.2, color=COL["red"],
            label="coupled computation, bowed passage")
    ax.axhline(a_data["graetz"]["Nu_fd"], ls=":", lw=0.8, color=COL["grey"])
    ax.annotate(r"$Nu_\infty=5.385$", xy=(1.0, 5.55), fontsize=7, color=COL["grey"])
    ax.set_xlabel(r"$x$ (mm)")
    ax.set_ylabel(r"$Nu(x)=2H_0h/k_f$")
    ax.set_ylim(4.5, 22.0)
    ax.legend(loc="upper right", borderpad=0.2, labelspacing=0.25)

    ax = axes[1]
    xx = x[:-1]
    m = (xx > 1e-3) & (Nu > 0)
    ratio = Nu[m] / np.interp(xx[m], xg, Nug)
    stretch = H0 / (H0 - w[:-1][m])
    ax.plot(stretch, ratio, "o", ms=2.0, color=COL["red"],
            label="computed ratio")
    cfit = a_data["comparison"]
    pexp = cfit["Nu_scaling_exponent"]
    r2 = cfit["Nu_scaling_r2"]
    ss = np.linspace(1.0, float(stretch.max()), 50)
    ax.plot(ss, ss ** pexp, "-", lw=1.0, color=COL["blue"],
            label=rf"$(H_0/H)^{{{pexp:.2f}}}$, $R^2={r2:.2f}$")
    ax.plot(ss, ss, "--", lw=0.9, color=COL["grey"], label=r"$(H_0/H)^{1}$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ticks = [1.0, 1.2, 1.4, 1.6, 1.8]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:.1f}" for t in ticks])
    ax.set_yticks([1.0, 1.2, 1.4, 1.6, 1.8])
    ax.set_yticklabels([f"{t:.1f}" for t in [1.0, 1.2, 1.4, 1.6, 1.8]])
    ax.minorticks_off()
    ax.set_xlim(1.0, 1.85)
    ax.set_ylim(0.97, 1.85)
    ax.set_xlabel(r"stretch $H_0/H(x)$")
    ax.set_ylabel(r"$Nu/Nu_{\rm Graetz}$")
    ax.legend(loc="upper left", handlelength=1.2, borderpad=0.2,
              labelspacing=0.25)
    fig.tight_layout()
    save(fig, "fig13_asymptotics")

    # ---------------------------------------------------------------- figure 14
    sweep = json.loads((DATA / "sweep_flux.json").read_text())
    a_pts, dp_pts = [], []
    for row in sweep:
        if row.get("converged"):
            a_pts.append(row["w_max"] / H0)
            dp_pts.append(row["flow_dp"])
    a_pts, dp_pts = np.array(a_pts), np.array(dp_pts)

    a = np.linspace(0.0, 0.5, 201)
    H0g, Lg, Leg, Log = (cfg["geometry"][k] for k in ("H0", "L", "Le", "Lo"))
    Qg = cfg["operating"]["U"] * H0g
    mu = cfg["fluid"]["mu"]
    dp_strip0 = 12.0 * mu * Qg * Lg / H0g**3          # 72 Pa at the design point
    dp_rigid = 12.0 * mu * Qg * (Leg + Log) / H0g**3   # rigid entrance and exit
    dp_closed = dp_rigid + dp_strip0 * hyp2f1(3.0, 0.5, 1.0, a)
    dp_lin = dp_rigid + dp_strip0 * (1.0 + 1.5 * a)

    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.5))
    ax = axes[0]
    ax.plot(a, dp_closed, "-", color=COL["blue"],
            label=r"$12\mu Q\,\int dx/H^3$, closed form")
    ax.plot(a, dp_lin, "--", lw=0.9, color=COL["green"], label="first-order series")
    ax.plot(a_pts, dp_pts, "o", ms=2.4, color=COL["red"], label="coupled computation")
    ax.set_xlabel(r"$a=w_{\max}/H_0$")
    ax.set_ylabel(r"$\Delta p$ (Pa)")
    ax.legend(loc="upper left")

    ax = axes[1]
    dp_sin = np.array([dp_rigid + dp_strip0 * hyp2f1(3.0, 0.5, 1.0, aa)
                       for aa in a_pts])
    ax.plot(a_pts, 100 * (dp_sin - dp_pts) / dp_pts, "o-", ms=2.4, lw=0.9,
            color=COL["red"], label=r"$w=w_{\max}\sin^2(\pi x/L)$")
    ax.axhline(0.0, lw=0.8, color=COL["grey"])
    ax.set_xlabel(r"$a=w_{\max}/H_0$")
    ax.set_ylabel(r"$(\Delta p_{\rm model}-\Delta p_{\rm FEM})/\Delta p_{\rm FEM}$ (%)")
    ax.legend(loc="lower left")
    fig.tight_layout()
    save(fig, "fig14_pressure_law")

    # -------------------------------------------------------------------- table
    c = a_data["comparison"]
    rows = [
        (r"$\Delta p$ (Pa), \eqref{eq:dpclosed}, computed shape",
         c["dp_lub_computed_profile"], c["dp_fem"], ""),
        (r"$\Delta p$ (Pa), \eqref{eq:dpclosed}, $\sin^2$ shape",
         c["dp_lub_sin2"], c["dp_fem"], ""),
        (r"$w_{\max}$ ($10^{-4}$~m), \eqref{eq:Wclosed}, frozen force",
         1e4 * c["w_frozen_closed_form"], 1e4 * c["w_fem"], ""),
        (r"$\bar\theta$ (K), series and one-dimensional wall",
         c["theta_bar_series"], c["theta_bar_fem"], ""),
    ]
    lines = [
        "% generated by tools/asymptotic_figures.py -- do not edit",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{The semi-analytical model of Section~\ref{sec:analytical} against the "
        r"coupled finite-element solution at the design point. The difference is "
        r"$(a-c)/c$ in per cent.}",
        r"\label{tab:asymptotics}",
        r"\small",
        r"\begin{tabular}{@{}lrrr@{}}",
        r"\hline",
        r"Quantity & Semi-analytical & Computed & Difference (\%) \\",
        r"\hline",
    ]
    for name, an, fem, _ in rows:
        rel = 100.0 * (an - fem) / fem
        lines.append(f"{name} & \\num{{{an:.6g}}} & \\num{{{fem:.6g}}} & {rel:+.2f} \\\\")
    lines += [r"\hline", r"\end{tabular}", r"\end{table}", ""]
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / "table_asymptotics.tex").write_text("\n".join(lines))
    print("wrote table_asymptotics.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
