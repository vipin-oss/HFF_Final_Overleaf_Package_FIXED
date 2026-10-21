"""Regression guard for the headline claim of the paper: the collapse.

The strip resistance of the bowed passage must be a function of the bow ratio alone.
The check is made on the saved output of the five sweeps so that it fails if either
the analysis or the underlying solver changes the conclusion:

  * the unfitted master integral, built from the design-point shape, must reproduce
    every converged run to better than 1 % (it achieves 0.40 %, mean 0.11 %);
  * the kinematic sin^2 law must be clearly worse (it is off by 19.7 %), which is
    what makes the collapse a statement rather than a tautology.
"""

import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "outputs" / "data"


@pytest.fixture(scope="module")
def collapse():
    path = DATA / "collapse.json"
    if not path.exists():
        pytest.skip("run tools/collapse_analysis.py first")
    return json.loads(path.read_text())


def test_master_integral_collapses_every_run(collapse):
    assert collapse["n_runs"] >= 18
    assert collapse["master_max_abs_rel_error"] < 1.0e-2
    assert collapse["master_mean_abs_rel_error"] < 2.0e-3


def test_the_collapse_is_not_vacuous(collapse):
    # the shape law that is being replaced is an order of magnitude worse
    assert collapse["sin2_max_abs_rel_error"] > 10 * collapse["master_max_abs_rel_error"]
    assert collapse["sin2_max_abs_rel_error"] > 0.15


def test_the_run_count_is_the_number_of_distinct_parameter_sets(collapse):
    # the sweeps are centred on the design point; its duplicates must not be counted as
    # independent validation points
    assert collapse["n_runs"] == 19


def test_bow_ratio_range_is_the_one_quoted(collapse):
    assert 0.05 < collapse["a_min"] < 0.10
    assert 0.40 < collapse["a_max"] < 0.50
    assert collapse["Re_min"] == pytest.approx(25.0)
    assert collapse["Re_max"] == pytest.approx(100.0)


def test_every_family_is_within_the_bound(collapse):
    # the table quotes one row per sweep; no family may hide behind the average
    rows = collapse.get("families") or {}
    assert rows, "the saved analysis must keep the per-sweep errors"
    for name, row in rows.items():
        assert row["n"] >= 1, name
        assert row["master"] < 1.0e-2, (name, row["master"])


@pytest.fixture(scope="module")
def certificate():
    path = DATA / "collapse_certificate.json"
    if not path.exists():
        pytest.skip("run tools/collapse_certificate.py first")
    return json.loads(path.read_text())


def test_the_shape_bound_holds_for_every_run(certificate):
    """The inequality, not the measurement, is the claim: |Pi(a;w) - Pi(a;w0)| <= B."""
    assert certificate["bound_respected"] is True
    for run in certificate["runs"]:
        assert abs(run["gap_of_integrals"]) <= run["bound"] * (1.0 + 1e-6) + 1e-15


def test_the_bound_is_sharp_and_covers_the_observed_deviation(certificate):
    # the weighted-L1 bound must not be vacuous: it exceeds the integral it bounds by <2 %
    assert certificate["bound_sharpness_max_ratio_of_bound_to_gap"] < 1.02
    # and it must cover the deviation of the coupled pressure drop from the master curve
    for run in certificate["runs"]:
        assert abs(run["err_master"]) <= run["bound"]


def test_the_integral_itself_is_verified_on_each_runs_own_shape(certificate):
    # substituting a run's own bow reproduces its coupled pressure drop far better than the
    # collapse does, which is what separates "shape difference" from "wrong integral"
    assert certificate["max_err_shape"] < 1.0e-3
    assert certificate["max_err_shape"] < certificate["max_observed_rel_error"]
