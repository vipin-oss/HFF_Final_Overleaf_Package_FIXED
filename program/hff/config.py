"""Configuration loading and validation for the HFF thermoelastic-channel program.

All material properties, geometric parameters, boundary data and numerical settings
live in JSON parameter files (``params/*.json``) so that they can be changed without
editing source code.  Every value is validated here; an invalid input raises
:class:`ConfigError` with a message naming the offending field.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any, Dict

PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"

#: Physical bounds used by the validator: (field, absolute lower, absolute upper)
_BOUNDS = {
    "geometry": {
        "H0": (1e-6, 1.0),
        "L": (1e-6, 10.0),
        "Le": (0.0, 10.0),
        "Lo": (0.0, 10.0),
        "d": (1e-6, 1.0),
    },
    "operating": {"U": (1e-9, 1e3), "q_flux": (-1e7, 1e7), "Tin": (1.0, 5000.0)},
    "fluid": {
        "rho": (1e-6, 1e6),
        "mu": (1e-12, 1e4),
        "cp": (1e-6, 1e6),
        "k": (1e-9, 1e4),
        "beta": (0.0, 1e0),
    },
    "solid": {
        "E": (1e-3, 1e15),
        "nu": (-0.999, 0.4999),
        "alpha": (0.0, 1e-2),
        "k": (1e-9, 1e4),
        "rho": (1e-6, 1e6),
        "cp": (1e-6, 1e6),
        "sigma_y": (1e-6, 1e14),
    },
    "physics": {"g": (0.0, 1e3)},
}


_NUMERIC_SCALARS = {"nx_heated", "nx_entrance", "nx_exit", "ny_fluid", "ny_solid",
                    "nx_solid", "wall_clustering"}


class ConfigError(ValueError):
    """Raised when a parameter file is missing, malformed, or physically inadmissible."""


def _require(d: Dict[str, Any], key: str, where: str) -> Any:
    if key not in d:
        raise ConfigError(f"missing required field '{where}.{key}'")
    return d[key]


def _check_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"field '{field}' must be a number, got {type(value).__name__}")
    value = float(value)
    if not math.isfinite(value):
        raise ConfigError(f"field '{field}' must be finite, got {value}")
    return value


def validate(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a raw parameter dictionary and return a normalised deep copy."""
    if not isinstance(cfg, dict):
        raise ConfigError("parameter file must contain a JSON object")
    out = copy.deepcopy(cfg)

    for group, fields in _BOUNDS.items():
        block = _require(out, group, "config")
        if not isinstance(block, dict):
            raise ConfigError(f"section '{group}' must be a JSON object")
        for name, (lo, hi) in fields.items():
            val = _check_number(_require(block, name, group), f"{group}.{name}")
            if not (lo <= val <= hi):
                raise ConfigError(
                    f"field '{group}.{name}' = {val:g} outside admissible range [{lo:g}, {hi:g}]"
                )
            block[name] = val

    # reject unknown fields: a typo in the parameter file must not be silently ignored
    # (e.g. "q_flux" misspelt would otherwise leave the baseline value in force)
    known = set(_BOUNDS) | {"numerics", "meta"}
    for group in out:
        if group not in known:
            raise ConfigError(f"unknown section '{group}' in the parameter file")
    for group in _BOUNDS:
        allowed = set(_BOUNDS[group])
        for name in out[group]:
            if name not in allowed:
                raise ConfigError(f"unknown field '{group}.{name}' in the parameter file")
    for name in out["numerics"]:
        if name in ("flow", "thermal", "coupling", "wall"):
            continue
        if name not in _NUMERIC_SCALARS:
            raise ConfigError(f"unknown field 'numerics.{name}' in the parameter file")
    for block, allowed in (("flow", {"re_continuation", "picard_max_iter", "picard_tol",
                                     "relaxation", "pressure_pin_penalty"}),
                           ("thermal", {"supg", "benchmark_flux"}),
                           ("coupling", {"max_iter", "tol_rel", "relaxation",
                                         "max_bow_fraction"}),
                           ("wall", {"n_points", "self_consistent", "fixed_point_tol",
                                     "fixed_point_max_iter", "pressure_load"})):
        for name in out["numerics"].get(block, {}):
            if name not in allowed:
                raise ConfigError(f"unknown field 'numerics.{block}.{name}'")

    geo, num = out["geometry"], _require(out, "numerics", "config")
    if geo["d"] < 10 * geo["H0"] * 1e-3:
        raise ConfigError("wall thickness d is vanishingly small relative to H0")
    if geo["L"] <= 0 or geo["H0"] <= 0:
        raise ConfigError("L and H0 must be positive")
    if num.get("nx_heated", 0) < 4 or num.get("ny_fluid", 0) < 2:
        raise ConfigError("numerics.nx_heated must be >= 4 and numerics.ny_fluid >= 2")
    if num.get("ny_solid", 0) < 2:
        raise ConfigError("numerics.ny_solid must be >= 2")
    coupling = num.get("coupling", {})
    if not (0.0 < float(coupling.get("relaxation", 0.5)) <= 1.0):
        raise ConfigError("numerics.coupling.relaxation must lie in (0, 1]")
    if float(coupling.get("max_bow_fraction", 0.45)) >= 0.9:
        raise ConfigError("numerics.coupling.max_bow_fraction must be < 0.9 (mesh validity)")

    # Buoyancy guard of the formulation (regime bound A-4): warn loudly, do not fail.
    if cfg.get("meta", {}).get("reference_temperature_K") is None:
        out.setdefault("meta", {})["reference_temperature_K"] = float(out["operating"]["Tin"])
    return out


def load(path: str | Path) -> Dict[str, Any]:
    """Load and validate a JSON parameter file."""
    p = Path(path)
    if not p.exists():
        alt = PARAMS_DIR / p.name
        if alt.exists():
            p = alt
        else:
            raise ConfigError(f"parameter file not found: {path}")
    try:
        raw = json.loads(p.read_text())
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ConfigError(f"invalid JSON in {p}: {exc}") from exc
    return validate(raw)


def derived(cfg: Dict[str, Any]) -> Dict[str, float]:
    """Secondary quantities fixed by the primary parameters."""
    g = cfg["geometry"]
    f, s = cfg["fluid"], cfg["solid"]
    nu = s["nu"]
    lam = s["E"] * nu / ((1 + nu) * (1 - 2 * nu))
    mu_l = s["E"] / (2 * (1 + nu))
    K = lam + 2.0 * mu_l / 3.0
    beta = 3.0 * K * s["alpha"]
    return {
        "Dh": 2.0 * g["H0"],
        "L_total": g["Le"] + g["L"] + g["Lo"],
        "lambda": lam,
        "mu_L": mu_l,
        "K": K,
        "beta": beta,
        "Ds": s["E"] * g["d"] ** 3 / (12.0 * (1.0 - nu**2)),
        "alpha_f": f["k"] / (f["rho"] * f["cp"]),
        "alpha_s": s["k"] / (s["rho"] * s["cp"]),
        "nu_kin": f["mu"] / f["rho"],
    }


def dump(cfg: Dict[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
