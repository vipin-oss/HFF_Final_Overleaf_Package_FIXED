"""Collapse of the hydraulic feedback over the whole parameter space.

Every converged coupled computation of the five sweeps (heat flux, wall
thickness, wall conductivity, thermal expansion and Reynolds number) is a run
with its own bow ratio ``a = w_max/H0``.  Two questions are answered here.

1. Is the hydraulic feedback a function of ``a`` alone?  The *master curve* is
   the single integral ``Pi(a) = int_0^1 dxi/(1 - a wh_hat)^3`` evaluated with
   ``wh_hat`` taken from the design-point shape and nothing else: no parameter
   enters, and no coefficient is fitted.  The script measures how far every run
   of every sweep lies from that one curve.
2. How do the two design alternatives compare with it?  The sine-squared closed
   form (a different shape) and the moment series truncated at ``O(a^3)`` (the
   same shape, truncated) are evaluated run by run.

Writes
    outputs/data/collapse.json
    outputs/tables/table_collapse.tex
    outputs/figures/fig16_collapse.{pdf,png}

Usage:  ./.venv/bin/python tools/collapse_analysis.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
from scipy.special import hyp2f1

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hff import asymptotics, config  # noqa: E402
from hff.figures import COL, STYLE, _Out, _panel  # noqa: E402

OUT = ROOT / "outputs"
DATA = OUT / "data"


def _runs(cfg: dict) -> list[dict]:
    """Collect the converged runs of every sweep with the data needed here."""
    g, op, f = cfg["geometry"], cfg["operating"], cfg["fluid"]
    H0, L, Le, Lo = g["H0"], g["L"], g["Le"], g["Lo"]
    mu, rho = f["mu"], f["rho"]
    runs: list[dict] = []

    base = json.loads((DATA / "coupled_baseline.json").read_text())
    runs.append({"family": "design point", "label": "design point",
                 "U": float(op["U"]), "dp": float(base["metrics"]["flow_dp"]),
                 "a": float(base["metrics"]["w_max_over_H0"])})

    def add(family: str, label: str, row: dict, dp_key: str, U=None):
        if not row.get("converged"):
            return
        if U is None:
            U = float(row["Re_Dh"]) * mu / (rho * 2.0 * H0)
        runs.append({"family": family, "label": label, "U": float(U),
                     "dp": float(row[dp_key]),
                     "a": float(row["w_max_over_H0"])})

    for row in json.loads((DATA / "sweep_flux.json").read_text()):
        add("heat flux", f"{row['q_flux'] / 1e3:g} kW/m2", row, "flow_dp", U=op["U"])
    for row in json.loads((DATA / "sweep_thickness.json").read_text()):
        add("thickness", f"d = {row['d'] * 1e3:g} mm", row, "flow_dp", U=op["U"])
    for row in json.loads((DATA / "sweep_conductivity.json").read_text()):
        add("conductivity", f"ks = {row['value']:g}", row, "dp", U=op["U"])
    for row in json.loads((DATA / "sweep_expansion.json").read_text()):
        add("expansion", f"alpha = {row['value']:.1e}", row, "dp", U=op["U"])
    for row in json.loads((DATA / "sweep_reynolds.json").read_text()):
        add("Reynolds", f"Re = {row['Re_Dh']:g}", row, "dp")

    for r in runs:
        Q = r["U"] * H0
        r["strip0"] = 12.0 * mu * Q * L / H0 ** 3
        r["rigid"] = 12.0 * mu * Q * (Le + Lo) / H0 ** 3
        r["Pi"] = (r["dp"] - r["rigid"]) / r["strip0"]
        r["Pi_sin2"] = float(hyp2f1(3.0, 0.5, 1.0, min(r["a"], 0.98)))
        r["Re_Dh"] = float(r["U"]) * 2.0 * H0 * rho / mu
    return runs


def main() -> None:
    cfg = config.load("params/baseline.json")
    runs = _runs(cfg)

    base = json.loads((DATA / "coupled_baseline.json").read_text())
    x = np.asarray(base["x"], dtype=float)
    w = np.asarray(base["w"], dtype=float)
    H0 = float(cfg["geometry"]["H0"])
    a_ref = float(w.max() / H0)
    ref = {"x": x, "wh_ref": w / H0 / a_ref}
    moments = asymptotics.self_similarity_moments(x, w)

    def master(a: float) -> tuple[float, float]:
        """Exact integral of the design-point shape, and its O(a^3) truncation."""
        res = asymptotics.pressure_series(ref, float(a))
        return res["exact"], res["series"]

    for r in runs:
        r["Pi_master"], r["Pi_series"] = master(r["a"])
        r["err_master"] = (r["Pi_master"] - r["Pi"]) / r["Pi"]
        r["err_series"] = (r["Pi_series"] - r["Pi"]) / r["Pi"]
        r["err_sin2"] = (r["Pi_sin2"] - r["Pi"]) / r["Pi"]
        r["err_sin2_total"] = ((r["rigid"] + r["strip0"] * r["Pi_sin2"]) - r["dp"]) / r["dp"]

    e_master = np.array([abs(r["err_master"]) for r in runs])
    e_series = np.array([abs(r["err_series"]) for r in runs])
    e_sin2 = np.array([abs(r["err_sin2"]) for r in runs])
    e_sin2_tot = np.array([abs(r["err_sin2_total"]) for r in runs])

    families: dict[str, dict] = {}
    for r in runs:
        fam = families.setdefault(r["family"], {"n": 0, "a_min": 9.0, "a_max": 0.0,
                                                "master": 0.0, "sin2": 0.0})
        fam["n"] += 1
        fam["a_min"] = min(fam["a_min"], r["a"])
        fam["a_max"] = max(fam["a_max"], r["a"])
        fam["master"] = max(fam["master"], abs(r["err_master"]))
        fam["sin2"] = max(fam["sin2"], abs(r["err_sin2"]))

    out = {
        "n_runs": len(runs),
        "a_min": float(min(r["a"] for r in runs)),
        "a_max": float(max(r["a"] for r in runs)),
        "Re_min": float(min(r["Re_Dh"] for r in runs)),
        "Re_max": float(max(r["Re_Dh"] for r in runs)),
        "master_max_abs_rel_error": float(e_master.max()),
        "master_mean_abs_rel_error": float(e_master.mean()),
        "series_max_abs_rel_error": float(e_series.max()),
        "sin2_max_abs_rel_error": float(e_sin2.max()),
        "sin2_max_abs_rel_error_total": float(e_sin2_tot.max()),
        "moments_c": moments["c"],
        "moments_C": moments["C"],
        "families": families,
        "runs": runs,
    }
    (DATA / "collapse.json").write_text(json.dumps(out, indent=1))

    # ------------------------------------------------------------------ table
    lines = [
        "% generated by tools/collapse_analysis.py -- do not edit",
        r"\begin{table}[htbp]", r"\centering",
        r"\caption{Collapse of the hydraulic feedback over the five sweeps "
        f"($n={len(runs)}$ converged coupled runs, "
        f"$\\mathrm{{Re}}_{{D_h}}={out['Re_min']:.0f}$--${out['Re_max']:.0f}$). "
        r"$\Pi=\Delta p_{\rm strip}/\Delta p_{\rm strip,0}$, $a=w_{\max}/H_0$. "
        r"$\epsilon_{\rm master}$ is the error of the single integral of the design-point "
        r"shape \eqref{eq:master}, which uses no fitted coefficient, and "
        r"$\epsilon_{\sin^2}$ the error of the kinematic design law at the same $a$.}",
        r"\label{tab:collapse}", r"\small",
        r"\begin{tabular}{@{}lrrrr@{}}", r"\toprule",
        r"Sweep & $n$ & $a$ range & max $|\epsilon_{\rm master}|$ (\%) & "
        r"max $|\epsilon_{\sin^2}|$ (\%) \\", r"\midrule",
    ]
    for fam, s in families.items():
        lines.append(f"{fam} & {s['n']} & {s['a_min']:.3f}--{s['a_max']:.3f} & "
                     f"{100 * s['master']:.2f} & {100 * s['sin2']:.1f} \\\\")
    lines += [r"\midrule",
              f"all & {len(runs)} & {out['a_min']:.3f}--{out['a_max']:.3f} & "
              f"{100 * out['master_max_abs_rel_error']:.2f} & "
              f"{100 * out['sin2_max_abs_rel_error']:.1f} \\\\",
              r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "tables" / "table_collapse.tex").write_text("\n".join(lines))

    # ----------------------------------------------------------------- figure
    import matplotlib.pyplot as plt  # noqa: E402

    plt.rcParams.update(STYLE)
    out_fig = _Out(OUT / "figures")
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.5))
    order = ["design point", "heat flux", "thickness", "conductivity", "expansion",
             "Reynolds"]
    colors = ["k", COL["blue"], COL["green"], COL["orange"],
              COL["purple"], COL["grey"]]
    markers = ["*", "o", "s", "^", "D", "v"]

    ax = axes[0]
    aa = np.linspace(0.0, out["a_max"] * 1.02, 240)
    ax.plot(aa, [master(v)[0] for v in aa], "-", lw=1.0, color="k",
            label="master integral, no fit")
    ax.plot(aa, hyp2f1(3.0, 0.5, 1.0, np.minimum(aa, 0.98)), "--", lw=0.9,
            color=COL["red"], label=r"$\sin^2$ design law")
    for fam, col, mk in zip(order, colors, markers):
        sel = [r for r in runs if r["family"] == fam]
        if not sel:
            continue
        ax.plot([r["a"] for r in sel], [r["Pi"] for r in sel], mk, ms=3.0,
                mfc="none", color=col, label=fam)
    ax.set_xlabel(r"$a=w_{\max}/H_0$")
    ax.set_ylabel(r"$\Pi=\Delta p_{\rm strip}/\Delta p_{\rm strip,0}$")
    ax.legend(loc="upper left", handlelength=1.2, borderpad=0.2,
              labelspacing=0.18, fontsize=5.4)
    _panel(ax, "a")

    ax = axes[1]
    ax.plot(aa, [100 * (hyp2f1(3.0, 0.5, 1.0, min(v, 0.98)) - master(v)[0])
                 / master(v)[0] for v in aa], "--", lw=0.9, color=COL["red"],
            label=r"$\sin^2$ law vs master")
    for fam, col, mk in zip(order, colors, markers):
        sel = [r for r in runs if r["family"] == fam]
        if not sel:
            continue
        ax.plot([r["a"] for r in sel], [100 * r["err_master"] for r in sel], mk,
                ms=3.0, mfc="none", color=col)
    ax.axhline(0.0, color=COL["grey"], lw=0.6)
    ax.set_xlabel(r"$a=w_{\max}/H_0$")
    ax.set_ylabel("deviation (%)")
    ax.legend(loc="lower left", handlelength=1.2, borderpad=0.2,
              labelspacing=0.18, fontsize=5.6)
    _panel(ax, "b")
    fig.tight_layout()
    out_fig.save(fig, "fig16_collapse")

    print(json.dumps({k: v for k, v in out.items() if k not in ("runs",)}, indent=1))


if __name__ == "__main__":
    main()
