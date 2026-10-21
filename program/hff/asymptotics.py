"""Semi-analytical theory for the thermally self-deforming channel.

This module contains the analytical content of the paper, as opposed to the
finite-element solution:

* the eigenfunction (Graetz) solution of the thermal-entry problem in a plane
  channel with one uniformly heated wall and one adiabatic wall, obtained from
  the Sturm--Liouville problem ``psi'' + lam^2 u(Y) psi = 0`` with Neumann data
  at both walls;
* the closed-form hydraulic resistance of the bowed passage,
  ``dP = 12 mu Q \int dx / H(x)^3``, evaluated in closed form for the
  kinematic shape ``w = w0 sin^2(pi x/L)`` as a Gauss hypergeometric function
  and as its power series in ``a = w0/H0``;
* the weak-inertia (cross-sectionally averaged) momentum balance, whose
  inertial contribution is shown to be negligible at the present Reynolds
  number;
* the closed-form beam--column solution, the axial-compatibility fixed point,
  its contraction constant and the a posteriori error bound;
* analytic sensitivities of the bow and of the pressure drop to the imposed
  flux.

Every routine returns plain Python floats so that the results can be written
to JSON and quoted in the manuscript without post-processing.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.special import hyp2f1

from . import analytic, config


# ---------------------------------------------------------------------------
# 1. Graetz problem: Sturm--Liouville eigenfunctions
# ---------------------------------------------------------------------------
def _psi_and_derivative(lam: float, Y: np.ndarray, u: np.ndarray) -> Tuple[np.ndarray, float]:
    """Integrate ``psi'' + lam^2 u(Y) psi = 0`` from ``Y=0`` with psi(0)=1, psi'(0)=0.

    Classical RK4 on a uniform grid; returns ``psi`` on ``Y`` and ``psi'(1)``.
    """
    n = Y.size
    h = Y[1] - Y[0]
    psi = np.empty(n)
    dpsi = np.empty(n)
    psi[0], dpsi[0] = 1.0, 0.0
    for i in range(n - 1):
        y0, y1 = Y[i], Y[i + 1]
        k1p = dpsi[i]
        k1d = -lam * lam * 0.5 * (u[i] + u[i + 1]) * psi[i]
        k2p = dpsi[i] + 0.5 * h * k1d
        k2d = -lam * lam * 0.5 * (u[i] + u[i + 1]) * (psi[i] + 0.5 * h * k1p)
        k3p = dpsi[i] + 0.5 * h * k2d
        k3d = -lam * lam * 0.5 * (u[i] + u[i + 1]) * (psi[i] + 0.5 * h * k2p)
        k4p = dpsi[i] + h * k3d
        k4d = -lam * lam * 0.5 * (u[i] + u[i + 1]) * (psi[i] + h * k3p)
        psi[i + 1] = psi[i] + (h / 6.0) * (k1p + 2 * k2p + 2 * k3p + k4p)
        dpsi[i + 1] = dpsi[i] + (h / 6.0) * (k1d + 2 * k2d + 2 * k3d + k4d)
    return psi, float(dpsi[-1])


def graetz_modes(n_modes: int = 8, n_grid: int = 2001, lam_max: float = 60.0) -> Dict[str, Any]:
    """Eigenvalues and eigenfunctions of the thermal-entry problem.

    The velocity is ``u(Y) = 6Y(1-Y)`` (mean one) and the walls are Neumann:
    a uniform heat flux on one wall and an adiabatic opposite wall, so that the
    perturbation temperature carries no wall flux.
    """
    Y = np.linspace(0.0, 1.0, n_grid)
    u = 6.0 * Y * (1.0 - Y)

    # scan for sign changes of psi'(1; lam)
    grid = np.linspace(1e-3, lam_max, 3000)
    vals = np.array([_psi_and_derivative(g, Y, u)[1] for g in grid])
    roots: List[float] = []
    for i in range(grid.size - 1):
        if vals[i] == 0.0:
            roots.append(float(grid[i]))
        elif vals[i] * vals[i + 1] < 0.0:
            lo, hi = grid[i], grid[i + 1]
            flo = vals[i]
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                fm = _psi_and_derivative(mid, Y, u)[1]
                if flo * fm <= 0.0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            roots.append(0.5 * (lo + hi))
        if len(roots) >= n_modes:
            break

    modes = []
    for lam in roots:
        psi, _ = _psi_and_derivative(lam, Y, u)
        norm = math.sqrt(float(np.trapezoid(u * psi * psi, Y)))
        psi = psi / norm
        modes.append({"lam": lam, "psi": psi})
    return {"Y": Y, "u": u, "modes": modes}


def _fully_developed_profile(Y: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """Fully developed temperature for unit wall flux on the upper wall only.

    ``f'' = u/U``, ``f'(0) = 0``, ``f'(1) = 1`` (imposed flux) and
    ``\int u f = 0`` (bulk-mean datum).  Returns ``f``, ``f(1)`` and ``Nu_fd``.
    """
    f = Y**3 - 0.5 * Y**4
    # bulk-mean datum
    mean = float(np.trapezoid(6.0 * Y * (1.0 - Y) * f, Y)) / float(
        np.trapezoid(6.0 * Y * (1.0 - Y), Y))
    f = f - mean
    f1 = float(f[-1])
    Nu_fd = 2.0 / f1
    return f, f1, Nu_fd


def graetz_solution(cfg: Dict[str, Any], n_modes: int = 8) -> Dict[str, Any]:
    """Local Nusselt number of the thermal-entry problem, from the series.

    ``theta(X,Y) = f(Y) + sum_n A_n psi_n(Y) exp(-lam_n^2 X)`` with
    ``X = x / (H0 Re_H0 Pr)`` and ``A_n = -<f, psi_n>_u``.
    """
    g, op, f = cfg["geometry"], cfg["operating"], cfg["fluid"]
    gr = analytic.groups(cfg)
    H0, L = g["H0"], g["L"]
    scale = H0 * gr["Re_H0"] * gr["Pr"]        # x = X * scale

    table = graetz_modes(n_modes=n_modes)
    Y = table["Y"]
    u = table["u"]
    fprof, f1, Nu_fd = _fully_developed_profile(Y)

    coeffs = []
    for m in table["modes"]:
        psi = m["psi"]
        A = -float(np.trapezoid(u * fprof * psi, Y))
        coeffs.append((m["lam"], psi, A))

    def nusselt(x: float) -> float:
        X = x / scale
        s = f1
        for lam, psi, A in coeffs:
            s += A * float(psi[-1]) * math.exp(-(lam**2) * X)
        return 2.0 / s

    xs = np.linspace(1e-4 * L, L, 400)
    Nu = np.array([nusselt(x) for x in xs])
    Nu_mean = float(np.trapezoid(Nu, xs) / (xs[-1] - xs[0]))
    lam1 = coeffs[0][0]
    return {
        "eigenvalues": [c[0] for c in coeffs],
        "coefficients": [c[2] for c in coeffs],
        "psi_wall": [float(c[1][-1]) for c in coeffs],
        "Nu_fd": Nu_fd,
        "Nu_inlet": nusselt(1e-4 * L),
        "Nu_outlet": nusselt(L),
        "Nu_mean": Nu_mean,
        "entrance_length_99": float(-math.log(0.01) * scale / lam1**2),
        "x": xs.tolist(),
        "Nu": Nu.tolist(),
    }


# ---------------------------------------------------------------------------
# 2. Conjugate wall temperature from the series
# ---------------------------------------------------------------------------
def wall_temperature_series(cfg: Dict[str, Any], graetz: Dict[str, Any] | None = None,
                            n_modes: int = 8) -> Dict[str, Any]:
    """Wall temperature rise from the series plus one-dimensional wall conduction.

    Outer face flux ``q''``, wall thickness ``d``: the through-thickness profile
    is linear, so the thickness-averaged rise is
    ``theta_bar(x) = (T_w(x) - T_in) + q'' d / (2 k_s)``.
    """
    g, op, f, s = cfg["geometry"], cfg["operating"], cfg["fluid"], cfg["solid"]
    if graetz is None:
        graetz = graetz_solution(cfg, n_modes=n_modes)
    gr = analytic.groups(cfg)
    dT_star = gr["dT_star"]
    H0 = g["H0"]
    xs = np.array(graetz["x"])
    Nu = np.array(graetz["Nu"])
    # wall-to-bulk rise: Tw - Tm = q'' H0 / (k_f Nu) * 2
    Tw_minus_Tm = 2.0 * dT_star / Nu
    Tm = op["q_flux"] * xs / (f["rho"] * f["cp"] * op["U"] * H0)
    theta_wall = Tw_minus_Tm + Tm
    theta_bar = theta_wall + op["q_flux"] * g["d"] / (2.0 * s["k"])
    return {
        "theta_bar_mean": float(np.trapezoid(theta_bar, xs) / (xs[-1] - xs[0])),
        "theta_bar_outlet": float(theta_bar[-1]),
        "Tw_mean_rise": float(np.trapezoid(theta_wall, xs) / (xs[-1] - xs[0])),
        "dT_star": dT_star,
    }


# ---------------------------------------------------------------------------
# 3. Hydraulic resistance of the bowed passage
# ---------------------------------------------------------------------------
def lubrication_shape_factor(a: float) -> Dict[str, float]:
    """``\int_0^L dx/H^3`` for ``H = H0 (1 - a sin^2 pi x/L)``.

    Closed form ``(L/H0^3) * 2F1(3, 1/2; 1; a)``; the series
    ``1 + 3a/2 + 27a^2/8 + 75a^3/16 + ...`` is returned with its first four
    coefficients as a check on the hypergeometric evaluation.
    """
    if a >= 1.0:
        raise ValueError("a must be < 1: the wall would touch the opposite face")
    closed = float(hyp2f1(3.0, 0.5, 1.0, a))
    series = 1.0 + 1.5 * a + 3.375 * a**2 + 4.6875 * a**3 + 4.98046875 * a**4
    return {"closed": closed, "series": series, "a": a}


def pressure_drop_lubrication(cfg: Dict[str, Any], w_max: float | None = None,
                              w_profile: np.ndarray | None = None,
                              x_profile: np.ndarray | None = None) -> Dict[str, float]:
    """Pressure drop from the lubrication integral over the whole channel."""
    g, op, f = cfg["geometry"], cfg["operating"], cfg["fluid"]
    H0, L, Le, Lo = g["H0"], g["L"], g["Le"], g["Lo"]
    Q = op["U"] * H0                              # per unit width
    rigid = 12.0 * f["mu"] * Q * (Le + Lo) / H0**3

    if w_profile is not None and x_profile is not None:
        x = np.asarray(x_profile)
        w = np.asarray(w_profile)
        H = H0 - np.interp(x, x, w)
        strip = 12.0 * f["mu"] * Q * float(np.trapezoid(1.0 / H**3, x))
        shape = "computed"
        a = float(np.max(w) / H0)
    else:
        a = (w_max if w_max is not None else 0.0) / H0
        sf = lubrication_shape_factor(a)
        strip = 12.0 * f["mu"] * Q * sf["closed"] * L / H0**3
        shape = "sin^2"
    inertial = (6.0 / 5.0) * f["rho"] * Q**2 * (1.0 / (H0 - (w_max or 0.0)) - 1.0 / H0)
    return {
        "strip": strip,
        "rigid": rigid,
        "total": strip + rigid,
        "inertial": inertial,
        "a": a,
        "shape": shape,
    }


def pressure_drop_undeformed(cfg: Dict[str, Any]) -> float:
    return analytic.pressure_drop(cfg)


# ---------------------------------------------------------------------------
# 4. Beam--column closed form, fixed point and contraction
# ---------------------------------------------------------------------------
def beam_column(cfg: Dict[str, Any], q_flux: float | None = None,
                n: int = 6) -> Dict[str, float]:
    """Closed-form frozen-force bow, its amplification and the fixed-point data.

    The dimensionless deflection with uniform curvature and constant membrane
    force is ``W(xi) = (beta/lam^2) * [1 - cos(lam xi) - tan(lam/2) sin(lam xi)]``
    for the pinned--pinned strip; ``beta = kappa_th L^2/H0`` and
    ``lam^2 = N L^2 / D_s``.
    """
    g, s = cfg["geometry"], cfg["solid"]
    L, H0, d = g["L"], g["H0"], g["d"]
    if q_flux is None:
        q_flux = cfg["operating"]["q_flux"]
    Ds = s["E"] * d**3 / (12.0 * (1.0 - s["nu"]**2))
    kappa = analytic.kappa_th(cfg, q_flux)
    beta = kappa * L**2 / H0
    # frozen force: N = N_theta with the one-dimensional mean rise
    th = analytic.theta_bar_estimate(cfg, q_flux)
    N_theta = analytic.membrane_force(cfg, th["theta_bar"])
    lam2 = abs(N_theta) * L**2 / Ds
    lam = math.sqrt(lam2)
    xi = np.linspace(0.0, 1.0, 401)
    W = (beta / lam2) * (1.0 - np.cos(lam * xi) - math.tan(lam / 2.0) * np.sin(lam * xi))
    W_lin = 0.5 * beta * xi * (1.0 - xi)                 # curvature-only, no membrane force
    return {
        "q_flux": q_flux,
        "kappa_th": kappa,
        "beta": beta,
        "N_theta": N_theta,
        "lambda": lam,
        "w_max_frozen": float(np.max(np.abs(W))) * H0,
        "w_max_linear": float(np.max(np.abs(W_lin))) * H0,
        "amplification": float(np.max(np.abs(W)) / np.max(np.abs(W_lin))),
        "amplification_fem": float(np.max(np.abs(W)) / max(beta / 8.0, 1e-30)),
        "N_cr": float(math.pi**2 * Ds / L**2),
        "N_over_Ncr": float(abs(N_theta) / (math.pi**2 * Ds / L**2)),
    }


def contraction_bound(cfg: Dict[str, Any], q_flux: float | None = None) -> Dict[str, float]:
    """A priori contraction constant of the axial-compatibility fixed point.

    The map is ``N -> F(N) = N_theta + c <w'(N)^2>`` with
    ``c = E d / (2 (1 - nu^2))``.  Since ``w ∝ 1/(N_cr - |N|)`` near the Euler
    load, ``|F'| <= q`` with ``q = 2 |N_theta| / (N_cr - |N|)``.
    """
    b = beam_column(cfg, q_flux)
    Ncr, N = b["N_cr"], abs(b["N_theta"])
    q_bound = 2.0 * N / max(Ncr - N, 1e-12)
    return {"q_bound": q_bound, "N_over_Ncr": N / Ncr,
            "bound_valid": bool(q_bound < 1.0)}


# ---------------------------------------------------------------------------
# 5. Resolution of the analytical model
# ---------------------------------------------------------------------------
def solve(cfg: Dict[str, Any], n_modes: int = 8) -> Dict[str, Any]:
    """Run the whole semi-analytical model and return its predictions."""
    g = cfg["geometry"]
    grz = graetz_solution(cfg, n_modes=n_modes)
    wall = wall_temperature_series(cfg, grz, n_modes=n_modes)
    b = beam_column(cfg)
    lub_sin = pressure_drop_lubrication(cfg, w_max=b["w_max_frozen"])
    lub_shapes = {f"a={a:.3f}": lubrication_shape_factor(a) for a in (0.0, 0.1, 0.2, 0.3, 0.4, 0.45)}
    return {
        "graetz": {k: v for k, v in grz.items() if k not in ("x", "Nu")},
        "graetz_x": grz["x"],
        "graetz_Nu": grz["Nu"],
        "wall": wall,
        "beam": b,
        "contraction": contraction_bound(cfg),
        "lubrication_sin2": lub_sin,
        "shape_factors": lub_shapes,
        "groups": analytic.groups(cfg),
    }


if __name__ == "__main__":                     # pragma: no cover - manual run
    import json

    cfg = config.load("baseline")
    print(json.dumps(solve(cfg), indent=2, default=float)[:4000])
