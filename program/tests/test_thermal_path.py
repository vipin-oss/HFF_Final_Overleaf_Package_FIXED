"""Verification of the wall-conduction closure and of the column averaging."""

from __future__ import annotations

import numpy as np
import pytest

from hff import asymptotics, config, fem, thermal


@pytest.fixture(scope="module")
def cfg():
    return config.load("params/baseline.json")


def _neumann(cfg, bow):
    """Strip with a Dirichlet interface and a uniform flux on the outer face."""
    solid = fem.solid_mesh(cfg)
    ng = solid.n_p2
    if bow is not None:
        # lower the interface row by the prescribed bow; the mid-side nodes follow
        # because p2_coordinates are the midpoints of the vertices
        solid.xy[solid.grid[0, :], 1] -= np.asarray(bow, dtype=float)
    sdata = fem.element_data(solid, solid.p2_coordinates(ng))
    k = float(cfg["solid"]["k"])
    q = float(cfg["operating"]["q_flux"])
    G = np.einsum("egam,egbm,eg->eab", sdata.dNdx, sdata.dNdx, sdata.w)
    K = fem.element_matrix(solid.p2, k * G, ng)
    rhs = thermal.boundary_flux_load(solid, "outer", q)
    dofs = solid.p2_boundary_dofs("interface")
    T, _ = fem.solve_dirichlet(K, rhs, dofs, np.zeros(dofs.size), return_residual=True)
    return solid, T, sdata


def test_neumann_wall_reproduces_the_one_dimensional_drop_exactly(cfg):
    solid, T, sdata = _neumann(cfg, None)
    q = float(cfg["operating"]["q_flux"])
    k = float(cfg["solid"]["k"])
    d = float(cfg["geometry"]["d"])
    prof = thermal.wall_profile(solid, sdata, T, cfg, reference=0.0)
    assert prof["theta_bar"].mean() == pytest.approx(q * d / (2.0 * k), rel=1e-12)
    assert prof["gamma"].mean() == pytest.approx(q / k, rel=1e-12)
    col = thermal.column_average(solid, T)
    assert col["theta_avg"].mean() == pytest.approx(q * d / (2.0 * k), rel=1e-12)
    # a flat wall has no through-thickness curvature: mid-surface = average
    assert col["theta_mid"].mean() == pytest.approx(col["theta_avg"].mean(), rel=1e-9)


def test_bow_lengthens_the_conduction_path_by_the_local_bow(cfg):
    H0 = float(cfg["geometry"]["H0"])
    g = cfg["geometry"]
    x = np.linspace(0.0, g["L"], int(cfg["numerics"]["nx_heated"]) + 1)
    w = 0.2 * H0 * np.sin(np.pi * x / g["L"]) ** 2
    solid, T, _ = _neumann(cfg, w)
    col = thermal.column_average(solid, T)
    q = float(cfg["operating"]["q_flux"])
    k = float(cfg["solid"]["k"])
    d = float(cfg["geometry"]["d"])
    h = col["thickness"]
    # thickness of the deformed strip is d + w on every column
    assert np.allclose(h, d + w, rtol=0, atol=1e-12)
    # the exact thickness average follows the deformed closure in the strip mean;
    # pointwise the closure carries an O(h^2 theta_i'') curvature residual, so only
    # the mean is asserted here (see the paper, Section 5)
    predicted = q * h / (2.0 * k)
    assert col["theta_avg"].mean() == pytest.approx(predicted.mean(), abs=5e-3)
    # the mid-surface value is biased above the average by the through-thickness
    # curvature, which is zero for the flat wall of the previous test
    assert col["theta_mid"].mean() > col["theta_avg"].mean()


def test_wall_path_closure_matches_the_one_dimensional_limits(cfg):
    theta_i = np.array([1.0, 2.0])
    out = asymptotics.wall_path_closure(cfg, theta_i, np.array([0.0, 0.0]))
    q, k, d = (float(cfg["operating"]["q_flux"]), float(cfg["solid"]["k"]),
               float(cfg["geometry"]["d"]))
    assert np.allclose(out["reference"], theta_i + q * d / (2 * k))
    assert np.allclose(out["corrected"], out["reference"])
    out = asymptotics.wall_path_closure(cfg, theta_i, np.array([0.0, d]))
    assert np.allclose(out["corrected"] - out["reference"], np.array([0.0, q * d / (2 * k)]))


def test_self_similarity_moments_and_the_truncation_bound(cfg):
    x = np.linspace(0.0, cfg["geometry"]["L"], 201)
    wh = np.sin(np.pi * x / cfg["geometry"]["L"]) ** 2
    m = asymptotics.self_similarity_moments(x, wh)
    from math import comb
    for k, c in enumerate(m["c"]):
        assert c == pytest.approx(comb(2 * k, k) / 4**k, rel=1e-6)
    # the a priori bound is monotone in the number of retained terms and blows up
    # as a -> 1, which is why it is informative only for small a
    for a in (0.1, 0.2, 0.4):
        b3 = asymptotics.pressure_truncation_bound(a, 3)
        b4 = asymptotics.pressure_truncation_bound(a, 4)
        assert 0.0 < b4 < b3
    with pytest.raises(ValueError):
        asymptotics.pressure_truncation_bound(1.0, 4)
