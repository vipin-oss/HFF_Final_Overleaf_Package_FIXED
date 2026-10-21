#!/usr/bin/env python3
"""Figures 2-5 of the manuscript, generated from the model output (no hand-typed data).

Figure 1 (geometry schematic) is a TikZ drawing, figures/fig1_geometry.tex.

Style: serif text (Times-compatible) at the manuscript text size -- 10 pt axis labels, 9 pt tick
labels, 8.5 pt legends -- single full-width figures of 16 cm (6.3 in), line widths 1.1-1.4 pt,
Okabe-Ito colours that remain distinguishable in greyscale thanks to distinct line styles and
markers.  Output: vector PDF (embedded fonts) and EPS; a PNG preview is written for inspection.
"""
from __future__ import annotations

import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import hff_model as hm

HERE = pathlib.Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
FIG.mkdir(exist_ok=True)
RES = HERE / "results"

BLUE, VERM, GREEN, BLACK, GREY = "#0072BD", "#D95319", "#009E73", "#000000", "#666666"
PINK, YELLOW = "#CC79A7", "#EDB120"   # colour set of the authors' earlier MATLAB figures

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["TeX Gyre Termes", "Liberation Serif", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "axes.linewidth": 0.8,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.top": False,
    "ytick.right": False,
    "axes.grid": True,
    "grid.linestyle": "-",
    "grid.linewidth": 0.4,
    "grid.color": "#d4d4d4",
    "axes.axisbelow": True,
    "lines.linewidth": 1.7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})
W = 6.3  # inches, full text width


def save(fig, name: str) -> None:
    for ax in fig.axes:                      # minor dotted grid, as in the authors' earlier figures
        ax.minorticks_on()
        ax.grid(which="minor", linestyle=":", linewidth=0.3, color="#e0e0e0")
        ax.tick_params(which="minor", length=1.5)
    for ext in ("pdf", "eps"):
        fig.savefig(FIG / f"{name}.{ext}")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)
    print("wrote", name)


def tag(ax, s, y=0.93):
    ax.text(0.03, y, s, transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")


# --------------------------------------------------------------------------------------
def fig2_bowing(p: hm.Params) -> None:
    r = hm.compute(p)
    L, H0 = p.L, p.H0
    x = np.linspace(0, L, 401)
    mu_f = np.sqrt(r["N_c"] / r["D_s"])
    mu_sc = np.sqrt(r["N_c_sc"] / r["D_s"])
    w_lin = r["kappa_th"] * x * (L - x) / 2
    w_fr = hm.w_thermal_beamcolumn(x, r["kappa_th"], mu_f, L)
    w_sc = hm.w_thermal_beamcolumn(x, r["kappa_th"], mu_sc, L)

    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.75), gridspec_kw={"wspace": 0.30})
    a.plot(x / L, w_lin / H0, color=GREY, ls="--", label="linear, $\\kappa_{\\rm th}x(L-x)/2$")
    a.plot(x / L, w_fr / H0, color=BLUE, ls="-", label="beam\u2013column, frozen force")
    a.plot(x / L, w_sc / H0, color=VERM, ls="-.", label="beam\u2013column, self-consistent")
    a.axhline(0.5, color=BLACK, lw=0.7, ls=":")
    a.text(0.98, 0.51, "guard $|w|/H_0=0.5$", fontsize=8.5, va="bottom", ha="right")
    a.set_xlabel("$x/L$")
    a.set_ylabel("$w/H_0$")
    a.set_xlim(0, 1)
    a.set_ylim(0, 0.62)
    a.legend(loc="lower center", frameon=False, handlelength=2.4)
    tag(a, "(a)", y=0.28)

    q = np.linspace(50.0, 10e3, 100)
    wl, wf, ws = [], [], []
    for qq in q:
        rr = hm.compute(p, qq)
        wl.append(rr["w_lin_over_H0"])
        wf.append(rr["w_frozen_over_H0"])
        ws.append(rr["w_sc_over_H0"])
    b.plot(q / 1e3, wl, color=GREY, ls="--")
    b.plot(q / 1e3, wf, color=BLUE, ls="-")
    b.plot(q / 1e3, ws, color=VERM, ls="-.")
    b.axhline(0.5, color=BLACK, lw=0.7, ls=":")
    c = hm.ceilings(p)
    for key, lab, dy in (("q_w_guard", "$w$", 0.0), ("q_stress_guard", "$\\sigma$", 0.0)):
        b.axvline(c[key] / 1e3, color=GREEN, lw=0.8, ls=(0, (1, 2)))
    b.text(c["q_w_guard"] / 1e3 - 0.15, 1.18, "$|w|/H_0$ guard", rotation=90, fontsize=8, ha="right", va="top", color=GREEN)
    b.text(c["q_stress_guard"] / 1e3 + 0.15, 1.18, "stress cap", rotation=90, fontsize=8, ha="left", va="top", color=GREEN)
    b.plot([p.q / 1e3], [r["w_frozen_over_H0"]], "o", color=BLUE, ms=5, mfc="white", mew=1.2)
    b.annotate("baseline", (p.q / 1e3, r["w_frozen_over_H0"]), xytext=(1.3, 0.72), fontsize=8.5,
               arrowprops=dict(arrowstyle="-", lw=0.6))
    b.set_xlabel(r"imposed heat flux $q^{\prime\prime}$  (kW m$^{-2}$)")
    b.set_ylabel("$w_{\\max}/H_0$")
    b.set_xlim(0, 10)
    b.set_ylim(0, 1.2)
    tag(b, "(b)")
    save(fig, "fig2_bowing")


# --------------------------------------------------------------------------------------
def fig3_q8() -> None:
    Q = json.loads((RES / "q8_study.json").read_text())
    runs = {(x["nx"], x["ny"]): x for x in Q["runs"]}
    nxs = sorted({k[0] for k in runs})
    sty = {2: dict(color=BLUE, marker="o", ls="-"), 4: dict(color=VERM, marker="s", ls="--"),
           8: dict(color=GREEN, marker="^", ls="-.")}
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.75), gridspec_kw={"wspace": 0.34})
    for ny, s in sty.items():
        y = [runs[(nx, ny)]["PIN"]["d/2"] for nx in nxs]
        a.plot(nxs, y, ms=4.5, mfc="white", label=f"$N_y={ny}$", **s)
    a.axhline(1.0, color=BLACK, lw=0.7, ls=":")
    a.text(190, 0.99995, "ideal point pin: 1.0000 on every mesh", fontsize=8.5, va="top", ha="right")
    a.set_xscale("log", base=2)
    a.set_xlabel("axial elements $N_x$")
    a.set_ylabel("$w(L/2,d/2)\\,/\\,(\\kappa_{\\rm th}L^2/8)$")
    a.set_ylim(0.9975, 1.0007)
    a.set_xticks(nxs)
    a.set_xticklabels([str(n) for n in nxs])
    a.set_title("full-edge pin ($u_y=0$ on each end edge)", fontsize=9)
    a.legend(loc="center right", frameon=False, title="through-thickness elements", title_fontsize=8.5)
    tag(a, "(a)", y=0.28)
    for ny, s in sty.items():
        y = [runs[(nx, ny)]["CLAMP"]["d/2"] for nx in nxs]
        b.plot(nxs, y, ms=4.5, mfc="white", **s)
    b.axhline(0.0, color=BLACK, lw=0.7, ls=":")
    b.text(190, 0.003, "beam theory for a clamp: 0", fontsize=8.5, va="bottom", ha="right")
    b.set_xscale("log", base=2)
    b.set_xlabel("axial elements $N_x$")
    b.set_ylabel("$w(L/2,d/2)\\,/\\,(\\kappa_{\\rm th}L^2/8)$")
    b.set_xticks(nxs)
    b.set_xticklabels([str(n) for n in nxs])
    b.set_ylim(-0.09, 0.02)
    tag(b, "(b)")
    b.set_title("clamp ($u_x=u_y=0$ on each end edge)", fontsize=9)
    save(fig, "fig4_q8_mesh")


# --------------------------------------------------------------------------------------
def fig4_passage(p: hm.Params) -> None:
    L, H0 = p.L, p.H0
    x = np.linspace(0, L, 401)
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.75), gridspec_kw={"wspace": 0.30})
    styles = [(0.0, GREY, ":"), (2.5e3, GREEN, "-."), (5.0e3, BLUE, "-"), (5.5e3, VERM, "--")]
    for qq, col, ls in styles:
        if qq > 0:
            rr = hm.compute(p, qq, self_consistent=False)
            mu_ = np.sqrt(rr["N_c"] / rr["D_s"])
            w = hm.w_thermal_beamcolumn(x, rr["kappa_th"], mu_, L)
        else:
            w = 0 * x
        a.plot(x / L, 1 + w / H0, color=col, ls=ls, label=f"$q^{{\\prime\\prime}}={qq / 1e3:.1f}$ kW m$^{{-2}}$")
    a.set_xlabel("$x/L$")
    a.set_ylabel("passage height $H(x)/H_0$")
    a.set_xlim(0, 1)
    a.set_ylim(0.95, 2.1)
    a.legend(loc="upper center", frameon=False, handlelength=1.8, ncol=2, fontsize=7.5, columnspacing=0.8)
    tag(a, "(a)", y=0.70)

    q = np.linspace(50.0, 6e3, 60)
    dpr, exr = [], []
    for qq in q:
        rr = hm.compute(p, qq, self_consistent=False)
        dpr.append(rr["dp_ratio_lub"])
        exr.append(rr["q_over_h_ratio"])
    b.plot(q / 1e3, dpr, color=BLUE, ls="-", label="pressure drop (lubrication)")
    b.plot(q / 1e3, exr, color=VERM, ls="--", label=r"wall excess $q^{\prime\prime}/h$")
    b.axhline(1.0, color=BLACK, lw=0.7, ls=":")
    b.set_xlabel(r"imposed heat flux $q^{\prime\prime}$  (kW m$^{-2}$)")
    b.set_ylabel("ratio to the undeformed passage")
    b.set_xlim(0, 6)
    b.set_ylim(0.3, 1.5)
    b.legend(loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.93))
    tag(b, "(b)", y=0.2)
    save(fig, "fig3_passage")


# --------------------------------------------------------------------------------------
def fig5_nonlinear(p: hm.Params) -> None:
    NL = json.loads((RES / "q8_nl.json").read_text())
    fine = NL["runs"][-1]
    r = hm.compute(p)
    L, H0 = p.L, p.H0
    x = np.array(fine["nonlinear"]["profile_x"])
    wn = np.array(fine["nonlinear"]["profile_w"])
    wl = np.array(fine["linear"]["profile_w"])
    xs = np.linspace(0, L, 401)
    mu_f, mu_s = np.sqrt(r["N_c"] / r["D_s"]), np.sqrt(r["N_c_sc"] / r["D_s"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.75), gridspec_kw={"wspace": 0.34})
    a.plot(xs / L, r["kappa_th"] * xs * (L - xs) / 2 / H0, color=GREY, ls="--", label="beam, linear")
    a.plot(xs / L, hm.w_thermal_beamcolumn(xs, r["kappa_th"], mu_f, L) / H0, color=BLUE, ls="-",
           label="beam\u2013column, frozen force")
    a.plot(xs / L, hm.w_thermal_beamcolumn(xs, r["kappa_th"], mu_s, L) / H0, color=VERM, ls="-.",
           label="beam\u2013column, self-consistent")
    k = slice(0, None, 12)
    a.plot(x[k] / L, wn[k] / H0, "o", color=BLACK, ms=3.6, mfc="white", mew=0.9, label="Q8, nonlinear")
    a.plot(x[k] / L, wl[k] / H0, "s", color=GREEN, ms=3.2, mfc="white", mew=0.9, label="Q8, linear")
    a.set_xlabel("$x/L$")
    a.set_ylabel("$w/H_0$")
    a.set_xlim(0, 1)
    a.set_ylim(0, 0.85)
    a.legend(loc="upper center", frameon=False, handlelength=2.2, fontsize=8, bbox_to_anchor=(0.55, 1.0))
    tag(a, "(a)", y=0.28)
    cx = np.array(fine["nonlinear"]["col_x"]) / L
    b.plot(cx, np.array(fine["linear"]["col_N"]) / 1e3, color=GREEN, ls=":", label="Q8, linear")
    b.plot(cx, np.array(fine["nonlinear"]["col_N"]) / 1e3, color=BLACK, ls="-", label="Q8, nonlinear")
    b.axhline(r["N_c"] / 1e3, color=BLUE, lw=1.1, ls="-", label="beam, frozen force")
    b.axhline(r["N_c_sc"] / 1e3, color=VERM, lw=1.1, ls="-.", label="beam, self-consistent")
    b.set_xlabel("$x/L$")
    b.set_ylabel("compressive membrane force $N_c$  (kN m$^{-1}$)")
    b.set_xlim(0, 1)
    b.set_ylim(24, 31)
    b.legend(loc="lower center", frameon=False, handlelength=2.2, fontsize=8)
    tag(b, "(b)")
    save(fig, "fig5_q8_nonlinear")


# --------------------------------------------------------------------------------------
def fig6_convergence(p: hm.Params) -> None:
    C = json.loads((RES / "convergence.json").read_text())
    SL = json.loads((RES / "slenderness.json").read_text())
    lv = C["levels"]
    h = np.array([x["h_x"] for x in lv]) * 1e3
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.75), gridspec_kw={"wspace": 0.34})
    for key, ric, col, mk, ls, lab in (("w_q8", "w_q8_richardson", BLUE, "o", "-", "Q8 quadrilaterals"),
                                       ("w_p2", "w_p2_richardson", VERM, "s", "--", "P2 triangles")):
        w = np.array([x[key] for x in lv])
        wext = C[ric][1]
        err = np.abs(w - wext) / wext
        a.loglog(h[:-1], err[:-1], marker=mk, ls=ls, color=col, ms=4.5, mfc="white", label=f"{lab}, $p={C[ric][0]:.2f}$")
    hh = np.array([h[0], h[-2]])
    a.loglog(hh, 0.6 * (hh / hh[0]) ** 2 * 1.0e-1 * 0.5 * 0.55, color=BLACK, ls=":", lw=1.0, label="slope 2")
    a.set_xlabel("axial element size $h_x$  (mm)")
    a.set_ylabel("$|w-w_{\\rm ext}|\\,/\\,w_{\\rm ext}$")
    from matplotlib.ticker import NullFormatter, FixedLocator, FixedFormatter
    a.xaxis.set_minor_formatter(NullFormatter())
    a.xaxis.set_major_locator(FixedLocator([0.25, 0.5, 1, 2]))
    a.xaxis.set_major_formatter(FixedFormatter(["0.25", "0.5", "1", "2"]))
    a.legend(loc="upper left", frameon=False, fontsize=8, bbox_to_anchor=(0.0, 0.9))
    tag(a, "(a)", y=0.28)
    rows = SL["rows"]
    dl = np.array([r["d_over_L"] for r in rows])
    dev = np.array([100 * (r["fe_w_nl"] / r["beam"]["w_sc"] - 1) for r in rows])
    b.plot(dl, dev, "o-", color=BLUE, ms=4.5, mfc="white", label="P2 FE vs beam--column (sc)".replace("--", "\u2013"))
    xx = np.linspace(0, dl.max(), 100)
    b.plot(xx, dev[0] * (xx / dl[0]) ** 2, color=GREY, ls="--", lw=1.1, label="$\\propto (d/L)^2$")
    b.axhline(0, color=BLACK, lw=0.7, ls=":")
    b.set_xlabel("slenderness $d/L$")
    b.set_ylabel("departure of $w_{\\max}$ from beam model  (%)")
    b.set_xlim(0, 0.11)
    b.legend(loc="upper left", frameon=False, fontsize=8, bbox_to_anchor=(0.0, 0.93))
    tag(b, "(b)", y=0.28)
    save(fig, "fig6_convergence")


if __name__ == "__main__":
    P = hm.Params()
    fig2_bowing(P)
    fig3_q8()
    fig4_passage(P)
    fig5_nonlinear(P)
    fig6_convergence(P)
