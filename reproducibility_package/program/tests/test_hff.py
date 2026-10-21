"""Automated tests of the HFF program.

Run with ``pytest`` from the ``program`` directory::

    python -m pytest -q            # full suite (about 3 minutes)
    python -m pytest -q -m "not slow"

The tests check (i) configuration validation and the algebraic identities of the
formulation, (ii) the finite-element primitives, (iii) the flow and thermal solvers
against the analytical plane-channel solutions, (iv) the beam--column solver against its
closed-form solution and limiting cases, and (v) the coupled driver on a coarse mesh.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from hff import analytic, benchmarks, config, fem, flow, thermal, wall

HERE = Path(__file__).resolve().parents[1]
PARAMS = HERE / "params" / "baseline.json"


@pytest.fixture(scope="session")
def cfg():
    return config.load(PARAMS)


@pytest.fixture(scope="session")
def coarse(cfg):
    c = json.loads(json.dumps(cfg))
    c["numerics"].update(nx_heated=24, nx_entrance=4, nx_exit=4, ny_fluid=5,
                         ny_solid=3, wall_clustering=1.0)
    c["numerics"]["wall"]["n_points"] = 25
    return c


# ---------------------------------------------------------------------------
#  configuration
# ---------------------------------------------------------------------------
def test_config_roundtrip(cfg, tmp_path):
    out = tmp_path / "copy.json"
    config.dump(cfg, out)
    again = config.load(out)
    assert again["geometry"]["H0"] == cfg["geometry"]["H0"]


def test_config_rejects_negative_height(cfg, tmp_path):
    bad = json.loads(json.dumps(cfg))
    bad["geometry"]["H0"] = -1e-4
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(config.ConfigError):
        config.load(path)


def test_config_rejects_unknown_key(cfg, tmp_path):
    bad = json.loads(json.dumps(cfg))
    bad["geometry"]["H0_mm"] = 1.0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(config.ConfigError):
        config.load(path)


def test_config_rejects_nonsense_numerics(cfg, tmp_path):
    bad = json.loads(json.dumps(cfg))
    bad["numerics"]["nx_heated"] = 0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(config.ConfigError):
        config.load(path)


# ---------------------------------------------------------------------------
#  algebraic identities
# ---------------------------------------------------------------------------
def test_groups(cfg):
    g = analytic.groups(cfg)
    assert g["Re_Dh"] == pytest.approx(2 * g["Re_H0"])
    assert g["Pr"] == pytest.approx(cfg["fluid"]["mu"] * cfg["fluid"]["cp"]
                                    / cfg["fluid"]["k"])
    assert g["f_D"] == pytest.approx(96.0 / g["Re_Dh"])


def test_pressure_drop_matches_poiseuille(cfg):
    # dp = 12 mu U L / H0^2 is the exact slit result; check the algebra
    g, f, op = cfg["geometry"], cfg["fluid"], cfg["operating"]
    dp = analytic.pressure_drop(cfg)
    assert dp == pytest.approx(12 * f["mu"] * op["U"] * g["L"] / g["H0"] ** 2)


def test_strip_pressure_datum(cfg):
    sp = analytic.strip_pressure(cfg)
    assert sp["p0"] - sp["pL"] == pytest.approx(analytic.pressure_drop(cfg))
    assert sp["p_mean"] == pytest.approx(0.5 * (sp["p0"] + sp["pL"]))


def test_critical_temperature_matches_euler_load(cfg):
    g, s = cfg["geometry"], cfg["solid"]
    Ds = config.derived(cfg)["Ds"]
    Ncr = math.pi**2 * Ds / g["L"] ** 2
    Tcr = analytic.critical_temperature(cfg)
    Ncr_from_T = abs(analytic.membrane_force(cfg, Tcr))
    assert Ncr_from_T == pytest.approx(Ncr, rel=1e-12)
    # the alpha(1+nu) factor of the strip is reproduced as well
    assert Tcr == pytest.approx(math.pi**2 * g["d"] ** 2
                                / (12 * s["alpha"] * (1 + s["nu"]) * g["L"] ** 2))


def test_ceiling_sweep_is_monotone(cfg):
    sw = analytic.ceiling_sweep(cfg)
    assert np.all(np.diff(sw["w_over_H0"]) > 0)
    assert np.all(np.diff(sw["N_over_Ncr"]) > 0)
    assert np.all(np.diff(sw["M_b"]) < 0)


# ---------------------------------------------------------------------------
#  finite-element primitives
# ---------------------------------------------------------------------------
def test_p2_partition_of_unity_and_gradient():
    N, dN = fem.p2_basis(fem._QP[:, 0], fem._QP[:, 1])
    assert np.allclose(N.sum(axis=1), 1.0)
    assert np.allclose(dN.sum(axis=1), 0.0)


def test_quadrature_integrates_area():
    assert fem._QW.sum() == pytest.approx(0.5)


def test_mesh_geometry(cfg):
    mesh = fem.fluid_mesh(cfg)
    tri = mesh.tris
    a = mesh.xy[tri[:, 1]] - mesh.xy[tri[:, 0]]
    b = mesh.xy[tri[:, 2]] - mesh.xy[tri[:, 0]]
    area = float(np.sum(np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]) / 2))
    data = fem.element_data(mesh)
    assert data.w.sum() == pytest.approx(area)
    g = cfg["geometry"]
    exact = g["H0"] * (g["Le"] + g["L"] + g["Lo"])
    assert data.w.sum() == pytest.approx(exact, rel=1e-12)


def test_boundary_tags_are_complete(cfg):
    """Every edge of the structured grid belongs to exactly one boundary tag."""
    mesh = fem.fluid_mesh(cfg)
    nid = mesh.grid
    ny, nx = nid.shape[0] - 1, nid.shape[1] - 1
    expected = 2 * nx + 2 * ny          # perimeter edges of the rectangular grid
    tagged = sum(mesh.boundary[k].shape[0] for k in
                 ("inlet", "outlet", "wall_bottom", "interface", "lids"))
    assert tagged == expected
    seen = [tuple(sorted((int(a), int(b))))
            for k in ("inlet", "outlet", "wall_bottom", "interface", "lids")
            for a, b in mesh.boundary[k]]
    assert len(seen) == len(set(seen))


def test_conforming_solid_mesh(cfg):
    fluid = fem.fluid_mesh(cfg)
    solid = fem.solid_mesh(cfg, fluid)
    n = fem.bind_shared(fluid, solid)
    assert n == solid.n_p2
    # the interface edges are shared: same global numbers on both sides
    assert np.array_equal(fluid.boundary["interface"], solid.boundary["interface"])
    assert np.allclose(fluid.xy[fluid.boundary["interface"].ravel()],
                       solid.xy[solid.boundary["interface"].ravel()])


def test_dirichlet_elimination_reproduces_imposed_values():
    A = np.array([[4.0, 1.0], [1.0, 3.0]])
    import scipy.sparse as sp
    b = np.array([1.0, 2.0])
    x = fem.solve_dirichlet(sp.csr_matrix(A), b, np.array([0]), [5.0])
    assert x[0] == 5.0
    # the eliminated equation is satisfied at the free degree of freedom
    assert A[1] @ x == pytest.approx(b[1])


# ---------------------------------------------------------------------------
#  beam--column solver
# ---------------------------------------------------------------------------
def test_wall_closed_form_agreement(cfg):
    g = cfg["geometry"]
    Ds = config.derived(cfg)["Ds"]
    x = np.linspace(0, g["L"], 121)
    kap = 1.234
    for mu2 in (0.0, 1.0, 2.0):
        st = wall.solve_wall(x, Ds, np.full_like(x, kap), N=mu2 * Ds)
        ref = wall.closed_form(x, kap, mu2)
        assert np.max(np.abs(st.w - ref)) / np.max(np.abs(ref)) < 1e-6


def test_wall_pressure_limit(cfg):
    g = cfg["geometry"]
    Ds = config.derived(cfg)["Ds"]
    x = np.linspace(0, g["L"], 151)
    p = 2.0e3
    st = wall.solve_wall(x, Ds, np.zeros_like(x), N=0.0, p=np.full_like(x, p))
    assert st.w_max == pytest.approx(5 * p * g["L"] ** 4 / (384 * Ds), rel=1e-6)


def test_wall_zero_load_gives_zero_bow(cfg):
    g = cfg["geometry"]
    Ds = config.derived(cfg)["Ds"]
    x = np.linspace(0, g["L"], 61)
    st = wall.solve_wall(x, Ds, np.zeros_like(x))
    assert st.w_max < 1e-16


def test_wall_rejects_bad_grid(cfg):
    with pytest.raises(ValueError):
        wall.solve_wall(np.array([0.0, 1.0]), 1.0, np.zeros(2))


def test_self_consistent_converges(cfg):
    g = cfg["geometry"]
    x = np.linspace(0, g["L"], int(cfg["numerics"]["wall"]["n_points"]))
    Ds = config.derived(cfg)["Ds"]
    kap = analytic.kappa_th(cfg)
    th = analytic.theta_bar_estimate(cfg)["theta_bar"]
    st = wall.self_consistent(x, Ds, np.full_like(x, kap), th, cfg)
    assert st.converged
    N0 = abs(analytic.membrane_force(cfg, th))
    # bowing relieves compression: N < N_theta in magnitude
    assert st.N < N0


@pytest.mark.slow
def test_consistency_error_curve(cfg):
    c = json.loads(json.dumps(cfg))
    c["numerics"]["wall"]["n_points"] = 41
    out = wall.consistency_error_curve(c, n_q=5)
    assert np.all(np.isfinite(out["rel_error"]))
    assert out["rel_error"][-1] > out["rel_error"][0]


# ---------------------------------------------------------------------------
#  flow and thermal solvers
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_poiseuille_benchmark(cfg):
    r = benchmarks.benchmark_poiseuille(cfg, nx=40, ny=6)
    assert r["f_Re"] == pytest.approx(96.0, rel=1e-6)
    assert r["u_profile_L2_rel"] < 1e-8


def test_thermal_benchmark_h1(cfg):
    r = benchmarks.benchmark_thermal(cfg, "H1", nx=200, ny=12, length_over_H=200)
    assert abs(r["rel_error"]) < 0.02


def test_thermal_benchmark_uniform_temperature(cfg):
    r = benchmarks.benchmark_thermal(cfg, "T", nx=200, ny=12, length_over_H=200)
    assert abs(r["rel_error"]) < 0.02


def test_coupled_flow_conserves_mass(coarse):
    mesh = fem.fluid_mesh(coarse)
    sol = flow.solve_flow(mesh, coarse)
    met = flow.flow_metrics(sol, coarse)
    assert sol.converged
    assert met["flux_outlet"] == pytest.approx(met["flux_inlet"], rel=1e-6)
    assert abs(met["flux_walls"]) < 1e-12
    assert met["dp"] > 0


def test_flow_pressure_drop_is_grid_independent(coarse, cfg):
    mesh = fem.fluid_mesh(coarse)
    sol = flow.solve_flow(mesh, coarse)
    met = flow.flow_metrics(sol, coarse)
    # the strip pressure carries the full-length pressure drop of the passage
    sp = analytic.strip_pressure(coarse)
    ref = sp["p0"] + sp["grad"] * coarse["geometry"]["Le"]   # inlet of the domain
    assert met["p_inlet"] == pytest.approx(ref, rel=0.10)


def test_thermal_energy_balance(coarse):
    fluid = fem.fluid_mesh(coarse)
    solid = fem.solid_mesh(coarse, fluid)
    n = fem.bind_shared(fluid, solid)
    sol = flow.solve_flow(fluid, coarse)
    th = thermal.solve_thermal(fluid, solid, sol, coarse, n)
    bal = thermal.enthalpy_balance(th, coarse)
    assert bal["Q_in"] == pytest.approx(coarse["operating"]["q_flux"]
                                        * coarse["geometry"]["L"])
    assert bal["rel_imbalance"] < 5e-3


def test_wall_temperature_rise_is_physical(coarse):
    fluid = fem.fluid_mesh(coarse)
    solid = fem.solid_mesh(coarse, fluid)
    n = fem.bind_shared(fluid, solid)
    sol = flow.solve_flow(fluid, coarse)
    th = thermal.solve_thermal(fluid, solid, sol, coarse, n)
    Tin = coarse["operating"]["Tin"]
    dT = coarse["operating"]["q_flux"] * coarse["geometry"]["d"] / coarse["solid"]["k"]
    assert th.T.min() >= Tin - 1.0
    # the through-thickness difference is q'' d / k_s
    nid = solid.grid
    top = th.T[nid[-1, :]] - th.T[nid[0, :]]
    assert np.mean(top) == pytest.approx(dT, rel=0.05)


def test_nusselt_is_positive_and_finite(coarse):
    fluid = fem.fluid_mesh(coarse)
    solid = fem.solid_mesh(coarse, fluid)
    n = fem.bind_shared(fluid, solid)
    sol = flow.solve_flow(fluid, coarse)
    th = thermal.solve_thermal(fluid, solid, sol, coarse, n)
    prof = thermal.nusselt_profile(th, coarse)
    Nu = np.asarray(prof["Nu"], dtype=float)[1:-1]
    assert np.all(np.isfinite(Nu))
    assert np.all(Nu > 0)


@pytest.mark.slow
def test_coupled_baseline_coarse(coarse):
    from hff import coupled
    c = json.loads(json.dumps(coarse))
    c["numerics"]["coupling"]["max_iter"] = 8
    res = coupled.solve_coupled(c)
    assert res.wall is not None
    assert np.max(np.abs(res.w)) / c["geometry"]["H0"] > 0.1
    assert res.termination != ""

    # determinism: the same call gives bit-identical results (the solver has no
    # stochastic component; the parameter file is the only source of randomness-free
    # input)
    res2 = coupled.solve_coupled(c)
    assert np.array_equal(res.w, res2.w)
    assert np.array_equal(res.wall.w, res2.wall.w)
