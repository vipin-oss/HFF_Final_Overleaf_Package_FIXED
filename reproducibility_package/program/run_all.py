#!/usr/bin/env python3
"""Main entry point of the heat-transfer / flow / wall (HFF) study.

Usage
-----
    python run_all.py                 # full study (default)
    python run_all.py --quick         # coarse meshes and shortened sweeps
    python run_all.py --only bench    # only the verification suite
    python run_all.py --params my.json

Stages
------
``analytic``  closed-form baseline of the formulation (Table 3)
``wall``      reduced beam--column wall model, frozen and self-consistent
``bench``     code-verification benchmarks (Poiseuille, Nusselt, wall limits)
``coupled``   partitioned fluid--thermal--structure solution (baseline point)
``mesh``      mesh-refinement study of the coupled result
``sweep``     imposed-flux and wall-thickness sweeps of the coupled result
``figures``   publication figures from the saved results
``tables``    LaTeX tables from the saved results

Every number written to ``outputs/data`` is produced by the code in this run; the
figures and tables are generated *from those files*, so the manuscript can be rebuilt
from the saved numerical results without re-running the solvers.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from hff import analytic, benchmarks, config, coupled, fem, flow, tables, thermal, wall  # noqa: E402

OUT = HERE / "outputs"
DATA = OUT / "data"
FIG = OUT / "figures"
TAB = OUT / "tables"


def _ensure_dirs() -> None:
    for d in (DATA, FIG, TAB):
        d.mkdir(parents=True, exist_ok=True)


def _write_json(name: str, payload: Any) -> Path:
    path = DATA / name
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2, default=_json_default)
    return path


def _json_default(obj):
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"not JSON serialisable: {type(obj)}")


def _save_csv(name: str, rows: List[Dict[str, Any]], header: List[str]) -> Path:
    path = DATA / name
    with open(path, "w") as fh:
        fh.write(",".join(header) + "\n")
        for r in rows:
            fh.write(",".join(_fmt(r.get(h)) for h in header) + "\n")
    return path


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.10g}"
    return str(v)


# ---------------------------------------------------------------------------
#  stages
# ---------------------------------------------------------------------------
def stage_analytic(cfg: Dict, quick: bool) -> Dict[str, Any]:
    print("[analytic] closed-form baseline")
    rows = analytic.baseline(cfg)
    _save_csv("table_analytic_baseline.csv", rows,
              ["symbol", "value", "unit", "expression", "kind"])
    doc: Dict[str, Any] = {
        "rows": rows,
        "groups": analytic.groups(cfg),
        "derived": config.derived(cfg),
        "strip_pressure": analytic.strip_pressure(cfg),
        "theta_bar_estimate": analytic.theta_bar_estimate(cfg),
        "time_scales": analytic.time_scales(cfg),
        "critical_temperature": analytic.critical_temperature(cfg),
        "pressure_drop": analytic.pressure_drop(cfg),
    }
    print(f"           {len(rows)} rows; kappa_th = {analytic.kappa_th(cfg):.6g} 1/m, "
          f"N_theta = {analytic.membrane_force(cfg, analytic.theta_bar_estimate(cfg)['theta_bar']):.6g} N/m")
    _write_json("analytic_baseline.json", doc)
    return doc


def stage_wall(cfg: Dict, quick: bool) -> Dict[str, Any]:
    print("[wall] beam--column solution (frozen force and self-consistent)")
    g = cfg["geometry"]
    x = np.linspace(0.0, g["L"], int(cfg["numerics"]["wall"]["n_points"]))
    Ds = config.derived(cfg)["Ds"]
    kap = analytic.kappa_th(cfg)
    th = analytic.theta_bar_estimate(cfg)["theta_bar"]
    N0 = analytic.membrane_force(cfg, th)
    frozen = wall.solve_wall(x, Ds, np.full_like(x, kap), N=abs(N0))
    consistent = wall.self_consistent(x, Ds, np.full_like(x, kap), th, cfg)
    bank = benchmarks.benchmark_wall(cfg)
    # model-form error of the frozen-force closure (slow at 241 nodes: coarsen the grid)
    c_con = json.loads(json.dumps(cfg))
    c_con["numerics"]["wall"]["n_points"] = 121
    consistency = wall.consistency_error_curve(c_con, n_q=31)

    def _series(st):
        return {
            "x": st.x.tolist(), "w": st.w.tolist(), "moment": st.moment.tolist(),
            "kappa_geo": st.kappa_geo.tolist(), "slope": st.theta.tolist(),
            "sigma_bend": st.bending_stress(g["d"]).tolist(),
        }

    doc = {
        "frozen": {**_series(frozen), "w_max": frozen.w_max, "N": frozen.N,
                   "M_mid": float(np.interp(0.5 * g["L"], x, frozen.moment)),
                   "slope_max": frozen.slope_max, "arc": frozen.arc},
        "self_consistent": {**_series(consistent), "w_max": consistent.w_max,
                            "N": consistent.N, "N_theta": consistent.N_theta,
                            "converged": bool(consistent.converged),
                            "n_iter": int(consistent.n_iter),
                            "M_mid": float(np.interp(0.5 * g["L"], x, consistent.moment)),
                            "history": consistent.history},
        "benchmarks": bank,
        "consistency": {k: np.asarray(v).tolist() for k, v in consistency.items()},
        "design_envelope": wall.design_envelope(cfg),
        "buckling_catalog": wall.buckling_catalog(cfg, np.linspace(1e-3, 6e-3, 11)),
    }
    print(f"           frozen-force error: {100 * consistency['rel_error'][2]:.2f}% at "
          f"q''=0.1e4, {100 * consistency['rel_error'][-1]:.1f}% at q''=1.0e4")
    print(f"           frozen w_max = {frozen.w_max:.6e} m ({frozen.w_max / g['H0']:.4f} H0); "
          f"self-consistent w_max = {consistent.w_max:.6e} m, N = {consistent.N:.2f} N/m "
          f"({'converged' if consistent.converged else 'NOT converged'})")
    _write_json("wall_baseline.json", doc)
    return doc


def stage_benchmarks(cfg: Dict, quick: bool) -> Dict[str, Any]:
    print("[bench] verification suite")
    nx, ny = (60, 6) if quick else (120, 10)
    poise = benchmarks.benchmark_poiseuille(cfg, nx=nx, ny=ny)
    print(f"           f Re = {poise['f_Re']:.6f} (reference 96), "
          f"profile error {poise['u_profile_L2_rel']:.2e}")

    grids = [(80, 8), (160, 12), (320, 18)] if quick else \
            [(100, 6), (200, 10), (300, 16), (450, 24)]
    thermal_runs = {}
    for nx_t, ny_t in grids:
        key = f"nx{nx_t}_ny{ny_t}"
        thermal_runs[key] = benchmarks.benchmark_all_thermal(cfg, nx=nx_t, ny=ny_t,
                                                             length_over_H=200.0)
        best = thermal_runs[key]
        print(f"           grid {key:14s} " + "  ".join(
            f"{k} {v['Nu']:.4f}" for k, v in best.items()))

    finest_key = list(thermal_runs)[-1]
    finest = thermal_runs[finest_key]
    summary = {k: {"Nu": finest[k]["Nu"], "reference": finest[k]["Nu_reference"],
                   "rel_error": finest[k]["rel_error"]} for k in finest}
    wall_bank = benchmarks.benchmark_wall(cfg)
    doc = {"poiseuille": poise, "nusselt_grids": thermal_runs,
           "nusselt_summary": summary, "wall": wall_bank,
           "references": {
               "f_Re": "Shah & London (1978), plane channel, D_h = 2H",
               "Nu": benchmarks.NU_REFERENCE,
           }}
    _write_json("verification_benchmarks.json", doc)
    _save_csv("verification_nusselt.csv",
              [{"grid": k, "kind": kk, "Nu": vv["Nu"], "reference": vv["Nu_reference"],
                "rel_error": vv["rel_error"]}
               for k, run in thermal_runs.items() for kk, vv in run.items()],
              ["grid", "kind", "Nu", "reference", "rel_error"])
    return doc


def stage_coupled(cfg: Dict, quick: bool, tag: str = "baseline") -> Dict[str, Any]:
    print(f"[coupled] partitioned fluid-thermal-structure solution ({tag})")
    t0 = time.time()
    res = coupled.solve_coupled(cfg, verbose=True)
    dt = time.time() - t0
    metrics = res.metrics(cfg)
    nu = thermal.nusselt_profile(res.thermal, cfg) if res.thermal is not None else {}
    # sampled fields for the figures
    samples = {"stations": [], "profiles": [], "p_iface": None, "x_iface": None,
               "p_bottom": None, "u_centre": None}
    if res.flow is not None:
        fl = res.flow.mesh
        xcols = np.array([fl.xy[fl.grid[0, i], 0] for i in range(fl.grid.shape[1])])
        for xs in (0.002, 0.008, 0.015, 0.022, 0.028):
            i = int(np.argmin(np.abs(xcols - xs)))
            ids = fl.grid[:, i]
            samples["stations"].append(float(xcols[i]))
            samples["profiles"].append({"y": fl.xy[ids, 1].tolist(),
                                        "u": res.flow.u[ids, 0].tolist(),
                                        "x": float(xcols[i])})
        pairs = fl.boundary["interface"]
        xif = 0.5 * (fl.xy[pairs[:, 0], 0] + fl.xy[pairs[:, 1], 0])
        pif = 0.5 * (res.flow.p[pairs[:, 0]] + res.flow.p[pairs[:, 1]])
        o = np.argsort(xif)
        samples["x_iface"] = xif[o].tolist()
        samples["p_iface"] = pif[o].tolist()
        pb = np.array([np.mean(res.flow.p[fl.grid[:, i]]) for i in range(fl.grid.shape[1])])
        samples["x_columns"] = xcols.tolist()
        samples["p_columns"] = pb.tolist()
        ymid = fl.grid[fl.grid.shape[0] // 2, :]
        samples["u_centre"] = (res.flow.u[ymid, 0]).tolist()

    doc = {
        "tag": tag,
        "converged": bool(res.converged),
        "termination": res.termination,
        "iterations": int(res.iterations),
        "runtime_s": float(dt),
        "metrics": metrics,
        "w": res.w.tolist(),
        "x": res.x.tolist(),
        "q": np.asarray(nu.get("q", [])).tolist(),
        "Tw": np.asarray(nu.get("Tw", [])).tolist(),
        "Tb": np.asarray(nu.get("Tb", [])).tolist(),
        "Nu": np.asarray(nu.get("Nu", [])).tolist(),
        "Nu_x": np.asarray(nu.get("x", [])).tolist(),
        "history": res.history,
        "theta_bar": res.thermal_theta_bar.tolist() if res.thermal_theta_bar is not None else [],
        "samples": samples,
        "geometry": {"H0": cfg["geometry"]["H0"], "L": cfg["geometry"]["L"],
                     "Le": cfg["geometry"]["Le"], "Lo": cfg["geometry"]["Lo"],
                     "d": cfg["geometry"]["d"]},
        "numerics": {k: cfg["numerics"][k] for k in
                     ("nx_heated", "nx_entrance", "nx_exit", "ny_fluid", "ny_solid")},
    }
    print(f"           w_max/H0 = {metrics['w_max_over_H0']:.5f}, dT_bar = "
          f"{metrics['theta_bar_mean']:.3f} K, dp = {metrics['flow_dp']:.2f} Pa, "
          f"Nu_out = {metrics['Nu_outlet']:.3f}, {res.iterations} iterations, {dt:.1f} s")
    _write_json(f"coupled_{tag}.json", doc)
    return doc


def stage_mesh_study(cfg: Dict, quick: bool) -> Dict[str, Any]:
    print("[mesh] refinement study of the coupled solution")
    if quick:
        levels = [(40, 8, 4), (60, 10, 5)]
    else:
        levels = [(60, 8, 4), (120, 10, 6), (240, 16, 8)]
    runs = []
    for (nxd, nyf, nys) in levels:
        c = json.loads(json.dumps(cfg))
        c["numerics"]["nx_heated"] = nxd
        c["numerics"]["nx_solid"] = nxd
        c["numerics"]["ny_fluid"] = nyf
        c["numerics"]["ny_solid"] = nys
        c["numerics"]["nx_entrance"] = max(6, nxd // 10)
        c["numerics"]["nx_exit"] = max(6, nxd // 10)
        c["numerics"]["wall"]["n_points"] = nxd + 1
        res = coupled.solve_coupled(c, verbose=False)
        m = res.metrics(c)
        runs.append({"nx_heated": nxd, "ny_fluid": nyf, "ny_solid": nys,
                     "w_max_over_H0": m["w_max_over_H0"], "w_max": m["w_max"],
                     "dp": m["flow_dp"], "theta_bar_mean": m["theta_bar_mean"],
                     "Nu_mean": m["Nu_mean"], "sigma_bend_max": m["sigma_bend_max"],
                     "M_mid": m["M_mid"], "energy_imbalance": m["energy_imbalance"],
                     "iterations": res.iterations, "converged": res.converged})
        print("           mesh {:>4d}x{:>2d}x{:>2d}: w_max/H0 = {:.6f}, dp = {:.3f} Pa".format(
            nxd, nyf, nys, m["w_max_over_H0"], m["flow_dp"]))

    # observed order from the three finest levels (uniform refinement factor 2)
    order = {}
    if len(runs) >= 3:
        f = [r["w_max"] for r in runs[-3:]]
        h = [1.0 / r["nx_heated"] for r in runs[-3:]]
        try:
            p = float(np.log(abs((f[2] - f[1]) / (f[1] - f[0]))) / np.log(h[1] / h[0]))
        except (ZeroDivisionError, ValueError):
            p = float("nan")
        ext = float(f[2] + (f[2] - f[1]) / (2**p - 1)) if np.isfinite(p) else float("nan")
        order = {"observed_order_w_max": p, "richardson_extrapolated_w_max": ext,
                 "finest_rel_change": float(abs(f[2] - f[1]) / abs(f[2]))}
        print(f"           observed order (w_max) = {p:.2f}, Richardson limit = {ext:.6e} m")
    doc = {"levels": runs, "order": order}
    _write_json("mesh_study.json", doc)
    return doc


def stage_sweeps(cfg: Dict, quick: bool) -> Dict[str, Any]:
    print("[sweep] imposed-flux and wall-thickness sweeps")
    q_values = ([1e3, 2e3, 3e3, 3.5e3, 4e3, 4.5e3, 5e3, 5.25e3, 5.5e3] if not quick
                else [2e3, 5e3, 7e3])
    flux_rows = []
    for q in q_values:
        c = json.loads(json.dumps(cfg))
        c["operating"]["q_flux"] = float(q)
        if quick:
            c["numerics"]["nx_heated"] = 60
            c["numerics"]["nx_solid"] = 60
            c["numerics"]["ny_fluid"] = 8
            c["numerics"]["wall"]["n_points"] = 61
        res = coupled.solve_coupled(c, verbose=False)
        m = res.metrics(c)
        row = {"q_flux": float(q), **{k: m[k] for k in
               ("w_max_over_H0", "w_max", "theta_bar_mean", "flow_dp", "Nu_mean",
                "sigma_bend_max", "M_mid", "N_membrane", "energy_imbalance", "arc")},
               "termination": res.termination, "converged": res.converged,
               "iterations": res.iterations}
        if not res.converged:
            # the reported bow is the first-iteration predictor (the fixed point was not
            # followed); the flow quantities belong to the undeformed passage and are not
            # part of the coupled state, so they carry a validity note
            row["predictor_w_max_over_H0"] = row["w_max_over_H0"]
            row["validity"] = ("uncoupled predictor only: the predicted bow exceeds the "
                              "kinematic ceiling, no coupled state within model validity")
        flux_rows.append(row)
        print("           q'' = {:7.0f} W/m2: w_max/H0 = {:.4f}, dT = {:.2f} K, "
              "dp = {:.1f} Pa, {}".format(q, m["w_max_over_H0"], m["theta_bar_mean"],
                                          m["flow_dp"], res.termination))
    _write_json("sweep_flux.json", flux_rows)

    d_values = [2.5e-3, 3e-3, 4e-3] if quick else \
        [2.5e-3, 3e-3, 3.5e-3, 4e-3, 5e-3, 6e-3, 8e-3]
    thick_rows = []
    for d in d_values:
        c = json.loads(json.dumps(cfg))
        c["geometry"]["d"] = float(d)
        if quick:
            c["numerics"]["nx_heated"] = 60
            c["numerics"]["nx_solid"] = 60
            c["numerics"]["ny_fluid"] = 8
            c["numerics"]["wall"]["n_points"] = 61
        res = coupled.solve_coupled(c, verbose=False)
        m = res.metrics(c)
        row = {"d": float(d), **{k: m[k] for k in
               ("w_max_over_H0", "w_max", "theta_bar_mean", "flow_dp", "sigma_bend_max",
                "M_mid", "N_membrane", "arc", "Nu_mean")},
               "T_cr": analytic.critical_temperature(c), "Ds": config.derived(c)["Ds"],
               "termination": res.termination, "converged": res.converged}
        if not res.converged:
            row["validity"] = ("uncoupled predictor only: the predicted bow exceeds the "
                              "kinematic ceiling")
        thick_rows.append(row)
        print("           d = {:.2e} m: w_max/H0 = {:.4f}, sigma_bend = {:.2f} MPa, {}".format(
            d, m["w_max_over_H0"], m["sigma_bend_max"] / 1e6,
            "converged" if res.converged else "outside model validity"))
    _write_json("sweep_thickness.json", thick_rows)
    return {"flux": flux_rows, "thickness": thick_rows}


def stage_figures(cfg: Dict, quick: bool) -> None:
    print("[figures] rendering")
    from hff import figures
    figures.make_all(DATA, FIG, cfg)


def stage_tables(cfg: Dict, quick: bool) -> None:
    print("[tables] LaTeX tables")
    tables.make_all(DATA, TAB)


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--params", default=str(HERE / "params" / "baseline.json"))
    ap.add_argument("--quick", action="store_true",
                    help="coarse meshes and short sweeps (used by the test suite)")
    ap.add_argument("--only", default="all",
                    help="comma-separated stage list, e.g. figures,tables "
                         "(default: all)")
    ap.add_argument("--skip-sweeps", action="store_true")
    args = ap.parse_args(argv)

    _ensure_dirs()
    cfg = config.load(args.params)
    started = time.time()
    meta = {
        "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "parameters": cfg,
        "quick": bool(args.quick),
    }
    try:
        import scipy
        meta["scipy"] = scipy.__version__
    except Exception:                                        # pragma: no cover
        meta["scipy"] = "not available"
    try:
        import matplotlib
        meta["matplotlib"] = matplotlib.__version__
    except Exception:                                        # pragma: no cover
        meta["matplotlib"] = "not available"

    stages = ("analytic", "wall", "bench", "coupled", "mesh", "sweep",
              "figures", "tables")
    only = set(stages) if args.only.strip() == "all" else \
        {s.strip() for s in args.only.split(",") if s.strip()}
    render_only = only <= {"figures", "tables"}
    unknown = only - set(stages)
    if unknown:
        ap.error(f"unknown stage(s): {', '.join(sorted(unknown))}; "
                 f"choose from {', '.join(stages)}")
    ran = []
    if "analytic" in only:
        stage_analytic(cfg, args.quick); ran.append("analytic")
    if "wall" in only:
        stage_wall(cfg, args.quick); ran.append("wall")
    if "bench" in only:
        stage_benchmarks(cfg, args.quick); ran.append("bench")
    if "coupled" in only:
        stage_coupled(cfg, args.quick); ran.append("coupled")
    if "mesh" in only:
        stage_mesh_study(cfg, args.quick); ran.append("mesh")
    if "sweep" in only and not args.skip_sweeps:
        stage_sweeps(cfg, args.quick); ran.append("sweep")
    if "figures" in only:
        stage_figures(cfg, args.quick); ran.append("figures")
    if "tables" in only:
        # the table generator reads the run metadata (parameter table), so a provisional
        # copy is written first and refreshed below with the final runtime
        if not (render_only and (DATA / "run_metadata.json").exists()):
            meta["stages"] = ran
            _write_json("run_metadata.json", meta)
        stage_tables(cfg, args.quick); ran.append("tables")

    meta["stages"] = ran
    meta["runtime_s"] = round(time.time() - started, 1)
    # A render-only invocation (figures/tables) must not overwrite the record of the run
    # that produced the data; the metadata file is the provenance of the numerics.
    if render_only and (DATA / "run_metadata.json").exists():
        print("\n(dataset metadata preserved: this run only re-rendered the figures/tables)")
    else:
        _write_json("run_metadata.json", meta)
    print(f"\ndone in {meta['runtime_s']} s; outputs in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
