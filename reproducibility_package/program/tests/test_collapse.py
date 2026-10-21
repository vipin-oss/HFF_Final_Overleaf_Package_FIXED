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
    assert collapse["n_runs"] >= 20
    assert collapse["master_max_abs_rel_error"] < 1.0e-2
    assert collapse["master_mean_abs_rel_error"] < 2.0e-3


def test_the_collapse_is_not_vacuous(collapse):
    # the shape law that is being replaced is an order of magnitude worse
    assert collapse["sin2_max_abs_rel_error"] > 10 * collapse["master_max_abs_rel_error"]
    assert collapse["sin2_max_abs_rel_error"] > 0.15


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
