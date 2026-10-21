"""Element-Peclet statistics and the effect of the SUPG term.

Reported in the manuscript (section "Conjugate thermal sub-problem").  Runs the
conjugate thermal solve on the converged baseline interface profile with the
streamline-upwind term switched on and off, and records the discrete
quantities that the stabilisation can affect.  Writes
``outputs/data/supg_sensitivity.json``.

Usage:  ./.venv/bin/python tools/supg_sensitivity.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from hff import config, coupled, fem, flow, thermal  # noqa: E402


def main() -> int:
    cfg = config.load(HERE / "params" / "baseline.json")
    base = json.loads((HERE / "outputs" / "data" / "coupled_baseline.json").read_text())
    w = np.asarray(base["w"], dtype=float)

    fluid = fem.fluid_mesh(cfg, w)
    solid = fem.solid_mesh(cfg, fluid)
    n_global = fem.bind_shared(fluid, solid)   # must precede the solves
    sol_flow = flow.solve_flow(fluid, cfg)
    fm = flow.flow_metrics(sol_flow, cfg)

    # element Peclet number statistics, evaluated with the code's own formula,
    # on the fluid numbering before the interface degrees of freedom are shared
    fdata = fem.element_data(fluid)
    u_gp = np.einsum("gn,enc->egc", fdata.N, sol_flow.u[fluid.p2])
    umag = np.sqrt(np.sum(u_gp ** 2, axis=2)).mean(axis=1)
    h = np.asarray(fdata.hsize, dtype=float)
    rho, cp, kf = cfg["fluid"]["rho"], cfg["fluid"]["cp"], cfg["fluid"]["k"]
    pe = rho * cp * umag * h / (2.0 * kf)
    tau = thermal.supg_tau(fdata, u_gp, rho, cp, kf)

    out = {
        "dof": {
            "fluid_p2_nodes": int(fluid.xy.shape[0]),
            "fluid_p1_nodes": int(fluid.n_vertices),
            "solid_p2_nodes": int(solid.xy.shape[0]),
        },
        "element_peclet": {
            "median": float(np.median(pe)), "max": float(pe.max()),
            "min": float(pe.min()),
        },
        "element_size": {"median": float(np.median(h)), "min": float(h.min()),
                         "max": float(h.max())},
        "tau_median": float(np.median(tau)),
        "cases": {},
    }
    for label, use_supg in (("supg", True), ("no_supg", False)):
        c = config.load(HERE / "params" / "baseline.json")
        c["numerics"]["thermal"]["supg"] = bool(use_supg)
        therm = thermal.solve_thermal(fluid, solid, sol_flow, c, n_global)
        sdata = fem.element_data(solid, solid.p2_coordinates(n_global))
        prof = thermal.wall_profile(solid, sdata, therm.T, c)
        bal = thermal.enthalpy_balance(therm, c)
        jump = thermal.interface_flux_jump(therm, c)
        nu = thermal.nusselt_profile(therm, c)
        out["cases"][label] = {
            "theta_bar_mean": float(np.mean(prof["theta_bar"])),
            "theta_bar_max": float(np.max(prof["theta_bar"])),
            "Nu_mean": float(np.mean(nu["Nu"])),
            "energy_imbalance": float(bal["rel_imbalance"]),
            "interface_flux_jump": float(jump),
        }
    a, b = out["cases"]["supg"], out["cases"]["no_supg"]
    out["differences"] = {
        "theta_bar_mean_rel": (b["theta_bar_mean"] - a["theta_bar_mean"]) / a["theta_bar_mean"],
        "Nu_mean_rel": (b["Nu_mean"] - a["Nu_mean"]) / a["Nu_mean"],
        "energy_imbalance_ratio": b["energy_imbalance"] / a["energy_imbalance"],
    }
    path = HERE / "outputs" / "data" / "supg_sensitivity.json"
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"written to {path}")
    print(f"flow unknowns: {out['dof']['fluid_p2_nodes']}; dp = {fm['dp']:.3f} Pa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
