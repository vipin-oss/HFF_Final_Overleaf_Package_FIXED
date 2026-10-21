"""Closed-form baseline arithmetic for the thermally self-deforming channel.

Every quantity of the analytical baseline table of the manuscript is recomputed here
from the parameter file, together with an explicit expression string and a ``kind``
label that distinguishes

``analytic``  a closed-form consequence of the governing equations,
``estimate``  a one-dimensional or engineering estimate with stated accuracy,
``derived``   a secondary combination of the two above.

This module contains no numerical solution of a PDE; it is the reference against which
the finite-element modules are verified, and the source of the design ceilings.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np

from . import config


def record(symbol: str, value: float, unit: str, expression: str, kind: str) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "value": float(value),
        "unit": unit,
        "expression": expression,
        "kind": kind,
    }


def groups(cfg: Dict[str, Any]) -> Dict[str, float]:
    """Dimensionless groups of the formulation, single-length (H0/Dh) basis stated."""
    g, op = cfg["geometry"], cfg["operating"]
    f, s = cfg["fluid"], cfg["solid"]
    d = config.derived(cfg)
    H0, Dh, L, U, qf = g["H0"], d["Dh"], g["L"], op["U"], op["q_flux"]

    Re_Dh = f["rho"] * U * Dh / f["mu"]
    Re_H0 = f["rho"] * U * H0 / f["mu"]
    Pr = f["mu"] * f["cp"] / f["k"]
    Pe = Re_Dh * Pr
    dT_star = qf * H0 / f["k"]
    Gr = cfg["physics"]["g"] * f["beta"] * dT_star * H0**3 / d["nu_kin"] ** 2
    Ri = Gr / Re_H0**2
    Br = f["mu"] * U**2 / (f["k"] * dT_star)
    return {
        "Re_Dh": Re_Dh,
        "Re_H0": Re_H0,
        "Pr": Pr,
        "Pe": Pe,
        "f_D": 96.0 / Re_Dh,
        "Gr": Gr,
        "Ri_H0": Ri,
        "Ri_Dh": Gr * 8.0 / Re_Dh**2,
        "Br": Br,
        "R_k": s["k"] / f["k"],
        "D_r": g["d"] / H0,
        "Lambda": L / H0,
        "Sig_kappa": s["alpha"] * qf * H0 / s["k"],
        "dT_star": dT_star,
    }


def pressure_drop(cfg: Dict[str, Any], U: float | None = None) -> float:
    """Slit pressure drop over the heated length, Dp = 12 mu U L / H0^2."""
    g, f = cfg["geometry"], cfg["fluid"]
    U = cfg["operating"]["U"] if U is None else U
    return 12.0 * f["mu"] * U * g["L"] / g["H0"] ** 2


def strip_pressure(cfg: Dict[str, Any], U: float | None = None) -> Dict[str, float]:
    """Gauge pressure carried by the deformable strip for the outlet datum p(L+L_o)=0.

    The channel is fed at mean velocity ``U``; the pressure gradient over the whole
    uniform-height passage is ``12 mu U / H0^2``.  With the outlet at p = 0 the gauge
    pressure rises linearly upstream, giving p(0) and p(L) on the strip and the
    datum-consistent mean load.
    """
    g, f = cfg["geometry"], cfg["fluid"]
    U = cfg["operating"]["U"] if U is None else U
    grad = 12.0 * f["mu"] * U / g["H0"] ** 2
    p_L = grad * g["Lo"]
    p_0 = grad * (g["Lo"] + g["L"])
    return {"grad": grad, "p0": p_0, "pL": p_L, "p_mean": 0.5 * (p_0 + p_L)}


def kappa_th(cfg: Dict[str, Any], q_flux: float | None = None) -> float:
    """Free thermal eigen-curvature, kappa_th = (1+nu) alpha q'' / k_s."""
    s = cfg["solid"]
    q = cfg["operating"]["q_flux"] if q_flux is None else q_flux
    return (1.0 + s["nu"]) * s["alpha"] * q / s["k"]


def delta_T_through(cfg: Dict[str, Any], q_flux: float | None = None) -> float:
    s, g = cfg["solid"], cfg["geometry"]
    q = cfg["operating"]["q_flux"] if q_flux is None else q_flux
    return q * g["d"] / s["k"]


def membrane_force(cfg: Dict[str, Any], theta_bar: float) -> float:
    """Signed thermal membrane resultant (tension positive), N_theta = -E d alpha th /(1-nu)."""
    g, s = cfg["geometry"], cfg["solid"]
    return -s["E"] * g["d"] * s["alpha"] * theta_bar / (1.0 - s["nu"])


def critical_temperature(cfg: Dict[str, Any], d: float | None = None) -> float:
    """Pinned-pinned thermal buckling threshold of the plane-strain strip."""
    g, s = cfg["geometry"], cfg["solid"]
    d = g["d"] if d is None else d
    return math.pi**2 * d**2 / (12.0 * s["alpha"] * (1.0 + s["nu"]) * g["L"] ** 2)


def theta_bar_estimate(cfg: Dict[str, Any], q_flux: float | None = None) -> Dict[str, float]:
    """One-dimensional estimate of the mean wall temperature rise.

    theta_bar = dT_t/2 + q''/h_rigid + dT_b/2, with h_rigid = Nu_H1 k_f / D_h and
    dT_b = q'' L / (rho U H0 cp) from the global enthalpy balance.  This is the
    'estimate' of the manuscript; the coupled computation replaces it by the computed
    thickness-averaged wall temperature.
    """
    g, op, f = cfg["geometry"], cfg["operating"], cfg["fluid"]
    q = op["q_flux"] if q_flux is None else q_flux
    h_rigid = 5.385 * f["k"] / (2.0 * g["H0"])
    dT_t = delta_T_through(cfg, q)
    dT_b = q * g["L"] / (f["rho"] * op["U"] * g["H0"] * f["cp"])
    theta = dT_t / 2.0 + q / h_rigid + dT_b / 2.0
    return {"theta_bar": theta, "dT_t": dT_t, "dT_b": dT_b, "h_rigid": h_rigid}


def time_scales(cfg: Dict[str, Any]) -> Dict[str, float]:
    g, s, f = cfg["geometry"], cfg["solid"], cfg["fluid"]
    d = config.derived(cfg)
    t_wave = g["d"] * math.sqrt(s["rho"] / s["E"])
    t_s = g["d"] ** 2 / d["alpha_s"]
    t_f = g["H0"] ** 2 / d["alpha_f"]
    t_adv = g["L"] / cfg["operating"]["U"]
    # thermoelastic coupling number xi = beta^2 T0 / [(lambda+2 mu_L) rho_s c_s]
    lam2 = d["lambda"] + 2.0 * d["mu_L"]
    T0 = cfg["meta"]["reference_temperature_K"]
    xi = d["beta"] ** 2 * T0 / (lam2 * s["rho"] * s["cp"])
    return {"t_wave": t_wave, "t_s": t_s, "t_f": t_f, "t_adv": t_adv, "xi": xi}


def bending_moment_scale(cfg: Dict[str, Any], kappa: float | None = None) -> float:
    """Unrestrained-moment scale E kappa (d/2)/(1-nu^2) quoted for reference only."""
    g, s = cfg["geometry"], cfg["solid"]
    kappa = kappa_th(cfg) if kappa is None else kappa
    return s["E"] * kappa * (g["d"] / 2.0) / (1.0 - s["nu"] ** 2)


def baseline(cfg: Dict[str, Any], theta_bar: float | None = None) -> List[Dict[str, Any]]:
    """Full analytical baseline table.

    ``theta_bar`` may be supplied by the coupled computation; when omitted the
    one-dimensional estimate of :func:`theta_bar_estimate` is used and every
    dependent row is labelled accordingly.
    """
    g, op, f, s = cfg["geometry"], cfg["operating"], cfg["fluid"], cfg["solid"]
    d = config.derived(cfg)
    gr = groups(cfg)
    est = theta_bar_estimate(cfg)
    th = est["theta_bar"] if theta_bar is None else float(theta_bar)
    th_kind = "estimate" if theta_bar is None else "computed"

    H0, L, dd, U, q = g["H0"], g["L"], g["d"], op["U"], op["q_flux"]
    Ds = d["Ds"]
    dp = pressure_drop(cfg)
    press = strip_pressure(cfg)
    kap = kappa_th(cfg)
    N = membrane_force(cfg, th)
    Ncr = math.pi**2 * Ds / L**2
    Tcr = critical_temperature(cfg)
    w_lin = kap * L**2 / 8.0
    # linear analytic bending deflection under the datum-consistent mean load
    w_p = 5.0 * press["p_mean"] * L**4 / (384.0 * Ds)
    rows: List[Dict[str, Any]] = [
        record("Re_Dh", gr["Re_Dh"], "-", "2 rho U H0 / mu", "analytic"),
        record("Re_H0", gr["Re_H0"], "-", "rho U H0 / mu", "analytic"),
        record("Pr", gr["Pr"], "-", "mu cp / kf", "analytic"),
        record("Pe", gr["Pe"], "-", "Re_Dh Pr", "analytic"),
        record("f_D", gr["f_D"], "-", "96 / Re_Dh (Darcy, Dh basis)", "analytic"),
        record("dp", dp, "Pa", "12 mu U L / H0^2", "analytic"),
        record("tau_w", 6.0 * f["mu"] * U / H0, "Pa", "6 mu U / H0", "analytic"),
        record("p_mean", press["p_mean"], "Pa", "[p(0)+p(L)]/2 with p(L+Lo)=0", "analytic"),
        record("dT_star", gr["dT_star"], "K", "q'' H0 / kf", "analytic"),
        record("dT_t", est["dT_t"], "K", "q'' d / ks", "analytic"),
        record("kappa_th", kap, "1/m", "(1+nu) alpha q'' / ks", "analytic"),
        record("w_lin", w_lin, "m", "kappa_th L^2 / 8", "analytic"),
        record("w_lin_over_H0", w_lin / H0, "-", "kappa_th L^2 / (8 H0)", "analytic"),
        record("theta_bar", th, "K", "mean wall rise (1D estimate or computed)", th_kind),
        record("N_theta", N, "N/m", "-E d alpha theta_bar/(1-nu)", th_kind),
        record("Ds", Ds, "N m", "E d^3/[12(1-nu^2)]", "analytic"),
        record("N_cr", Ncr, "N/m", "pi^2 Ds / L^2", "analytic"),
        record("N_over_Ncr", abs(N) / Ncr, "-", "|N_theta| / N_cr", th_kind),
        record("T_cr", Tcr, "K", "pi^2 d^2/[12 alpha (1+nu) L^2]", "analytic"),
        record("M_b", Tcr / th, "-", "T_cr / theta_bar", th_kind),
        record("w_p", w_p, "m", "5 p_mean L^4/(384 Ds)", "analytic"),
        record("Gamma_p", w_lin / w_p, "-", "w_th / w_p (linear limit)", "derived"),
        record("sigma_memb", -s["E"] * s["alpha"] * th / (1.0 - s["nu"]), "Pa",
               "-E alpha theta_bar/(1-nu)", th_kind),
        record("Gr", gr["Gr"], "-", "g beta_f dT* H0^3/nu_kin^2", "analytic"),
        record("Ri_H0", gr["Ri_H0"], "-", "Gr / Re_H0^2", "analytic"),
        record("Ri_Dh", gr["Ri_Dh"], "-", "Gr_Dh / Re_Dh^2", "analytic"),
        record("Br", gr["Br"], "-", "mu U^2 / (kf dT*)", "analytic"),
        record("dT_b", est["dT_b"], "K", "q'' L /(rho U H0 cp)", "analytic"),
        record("h_rigid", est["h_rigid"], "W/(m2 K)", "Nu_H1 kf / Dh", "analytic"),
        record("q_over_h", q / est["h_rigid"], "K", "q'' / h_rigid", "estimate"),
        record("t_wave", time_scales(cfg)["t_wave"], "s", "d sqrt(rho_s/E)", "analytic"),
        record("t_s", time_scales(cfg)["t_s"], "s", "d^2/alpha_s", "analytic"),
        record("t_f", time_scales(cfg)["t_f"], "s", "H0^2/alpha_f", "analytic"),
        record("xi", time_scales(cfg)["xi"], "-", "beta^2 T0/[(lam+2muL) rho_s c_s]", "analytic"),
        record("sigma_bend_scale", bending_moment_scale(cfg), "Pa",
               "E kappa_th (d/2)/(1-nu^2) (unrestrained scale)", "derived"),
    ]
    return rows


def ceiling_sweep(cfg: Dict[str, Any],
                  q_values: np.ndarray | None = None) -> Dict[str, np.ndarray]:
    """One-dimensional design quantities as a function of the imposed flux.

    Returns the mean wall rise from the 1D estimate, the blocked-state membrane
    resultant relative to the Euler load, the free curvature, the *linear* bow and the
    buckling margin.  The geometric-stiffness amplification of the bow and the
    associated fibre strain are supplied by :mod:`hff.wall`, which solves the
    beam--column problem; this function deliberately reports only the analytic part.
    """
    g, s = cfg["geometry"], cfg["solid"]
    q_values = np.asarray(q_values if q_values is not None else np.linspace(0.0, 1.2e4, 241))
    H0, dd, L = g["H0"], g["d"], g["L"]
    Ds = config.derived(cfg)["Ds"]
    Ncr = math.pi**2 * Ds / L**2
    Tcr = critical_temperature(cfg)
    h_rigid = 5.385 * cfg["fluid"]["k"] / (2.0 * H0)
    mdot_cp = cfg["fluid"]["rho"] * cfg["operating"]["U"] * H0 * cfg["fluid"]["cp"]

    theta = (q_values * dd / s["k"]) / 2.0 + q_values / h_rigid + (q_values * L / mdot_cp) / 2.0
    kap = (1.0 + s["nu"]) * s["alpha"] * q_values / s["k"]
    N = abs(membrane_force(cfg, 0.0)) * 0.0  # placeholder to keep dtype/shape explicit
    N = np.array([abs(membrane_force(cfg, t)) for t in theta])
    out = {
        "q": q_values,
        "theta_bar": theta,
        "kappa_th": kap,
        "N_over_Ncr": N / Ncr,
        "w_lin": kap * L**2 / 8.0,
        "w_over_H0": kap * L**2 / 8.0 / H0,
        "M_b": np.where(theta > 0, Tcr / np.maximum(theta, 1e-30), np.inf),
        "sigma_bend_scale": s["E"] * kap * (dd / 2.0) / (1.0 - s["nu"] ** 2),
        "sigma_memb": -s["E"] * s["alpha"] * theta / (1.0 - s["nu"]),
        "eps_memb": (1.0 + s["nu"]) * s["alpha"] * theta,
    }
    return out
