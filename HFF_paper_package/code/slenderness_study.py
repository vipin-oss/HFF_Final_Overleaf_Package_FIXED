#!/usr/bin/env python3
"""Thin-strip (slenderness) study: is the finite-element/beam-column departure a thickness effect?

Beam theory has no shear flexibility and no end effects, so if the 2-D wall departs from the
beam-column prediction because the baseline strip is thick (d/L = 0.1), the departure must shrink as
d/L -> 0 at fixed dimensionless loading.  We keep fixed
    * the free curvature kappa_th (so the linear bow kappa L^2/8 is unchanged), and
    * the force ratio N_c/N_cr = 12 (1+nu) alpha theta_bar L^2 / (pi^2 d^2)  (so theta_bar ~ d^2),
and vary d.  Each case is solved with the independent code of fe_independent.py (P2 triangles) and
compared with the frozen-force and self-consistent beam-column values computed here from the same
inputs (the self-consistent fixed point is checked against hff_model at the baseline).
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
from scipy.optimize import brentq

import fe_independent as fe
import hff_model as hm

P = hm.Params()
R0 = hm.compute(P)
L, E, NU, AL = P.L, P.E, P.nu, P.alpha


def beam(d, thbar, dtt):
    kappa = (1 + NU) * AL * dtt / d
    Ds = E * d**3 / (12 * (1 - NU**2))
    N0 = E * d * AL * thbar / (1 - NU)
    Ncr = math.pi**2 * Ds / L**2
    xs = np.linspace(0.0, L, 4001)

    def w_of(N):
        return hm.w_thermal_beamcolumn(xs, kappa, math.sqrt(N / Ds), L)

    def slope_sq(N):
        mu = math.sqrt(N / Ds)
        return float(np.trapezoid(hm.dw_thermal_beamcolumn(xs, kappa, mu, L) ** 2, xs) / L)

    relax = lambda N: N0 - E * d / (2 * (1 - NU**2)) * slope_sq(N) - N
    Nsc = brentq(relax, 1e-3 * N0, N0)
    return {"kappa": kappa, "Ds": Ds, "N0": N0, "Ncr": Ncr, "ratio": N0 / Ncr,
            "w_lin": kappa * L**2 / 8, "w_frozen": float(w_of(N0)[2000]), "w_sc": float(w_of(Nsc)[2000]),
            "N_sc": Nsc}


def main():
    b0 = beam(P.d, R0["theta_bar"], R0["dT_t"])
    assert abs(b0["w_sc"] - R0["w_sc"]) / R0["w_sc"] < 1e-5 and abs(b0["w_frozen"] - R0["w_frozen"]) / R0["w_frozen"] < 1e-9
    out = {"force_ratio": b0["ratio"], "kappa_th": b0["kappa"], "rows": []}
    for d in (3.0e-3, 2.25e-3, 1.5e-3, 1.05e-3, 0.75e-3):
        thbar = R0["theta_bar"] * (d / P.d) ** 2
        dtt = R0["dT_t"] * d / P.d
        b = beam(d, thbar, dtt)
        r = fe.solve(d, thbar, dtt, 192, 8)
        row = {"d": d, "d_over_L": d / L, "theta_bar": thbar, "dT_t": dtt, "ratio_Nc_Ncr": b["ratio"],
               "kappa_th": b["kappa"], "beam": b, "fe_w_lin": r["w_lin"], "fe_w_nl": r["w_nl"],
               "fe_Nc_nl": r["Nc_nl"], "fe_Nc_lin": r["Nc_lin"]}
        out["rows"].append(row)
        print(f"d/L={d / L:.4f}  Nc/Ncr={b['ratio']:.4f} kappa={b['kappa']:.3f}  FE/beam_sc={r['w_nl'] / b['w_sc']:.4f} "
              f"FE/beam_frozen={r['w_nl'] / b['w_frozen']:.4f} FElin/beamlin={r['w_lin'] / b['w_lin']:.4f} "
              f"Nlin/N0={r['Nc_lin'] / b['N0']:.4f} Nnl/Nsc={r['Nc_nl'] / b['N_sc']:.4f}", flush=True)
    # mesh sensitivity of the thinnest case: 192x8 versus 384x16
    d = out["rows"][-1]["d"]
    b = beam(d, out["rows"][-1]["theta_bar"], out["rows"][-1]["dT_t"])
    rf = fe.solve(d, out["rows"][-1]["theta_bar"], out["rows"][-1]["dT_t"], 384, 16)
    out["mesh_check"] = {"d_over_L": d / L, "ratio_192x8": out["rows"][-1]["fe_w_nl"] / b["w_sc"],
                         "ratio_384x16": rf["w_nl"] / b["w_sc"]}
    print("mesh check (d/L=%.3f): FE/beam_sc 192x8 = %.5f, 384x16 = %.5f" % (d / L, out["mesh_check"]["ratio_192x8"], out["mesh_check"]["ratio_384x16"]))
    (pathlib.Path(__file__).resolve().parent / "results" / "slenderness.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
