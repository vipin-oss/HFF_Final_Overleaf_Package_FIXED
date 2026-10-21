#!/usr/bin/env python3
"""Reduced-order thermoelastic model of the heated polymer channel wall.

Every number quoted in the manuscript that comes from the analytical part of the study is
computed here, from the inputs of Tables I and III of the paper, and nowhere else.

Sign conventions (identical to the paper)
-----------------------------------------
* y points from the fluid into the solid (upwards); the strip occupies H0 <= y <= H0 + d.
* Deflection w is positive AWAY from the channel (w = +d_2).
* q'' > 0 is heat SUPPLIED to the solid on the outer face y = H0 + d:  +k_s dT/dy = q''.
  Hence T increases with y across the wall and the outer (upper) face is the hot face.
* Free thermal curvature kappa_th > 0 gives, for pinned ends, w = kappa_th x (L - x) / 2 >= 0,
  i.e. the strip bows away from the channel and the passage widens.

Nothing in this module is a coupled fluid-structure solution.  The quantities labelled
"reduced-order" (lubrication pressure drop, quasi-developed wall excess) are order-of-magnitude
estimates and are labelled as such in the paper.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict

import numpy as np

_trapz = getattr(np, "trapezoid", None) or np.trapz  # numpy >= 2.0 / 1.x
from scipy.integrate import quad
from scipy.optimize import brentq


@dataclass(frozen=True)
class Params:
    # fluid (near-ambient water)
    rho: float = 1.0e3
    mu: float = 1.0e-3
    cp: float = 4.18e3
    kf: float = 0.60
    beta_f: float = 2.1e-4
    # solid (unfilled-PEEK-class, datasheet-representative)
    E: float = 3.6e9
    nu: float = 0.40
    alpha: float = 5.0e-5
    ks: float = 0.25
    rho_s: float = 1.3e3
    c_s: float = 1.1e3
    sigma_y: float = 9.0e7
    # geometry
    H0: float = 5.0e-4
    L: float = 3.0e-2
    Le: float = 1.0e-2
    Lo: float = 2.0e-2
    d: float = 3.0e-3
    # operation
    U: float = 5.0e-2
    q: float = 5.0e3
    # rigid-slit, one wall heated / other adiabatic (H1), D_h = 2 H0 (Shah and London, 1978)
    Nu_H1: float = 5.385
    g: float = 9.81


# ----------------------------------------------------------------------------------------
# closed-form beam-column kernels
# ----------------------------------------------------------------------------------------
def w_thermal_beamcolumn(x, kappa, mu_, L):
    """Pinned-pinned strip, total moment M = D (w'' + kappa) = 0 at the ends, compressive
    membrane force N_c = D mu^2 frozen.  w = (kappa/mu^2)[(1-cos mu L)/sin mu L sin mu x
    + cos mu x - 1].   Limit mu -> 0: kappa x (L - x)/2."""
    x = np.asarray(x, dtype=float)
    if mu_ * L < 1e-6:
        return 0.5 * kappa * x * (L - x)
    # (1 - cos a)/sin a = tan(a/2): numerically safer for small a
    t = math.tan(0.5 * mu_ * L)
    return kappa / mu_**2 * (t * np.sin(mu_ * x) + np.cos(mu_ * x) - 1.0)


def dw_thermal_beamcolumn(x, kappa, mu_, L):
    x = np.asarray(x, dtype=float)
    if mu_ * L < 1e-6:
        return 0.5 * kappa * (L - 2 * x)
    t = math.tan(0.5 * mu_ * L)
    return kappa / mu_ * (t * np.cos(mu_ * x) - np.sin(mu_ * x))


def d2w_thermal_beamcolumn(x, kappa, mu_, L):
    x = np.asarray(x, dtype=float)
    if mu_ * L < 1e-6:
        return -kappa * np.ones_like(x)
    t = math.tan(0.5 * mu_ * L)
    return -kappa * (t * np.sin(mu_ * x) + np.cos(mu_ * x))


def w_uniform_load(x, p, D, N_c, L, nterms=401):
    """Pinned-pinned strip under uniform transverse load p (positive away from the channel)
    and compressive axial force N_c: D w'''' + N_c w'' = p.  Sine-series solution; converges as
    n^-5 and is free of the cancellation that afflicts the closed form at small N_c."""
    x = np.asarray(x, dtype=float)
    w = np.zeros_like(x)
    for n in range(1, nterms + 1, 2):
        k = n * math.pi / L
        pn = 4.0 * p / (n * math.pi)
        w += pn / (D * k**4 - N_c * k**2) * np.sin(k * x)
    return w


# ----------------------------------------------------------------------------------------
# baseline
# ----------------------------------------------------------------------------------------
def compute(p: Params | None = None, q: float | None = None, self_consistent: bool = True) -> dict:
    p = p or Params()
    q = p.q if q is None else q
    r: dict = {}
    nu, E, d, L, H0 = p.nu, p.E, p.d, p.L, p.H0

    # --- dimensionless groups and rigid-slit hydraulics ---
    r["Re"] = 2 * p.rho * p.U * H0 / p.mu
    r["Pr"] = p.mu * p.cp / p.kf
    r["Pe"] = r["Re"] * r["Pr"]
    r["dp"] = 12 * p.mu * p.U * L / H0**2
    r["tau_w"] = 6 * p.mu * p.U / H0
    r["fD_Re"] = 96.0

    # --- thermal bookkeeping ---
    r["dT_scale"] = q * H0 / p.kf
    r["Ri"] = p.g * p.beta_f * r["dT_scale"] * H0 / p.U**2
    r["Br"] = p.mu * p.U**2 / (p.kf * r["dT_scale"])
    r["dT_t"] = q * d / p.ks
    r["dT_b"] = q * L / (p.rho * p.U * H0 * p.cp)
    r["h_rigid"] = p.Nu_H1 * p.kf / (2 * H0)
    r["q_over_h"] = q / r["h_rigid"]
    r["theta_bar"] = r["dT_t"] / 2 + r["q_over_h"] + r["dT_b"] / 2

    # --- strip mechanics ---
    r["kappa_th"] = (1 + nu) * p.alpha * q / p.ks
    r["D_s"] = E * d**3 / (12 * (1 - nu**2))
    r["N_theta"] = -E * d * p.alpha * r["theta_bar"] / (1 - nu)
    r["N_c"] = abs(r["N_theta"])
    r["N_cr"] = math.pi**2 * r["D_s"] / L**2
    r["Nc_over_Ncr"] = r["N_c"] / r["N_cr"]
    r["T_cr"] = math.pi**2 * d**2 / (12 * p.alpha * (1 + nu) * L**2)
    r["M_b"] = r["T_cr"] / r["theta_bar"]
    r["w_lin"] = r["kappa_th"] * L**2 / 8

    mu_f = math.sqrt(r["N_c"] / r["D_s"])
    r["mu_L_frozen"] = mu_f * L
    xm = L / 2
    r["w_frozen"] = float(w_thermal_beamcolumn(xm, r["kappa_th"], mu_f, L))
    r["amplification_frozen"] = r["w_frozen"] / r["w_lin"]
    r["amplification_euler"] = 1.0 / (1.0 - r["Nc_over_Ncr"])

    # --- self-consistent von Karman: N_c = |N_theta| - E d /(2(1-nu^2)) <w'^2> (scalar fixed point)
    k_arc = E * d / (2 * (1 - nu**2))

    def mean_slope_sq(Nc):
        mu_ = math.sqrt(Nc / r["D_s"])
        val, _ = quad(lambda x: float(dw_thermal_beamcolumn(x, r["kappa_th"], mu_, L)) ** 2, 0, L)
        return val / L

    if self_consistent:
        Nc = r["N_c"]
        for _ in range(500):
            Nc_new = r["N_c"] - k_arc * mean_slope_sq(max(Nc, 1e-9))
            if abs(Nc_new - Nc) < 1e-12 * r["N_c"]:
                Nc = Nc_new
                break
            Nc = 0.5 * Nc + 0.5 * Nc_new
        r["N_c_sc"] = Nc
        r["relaxation_sc"] = 1.0 - Nc / r["N_c"]
        mu_sc = math.sqrt(Nc / r["D_s"])
        r["w_sc"] = float(w_thermal_beamcolumn(xm, r["kappa_th"], mu_sc, L))
        r["frozen_over_sc_excess"] = r["w_frozen"] / r["w_sc"] - 1.0
    else:
        r["N_c_sc"] = r["relaxation_sc"] = r["w_sc"] = r["frozen_over_sc_excess"] = float("nan")

    # kinematics and stresses of the frozen-force state
    xs = np.linspace(0, L, 4001)
    slope = dw_thermal_beamcolumn(xs, r["kappa_th"], mu_f, L)
    r["slope_max"] = float(np.max(np.abs(slope)))
    r["arc_strain_frozen"] = 0.5 * float(_trapz(slope**2, xs) / L)
    r["w_max_slope_in_frozen"] = r["slope_max"]
    kappa_geo_mid = -float(d2w_thermal_beamcolumn(xm, r["kappa_th"], mu_f, L))
    r["fibre_strain"] = (kappa_geo_mid - r["kappa_th"]) * d / 2
    M_mid = r["D_s"] * (float(d2w_thermal_beamcolumn(xm, r["kappa_th"], mu_f, L)) + r["kappa_th"])
    r["M_mid"] = M_mid
    r["sigma_bend"] = 6 * abs(M_mid) / d**2
    r["sigma_memb"] = E * p.alpha * r["theta_bar"] / (1 - nu)
    r["sigma_max"] = r["sigma_bend"] + r["sigma_memb"]
    r["stress_fraction"] = r["sigma_max"] / p.sigma_y

    # --- passage height (beam-model, not a prescribed clearance) ---
    r["w_frozen_over_H0"] = r["w_frozen"] / H0
    r["w_sc_over_H0"] = r["w_sc"] / H0
    r["w_lin_over_H0"] = r["w_lin"] / H0
    r["H_mid_frozen"] = H0 + r["w_frozen"]
    r["H_mid_frozen_over_H0"] = r["H_mid_frozen"] / H0
    r["H_mid_sc_over_H0"] = 1 + r["w_sc_over_H0"]

    # --- hydraulic load and the thermal/hydraulic deformation ratio Gamma_p ---
    g_out = 12 * p.mu * p.U / H0**2               # |dp/dx| of the rigid slit
    p_L = g_out * p.Lo                            # gauge level at the strip exit, outlet datum 0
    p_0 = p_L + r["dp"]
    r["p_strip_exit"], r["p_strip_entry"] = p_L, p_0
    r["p_bar"] = 0.5 * (p_0 + p_L)
    r["w_p_lin"] = 5 * r["p_bar"] * L**4 / (384 * r["D_s"])
    # like-for-like ratios: thermal and pressure bows computed with the SAME wall model
    r["Gamma_p_lin"] = r["w_lin"] / r["w_p_lin"]                        # both zero-membrane
    r["w_p_bc"] = float(w_uniform_load(xm, r["p_bar"], r["D_s"], r["N_c"], L))
    r["Gamma_p_bc"] = r["w_frozen"] / r["w_p_bc"]                       # both with the same N_c
    r["Gamma_p_mixed"] = r["w_frozen"] / r["w_p_lin"]                   # NOT like-for-like
    r["Gamma_p_closed_form_lin"] = 48 * r["kappa_th"] * r["D_s"] / (5 * r["p_bar"] * L**2)

    # --- reduced-order consequences for the passage (indicative only) ---
    xs2 = np.linspace(0, L, 2001)
    w_x = w_thermal_beamcolumn(xs2, r["kappa_th"], mu_f, L)
    H_x = H0 + w_x
    # lubrication: flow rate per unit depth U H0 fixed;  dp/dx = -12 mu U H0 / H^3
    lub = 12 * p.mu * p.U * H0 * float(_trapz(1.0 / H_x**3, xs2))
    r["dp_lub_deformed"] = lub
    r["dp_ratio_lub"] = lub / r["dp"]
    # quasi-developed local coefficient h = Nu_H1 k_f / (2 H(x)), excess q/h(x) = q 2H/(Nu k_f)
    excess = q * 2 * H_x / (p.Nu_H1 * p.kf)
    r["q_over_h_mean_deformed"] = float(_trapz(excess, xs2) / L)
    r["q_over_h_ratio"] = r["q_over_h_mean_deformed"] / r["q_over_h"]
    r["Re_Hover_L"] = 0.5 * r["Re"] * H0 / L          # lubrication parameter  Re_H (H0/L)
    r["L_T_est"] = 0.05 * r["Pe"] * 2 * H0
    r["L_over_LT"] = L / r["L_T_est"]
    return r


def feedback_on_deflection(p: Params | None = None) -> dict:
    """Effect of the fluid-side thermal loop on the bow: raise the mean wall rise by the extra
    interface excess q/h(deformed) - q/h(flat) (quasi-developed estimate) and recompute w."""
    p = p or Params()
    r0 = compute(p)
    extra = r0["q_over_h_mean_deformed"] - r0["q_over_h"]
    dtheta = extra
    nu = p.nu
    N_theta = -p.E * p.d * p.alpha * (r0["theta_bar"] + dtheta) / (1 - nu)
    mu_ = math.sqrt(abs(N_theta) / r0["D_s"])
    w1 = float(w_thermal_beamcolumn(p.L / 2, r0["kappa_th"], mu_, p.L))
    return {
        "extra_interface_excess_K": extra,
        "w_frozen_with_feedback": w1,
        "relative_change_in_w": w1 / r0["w_frozen"] - 1.0,
    }


def ceilings(p: Params | None = None) -> dict:
    """Heat fluxes at which each admissibility guard is reached (frozen-force wall model)."""
    p = p or Params()

    def f_w(q):  # |w|/H0 - 0.5
        return compute(p, q, False)["w_frozen_over_H0"] - 0.5

    def f_s(q):  # stress fraction - 0.2
        return compute(p, q, False)["stress_fraction"] - 0.2

    def f_b(q):  # M_b - 2
        return compute(p, q, False)["M_b"] - 2.0

    out = {}
    out["q_w_guard"] = brentq(f_w, 1e3, 8.5e3)
    out["q_stress_guard"] = brentq(f_s, 1e3, 8.5e3)
    out["q_buckling_guard"] = brentq(f_b, 1e3, 1.5e4)
    for key in ("q_w_guard", "q_stress_guard", "q_buckling_guard"):
        rr = compute(p, out[key], False)
        out[key.replace("q_", "ratio_")] = rr["Nc_over_Ncr"]
        out[key.replace("q_", "wH0_")] = rr["w_frozen_over_H0"]
        out[key.replace("q_", "excess_")] = compute(p, out[key], True)["frozen_over_sc_excess"]
    return out


def stainless_contrast(p: Params | None = None) -> dict:
    p = p or Params()
    ks, alpha, nu, E = 16.0, 1.7e-5, 0.30, 193e9   # typical austenitic stainless steel
    kappa = (1 + nu) * alpha * p.q / ks
    w_lin = kappa * p.L**2 / 8
    return {"kappa_th": kappa, "w_lin_over_H0": w_lin / p.H0}


def main() -> None:
    p = Params()
    r = compute(p)
    out = {
        "params": asdict(p),
        "baseline": r,
        "feedback": feedback_on_deflection(p),
        "ceilings": ceilings(p),
        "stainless": stainless_contrast(p),
    }
    for k, v in r.items():
        print(f"{k:32s} {v:.6g}")
    print()
    for blk in ("feedback", "ceilings", "stainless"):
        print(blk)
        for k, v in out[blk].items():
            print(f"  {k:30s} {v:.6g}")
    import pathlib

    res = pathlib.Path(__file__).resolve().parent / "results"
    res.mkdir(exist_ok=True)
    (res / "baseline.json").write_text(json.dumps(out, indent=2))
    print("\nwritten", res / "baseline.json")


if __name__ == "__main__":
    main()
