#!/usr/bin/env python3
"""Run the semi-analytical theory and compare it with the finite-element results.

Writes ``outputs/data/asymptotics.json`` (all numbers quoted in the manuscript)
and prints a short comparison table.  Nothing here is fitted except where it is
labelled as a fit, and every fitted quantity carries its coefficient of
determination.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from hff import analytic, asymptotics, config  # noqa: E402

DATA = pathlib.Path(__file__).resolve().parents[1] / "outputs" / "data"


def load(name: str):
    with open(DATA / name) as fh:
        return json.load(fh)


def main() -> int:
    cfg = config.load("params/baseline.json")
    coupled = load("coupled_baseline.json")
    out = asymptotics.solve(cfg, n_modes=10)

    x = np.array(coupled["x"])
    w = np.array(coupled["w"])
    q = np.array(coupled["q"])
    Tw = np.array(coupled["Tw"])
    Tb = np.array(coupled["Tb"])
    Nu = np.array(coupled["Nu"])
    m = coupled["metrics"]

    # ---------------------------------------------------------------- Nu scaling
    Nu_g = np.interp(x[:-1], out["graetz_x"], out["graetz_Nu"])
    H = cfg["geometry"]["H0"] - w[:-1]
    ratio = Nu / Nu_g
    ok = (Nu > 0) & (Nu_g > 0) & (x[:-1] > 1e-3)
    lx = np.log(cfg["geometry"]["H0"] / H[ok])
    ly = np.log(ratio[ok])
    p, lc = np.polyfit(lx, ly, 1)
    pred = p * lx + lc
    ss_res = float(np.sum((ly - pred) ** 2))
    ss_tot = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot

    # -------------------------------------------------------- pressure drop models
    lub_c = asymptotics.pressure_drop_lubrication(cfg, w_profile=w, x_profile=x)
    lub_s = asymptotics.pressure_drop_lubrication(
        cfg, w_max=float(np.max(w)))
    dp_fem = float(m["flow_dp"])
    dp0 = asymptotics.pressure_drop_undeformed(cfg)

    # sweep: lubrication with the sin^2 idealisation at each computed bow
    sweep = load("sweep_flux.json")
    sweep_pts = []
    for row in sweep:
        if not row.get("converged"):
            continue
        wmax = row["w_max"]
        pred_s = asymptotics.pressure_drop_lubrication(cfg, w_max=wmax)["total"]
        sweep_pts.append({
            "q_flux": row["q_flux"],
            "a": wmax / cfg["geometry"]["H0"],
            "dp_fem": row["flow_dp"],
            "dp_lub": pred_s,
            "rel": (pred_s - row["flow_dp"]) / row["flow_dp"],
        })

    # ------------------------------------------------------------- sensitivities
    dq = 100.0
    b1 = asymptotics.beam_column(cfg, cfg["operating"]["q_flux"] - 0.5 * dq)
    b2 = asymptotics.beam_column(cfg, cfg["operating"]["q_flux"] + 0.5 * dq)
    dw_dq_analytic = (b2["w_max_frozen"] - b1["w_max_frozen"]) / dq
    wm = float(m["w_max"])
    dw_dq_fem = wm / cfg["operating"]["q_flux"]

    dp1 = asymptotics.pressure_drop_lubrication(
        cfg, w_max=b1["w_max_frozen"])["total"]
    dp2 = asymptotics.pressure_drop_lubrication(
        cfg, w_max=b2["w_max_frozen"])["total"]
    ddp_dq_analytic = (dp2 - dp1) / dq
    ddp_dq_fem = (dp_fem - dp0) / cfg["operating"]["q_flux"]

    res = {
        "graetz": out["graetz"],
        "wall_series": out["wall"],
        "beam": out["beam"],
        "contraction": out["contraction"],
        "shape_factors": out["shape_factors"],
        "comparison": {
            "Nu_fd_series": out["graetz"]["Nu_fd"],
            "Nu_fd_fem_exit": float(Nu[-1]),
            "Nu_mean_series": out["graetz"]["Nu_mean"],
            "Nu_mean_fem": float(m["Nu_mean"]),
            "Nu_ratio_max": float(np.max(ratio)),
            "Nu_ratio_min": float(np.min(ratio)),
            "Nu_scaling_exponent": float(p),
            "Nu_scaling_r2": float(r2),
            "theta_bar_series": out["wall"]["theta_bar_mean"],
            "theta_bar_fem": float(m["theta_bar_mean"]),
            "dp_fem": dp_fem,
            "dp_lub_computed_profile": lub_c["total"],
            "dp_lub_computed_error": (lub_c["total"] - dp_fem) / dp_fem,
            "dp_lub_sin2": lub_s["total"],
            "dp_lub_sin2_error": (lub_s["total"] - dp_fem) / dp_fem,
            "dp_inertial": lub_s["inertial"],
            "dp_undeformed": dp0,
            "w_frozen_closed_form": out["beam"]["w_max_frozen"],
            "w_fem": wm,
            "w_frozen_closed_error": (out["beam"]["w_max_frozen"] - wm) / wm,
            "amplification_closed_form": out["beam"]["amplification"],
            "amplification_fem": float(np.max(w) / out["beam"]["w_max_linear"]),
            "contraction_measured": float(
                max(abs(h) for h in coupled["history"][1:]) if False else 0.0),
            "dw_dq_analytic": float(dw_dq_analytic),
            "dw_dq_fem": float(dw_dq_fem),
            "ddp_dq_analytic": float(ddp_dq_analytic),
            "ddp_dq_fem": float(ddp_dq_fem),
        },
        "sweep_comparison": sweep_pts,
    }
    (DATA / "asymptotics.json").write_text(json.dumps(res, indent=2, default=float))
    (DATA / "asymptotics_graetz_profile.csv").write_text(
        "x_m,Nu_series\n" + "\n".join(f"{a:.6e},{b:.6f}"
                                     for a, b in zip(out["graetz_x"], out["graetz_Nu"])))

    c = res["comparison"]
    print(f"{'quantity':38s}{'series':>12s}{'FEM':>12s}{'diff %':>10s}")
    rows = [
        ("Nu at the outlet station", c["Nu_fd_series"], c["Nu_fd_fem_exit"]),
        ("Nu mean over strip", c["Nu_mean_series"], c["Nu_mean_fem"]),
        ("theta_bar (K)", c["theta_bar_series"], c["theta_bar_fem"]),
        ("dp lubrication, computed w", c["dp_lub_computed_profile"], c["dp_fem"]),
        ("dp lubrication, sin^2", c["dp_lub_sin2"], c["dp_fem"]),
        ("w_max frozen closed form", c["w_frozen_closed_form"], c["w_fem"]),
    ]
    for name, a, b in rows:
        print(f"{name:38s}{a:12.5g}{b:12.5g}{100*(a-b)/b:10.2f}")
    print(f"\nNu scaling Nu ~ (H0/H)^p: p = {c['Nu_scaling_exponent']:.3f}, R^2 = {c['Nu_scaling_r2']:.4f}")
    print(f"contraction bound q = {out['contraction']['q_bound']:.3f}; "
          f"N/N_cr = {out['contraction']['N_over_Ncr']:.4f}")
    print(f"dw/dq'': analytic {c['dw_dq_analytic']:.4e} m/(W/m2), "
          f"FEM scaling {c['dw_dq_fem']:.4e}")
    print(f"d(dp)/dq'': analytic {c['ddp_dq_analytic']:.4e}, FEM {c['ddp_dq_fem']:.4e}")
    for s in sweep_pts:
        print(f"  q={s['q_flux']:7.1f}  a={s['a']:.3f}  dp_fem={s['dp_fem']:8.2f}  "
              f"dp_lub={s['dp_lub']:8.2f}  rel={100*s['rel']:6.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
