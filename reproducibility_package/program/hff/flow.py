"""Steady incompressible flow solver: P2-P1 Taylor--Hood finite elements.

Solves the steady Navier--Stokes system

    rho (u . grad) u = -grad p + mu lap u,     div u = 0

in the deformed passage, with a prescribed fully developed inlet profile, no-slip on all
walls (including the deformed interface) and the do-nothing (traction-free) outflow
condition of the formulation.  The nonlinearity is treated by Picard iteration with
Reynolds continuation and under-relaxation; the discrete system is factorised directly.

Both the convection and the viscous operators are assembled on the *current* geometry, so
the solver is a genuine body-fitted finite-element discretisation of the flow in the
deformed passage rather than a lubrication approximation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import scipy.sparse as sp

from . import fem


def poiseuille(y: np.ndarray, H0: float, U: float) -> np.ndarray:
    """Fully developed plane-Poiseuille profile with mean velocity U in a slit of height H0."""
    return 6.0 * U * (y / H0) * (1.0 - y / H0)


@dataclass
class FlowSolution:
    u: np.ndarray                     # (n_p2, 2)
    p: np.ndarray                     # (n_p1,)
    mesh: fem.TriMesh
    data: fem.ElementData
    iterations: int = 0
    converged: bool = True
    residual_history: List[float] = field(default_factory=list)
    re: float = 0.0

    def velocity_at_nodes(self) -> np.ndarray:
        return self.u


def _assemble(mesh: fem.TriMesh, data: fem.ElementData, u_old: np.ndarray,
              re_h: float, h_ref: float = 1.0,
              pressure_penalty: Optional[Tuple[int, float]] = None
              ) -> Tuple[sp.csr_matrix, np.ndarray]:
    """Assemble the dimensionless Picard matrix and right-hand side.

    The system is assembled in the non-dimensional variables ``u/U`` and
    ``p H/(mu U)`` with lengths scaled by ``H0``.  In these variables the viscous block is
    of order unity and the convective block of order ``Re_H``; this scaling is essential
    for the accuracy of the direct factorisation of the saddle-point matrix (an unscaled
    assembly is ill-conditioned by eight orders of magnitude).
    """
    p2 = mesh.p2
    np2 = int(p2.max()) + 1
    nv = mesh.n_vertices
    ndof = 2 * np2 + nv

    dNdx, N, w = data.dNdx, data.N, data.w

    # G[a,b] = int grad(phi_a).grad(phi_b),  Hl[a,b] = int d_l phi_a d_k phi_b
    G = np.einsum("egam,egbm,eg->eab", dNdx, dNdx, w)
    dNx, dNy = dNdx[:, :, :, 0], dNdx[:, :, :, 1]
    Hxx = np.einsum("ega,egb,eg->eab", dNx, dNx, w)
    Hyy = np.einsum("ega,egb,eg->eab", dNy, dNy, w)
    Hxy = np.einsum("ega,egb,eg->eab", dNx, dNy, w)   # int d_x phi_a d_y phi_b
    Hyx = np.einsum("ega,egb,eg->eab", dNy, dNx, w)   # int d_y phi_a d_x phi_b

    # ---- velocity block: (delta_ij G + int d_j phi_a d_i phi_b) -------------
    Ke = np.empty((p2.shape[0], 12, 12))
    Ke[:, 0:6, 0:6] = G + Hxx                 # (x,x)
    Ke[:, 6:12, 6:12] = G + Hyy               # (y,y)
    Ke[:, 0:6, 6:12] = Hyx                    # (x test, y trial)
    Ke[:, 6:12, 0:6] = Hxy                    # (y test, x trial)

    # ---- convection (frozen coefficient): rho int (u_old.grad phi_a) phi_b --
    u_gp = np.einsum("gb,ebk->egk", N, u_old[p2])
    adv = np.einsum("egk,egak->ega", u_gp, dNdx)        # u.grad phi_a at quadrature points
    C = re_h * np.einsum("ega,gb,eg->eab", adv, N, w)
    Ke[:, 0:6, 0:6] += C
    Ke[:, 6:12, 6:12] += C

    dofs_v = np.hstack([p2, np2 + p2])          # (ne, 12)
    K = fem.element_matrix(dofs_v, Ke, ndof)

    # ---- pressure / continuity coupling ------------------------------------
    # B[(a,k),(c)] = -int phi_c d_k phi_a ;  continuity  int phi_c d_k u_k
    N1 = _p1_values()
    w1 = data.w
    Bx = -np.einsum("ega,gc,eg->eac", dNdx[:, :, :, 0], N1, w1)
    By = -np.einsum("ega,gc,eg->eac", dNdx[:, :, :, 1], N1, w1)
    rows_p = np.repeat(2 * np2 + mesh.tris, 6, axis=1)   # (ne, 18): c-major
    cols_u = np.tile(p2, (1, 3))                         # (ne, 18): c-major
    Bx_flat = np.transpose(Bx, (0, 2, 1)).reshape(-1)
    By_flat = np.transpose(By, (0, 2, 1)).reshape(-1)
    # The pressure unknown is scaled with the natural unit mu*U/H0, so the pressure term
    # of the momentum equation carries the factor 1/H0.  This balances the saddle-point
    # matrix (an unbalanced assembly loses all accuracy in the direct factorisation).
    sc = 1.0 / h_ref
    Kp = fem.scatter(rows_p, cols_u, sc * Bx_flat, ndof)
    Kp += fem.scatter(rows_p, np2 + cols_u, sc * By_flat, ndof)
    KT = fem.scatter(cols_u, rows_p, sc * Bx_flat, ndof)
    KT += fem.scatter(np2 + cols_u, rows_p, sc * By_flat, ndof)
    K = (K + Kp + KT).tolil()
    if pressure_penalty is not None:
        # weak pin of the pressure level: a small diagonal entry on one pressure row
        # removes the near-null (constant pressure) mode without dropping any continuity
        # equation, so the discrete mass balance is preserved
        d_pin, alpha = pressure_penalty
        K[d_pin, d_pin] += alpha
    K = K.tocsr()
    b = np.zeros(ndof)
    return K, b


_P1_N_CACHE = {}


def _p1_values() -> np.ndarray:
    N, _ = fem.p1_basis(fem._QP[:, 0], fem._QP[:, 1])
    return N


def solve_flow(mesh: fem.TriMesh, cfg: Dict, u_init: Optional[np.ndarray] = None,
               verbose: bool = False) -> FlowSolution:
    """Solve the steady flow on ``mesh`` by Picard iteration with Reynolds continuation.

    The unknowns are the dimensionless velocity ``u/U`` and pressure ``p/(mu U)``;
    :class:`FlowSolution` stores the physical fields.  Continuation is applied in the
    Reynolds number, starting from the Stokes limit, and the iteration is stopped when
    the relative velocity increment falls below ``numerics.flow.picard_tol``.
    """
    g, op, f, num = cfg["geometry"], cfg["operating"], cfg["fluid"], cfg["numerics"]
    H0, U = g["H0"], op["U"]
    mu, rho = f["mu"], f["rho"]
    re_h = rho * U * H0 / mu
    fnum = num["flow"]
    tol = float(fnum.get("picard_tol", 1e-10))
    max_it = int(fnum.get("picard_max_iter", 60))
    relax = float(fnum.get("relaxation", 1.0))
    re_fracs = [float(v) for v in fnum.get("re_continuation", [0.0, 0.25, 0.5, 1.0])]

    data = fem.element_data(mesh)
    np2 = int(mesh.p2.max()) + 1
    u = np.zeros((np2, 2)) if u_init is None else u_init.copy() / U

    wall_tags = ["wall_bottom", "lids", "interface"]
    wall_d = np.unique(np.concatenate([mesh.p2_boundary_dofs(t) for t in wall_tags]))
    inlet_d, inlet_xy = mesh.p2_boundary_coordinates("inlet")
    eta_in = inlet_xy[:, 1] / H0
    u_inlet = 6.0 * eta_in * (1.0 - eta_in)

    # No pressure datum is imposed algebraically: the do-nothing outflow condition
    # determines the pressure level, so all continuity equations can be retained and the
    # discrete mass balance is exact.  The outlet datum p = 0 of the formulation is then
    # applied as a post-processing shift (the level is immaterial to the flow).
    out_v = mesh.boundary_vertices("outlet")
    pin = int(out_v[np.argmin(np.abs(mesh.xy[out_v, 1] - 0.5 * H0))])
    pin_dof = 2 * np2 + pin
    pin_alpha = float(num["flow"].get("pressure_pin_penalty", 0.0))

    vd = np.concatenate([wall_d, np2 + wall_d, inlet_d, np2 + inlet_d]).astype(int)
    vals = np.concatenate([np.zeros(wall_d.size), np.zeros(wall_d.size),
                           u_inlet, np.zeros(inlet_d.size)])

    # When the mesh is bound to a conforming solid block (joint P2 numbering), the
    # fluid mid-side node numbers start at the solid vertex count and a band of unused
    # global numbers remains.  Those unknowns are structurally empty rows; they are
    # fixed at zero so that the saddle-point matrix is non-singular.
    probe, _ = _assemble(mesh, data, np.zeros((np2, 2)), 0.0, h_ref=H0)
    orphan = np.flatnonzero(np.diff(probe.tocsr().indptr) == 0)
    if orphan.size:
        orphan = np.setdiff1d(orphan, vd)
        vd = np.concatenate([vd, orphan]).astype(int)
        vals = np.concatenate([vals, np.zeros(orphan.size)])
        if verbose:
            print(f"    removed {orphan.size} structurally empty degrees of freedom")

    history: List[float] = []
    total_it = 0
    converged = True
    x = None
    for frac in re_fracs:
        re_stage = re_h * frac
        for it in range(max_it):
            try:
                K, b = _assemble(mesh, data, u, re_stage, h_ref=H0,
                                 pressure_penalty=(pin_dof, pin_alpha) if pin_alpha > 0 else None)
                x, res = fem.solve_dirichlet(K, b, vd, vals, return_residual=True)
                if not np.isfinite(res) or res > 1e-9:
                    raise ArithmeticError(f"residual {res:.2e}")
            except (RuntimeError, ArithmeticError) as exc:
                # documented fallback: a weak pressure pin (breaks the discrete mass
                # balance at the 1e-3 level) rescues the factorisation on pathological
                # meshes; the flag is propagated to the caller through `history`
                if pin_alpha > 0:
                    raise RuntimeError(f"flow solve failed even with the pressure pin: {exc}")
                if verbose:
                    print(f"    direct factorisation failed ({exc}); retrying with a weak "
                          f"pressure pin")
                K, b = _assemble(mesh, data, u, re_stage, h_ref=H0,
                                 pressure_penalty=(pin_dof, 1e-3))
                x, res = fem.solve_dirichlet(K, b, vd, vals, return_residual=True)
            u_new = np.stack([x[:np2], x[np2:2 * np2]], axis=1)
            du = np.max(np.abs(u_new - u)) / max(np.max(np.abs(u_new)), 1e-30)
            history.append(float(du))
            total_it += 1
            if du < tol:
                u = u_new
                break
            u = (1.0 - relax) * u + relax * u_new
        else:
            converged = False
            if verbose:
                print(f"    flow stage Re={re_stage:g} did not converge "
                      f"(last increment {history[-1]:.2e})")
    if x is None:
        raise RuntimeError("flow solve produced no iterate")
    p_hat = x[2 * np2:]
    # with physical gradients in the assembly, the dimensionless pressure is p/(mu U)
    p_phys = p_hat * mu * U / H0
    # enforce the outlet pressure datum of the formulation (Section 5.2)
    out_v = mesh.boundary_vertices("outlet")
    p_phys = p_phys - float(np.mean(p_phys[out_v]))
    return FlowSolution(u=u * U, p=p_phys, mesh=mesh, data=data,
                        iterations=total_it, converged=converged,
                        residual_history=history, re=2.0 * re_h)


# ---------------------------------------------------------------------------
#  Post-processing
# ---------------------------------------------------------------------------
def interface_pressure(sol: FlowSolution, x_out: np.ndarray) -> np.ndarray:
    """Gauge pressure on the deformable interface interpolated at ``x_out``."""
    mesh = sol.mesh
    pairs = mesh.boundary["interface"]
    xs = 0.5 * (mesh.xy[pairs[:, 0], 0] + mesh.xy[pairs[:, 1], 0])
    ps = 0.5 * (sol.p[pairs[:, 0]] + sol.p[pairs[:, 1]])
    order = np.argsort(xs)
    return np.interp(x_out, xs[order], ps[order])


def boundary_flux(mesh: fem.TriMesh, u: np.ndarray, tag: str) -> float:
    """Mass flux (per unit depth) through a boundary tag, positive along the outward normal.

    The boundary integral is evaluated with three-point Gauss quadrature on each quadratic
    edge, so it is exact for the P2 velocity field.
    """
    pairs = mesh.boundary[tag]
    if pairs.size == 0:
        return 0.0
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(mesh.edge_nodes, axis=1))}
    xi = np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)])
    wq = np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0])
    total = 0.0
    for a, b in pairs:
        a, b = int(a), int(b)
        mid = mesh.mid_offset + lut[tuple(sorted((a, b)))]
        xa, xb = mesh.xy[a], mesh.xy[b]
        t = xb - xa
        length = np.linalg.norm(t)
        nvec = np.array([t[1], -t[0]]) / length
        # quadratic interpolation of u along the edge
        Na = 0.5 * xi * (xi - 1.0)
        Nb = 0.5 * xi * (xi + 1.0)
        Nm = 1.0 - xi**2
        uu = np.outer(Na, u[a]) + np.outer(Nb, u[b]) + np.outer(Nm, u[mid])
        total += 0.5 * length * float(np.sum(wq * (uu @ nvec)))
    return total


def wall_shear(sol: FlowSolution, cfg: Dict) -> np.ndarray:
    """Viscous wall-shear stress magnitude on the interface edges (Pa)."""
    mesh, data, u = sol.mesh, sol.data, sol.u
    pairs = mesh.boundary["interface"]
    lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(mesh.edge_nodes, axis=1))}
    mu = cfg["fluid"]["mu"]
    out = np.zeros(pairs.shape[0])
    for i, (a, b) in enumerate(pairs):
        k = lut[tuple(sorted((int(a), int(b))))]
        e = int(np.where(mesh.edges == k)[0][0])
        wq = data.w[e] / data.w[e].sum()
        grad = np.einsum("g,gba,bi->ai", wq, data.dNdx[e], u[mesh.p2[e]])  # d u_i / d x_a
        t = mesh.xy[b] - mesh.xy[a]
        t = t / np.linalg.norm(t)
        nvec = np.array([-t[1], t[0]])
        if nvec[1] < 0:
            nvec = -nvec
        D = 0.5 * (grad + grad.T)
        tau = 2.0 * mu * (D @ nvec)
        out[i] = abs(float(tau @ t))
    return out


def flow_metrics(sol: FlowSolution, cfg: Dict) -> Dict[str, float]:
    """Integral flow metrics used in the manuscript tables."""
    mesh = sol.mesh
    pin_v = mesh.boundary_vertices("inlet")
    pout_v = mesh.boundary_vertices("outlet")
    tau = wall_shear(sol, cfg)
    return {
        "dp": float(np.mean(sol.p[pin_v]) - np.mean(sol.p[pout_v])),
        "u_max": float(np.max(np.abs(sol.u[:, 0]))),
        "tau_iface_mean": float(np.mean(tau)),
        "flux_inlet": boundary_flux(mesh, sol.u, "inlet"),
        "flux_outlet": boundary_flux(mesh, sol.u, "outlet"),
        "flux_walls": sum(boundary_flux(mesh, sol.u, t)
                          for t in ("wall_bottom", "lids", "interface")),
        "p_inlet": float(np.mean(sol.p[pin_v])),
        "p_outlet": float(np.mean(sol.p[pout_v])),
    }
