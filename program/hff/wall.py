"""Reduced von Karman wall model of the thermoelastic strip.

The strip is represented by its transverse member with full geometric stiffness of the
axial membrane state (the reduced, frozen-force von Karman reduction of the manuscript):

    D_s w'''' + N w'' = -p - D_s kappa_th''

with pinned ends ``w(0) = w(L) = 0`` and vanishing total end moment
``D_s (w'' + kappa_th) = 0``.  The equation is discretised with cubic Hermite
(beam) finite elements, so that the eigen-curvature enters through the consistent load
vector ``-∫ D_s kappa_th phi''`` and never requires differentiating a computed
curvature field.  The membrane force is updated through the axial-compatibility relation

    N = N_theta + E d / (2 (1 - nu^2)) <w'^2>,

which is solved as a scalar fixed point (the "self-consistent" von Karman solution);
freezing ``N`` at its blocked-state value ``N_theta`` gives the reduced model used for
design estimates.

All quantities are per unit out-of-plane depth.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

import numpy as np

from . import analytic, config

# Gauss points on [-1, 1] (4 points integrate the cubic Hermite products exactly)
_GP = np.array([-0.8611363115940526, -0.3399810435848563,
                0.3399810435848563, 0.8611363115940526])
_GW = np.array([0.3478548451374538, 0.6521451548625461,
                0.6521451548625461, 0.3478548451374538])


def _hermite(s, h):
    """Cubic Hermite basis and its first/second derivatives with respect to x.

    ``s`` is the local coordinate in [0, 1] and ``h`` the element length.  The rotation
    degrees of freedom are slopes (dimensionless), so the associated basis functions
    carry the factor ``h``.
    """
    s = np.atleast_1d(np.asarray(s, dtype=float))
    N = np.array([1 - 3 * s**2 + 2 * s**3,
                  h * (s - 2 * s**2 + s**3),
                  3 * s**2 - 2 * s**3,
                  h * (-s**2 + s**3)])
    dN = np.array([(-6 * s + 6 * s**2) / h,
                   (1 - 4 * s + 3 * s**2),
                   (6 * s - 6 * s**2) / h,
                   (-2 * s + 3 * s**2)])
    ddN = np.array([(-6 + 12 * s) / h**2,
                    (-4 + 6 * s) / h,
                    (6 - 12 * s) / h**2,
                    (-2 + 6 * s) / h])
    return N, dN, ddN


@dataclass
class WallState:
    """Result of a wall solve on a one-dimensional grid."""

    x: np.ndarray
    w: np.ndarray
    theta: np.ndarray          # slope dw/dx
    kappa_geo: np.ndarray      # -w''
    kappa_th: np.ndarray
    moment: np.ndarray         # M(x) = D_s (w'' + kappa_th)
    N: float
    N_theta: float
    p_mean: float
    arc: float                 # 0.5 <w'^2>
    n_iter: int = 1
    converged: bool = True
    history: list = field(default_factory=list)

    @property
    def w_max(self) -> float:
        return float(np.max(np.abs(self.w)))

    @property
    def x_at_wmax(self) -> float:
        return float(self.x[int(np.argmax(np.abs(self.w)))])

    @property
    def slope_max(self) -> float:
        return float(np.max(np.abs(self.theta)))

    def bending_stress(self, d: float) -> np.ndarray:
        """Extreme fibre bending stress, sigma = 6|M|/d^2 (both faces)."""
        return 6.0 * np.abs(self.moment) / d**2

    def surface_strain_bending(self, d: float) -> np.ndarray:
        """Bending fibre strain (kappa_geo - kappa_th) d/2."""
        return np.abs(self.kappa_geo - self.kappa_th) * d / 2.0


def _assemble(n_elem: int, L: float, Ds: float,
              N_of_x: Optional[Callable[[np.ndarray], np.ndarray]] = None,
              N_const: float = 0.0,
              p_of_x: Optional[Callable[[np.ndarray], np.ndarray]] = None,
              kap_of_x: Optional[Callable[[np.ndarray], np.ndarray]] = None):
    """Assemble the Hermite beam stiffness (elastic + geometric) and load vector."""
    ndof = 2 * (n_elem + 1)
    K = np.zeros((ndof, ndof))
    f = np.zeros(ndof)
    ngp = _GP.size
    for e in range(n_elem):
        x0 = e * L / n_elem
        h = L / n_elem
        dofs = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        ke = np.zeros((4, 4))
        fe = np.zeros(4)
        for g in range(ngp):
            s = 0.5 * (_GP[g] + 1.0)
            xg = x0 + s * h
            Nsh, dNsh, ddNsh = _hermite(s, h)
            Nsh, dNsh, ddNsh = Nsh[:, 0], dNsh[:, 0], ddNsh[:, 0]
            wq = 0.5 * _GW[g] * h          # dx = h ds, Gauss weight on [-1,1]
            Ng = N_of_x(np.array([xg]))[0] if N_of_x is not None else N_const
            ke += wq * (Ds * np.outer(ddNsh, ddNsh) - Ng * np.outer(dNsh, dNsh))
            pg = p_of_x(np.array([xg]))[0] if p_of_x is not None else 0.0
            kg = kap_of_x(np.array([xg]))[0] if kap_of_x is not None else 0.0
            fe += wq * (pg * Nsh - Ds * kg * ddNsh)
        K[np.ix_(dofs, dofs)] += ke
        f[dofs] += fe
    return K, f


def solve_wall(x: np.ndarray, Ds: float, kappa_th: np.ndarray,
               N: float = 0.0, p: Optional[np.ndarray] = None) -> WallState:
    """Solve the reduced von Karman wall problem for a prescribed membrane force.

    ``kappa_th`` and ``p`` are sampled at the nodes of ``x`` (uniform grid, ascending);
    the eigen-curvature is interpolated linearly and the pressure load is applied through
    the consistent load vector.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or x.size < 3:
        raise ValueError("wall grid must be one-dimensional with at least 3 nodes")
    if np.any(np.diff(x) <= 0):
        raise ValueError("wall grid must be strictly increasing")
    L = float(x[-1] - x[0])
    kappa_th = np.asarray(kappa_th, dtype=float)
    if kappa_th.shape != x.shape:
        raise ValueError("kappa_th must be sampled on the wall grid")
    n_elem = x.size - 1

    def kap_f(xq):
        return np.interp(xq, x, kappa_th)

    if p is None:
        p_f = None
        p_mean = 0.0
    else:
        p = np.asarray(p, dtype=float)
        if p.shape != x.shape:
            raise ValueError("p must be sampled on the wall grid")
        p_f = lambda xq: np.interp(xq, x, p)
        p_mean = float(np.trapezoid(p, x) / L)

    K, f = _assemble(n_elem, L, Ds, N_const=N, p_of_x=p_f, kap_of_x=kap_f)
    # pinned ends: w = 0 at x = 0 and x = L (rotation free)
    free = np.setdiff1d(np.arange(2 * (n_elem + 1)), [0, 2 * n_elem])
    u = np.zeros(2 * (n_elem + 1))
    u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    w = u[0::2]
    theta = u[1::2]

    # curvature and moment on the element interiors, reported at the nodes through the
    # element-wise constant-plus-linear reconstruction of w'' (Hermite: exact at nodes)
    # kappa_geo = -w'' is the geometric curvature (positive when the wall bows into
    # the channel); the total bending moment is M = D_s (w'' + kappa_th).
    kappa_geo = -_nodal_second_derivative(u, x)   # kappa = -w''  (manuscript sign)
    moment = Ds * (-kappa_geo + kappa_th)
    arc = 0.5 * float(np.trapezoid(theta**2, x) / L)
    return WallState(x=x, w=w, theta=theta, kappa_geo=kappa_geo, kappa_th=kappa_th,
                     moment=moment, N=float(N), N_theta=float(N), p_mean=p_mean,
                     arc=arc)


def _nodal_second_derivative(u: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Nodal w'' from the Hermite dofs (each node is shared by two elements)."""
    n_elem = x.size - 1
    vals = np.zeros((n_elem, 2))
    for e in range(n_elem):
        h = x[e + 1] - x[e]
        w0, t0, w1, t1 = u[2 * e], u[2 * e + 1], u[2 * e + 2], u[2 * e + 3]
        vals[e, 0] = (-6.0 * w0 - 4.0 * h * t0 + 6.0 * w1 - 2.0 * h * t1) / h**2
        vals[e, 1] = (6.0 * w0 + 2.0 * h * t0 - 6.0 * w1 + 4.0 * h * t1) / h**2
    out = np.zeros(x.size)
    out[0] = vals[0, 0]
    out[-1] = vals[-1, 1]
    out[1:-1] = 0.5 * (vals[:-1, 1] + vals[1:, 0])
    return out


def self_consistent(x: np.ndarray, Ds: float, kappa_th: np.ndarray,
                    theta_bar: float, cfg: Dict[str, Any],
                    p: Optional[np.ndarray] = None) -> WallState:
    """Solve the wall problem with the axial-compatibility update of the membrane force.

    The scalar fixed point ``N = N_theta + E d/(2(1-nu^2)) <w'^2>`` is iterated to
    machine precision; ``N_theta`` is evaluated from the thickness-averaged wall rise
    at the *same* state (``theta_bar`` may be a scalar or a nodal array).
    """
    g, s = cfg["geometry"], cfg["solid"]
    d, nu, E = g["d"], s["nu"], s["E"]
    Ds = float(Ds)
    theta_bar = np.asarray(theta_bar, dtype=float)
    th_mean = float(np.mean(theta_bar)) if theta_bar.ndim else float(theta_bar)
    N0 = analytic.membrane_force(cfg, th_mean)
    N = abs(N0)  # start from the blocked-state compressive magnitude
    tol = float(cfg["numerics"]["wall"].get("fixed_point_tol", 1e-12))
    max_it = int(cfg["numerics"]["wall"].get("fixed_point_max_iter", 200))
    hist = []
    state = None
    for it in range(1, max_it + 1):
        state = solve_wall(x, Ds, kappa_th, N=N, p=p)
        # signed compatibility: N = N_theta + k <w'^2>/2 with N_theta < 0 in compression;
        # the stiffness uses the compressive magnitude, hence
        # Signed compatibility N = N_theta + k <w'^2>/2, with N_theta < 0 (compression)
        # and k = E d / [2 (1 - nu^2)]; the beam stiffness is driven by the compressive
        # magnitude |N|, which therefore decreases as the wall bows and picks up arc
        # length:  |N| = |N_theta| - k <w'^2>/2.
        N_comp = max(-(N0 + E * d / (2.0 * (1.0 - nu**2)) * state.arc), 0.0)
        hist.append({"iter": it, "N": N, "N_next": N_comp, "w_max": state.w_max})
        if abs(N_comp - N) <= tol * max(abs(N), 1.0):
            state.N = N_comp
            state.N_theta = N0
            state.n_iter = it
            state.converged = True
            state.history = hist
            return state
        N = N_comp if N_comp > 0 else 0.0
    state.N = N
    state.N_theta = N0
    state.n_iter = max_it
    state.converged = False
    state.history = hist
    return state


def frozen_force(x: np.ndarray, Ds: float, kappa_th: float, N: float,
                 p: Optional[np.ndarray] = None) -> WallState:
    """Frozen-force solve with a constant eigen-curvature (wrapper for benchmarks)."""
    kappa = np.full_like(np.asarray(x, dtype=float), float(kappa_th))
    return solve_wall(x, Ds, kappa, N=N, p=p)


def closed_form(x: np.ndarray, kappa: float, mu2: float) -> np.ndarray:
    """Analytical beam-column deflection for constant kappa and mu^2 = N/D_s.

    Returns ``w`` of Eq. (beamcolsol) of the manuscript; the limit ``mu^2 -> 0`` is the
    parabolic bow ``kappa x (L-x)/2``.
    """
    x = np.asarray(x, dtype=float)
    L = x[-1]
    if mu2 <= 1e-8:
        return 0.5 * kappa * x * (L - x)
    mu = math.sqrt(mu2)
    s = mu * L
    if abs(math.sin(s)) < 1e-12:
        raise ValueError("mu*L is a multiple of pi: at or beyond the buckling threshold")
    a = (1.0 - math.cos(s)) / math.sin(s)
    return kappa / mu2 * (a * np.sin(mu * x) + np.cos(mu * x) - 1.0)


def buckling_catalog(cfg: Dict[str, Any], d_values: np.ndarray) -> Dict[str, np.ndarray]:
    """Critical mean wall rise, Euler load and flexural rigidity versus wall thickness."""
    x = np.linspace(0.0, cfg["geometry"]["L"], 101)
    L = float(cfg["geometry"]["L"])
    Tcr, Ncr, Ds = [], [], []
    for d in d_values:
        sub = _with_thickness(cfg, float(d))
        Tcr.append(analytic.critical_temperature(sub))
        Ds.append(config.derived(sub)["Ds"])
        Ncr.append(math.pi**2 * Ds[-1] / L**2)
    return {"d": np.asarray(d_values, dtype=float), "T_cr": np.asarray(Tcr),
            "N_cr": np.asarray(Ncr), "Ds": np.asarray(Ds)}


def _with_thickness(cfg: Dict[str, Any], d: float) -> Dict[str, Any]:
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in cfg.items()}
    out["geometry"] = dict(cfg["geometry"])
    out["geometry"]["d"] = d
    return out


def design_envelope(cfg: Dict[str, Any], q_values: Optional[np.ndarray] = None,
                    n_grid: int = 201) -> Dict[str, np.ndarray]:
    """Admissible-envelope curves using the beam--column wall model.

    For each imposed flux the wall problem is solved at the blocked-state membrane force
    with the 1D mean wall rise, giving the beam-column bow, fibre strain, membrane and
    bending stress, and the buckling margin.  The three design ceilings of the
    formulation (mesh-validity bound, wall-stress cap, buckling margin) are located on
    these curves.
    """
    g, s = cfg["geometry"], cfg["solid"]
    H0, d, L = g["H0"], g["d"], g["L"]
    Ds = config.derived(cfg)["Ds"]
    Ncr = math.pi**2 * Ds / L**2
    Tcr = analytic.critical_temperature(cfg)
    q_values = np.asarray(q_values if q_values is not None else np.linspace(0, 1.2e4, 241))
    base = analytic.ceiling_sweep(cfg, q_values)
    x = np.linspace(0.0, L, int(cfg["numerics"]["wall"].get("n_points", 241)))
    keys = ("w_max", "w_over_H0", "eps_fibre", "sigma_bend", "sigma_max", "sigma_over_sy",
            "slope_max", "N_over_Ncr_bc", "arc")
    out = {k: np.zeros_like(q_values) for k in keys}
    for i, q in enumerate(q_values):
        th = base["theta_bar"][i]
        kap = base["kappa_th"][i]
        N = abs(analytic.membrane_force(cfg, th))
        st = solve_wall(x, Ds, np.full_like(x, kap), N=N)
        out["w_max"][i] = st.w_max
        out["w_over_H0"][i] = st.w_max / H0
        out["eps_fibre"][i] = float(np.max(st.surface_strain_bending(d)))
        out["sigma_bend"][i] = float(np.max(st.bending_stress(d)))
        out["sigma_max"][i] = out["sigma_bend"][i] + abs(base["sigma_memb"][i])
        out["sigma_over_sy"][i] = out["sigma_max"][i] / s["sigma_y"]
        out["slope_max"][i] = st.slope_max
        out["N_over_Ncr_bc"][i] = st.N / Ncr
        out["arc"][i] = st.arc
    out.update({k: v for k, v in base.items() if k not in out})
    out["M_b"] = np.where(base["theta_bar"] > 0, Tcr / np.maximum(base["theta_bar"], 1e-30), np.inf)
    return out


def consistency_error_curve(cfg: Dict[str, Any], n_q: int = 41) -> Dict[str, np.ndarray]:
    """Frozen-force versus self-consistent von Karman solution over the flux range.

    Quantifies the model-form error of the reduced wall equation: the relative error of
    the frozen-force deflection, the force relaxation fraction and the resulting moment
    error, as functions of the imposed flux.
    """
    g, s = cfg["geometry"], cfg["solid"]
    L, d = g["L"], g["d"]
    Ds = config.derived(cfg)["Ds"]
    x = np.linspace(0.0, L, int(cfg["numerics"]["wall"].get("n_points", 241)))
    q_vals = np.linspace(1.0e2, 1.0e4, n_q)
    res = {k: np.zeros(n_q) for k in
           ("q", "N_over_Ncr", "w_frozen", "w_consistent", "rel_error", "relaxation",
            "M_frozen", "M_consistent", "moment_error")}
    res["q"] = q_vals
    for i, q in enumerate(q_vals):
        th = analytic.theta_bar_estimate(cfg, q)["theta_bar"]
        kap = analytic.kappa_th(cfg, q)
        N0 = analytic.membrane_force(cfg, th)
        frozen = solve_wall(x, Ds, np.full_like(x, kap), N=abs(N0))
        cons = self_consistent(x, Ds, np.full_like(x, kap), th, cfg)
        res["N_over_Ncr"][i] = abs(N0) / (math.pi**2 * Ds / L**2)
        res["w_frozen"][i] = frozen.w_max
        res["w_consistent"][i] = cons.w_max
        res["rel_error"][i] = (frozen.w_max - cons.w_max) / cons.w_max
        res["relaxation"][i] = (abs(N0) - cons.N) / abs(N0)
        res["M_frozen"][i] = float(np.max(np.abs(frozen.moment)))
        res["M_consistent"][i] = float(np.max(np.abs(cons.moment)))
        res["moment_error"][i] = (res["M_frozen"][i] - res["M_consistent"][i]) / res["M_consistent"][i]
    return res
