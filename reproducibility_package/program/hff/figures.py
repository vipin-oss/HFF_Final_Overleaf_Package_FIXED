"""Publication figures generated from the saved numerical results.

Every figure is written twice: a vector PDF for the manuscript and a 400 dpi PNG for
inspection.  Figures that are *not* computed - namely the geometry schematic - are
labelled as schematics in the caption; nothing else is drawn by hand.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

# ---------------------------------------------------------------------------
#  house style
# ---------------------------------------------------------------------------
STYLE = {
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.0,
    "lines.markersize": 3.0,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "legend.frameon": False,
    "figure.dpi": 120,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "axes.grid": False,
}
COL = {"blue": "#1f4e79", "red": "#b2182b", "green": "#1b7837", "grey": "#666666",
       "orange": "#d95f02", "purple": "#6a3d9a", "light": "#9ecae1"}


def _load(data: Path, name: str) -> Any:
    path = Path(data) / name
    if not path.exists():
        raise FileNotFoundError(f"missing {path}; run run_all.py first")
    with open(path) as fh:
        return json.load(fh)


class _Out:
    def __init__(self, figdir: Path):
        self.figdir = Path(figdir)
        self.figdir.mkdir(parents=True, exist_ok=True)

    def save(self, fig, name: str) -> None:
        fig.savefig(self.figdir / f"{name}.pdf")
        fig.savefig(self.figdir / f"{name}.png", dpi=400)
        plt.close(fig)


def _panel(ax, letter: str, dx: float = -0.02, dy: float = 1.02) -> None:
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8)


# ---------------------------------------------------------------------------
#  Fig. 1 - geometry and boundary conditions (schematic, not to scale)
# ---------------------------------------------------------------------------
def fig_geometry(cfg: Dict, out: _Out) -> None:
    g = cfg["geometry"]
    H0, L, Le, Lo, d = g["H0"], g["L"], g["Le"], g["Lo"], g["d"]
    fig, ax = plt.subplots(figsize=(6.4, 2.1))
    x0, x1 = -Le, L + Lo
    # wall strip on the deformable segment
    ax.add_patch(Rectangle((0, H0), L, d, facecolor="#f0e6d2", edgecolor="k", lw=0.6))
    ax.plot([x0, 0], [H0, H0], color="k", lw=0.8)
    ax.plot([L, x1], [H0, H0], color="k", lw=0.8)
    ax.plot([x0, x1], [0, 0], color="k", lw=0.8)
    ax.plot([x0, x0], [0, H0], color="k", lw=0.8, ls=(0, (4, 2)))
    ax.plot([x1, x1], [0, H0], color="k", lw=0.6, ls=(0, (1, 1.5)))
    # deformed interface suggestion (exaggerated)
    xs = np.linspace(0, L, 120)
    ax.plot(xs, H0 - 0.32 * H0 * np.sin(np.pi * xs / L), color=COL["red"], lw=0.9,
            ls="--")
    # arrows
    ax.annotate("", xy=(x0 - 0.004, 0.5 * H0), xytext=(x0 - 0.009, 0.5 * H0),
                arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(x0 - 0.0095, 0.62 * H0, "inlet\n$U,\\ T_{in}$", fontsize=7, ha="right")
    ax.annotate("", xy=(x1 + 0.009, 0.5 * H0), xytext=(x1 + 0.004, 0.5 * H0),
                arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(x1 + 0.0095, 0.62 * H0, "outlet\n$p=0$", fontsize=7, ha="left")
    for k in range(7):
        xa = 0.06 * L + k * 0.13 * L
        ax.annotate("", xy=(xa, H0 + d + 0.0032), xytext=(xa, H0 + d),
                    arrowprops=dict(arrowstyle="->", lw=0.6, color=COL["red"]))
    ax.text(0.5 * L, H0 + d + 0.0055, "$q''$ (imposed flux)", fontsize=7,
            color=COL["red"], ha="center")
    # dimensions
    ax.annotate("", xy=(0, -0.0032), xytext=(L, -0.0032),
                arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(0.5 * L, -0.0052, "$L$", fontsize=7, ha="center")
    ax.annotate("", xy=(L + 0.002, 0), xytext=(L + 0.002, H0),
                arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(L + 0.003, 0.5 * H0, "$H_0$", fontsize=7, va="center")
    ax.text(L - 0.002, H0 + 0.5 * d, "$d$", fontsize=7, va="center", ha="right")
    ax.text(0.5 * L, H0 - 0.5 * H0 * 0.32 - 0.0022, "deformed interface $w(x)$",
            fontsize=6.5, color=COL["red"], ha="center")
    ax.set_xlim(x0 - 0.013, x1 + 0.013)
    ax.set_ylim(-0.007, H0 + d + 0.009)
    ax.set_aspect("equal")
    ax.axis("off")
    out.save(fig, "fig01_geometry")


# ---------------------------------------------------------------------------
#  Fig. 2 - discretisation and deformed mesh
# ---------------------------------------------------------------------------
def fig_mesh(data: Path, out: _Out, cfg: Dict) -> None:
    """Discretisation: full domain and a zoom on the deformed throat and the wall."""
    from . import fem
    doc = _load(data, "coupled_baseline.json")
    w = np.asarray(doc["w"])
    mesh = fem.fluid_mesh(cfg, w)
    solid = fem.solid_mesh(cfg, mesh)
    g = cfg["geometry"]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.3))
    ax = axes[0]
    ax.add_patch(Rectangle((-g["Le"] * 1e3, g["H0"] * 1e3), (g["L"] + g["Le"] + g["Lo"]) * 1e3,
                           g["d"] * 1e3, facecolor="#f2ead9", edgecolor="k", lw=0.5,
                           zorder=0))
    for tri in mesh.tris:
        xy = mesh.xy[tri] * 1e3
        ax.plot(np.append(xy[:, 0], xy[0, 0]), np.append(xy[:, 1], xy[0, 1]),
                color=COL["blue"], lw=0.1, zorder=1)
    pairs = mesh.boundary["interface"]
    ax.plot(0.5 * (mesh.xy[pairs[:, 0], 0] + mesh.xy[pairs[:, 1], 0]) * 1e3,
            0.5 * (mesh.xy[pairs[:, 0], 1] + mesh.xy[pairs[:, 1], 1]) * 1e3,
            color=COL["red"], lw=0.8, zorder=2)
    for xtxt, txt in ((-5.0, "entrance"), (40.0, "exit")):
        ax.text(xtxt, 0.55, txt, fontsize=6.5, ha="center", color=COL["grey"])
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("$y$ (mm)")
    ax.set_xlim(-10.3, 50.3)
    ax.set_ylim(-0.03, 0.66)
    _panel(ax, "a")

    ax = axes[1]
    lo, hi = 1.0e-3, 4.0e-3   # inside the heated segment, clear of the lid corner
    for tri in mesh.tris:
        xy = mesh.xy[tri] * 1e3
        if xy[:, 0].mean() < lo * 1e3 or xy[:, 0].mean() > hi * 1e3:
            continue
        ax.plot(np.append(xy[:, 0], xy[0, 0]), np.append(xy[:, 1], xy[0, 1]),
                color=COL["blue"], lw=0.35)
    for tri in solid.tris:
        xy = solid.xy[tri] * 1e3
        if xy[:, 0].mean() < lo * 1e3 or xy[:, 0].mean() > hi * 1e3:
            continue
        ax.plot(np.append(xy[:, 0], xy[0, 0]), np.append(xy[:, 1], xy[0, 1]),
                color=COL["orange"], lw=0.35)
    m = (mesh.xy[pairs[:, 0], 0] >= lo) & (mesh.xy[pairs[:, 0], 0] <= hi)
    ax.plot(0.5 * (mesh.xy[pairs[m, 0], 0] + mesh.xy[pairs[m, 1], 0]) * 1e3,
            0.5 * (mesh.xy[pairs[m, 0], 1] + mesh.xy[pairs[m, 1], 1]) * 1e3,
            color=COL["red"], lw=0.9)
    ax.axhline(g["H0"] * 1e3, color=COL["grey"], lw=0.6, ls="--")
    ax.text(lo * 1e3 + 0.06, g["H0"] * 1e3 + 0.006,
            "undeformed interface $y=H_0$", fontsize=6.5, color=COL["grey"])
    ax.text(lo * 1e3 + 0.10, 0.60, "wall (P2)", fontsize=6.5, color=COL["orange"],
            va="top")
    ax.text(lo * 1e3 + 0.10, 0.345, "fluid (P2/P1)", fontsize=6.5, color=COL["blue"])
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("$y$ (mm)")
    ax.set_xlim(lo * 1e3, hi * 1e3)
    ax.set_ylim(0.32, 0.615)
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig02_mesh")


# ---------------------------------------------------------------------------
#  Fig. 3 - computed flow field
# ---------------------------------------------------------------------------
def fig_flow(data: Path, out: _Out, cfg: Dict) -> None:
    doc = _load(data, "coupled_baseline.json")
    s = doc["samples"]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.75))
    ax = axes[0]
    for k, prof in enumerate(s["profiles"]):
        y = np.asarray(prof["y"]) * 1e3
        u = np.asarray(prof["u"])
        ax.plot(u, y, lw=0.9, color=plt.cm.viridis(k / max(1, len(s["profiles"]) - 1)),
                label=f"$x$ = {prof['x'] * 1e3:.1f} mm")
    u_in = 6 * cfg["operating"]["U"] * (np.linspace(0, 1, 50) *
                                        (1 - np.linspace(0, 1, 50)))
    ax.plot(u_in, np.linspace(0, 1, 50) * cfg["geometry"]["H0"] * 1e3, ls=":",
            color=COL["grey"], lw=0.8, label="inlet profile")
    ax.set_xlabel("$u_x$ (m/s)")
    ax.set_ylabel("$y$ (mm)")
    ax.set_ylim(-0.02, 0.55)
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.26), ncol=3,
              handlelength=1.0, columnspacing=1.0, frameon=False)
    _panel(ax, "a")

    ax = axes[1]
    xc = np.asarray(s["x_columns"]) * 1e3
    ax.plot(xc, s["p_columns"], color=COL["blue"], lw=0.9)
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("$\\bar p$ (Pa)")
    ax.set_xlim(-10, 50)
    ax.axvspan(0, 30, color=COL["light"], alpha=0.25, lw=0)
    ax.text(15, max(s["p_columns"]) * 0.5, "deformable strip", fontsize=6.5,
            ha="center", color=COL["blue"])
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig03_flow")


# ---------------------------------------------------------------------------
#  Fig. 4 - conjugate thermal results
# ---------------------------------------------------------------------------
def fig_thermal(data: Path, out: _Out, cfg: Dict) -> None:
    doc = _load(data, "coupled_baseline.json")
    ana = _load(data, "analytic_baseline.json")
    x = np.asarray(doc["Nu_x"]) * 1e3
    Nu = np.asarray(doc["Nu"], dtype=float)
    keep = np.ones_like(Nu, dtype=bool)
    keep[:2] = False           # first stations: discrete singularity of the entry length
    keep[-2:] = False          # trailing edges of the heated segment
    x, Nu = x[keep], Nu[keep]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.5))
    ax = axes[0]
    ax.plot(x, Nu, color=COL["blue"], lw=1.0, label="computed, conjugate")
    ax.axhline(5.385, color=COL["red"], lw=0.8, ls="--",
               label="$Nu_{H1}=5.385$ (fully developed)")
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("$Nu = 2H_0h/k_f$")
    ax.set_ylim(4.0, max(6.5, np.nanmax(Nu) * 1.05))
    ax.legend(loc="upper right", handlelength=1.6)
    _panel(ax, "a")

    ax = axes[1]
    Tw = np.asarray(doc["Tw"]) - cfg["operating"]["Tin"]
    Tb = np.asarray(doc["Tb"]) - cfg["operating"]["Tin"]
    xs = np.linspace(0, cfg["geometry"]["L"], len(Tw)) * 1e3
    ax.plot(xs, Tw, color=COL["red"], lw=1.0, label="$\\theta_w$ (interface)")
    ax.plot(xs, Tb, color=COL["blue"], lw=1.0, label="$\\theta_b$ (bulk)")
    tb = np.asarray(doc["theta_bar"])
    ax.plot(np.linspace(0, cfg["geometry"]["L"], len(tb)) * 1e3, tb,
            color=COL["green"], lw=0.9, ls="-.", label="$\\bar\\theta$ (wall mean)")
    est = ana["theta_bar_estimate"]["theta_bar"]
    ax.axhline(est, color=COL["grey"], lw=0.7, ls=":", label="1-D estimate")
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("temperature rise (K)")
    ax.legend(loc="upper left", handlelength=1.8)
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig04_thermal")


# ---------------------------------------------------------------------------
#  Fig. 5 - wall response
# ---------------------------------------------------------------------------
def fig_wall(data: Path, out: _Out, cfg: Dict) -> None:
    wa = _load(data, "wall_baseline.json")
    co = _load(data, "coupled_baseline.json")
    g = cfg["geometry"]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.5))
    ax = axes[0]
    x = np.asarray(wa["frozen"]["x"]) * 1e3
    ax.plot(x, np.asarray(wa["frozen"]["w"]) / g["H0"], color=COL["blue"], lw=1.0,
            label="frozen force ($\\kappa_{th}$ from 1-D)")
    ax.plot(x, np.asarray(wa["self_consistent"]["w"]) / g["H0"], color=COL["green"],
            lw=1.0, ls="--", label="self-consistent $N$")
    ax.plot(np.asarray(co["x"]) * 1e3, np.asarray(co["w"]) / g["H0"],
            color=COL["red"], lw=1.0, ls="-.",
            label="coupled (2-D conjugate)")
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("$w/H_0$")
    ax.set_ylim(0, 0.52)
    ax.axhline(0.5, color=COL["grey"], lw=0.6, ls=":")
    ax.text(1.0, 0.51, "kinematic ceiling $0.5H_0$", fontsize=6.5, color=COL["grey"])
    ax.legend(loc="lower center", handlelength=1.8)
    _panel(ax, "a")

    ax = axes[1]
    ax.plot(x, np.asarray(wa["frozen"]["moment"]), color=COL["blue"], lw=1.0,
            label="frozen force")
    ax.plot(x, np.asarray(wa["self_consistent"]["moment"]), color=COL["green"],
            lw=1.0, ls="--", label="self-consistent")
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("$M$ (N m/m)")
    ax.legend(loc="upper right", handlelength=1.8)
    ax2 = ax.twinx()
    ax2.plot(x, np.asarray(wa["frozen"]["sigma_bend"]) / 1e6, color=COL["orange"],
             lw=0.8, ls=":")
    ax2.set_ylabel("$\\sigma_b$ (MPa)", color=COL["orange"])
    ax2.tick_params(axis="y", colors=COL["orange"])
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig05_wall")


# ---------------------------------------------------------------------------
#  Fig. 6 - convergence
# ---------------------------------------------------------------------------
def fig_convergence(data: Path, out: _Out, cfg: Dict) -> None:
    co = _load(data, "coupled_baseline.json")
    ms = _load(data, "mesh_study.json")
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4))
    ax = axes[0]
    hist = co["history"]
    it = [h["iteration"] for h in hist]
    d = np.maximum([h["delta_rel"] for h in hist], 1e-16)
    ax.semilogy(it, d, "o-", color=COL["blue"], lw=0.9, ms=2.5)
    ax.set_xlabel("coupling iteration")
    ax.set_ylabel("$\\|w^{k+1}-w^{k}\\|_\\infty/\\|w^{k+1}\\|_\\infty$")
    ax.set_xlim(0.5, it[-1] + 0.5)
    _panel(ax, "a")

    ax = axes[1]
    lv = ms["levels"]
    nx = np.array([r["nx_heated"] for r in lv], dtype=float)
    wm = np.array([r["w_max"] for r in lv])
    if len(lv) >= 3:
        ax.semilogx(nx, wm * 1e4, "s-", color=COL["red"], lw=0.9, ms=3.0)
        ax.set_xlabel("elements along the strip, $n_x$")
        ax.set_ylabel("$w_{\\max}$ ($10^{-4}$ m)")
        order = ms.get("order", {})
        if order.get("observed_order_w_max") == order.get("observed_order_w_max"):
            ax.text(0.04, 0.10,
                    "observed order $p$ = %.2f\nRichardson limit = %.4f$\\times10^{-4}$ m"
                    % (order["observed_order_w_max"],
                       order["richardson_extrapolated_w_max"] * 1e4),
                    transform=ax.transAxes, fontsize=6.8)
    else:
        ax.plot(nx, wm * 1e4, "s-", color=COL["red"], lw=0.9, ms=3.0)
        ax.set_xlabel("elements along the strip, $n_x$")
        ax.set_ylabel("$w_{\\max}$ ($10^{-4}$ m)")
        ax.text(0.04, 0.86, "coarse study only (run without --quick\n"
                            "for the refinement order)", transform=ax.transAxes,
                fontsize=6.8, color=COL["grey"])
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig06_convergence")


# ---------------------------------------------------------------------------
#  Fig. 7 - parameter sensitivity
# ---------------------------------------------------------------------------
def fig_sensitivity(data: Path, out: _Out, cfg: Dict) -> None:
    """Coupled response to the imposed flux and to the wall thickness."""
    fl = _load(data, "sweep_flux.json")
    th = _load(data, "sweep_thickness.json")
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.6))

    ax = axes[0]
    q = np.array([r["q_flux"] for r in fl]) / 1e3
    w = np.array([r["w_max_over_H0"] for r in fl])
    ok = np.array([bool(r.get("converged")) for r in fl])
    ax.plot(q[ok], w[ok], "o-", color=COL["blue"], lw=1.0, ms=3.0,
            label="coupled solution")
    ax.plot(q[~ok], w[~ok], "o", mfc="none", mec=COL["blue"], ms=3.5,
            label="first-iteration predictor")
    ax.axhspan(0.45, 0.85, color=COL["grey"], alpha=0.12, lw=0)
    ax.axhline(0.45, color=COL["grey"], lw=0.6, ls="--")
    ax.text(q[0], 0.462, "kinematic ceiling", fontsize=6.3, color=COL["grey"])
    ax.set_xlabel("$q''$ (kW m$^{-2}$)")
    ax.set_ylabel("$w_{\\max}/H_0$")
    ax.set_ylim(0, 0.78)
    ax.set_xlim(0.5, q[-1] + 0.4)
    ax2 = ax.twinx()
    ax2.plot(q[ok], np.array([r["flow_dp"] for r in fl])[ok], "s--", color=COL["red"],
             lw=0.9, ms=2.5)
    ax2.set_ylabel("$\\Delta p$ (Pa)", color=COL["red"])
    ax2.tick_params(axis="y", colors=COL["red"])
    ax2.set_ylim(140, 480)
    ax.legend(loc="lower right", handlelength=1.4)
    _panel(ax, "a")

    ax = axes[1]
    d = np.array([r["d"] for r in th]) * 1e3
    w = np.array([r["w_max_over_H0"] for r in th])
    ok = np.array([bool(r.get("converged")) for r in th])
    ax.plot(d[ok], w[ok], "o-", color=COL["blue"], lw=1.0, ms=3.0,
            label="coupled solution")
    ax.plot(d[~ok], w[~ok], "o", mfc="none", mec=COL["blue"], ms=3.5,
            label="predictor")
    ax.axhspan(0.45, 0.72, color=COL["grey"], alpha=0.12, lw=0)
    ax.axhline(0.45, color=COL["grey"], lw=0.6, ls="--")
    ax.text(d.min(), 0.462, "kinematic ceiling", fontsize=6.3, color=COL["grey"])
    ax.set_xlabel("$d$ (mm)")
    ax.set_ylabel("$w_{\\max}/H_0$")
    ax.set_ylim(0.3, 0.72)
    ax2 = ax.twinx()
    ok2 = ok
    ax2.plot(d[ok2], np.array([r["sigma_bend_max"] for r in th])[ok2] / 1e6, "s--",
             color=COL["orange"], lw=0.9, ms=2.5)
    ax2.set_ylabel("$\\sigma_b^{\\max}$ (MPa)", color=COL["orange"])
    ax2.tick_params(axis="y", colors=COL["orange"])
    ax2.set_ylim(3.4, 5.0)
    ax.legend(loc="upper right", handlelength=1.4)
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig07_sensitivity")


def fig_model_form(data: Path, out: _Out, cfg: Dict) -> None:
    """Model-form error of the frozen-force closure of the wall equation."""
    wa = _load(data, "wall_baseline.json")
    con = wa["consistency"]
    q = np.asarray(con["q"]) / 1e3
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4))
    ax = axes[0]
    ax.plot(q, 100 * np.asarray(con["rel_error"]), "o-", color=COL["blue"], lw=1.0,
            ms=2.5, label="bow: $(w_{fr}-w_{sc})/w_{sc}$")
    ax.plot(q, 100 * np.asarray(con["moment_error"]), "s--", color=COL["red"], lw=1.0,
            ms=2.5, label="moment: $(M_{fr}-M_{sc})/M_{sc}$")
    ax.plot(q, 100 * np.asarray(con["relaxation"]), "^-.", color=COL["green"], lw=1.0,
            ms=2.5, label="force relief $(|N_\\theta|-|N|)/|N_\\theta|$")
    ax.set_xlabel("$q''$ (kW m$^{-2}$)")
    ax.set_ylabel("relative difference (\\%)")
    ax.axhline(0, color="k", lw=0.5)
    ax.legend(loc="upper left", handlelength=1.8)
    _panel(ax, "a")

    ax = axes[1]
    ax.plot(np.asarray(con["N_over_Ncr"]), np.asarray(con["w_frozen"]) / cfg["geometry"]["H0"],
            "-", color=COL["blue"], lw=1.0, label="frozen force")
    ax.plot(np.asarray(con["N_over_Ncr"]),
            np.asarray(con["w_consistent"]) / cfg["geometry"]["H0"], "--",
            color=COL["green"], lw=1.0, label="self-consistent")
    ax.axhline(0.45, color=COL["grey"], lw=0.6, ls="--")
    ax.text(0.02, 0.46, "kinematic ceiling", fontsize=6.3, color=COL["grey"])
    ax.set_xlabel("$|N_\\theta|/N_{cr}$")
    ax.set_ylabel("$w_{\\max}/H_0$")
    ax.legend(loc="upper left", handlelength=1.6)
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig09_model_form")


# ---------------------------------------------------------------------------
#  Fig. 8 - verification
# ---------------------------------------------------------------------------
def fig_verification(data: Path, out: _Out, cfg: Dict) -> None:
    ben = _load(data, "verification_benchmarks.json")
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4))
    ax = axes[0]
    grids = ben["nusselt_grids"]
    keys = list(grids)
    total_nodes = [grids[k]["H2"]["n_nodes"] for k in keys]
    for kind, colour, label in [("H2", COL["blue"], "$H2$"), ("H1", COL["red"], "$H1$"),
                                ("T", COL["green"], "$T$"), ("T1", COL["purple"], "$T1$")]:
        vals = [grids[k][kind]["Nu"] for k in keys]
        ref = grids[keys[0]][kind]["Nu_reference"]
        ax.semilogx(np.array(total_nodes), (np.array(vals) - ref) / ref * 100, "o-",
                color=colour, lw=0.9, ms=2.5, label=label)
    ax.axhline(0.0, color="k", lw=0.6)
    ax.axhspan(-1, 1, color=COL["light"], alpha=0.25, lw=0)
    ax.set_xlabel("P2 temperature nodes, $N$")
    ax.set_ylabel("$Nu$ error (\\%)")
    ax.set_xticks(total_nodes)
    ax.set_xticklabels([f"{n / 1000:.1f}k" if n >= 1000 else str(n) for n in total_nodes])
    ax.minorticks_off()
    ax.legend(loc="lower right", ncol=2, handlelength=1.2, columnspacing=1.0)
    _panel(ax, "a")

    ax = axes[1]
    nu = ben["nusselt_summary"]
    labels = [r"$Nu_{H2}$", r"$Nu_{H1}$", r"$Nu_{T}$", r"$Nu_{T1}$"]
    keys2 = ["H2", "H1", "T", "T1"]
    vals = [nu[k]["Nu"] for k in keys2]
    refs = [nu[k]["reference"] for k in keys2]
    xx = np.arange(len(vals))
    ax.bar(xx - 0.18, refs, width=0.34, color=COL["light"], edgecolor="k", lw=0.4,
           label="reference")
    ax.bar(xx + 0.18, vals, width=0.34, color=COL["blue"], edgecolor="k", lw=0.4,
           label="computed")
    ax.set_xticks(xx)
    ax.set_xticklabels(labels)
    ax.set_ylabel("$Nu$")
    ax.set_ylim(0, 9.5)
    p = ben["poiseuille"]
    ax.text(0.5, 0.86, f"$f\\,Re_{{D_h}}$ = {p['f_Re']:.3f} (reference 96)",
            transform=ax.transAxes, fontsize=7, ha="center")
    ax.legend(loc="upper center", ncol=2, handlelength=1.0, framealpha=0.9,
              frameon=True, edgecolor="none")
    _panel(ax, "b")
    fig.tight_layout()
    out.save(fig, "fig08_verification")


# ---------------------------------------------------------------------------
def make_all(data: Path, figdir: Path, cfg: Dict) -> List[str]:
    plt.rcParams.update(STYLE)
    out = _Out(figdir)
    made: List[str] = []
    for fn, args in ((fig_geometry, (cfg, out)),
                     (fig_mesh, (data, out, cfg)),
                     (fig_flow, (data, out, cfg)),
                     (fig_thermal, (data, out, cfg)),
                     (fig_wall, (data, out, cfg)),
                     (fig_convergence, (data, out, cfg)),
                     (fig_sensitivity, (data, out, cfg)),
                     (fig_verification, (data, out, cfg)),
                     (fig_model_form, (data, out, cfg))):
        try:
            fn(*args)
            made.append(fn.__name__)
        except FileNotFoundError as exc:
            print(f"  [figures] skipped {fn.__name__}: {exc}")
    print(f"  [figures] {len(made)} figures written to {figdir}")
    return made
