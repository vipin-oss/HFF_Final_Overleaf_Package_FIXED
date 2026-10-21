"""Tests of the semi-analytical theory against its own exact limits."""

import math

import numpy as np
import pytest

from hff import asymptotics, config


@pytest.fixture(scope="module")
def cfg():
    return config.load("params/baseline.json")


def test_fully_developed_nusselt_number_is_70_over_13():
    Y = np.linspace(0.0, 1.0, 20001)
    _, f1, Nu_fd = asymptotics._fully_developed_profile(Y)
    assert f1 == pytest.approx(13.0 / 35.0, rel=1e-7)
    assert Nu_fd == pytest.approx(70.0 / 13.0, rel=1e-7)


def test_first_eigenvalue_of_the_entry_problem():
    table = asymptotics.graetz_modes(n_modes=2, n_grid=1201)
    lams = [m["lam"] for m in table["modes"]]
    assert lams[0] == pytest.approx(3.6956, abs=2e-3)
    assert lams[1] == pytest.approx(7.0010, abs=5e-3)
    # eigenfunctions are Neumann at both walls: derivative vanishes at Y=1
    psi = table["modes"][0]["psi"]
    assert abs(psi[-1] - psi[-2]) < 5e-3 * abs(psi[-1])


def test_hypergeometric_resistance_matches_its_series():
    # Taylor coefficients of 2F1(3, 1/2; 1; a) are 1, 3/2, 27/8, 75/16
    h = 1e-4
    sf = asymptotics.lubrication_shape_factor(h)
    first = (sf["closed"] - 1.0) / h
    assert first == pytest.approx(1.5, rel=1e-3)
    sf2 = asymptotics.lubrication_shape_factor(0.2)
    assert sf2["closed"] == pytest.approx(1.4237464, rel=1e-6)


def test_resistance_tends_to_the_undeformed_value(cfg):
    zero = asymptotics.pressure_drop_lubrication(cfg, w_max=0.0)
    g, f, op = cfg["geometry"], cfg["fluid"], cfg["operating"]
    Q = op["U"] * g["H0"]
    expected = 12.0 * f["mu"] * Q * (g["Le"] + g["L"] + g["Lo"]) / g["H0"] ** 3
    assert zero["total"] == pytest.approx(expected, rel=1e-12)
    assert asymptotics.pressure_drop_undeformed(cfg) == pytest.approx(expected / 2, rel=1e-12)


def test_contraction_bound_is_below_one_at_the_design_point(cfg):
    c = asymptotics.contraction_bound(cfg)
    assert 0.0 < c["q_bound"] < 1.0
    assert c["bound_valid"]


def test_closed_form_bow_reproduces_the_scaling_of_the_Euler_load(cfg):
    b = asymptotics.beam_column(cfg)
    # geometric amplification of the thermal bow by the membrane force
    assert 1.3 < b["amplification"] < 1.5
    assert b["w_max_frozen"] == pytest.approx(2.19e-4, rel=0.02)
