"""Conjugate heat transfer: fluid energy equation coupled to wall conduction.

The fluid energy equation (advection--diffusion, SUPG-stabilised at the baseline Peclet
number) and the steady conduction equation of the wall are assembled into a *single*
algebraic system on a shared set of interface unknowns.  Temperature continuity is
therefore exact by construction, and the interface heat-flux condition is satisfied in
the weak sense without any interpolated flux being passed between the subdomains - the
interface boundary terms cancel identically at assembly, as in the monolithic statement
of the formulation.

The thermal problem is linear; it is solved once per coupled iteration with the current
velocity field and geometry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import scipy.sparse as sp

from . import fem, flow


@dataclass
class ThermalSolution:
    T: np.ndarray                    # global P2 temperature (joint numbering)
    fluid: fem.TriMesh
    solid: fem.TriMesh
    flow: flow.FlowSolution
    n_global: int
    residual: float = 0.0

    @property
    def T_fluid_nodes(self) -> np.ndarray:
        """Temperature at the fluid P2 nodes, shape (n_elem, 6)."""
        return self.T[self.fluid.p2]


# ---------------------------------------------------------------------------
#  Boundary loads and line integrals
# ---------------------------------------------------------------------------
_GAUSS1 = np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)])
_GW1 = np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0])


def _edge_basis(xi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Quadratic basis on an edge: (values at a, b, midpoint) for points xi in [-1,1]."""
    Na = 0.5 * xi * (xi - 1.0)
    Nb = 0.5 * xi * (xi + 1.0)
    Nm = 1.0 - xi**2
    return Na, Nb, Nm


def boundary_flux_load(mesh: fem.TriMesh, tag: str, value: float = 1.0,
                       coefficient: Optional[Callable[[np.ndarray], np.ndarray]] = None
                       ) -> np.ndarray:
    """Consistent P2 load of a boundary flux ``q . n = value`` over a boundary tag.

    The integrand is constant (or supplied as a function of the edge coordinate), and the
    integral is evaluated with three-point Gauss quadrature on each quadratic edge, i.e.
    exactly for a quadratic temperature field.
    """
    n = mesh.n_p2
    f = np.zeros(n)
    pairs = mesh.boundary.get(tag, np.zeros((0, 2), dtype=int))
    if pairs.size == 0:
        return f
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(mesh.edge_nodes, axis=1))}
    for a, b in pairs:
        a, b = int(a), int(b)
        mid = mesh.mid_offset + lut[tuple(sorted((a, b)))]
        xa, xb = mesh.xy[a], mesh.xy[b]
        xm = 0.5 * (xa + xb)
        length = np.linalg.norm(xb - xa)
        Na, Nb, Nm = _edge_basis(_GAUSS1)
        for g in range(3):
            xg = 0.5 * (1 - _GAUSS1[g]) * xa + 0.5 * (1 + _GAUSS1[g]) * xb
            qv = value if coefficient is None else float(coefficient(np.array([xg[0]]))[0])
            w = 0.5 * length * _GW1[g] * qv
            f[a] += w * Na[g]
            f[b] += w * Nb[g]
            f[mid] += w * Nm[g]
    return f


def line_integral(mesh: fem.TriMesh, values: np.ndarray, pairs: np.ndarray) -> float:
    """Integral of the P2 field ``values`` along a polyline of quadratic edges."""
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(mesh.edge_nodes, axis=1))}
    total = 0.0
    for a, b in pairs:
        a, b = int(a), int(b)
        mid = mesh.mid_offset + lut[tuple(sorted((a, b)))]
        xa, xb = mesh.xy[a], mesh.xy[b]
        length = np.linalg.norm(xb - xa)
        Na, Nb, Nm = _edge_basis(_GAUSS1)
        va = Na * values[a] + Nb * values[b] + Nm * values[mid]
        total += 0.5 * length * float(np.sum(_GW1 * va))
    return total


# ---------------------------------------------------------------------------
#  Energy assembly
# ---------------------------------------------------------------------------
def supg_tau(data: fem.ElementData, u_gp: np.ndarray, rho: float, cp: float,
             k: float) -> np.ndarray:
    """Residual-based SUPG coefficient per element (mean over quadrature points)."""
    umag = np.sqrt(np.sum(u_gp**2, axis=2))            # (ne, nqp)
    u_e = np.maximum(umag.mean(axis=1), 1e-30)
    h = data.hsize
    pe = rho * cp * u_e * h / (2.0 * k)
    small = pe < 1e-8
    coth = np.where(small, 1.0 / np.maximum(pe, 1e-30), 1.0 / np.tanh(np.where(small, 1.0, pe)))
    tau = h / (2.0 * u_e) * (coth - np.where(small, 0.0, 1.0 / np.maximum(pe, 1e-30)))
    tau = np.where(small, h**2 / (12.0 * k / (rho * cp)), tau)
    return tau


def assemble_energy(fluid: fem.TriMesh, solid: fem.TriMesh, fdata: fem.ElementData,
                    sdata: fem.ElementData, u: np.ndarray, cfg: Dict,
                    n_global: int, use_supg: bool = True) -> Tuple[sp.csr_matrix, np.ndarray]:
    """Assemble the monolithic fluid + solid energy system on the joint numbering."""
    f, s = cfg["fluid"], cfg["solid"]
    rho, cp, kf = f["rho"], f["cp"], f["k"]
    ks = s["k"]

    # ---------------- fluid --------------------------------------------------
    u_gp = np.einsum("gb,ebk->egk", fdata.N, u[fluid.p2])
    dNdx, N, w = fdata.dNdx, fdata.N, fdata.w
    # adv[g,b] = u . grad phi_b ; the Galerkin advection matrix is
    # C[a,b] = int rho cp (u . grad phi_b) phi_a  (test index a, trial index b)
    adv = np.einsum("egk,egbk->egb", u_gp, dNdx)
    G = np.einsum("egam,egbm,eg->eab", dNdx, dNdx, w)
    C = rho * cp * np.einsum("ga,egb,eg->eab", N, adv, w)
    Ke = kf * G + C
    if use_supg:
        tau = supg_tau(fdata, u_gp, rho, cp, kf)
        S = np.einsum("e,ega,egb,eg->eab", tau * rho * cp, adv, adv, w)  # symmetric
        Ke = Ke + S
    Kf = fem.element_matrix(fluid.p2, Ke, n_global)
    rhs = np.zeros(n_global)

    # ---------------- solid --------------------------------------------------
    Gs = np.einsum("egam,egbm,eg->eab", sdata.dNdx, sdata.dNdx, sdata.w)
    Ks = fem.element_matrix(solid.p2, ks * Gs, n_global)
    return (Kf + Ks).tocsr(), rhs


def solve_thermal(fluid: fem.TriMesh, solid: fem.TriMesh, sol_flow: flow.FlowSolution,
                  cfg: Dict, n_global: int) -> ThermalSolution:
    """Solve the steady conjugate thermal problem for the current geometry and flow."""
    op = cfg["operating"]
    fdata = sol_flow.data
    sdata = fem.element_data(solid, solid.p2_coordinates(n_global))
    K, rhs = assemble_energy(fluid, solid, fdata, sdata, sol_flow.u, cfg, n_global,
                             use_supg=bool(cfg["numerics"]["thermal"].get("supg", True)))
    # imposed flux on the outer face of the strip
    rhs += boundary_flux_load(solid, "outer", float(op["q_flux"]))
    # Dirichlet inlet temperature (all P2 nodes of the inlet edge)
    inlet_d, _ = fluid.p2_boundary_coordinates("inlet")
    dofs = inlet_d
    vals = np.full(inlet_d.size, float(op["Tin"]))
    T, res = fem.solve_dirichlet(K, rhs, dofs, vals, return_residual=True)
    return ThermalSolution(T=T, fluid=fluid, solid=solid, flow=sol_flow,
                           n_global=n_global, residual=float(res))


# ---------------------------------------------------------------------------
#  Thickness average of the wall temperature
# ---------------------------------------------------------------------------
def column_average(solid: fem.TriMesh, T: np.ndarray, reference: float = 0.0
                   ) -> Dict[str, np.ndarray]:
    """Exact thickness average and mid-surface value of the wall temperature.

    Along each column of the structured wall mesh the P2 field is a quadratic on
    every element, so Simpson's rule integrates it exactly.  The returned
    ``theta_avg`` is therefore the true thickness average
    ``(1/h) int theta dy``, whereas ``theta_mid`` is the value at the geometric
    mid-surface of the least-squares line of :func:`wall_profile`.  The two differ
    by the curvature of the through-thickness profile, which vanishes in a
    one-dimensional (uniform-flux) wall.
    """
    if solid.grid is None:
        raise RuntimeError("column_average requires the structured solid grid map")
    nid = solid.grid
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(solid.edge_nodes, axis=1))}
    ncol = nid.shape[1]
    theta_avg = np.zeros(ncol)
    theta_mid = np.zeros(ncol)
    thick = np.zeros(ncol)
    x = np.zeros(ncol)
    for i in range(ncol):
        ids = nid[:, i]
        yv = solid.xy[ids, 1]
        mids = np.array([solid.mid_offset + lut[tuple(sorted((int(a), int(b))))]
                         for a, b in zip(ids[:-1], ids[1:])], dtype=int)
        Tv = T[ids] - reference
        Tm = T[mids] - reference
        h = float(yv[-1] - yv[0])
        theta_avg[i] = float(np.sum((yv[1:] - yv[:-1]) / 6.0
                                    * (Tv[:-1] + 4.0 * Tm + Tv[1:])) / h)
        y = np.concatenate([yv, 0.5 * (yv[:-1] + yv[1:])])
        th = np.concatenate([Tv, Tm])
        A = np.stack([np.ones_like(y), y - yv.mean()], axis=1)
        theta_mid[i] = float(np.linalg.lstsq(A, th, rcond=None)[0][0])
        thick[i] = h
        x[i] = float(solid.xy[ids[0], 0])
    return {"x": x, "theta_avg": theta_avg, "theta_mid": theta_mid,
            "thickness": thick}


# ---------------------------------------------------------------------------
#  Post-processing
# ---------------------------------------------------------------------------
def boundary_heat_flux(mesh: fem.TriMesh, data: fem.ElementData, T: np.ndarray,
                       tag: str, conductivity: float = 1.0,
                       normal_sign: Optional[np.ndarray] = None
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """Heat flux normal to a boundary tag, ``q = +k grad T . n`` (n pointing outward).

    ``normal_sign`` optionally forces the sign of the outward normal for tags whose
    orientation is not known a priori (``[sx, sy]``: flip the normal so that its
    component along this vector is positive).
    """
    k = float(conductivity)
    pairs = mesh.boundary.get(tag, np.zeros((0, 2), dtype=int))
    if pairs.size == 0:
        return np.zeros(0), np.zeros(0)
    lut = {tuple(sorted(p)): e for e, p in enumerate(np.sort(mesh.edge_nodes, axis=1))}
    # element lookup: first element carrying each edge
    owner = {}
    for e, tri in enumerate(mesh.edges):
        for kk in tri:
            owner.setdefault(int(kk), e)
    xs, qs = [], []
    for a, b in pairs:
        a, b = int(a), int(b)
        kk = lut[tuple(sorted((a, b)))]
        e = owner[kk]
        Tloc = T[mesh.p2[e]]
        grad = np.einsum("gba,b->ga", data.dNdx[e], Tloc)
        wq = data.w[e] / data.w[e].sum()
        g = np.einsum("g,ga->a", wq, grad)
        t = mesh.xy[b] - mesh.xy[a]
        t = t / np.linalg.norm(t)
        nvec = np.array([-t[1], t[0]])
        if normal_sign is not None and float(nvec @ np.asarray(normal_sign, float)) < 0:
            nvec = -nvec
        xs.append(0.5 * (mesh.xy[a, 0] + mesh.xy[b, 0]))
        qs.append(k * float(g @ nvec))
    xs = np.asarray(xs)
    qs = np.asarray(qs)
    o = np.argsort(xs)
    return xs[o], qs[o]


def interface_heat_flux(fluid: fem.TriMesh, fdata: fem.ElementData, T: np.ndarray,
                        sol_flow: Optional[flow.FlowSolution] = None,
                        conductivity: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """Wall heat flux into the fluid, ``q_w = -k_f grad T . n``, on the interface edges.

    ``n`` is the unit normal of the fluid domain (pointing into the solid), so ``q_w > 0``
    means heat entering the fluid.  Values are returned together with the edge mid-point
    x-coordinates, sorted along the segment.
    """
    # the fluid interface normal points into the solid, i.e. upwards (+y)
    return boundary_heat_flux(fluid, fdata, T, "interface", conductivity,
                              normal_sign=np.array([0.0, 1.0]))


def solid_heat_flux(solid: fem.TriMesh, sdata: fem.ElementData, T: np.ndarray,
                    conductivity: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """Conductive flux at the interface evaluated from the *solid* side (verification)."""
    return boundary_heat_flux(solid, sdata, T, "interface", conductivity,
                              normal_sign=np.array([0.0, 1.0]))


def wall_profile(solid: fem.TriMesh, sdata: fem.ElementData, T: np.ndarray,
                 cfg: Dict, reference: Optional[float] = None) -> Dict[str, np.ndarray]:
    """Thickness-averaged wall temperature and thermal eigen-curvature along the strip.

    For each column of the structured wall mesh the temperature is fitted by the
    least-squares linear profile ``theta(y) = theta_bar + Gamma (y - y_c)``; the mean
    ``theta_bar(x)`` drives the membrane force and the slope ``Gamma(x)`` gives the free
    thermal curvature ``kappa_th = (1+nu) alpha Gamma``.  ``theta`` is reported as a
    *rise* above the reference temperature (the inlet temperature by default), so that it
    can be used directly in the thermoelastic relations of the formulation.
    """
    g = cfg["geometry"]
    s = cfg["solid"]
    if reference is None:
        reference = float(cfg["operating"]["Tin"])
    nxd = int(cfg["numerics"]["nx_heated"])
    ny = int(cfg["numerics"]["ny_solid"])
    nid = solid.grid
    if nid is None:
        raise RuntimeError("wall_profile requires the structured solid grid map")
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(solid.edge_nodes, axis=1))}
    iface_xy = solid.xy[nid[0, :], :]
    theta_bar = np.zeros(nxd + 1)
    gamma = np.zeros(nxd + 1)
    for i in range(nxd + 1):
        ids = nid[:, i]
        mids = np.array([solid.mid_offset + lut[tuple(sorted((int(a), int(b))))]
                         for a, b in zip(ids[:-1], ids[1:])], dtype=int)
        xcol = solid.xy[ids, 0]
        if np.max(np.abs(xcol - xcol[0])) > 1e-12:
            raise RuntimeError("solid grid column is not vertical")
        yv = np.concatenate([solid.xy[ids, 1], 0.5 * (solid.xy[ids[:-1], 1]
                                                      + solid.xy[ids[1:], 1])])
        Tv = np.concatenate([T[ids], T[mids]]) - reference
        yy = yv - (solid.xy[ids, 1].mean())
        A = np.stack([np.ones_like(yy), yy], axis=1)
        coef, *_ = np.linalg.lstsq(A, Tv, rcond=None)
        theta_bar[i] = coef[0]
        gamma[i] = coef[1]
    return {"x": iface_xy[:, 0].copy(), "theta_bar": theta_bar, "gamma": gamma,
            "kappa_th": (1.0 + s["nu"]) * s["alpha"] * gamma}


def bulk_temperature(fluid: fem.TriMesh, T: np.ndarray, sol_flow: flow.FlowSolution,
                     x_index: int) -> float:
    """Mass-flux-weighted bulk temperature on the vertical mesh column ``x_index``."""
    nid = fluid.grid
    if nid is None:
        raise RuntimeError("bulk temperature requires the structured grid map")
    ny_fluid = nid.shape[0] - 1
    pairs = np.array([(nid[j, x_index], nid[j + 1, x_index]) for j in range(ny_fluid)])
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(fluid.edge_nodes, axis=1))}
    num = 0.0
    den = 0.0
    Na, Nb, Nm = _edge_basis(_GAUSS1)
    for a, b in pairs:
        mid = fluid.mid_offset + lut[tuple(sorted((int(a), int(b))))]
        xa, xb = fluid.xy[a], fluid.xy[b]
        length = np.linalg.norm(xb - xa)
        # normal to the edge, aligned with the streamwise direction
        t = (xb - xa) / length
        nvec = np.array([-t[1], t[0]])
        if nvec[0] < 0:
            nvec = -nvec
        for g in range(3):
            w = 0.5 * length * _GW1[g]
            uu = (Na[g] * sol_flow.u[a] + Nb[g] * sol_flow.u[b] + Nm[g] * sol_flow.u[mid])
            TT = Na[g] * T[a] + Nb[g] * T[b] + Nm[g] * T[mid]
            un = float(uu @ nvec)
            num += w * un * TT
            den += w * un
    return num / den if abs(den) > 0 else float("nan")


def nusselt_profile(thermal: ThermalSolution, cfg: Dict, n_points: int = 61
                    ) -> Dict[str, np.ndarray]:
    """Local Nusselt number along the heated segment, Nu = 2 H0 h / k_f."""
    fluid, T = thermal.fluid, thermal.T
    H0 = cfg["geometry"]["H0"]
    kf = cfg["fluid"]["k"]
    xs, q = interface_heat_flux(fluid, thermal.flow.data, T, thermal.flow,
                               conductivity=kf)
    # wall temperature at the same stations (shared interface dofs)
    pairs = fluid.boundary["interface"]
    Tw = 0.5 * (T[pairs[:, 0]] + T[pairs[:, 1]])
    xw = 0.5 * (fluid.xy[pairs[:, 0], 0] + fluid.xy[pairs[:, 1], 0])
    o = np.argsort(xw)
    xw, Tw = xw[o], Tw[o]
    grid = fluid.grid
    nxd = int(cfg["numerics"]["nx_heated"])
    nxe = int(cfg["numerics"]["nx_entrance"])
    x_st = xw
    Tb = np.array([bulk_temperature(fluid, T, thermal.flow, nxe + i)
                   for i in range(nxd + 1)])
    # interpolate the bulk temperature at the edge mid-points
    x_nodes = np.linspace(0.0, cfg["geometry"]["L"], nxd + 1)
    Tb_mid = np.interp(x_st, x_nodes, Tb)
    dT = Tw - Tb_mid
    with np.errstate(divide="ignore", invalid="ignore"):
        h = np.where(np.abs(dT) > 1e-9, q / dT, np.nan)
    Nu = 2.0 * H0 * h / kf
    return {"x": x_st, "q": q, "Tw": Tw, "Tb": Tb_mid, "h": h, "Nu": Nu,
            "Tb_nodes": Tb, "x_nodes": x_nodes}


def enthalpy_balance(thermal: ThermalSolution, cfg: Dict) -> Dict[str, float]:
    """Global energy balance of the coupled solution.

    ``Q_in`` is the imposed flux integrated over the outer face; ``Q_out`` is the
    enthalpy flux through the outlet plane relative to the inlet temperature.  The
    relative imbalance is the discrete conservation error used as a per-run control.
    """
    fluid, solid, T = thermal.fluid, thermal.solid, thermal.T
    f, op = cfg["fluid"], cfg["operating"]
    Q_in = line_integral(solid, np.ones(solid.n_p2) * op["q_flux"], solid.boundary["outer"])
    # outlet plane: x = L + Lo corresponds to the last column of the structured grid
    nid = fluid.grid
    nx = nid.shape[1] - 1
    ny = nid.shape[0] - 1
    pairs = np.array([(nid[j, nx], nid[j + 1, nx]) for j in range(ny)])
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(fluid.edge_nodes, axis=1))}
    Q_out = 0.0
    Na, Nb, Nm = _edge_basis(_GAUSS1)
    for a, b in pairs:
        mid = fluid.mid_offset + lut[tuple(sorted((int(a), int(b))))]
        xa, xb = fluid.xy[a], fluid.xy[b]
        length = np.linalg.norm(xb - xa)
        t = (xb - xa) / length
        nvec = np.array([-t[1], t[0]])
        if nvec[0] < 0:
            nvec = -nvec
        for g in range(3):
            w = 0.5 * length * _GW1[g]
            uu = (Na[g] * thermal.flow.u[a] + Nb[g] * thermal.flow.u[b]
                  + Nm[g] * thermal.flow.u[mid])
            TT = Na[g] * T[a] + Nb[g] * T[b] + Nm[g] * T[mid]
            Q_out += w * f["rho"] * f["cp"] * float(uu @ nvec) * (TT - op["Tin"])
    return {"Q_in": Q_in, "Q_out": Q_out,
            "rel_imbalance": abs(Q_out - Q_in) / abs(Q_in) if Q_in != 0 else float("inf")}


def interface_flux_jump(thermal: ThermalSolution, cfg: Dict) -> float:
    """Relative norm of the discrete interface flux jump ``[k d_n T]``.

    Both sides of the interface are evaluated on the same conforming quadrature points;
    a vanishing jump indicates that the monolithic assembly satisfies the conjugate
    condition (the residual is a discretisation, not a modelling, quantity).
    """
    fluid, solid, T = thermal.fluid, thermal.solid, thermal.T
    sdata = fem.element_data(solid, solid.p2_coordinates(thermal.n_global))
    cfg_f, cfg_s = cfg["fluid"]["k"], cfg["solid"]["k"]
    xs_f, qf = interface_heat_flux(fluid, thermal.flow.data, T, thermal.flow,
                                   conductivity=cfg_f)
    xs_s, qs = solid_heat_flux(solid, sdata, T, conductivity=cfg_s)
    qf = np.abs(qf)
    qs = np.abs(qs)
    n = min(qf.size, qs.size)
    jump = np.abs(qf[:n] - qs[:n])
    denom = float(np.linalg.norm(qf[:n]))
    return float(np.linalg.norm(jump) / denom) if denom > 0 else 0.0
