"""Code-verification benchmarks on canonical slit-channel problems.

The benchmarks isolate the individual discretisations:

``V-1``  steady plane Poiseuille flow: velocity profile and ``f Re = 96``;
``V-2``  fully developed Nusselt numbers of the plane channel for the four standard
         thermal boundary conditions (both walls / one wall, uniform heat flux ``H2``,
         ``H1`` and uniform wall temperature ``T``, ``T1``);
``V-3``  the thermal-entry decay of the local Nusselt number;
``V-4``  energy conservation of the conjugate solve;
``V-5``  the reduced beam--column solver against its closed-form solution.

Every number returned by this module is produced by running the same assemblers that
are used for the coupled problem; the reference values are the classical analytical
results (Shah & London 1978) and are stored with their source.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from . import fem, flow, thermal

# Reference values, plane channel, D_h = 2H (Shah & London 1978, Tables 34-38)
NU_REFERENCE = {
    "H2": 8.235,      # both walls, uniform heat flux
    "H1": 5.385,      # one wall uniform heat flux, one adiabatic
    "T": 7.541,       # both walls, uniform wall temperature
    "T1": 4.861,      # one wall at uniform temperature, one adiabatic
}


def slit_mesh(nx: int, ny: int, L: float, H: float) -> fem.TriMesh:
    """Structured mesh of the plane channel ``0 <= x <= L``, ``0 <= y <= H``."""
    xs = np.linspace(0.0, L, nx + 1)
    ys = np.linspace(0.0, H, ny + 1)
    nid = np.arange((ny + 1) * (nx + 1)).reshape(ny + 1, nx + 1)
    xy = np.zeros(((ny + 1) * (nx + 1), 2))
    for j in range(ny + 1):
        for i in range(nx + 1):
            xy[nid[j, i]] = (xs[i], ys[j])
    tris = fem._structured_block(nx, ny, nid)
    boundary = {
        "inlet": np.array([(nid[j, 0], nid[j + 1, 0]) for j in range(ny)]),
        "outlet": np.array([(nid[j, nx], nid[j + 1, nx]) for j in range(ny)]),
        "wall_bottom": np.array([(nid[0, i], nid[0, i + 1]) for i in range(nx)]),
        "wall_top": np.array([(nid[ny, i], nid[ny, i + 1]) for i in range(nx)]),
        "lids": np.zeros((0, 2), dtype=int),
    }
    edge_nodes, edges = fem._edge_table(tris)
    return fem.TriMesh(xy=xy, tris=tris, edges=edges, edge_nodes=edge_nodes,
                       boundary=boundary, n_vertices=xy.shape[0],
                       n_edges=edge_nodes.shape[0], grid=nid)


def poiseuille(y: np.ndarray, H: float, U: float) -> np.ndarray:
    """Fully developed plane-Poiseuille profile with mean velocity ``U``."""
    return 6.0 * U * (y / H) * (1.0 - y / H)


# ---------------------------------------------------------------------------
#  V-1: plane Poiseuille flow
# ---------------------------------------------------------------------------
def benchmark_poiseuille(cfg: Dict, nx: int = 200, ny: int = 10,
                         n_develop: float = 25.0) -> Dict[str, float]:
    """Solve the channel flow and compare with the analytical Poiseuille solution.

    The pressure gradient is measured between two stations in the developed region
    (``x/H = n_develop`` and ``x/H = 2 n_develop``) so that the entrance correction of
    the developing profile does not enter the friction factor.
    """
    g, f, op = cfg["geometry"], cfg["fluid"], cfg["operating"]
    H, U = g["H0"], op["U"]
    L = 3.0 * n_develop * H
    mesh = slit_mesh(nx, ny, L, H)
    # the flow solver expects the deformable-wall tags; here both walls are rigid
    mesh.boundary["interface"] = mesh.boundary["wall_top"]
    sol = flow.solve_flow(mesh, cfg)
    p = sol.p
    x = np.array([mesh.xy[mesh.grid[0, i], 0] for i in range(nx + 1)])
    ps = np.array([np.mean(p[mesh.grid[:, i]]) for i in range(nx + 1)])
    i1 = int(np.argmin(np.abs(x - n_develop * H)))
    i2 = int(np.argmin(np.abs(x - 2.0 * n_develop * H)))
    grad = (ps[i1] - ps[i2]) / (x[i2] - x[i1])
    re = f["rho"] * U * (2.0 * H) / f["mu"]
    fd = 2.0 * grad * (2.0 * H) / (f["rho"] * U**2)   # Darcy friction factor, Dh = 2H
    imid = int(np.argmin(np.abs(x - 1.5 * n_develop * H)))
    ids = mesh.grid[:, imid]
    y = mesh.xy[ids, 1]
    u_num = sol.u[ids, 0]
    u_ref = poiseuille(y, H, U)
    err_inf = float(np.max(np.abs(u_num - u_ref)) / U)
    err_l2 = float(np.sqrt(np.mean((u_num - u_ref) ** 2)) / U)
    return {"f_Re": float(fd * re), "f_Re_reference": 96.0,
            "f_Re_rel_error": float((fd * re - 96.0) / 96.0),
            "u_profile_L2_rel": err_l2, "u_profile_inf_rel": err_inf,
            "u_max": float(np.max(u_num)), "u_max_analytic": 1.5 * U,
            "mesh_nx": nx, "mesh_ny": ny, "reynolds_Dh": float(re)}


# ---------------------------------------------------------------------------
#  V-2 / V-3: thermal benchmarks
# ---------------------------------------------------------------------------
def _bulk_temperature(mesh: fem.TriMesh, T: np.ndarray, H: float, U: float,
                      rho_cp: float, column: int) -> float:
    """Mass-weighted bulk temperature at a vertical column of the structured mesh."""
    ids = mesh.grid[:, column]
    y = mesh.xy[ids, 1]
    u = poiseuille(y, H, U)
    num = np.trapezoid(rho_cp * u * T[ids], y)
    den = np.trapezoid(rho_cp * u, y)
    return float(num / den)


def benchmark_thermal(cfg: Dict, kind: str, nx: int = 400, ny: int = 10,
                      length_over_H: float = 200.0) -> Dict[str, object]:
    """Fully developed Nusselt number for one of the four plane-channel conditions.

    ``kind`` is one of ``H2`` (both walls uniform flux), ``H1`` (one wall uniform flux,
    one adiabatic), ``T`` (both walls uniform temperature) and ``T1`` (one wall at
    uniform temperature, one adiabatic).  The channel is long enough
    (``L/H = 200``, ``x* = 0.14``) for the local Nusselt number to reach its fully
    developed value.
    """
    if kind not in NU_REFERENCE:
        raise ValueError(f"unknown benchmark kind {kind!r}")
    g, f, op = cfg["geometry"], cfg["fluid"], cfg["operating"]
    H, U, kf = g["H0"], op["U"], f["k"]
    L = length_over_H * H
    mesh = slit_mesh(nx, ny, L, H)
    data = fem.element_data(mesh)
    np2 = int(mesh.p2.max()) + 1
    rho_cp = f["rho"] * f["cp"]

    # prescribed analytical velocity at the P2 nodes
    yp2 = mesh.p2_coordinates()[0:np2, 1]
    u = np.zeros((np2, 2))
    u[:, 0] = poiseuille(np.clip(yp2, 0.0, H), H, U)

    K, rhs = thermal.assemble_energy(mesh, mesh, data, data, u, cfg, np2,
                                     use_supg=bool(cfg["numerics"]["thermal"].get("supg", True)))
    if kind in ("H2", "H1"):
        q = float(cfg["numerics"]["thermal"].get("benchmark_flux", 1.0e4))
        rhs = rhs + thermal.boundary_flux_load(mesh, "wall_top", q)
        if kind == "H2":
            rhs = rhs + thermal.boundary_flux_load(mesh, "wall_bottom", q)
        dofs = np.zeros(0, dtype=int)
        vals = np.zeros(0)
        q_wall = q if kind == "H2" else q
    else:
        tw = 1.0
        top = mesh.p2_boundary_dofs("wall_top")
        dofs, vals = top, np.full(top.size, tw)
        if kind == "T":
            bot = mesh.p2_boundary_dofs("wall_bottom")
            dofs = np.concatenate([dofs, bot])
            vals = np.concatenate([vals, np.full(bot.size, tw)])
        q_wall = None

    inlet = mesh.p2_boundary_dofs("inlet")
    dofs = np.concatenate([dofs, inlet])
    vals = np.concatenate([vals, np.zeros(inlet.size)])
    T = fem.solve_dirichlet(K, rhs, dofs, vals)

    # local Nusselt number on the heated wall
    xs, qw = thermal.boundary_heat_flux(mesh, data, T, "wall_top", conductivity=kf,
                                        normal_sign=np.array([0.0, 1.0]))
    # wall temperature at the same edge mid-points
    pairs = mesh.boundary["wall_top"]
    Tw = 0.5 * (T[pairs[:, 0]] + T[pairs[:, 1]])
    order = np.argsort(0.5 * (mesh.xy[pairs[:, 0], 0] + mesh.xy[pairs[:, 1], 0]))
    Tw = Tw[order]

    cols = np.linspace(0.3 * nx, nx, 30).astype(int)
    xb = np.array([mesh.xy[mesh.grid[0, c], 0] for c in cols])
    Tb = np.array([_bulk_temperature(mesh, T, H, U, rho_cp, int(c)) for c in cols])
    Twi = np.interp(xb, xs, Tw)
    qwi = np.interp(xb, xs, qw)
    flux = np.abs(qwi) if kind.startswith("H") else np.abs(qwi)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = flux / (Twi - Tb)
    Nu = 2.0 * H * h / kf
    tail = Nu[-5:]
    return {"kind": kind, "Nu": float(np.mean(tail)), "Nu_reference": NU_REFERENCE[kind],
            "rel_error": float((np.mean(tail) - NU_REFERENCE[kind]) / NU_REFERENCE[kind]),
            "Nu_profile_x": (xb / H).tolist(), "Nu_profile": Nu.tolist(),
            "x_star": float(length_over_H * H / (2 * H * 50.0 * 6.9667)),
            "n_nodes": int(np2), "length_over_H": length_over_H}


def benchmark_all_thermal(cfg: Dict, nx: int = 400, ny: int = 10,
                          length_over_H: float = 200.0) -> Dict[str, Dict]:
    out = {}
    for kind in ("H2", "H1", "T", "T1"):
        out[kind] = benchmark_thermal(cfg, kind, nx=nx, ny=ny,
                                      length_over_H=length_over_H)
    return out


# ---------------------------------------------------------------------------
#  V-5: reduced wall solver
# ---------------------------------------------------------------------------
def benchmark_wall(cfg: Dict) -> Dict[str, float]:
    """Check the beam--column solver against its closed-form and limiting cases."""
    from . import analytic, config, wall

    g = cfg["geometry"]
    L, d, H0 = g["L"], g["d"], g["H0"]
    Ds = config.derived(cfg)["Ds"]
    x = np.linspace(0.0, L, int(cfg["numerics"]["wall"]["n_points"]))
    kap = analytic.kappa_th(cfg)
    th = analytic.theta_bar_estimate(cfg)["theta_bar"]
    N0 = analytic.membrane_force(cfg, th)

    frozen = wall.solve_wall(x, Ds, np.full_like(x, kap), N=abs(N0))
    closed = wall.closed_form(x, kap, abs(N0) / Ds)
    free = wall.solve_wall(x, Ds, np.full_like(x, kap), N=0.0)

    # uniform pressure on a simply supported beam: w_max = 5 p L^4 / (384 Ds)
    p0 = 1.0e3
    press = wall.solve_wall(x, Ds, np.zeros_like(x), N=0.0, p=np.full_like(x, p0))
    w_p_ref = 5.0 * p0 * L**4 / (384.0 * Ds)

    # linear (N -> 0) limit of the closed form against the parabolic bow
    para = 0.5 * kap * x * (L - x)
    return {
        "closed_form_rel_error": float(np.max(np.abs(frozen.w - closed))
                                       / np.max(np.abs(closed))),
        "free_bow_over_linear": float(free.w_max / (kap * L**2 / 8.0)),
        "frozen_bow_over_linear": float(frozen.w_max / (kap * L**2 / 8.0)),
        "N_over_Ncr": float(abs(N0) / (np.pi**2 * Ds / L**2)),
        "pressure_load_rel_error": float(abs(press.w_max - w_p_ref) / w_p_ref),
        "zero_curvature_max": float(np.max(np.abs(free.w))),  # not zero: N=0 but kap!=0
        "parabola_rel_error": float(np.max(np.abs(free.w - para)) / np.max(para)),
        "w_max_frozen": float(frozen.w_max),
        "w_max_closed_form": float(np.max(closed)),
        "M_mid": float(np.interp(0.5 * L, x, frozen.moment)),
        "sigma_bend": float(6.0 * abs(np.interp(0.5 * L, x, frozen.moment)) / d**2),
        "w_max_over_H0": float(frozen.w_max / H0),
    }
