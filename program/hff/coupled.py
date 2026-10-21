"""Partitioned fluid--thermal--structure coupling.

The three sub-problems are solved in a fixed-point loop on the interface deflection:

1.  **Flow.**  The steady Navier--Stokes equations are solved on the body-fitted mesh of
    the passage whose upper wall is the current interface shape ``w(x)``; the pressure
    distribution on the interface and the wall shear are extracted.
2.  **Conjugate heat transfer.**  The fluid energy equation and the wall conduction
    equation are solved monolithically on the conforming fluid/solid discretisation;
    the thickness-averaged wall temperature and the through-thickness gradient give the
    eigen-curvature ``kappa_th(x)`` of the strip.
3.  **Structure.**  The reduced von Karman beam--column problem of the formulation is
    solved with ``kappa_th(x)`` as the imposed eigen-curvature, the fluid pressure as the
    transverse load and the axial-compatibility fixed point for the membrane force; the
    result is the new interface shape.

The loop is under-relaxed.  ``max_bow_fraction`` stops the run when the predicted
deflection exceeds a prescribed fraction of the undeformed height, which is where the
kinematic assumptions of the formulation (small slope, thin wall, slowly varying
passage) stop being defensible.  Nothing is silently capped: the reason for a stopped
run is recorded in ``CoupledResult.termination``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from . import analytic, config, fem, flow, thermal, wall


@dataclass
class CoupledResult:
    wall: Optional[wall.WallState]
    flow: Optional[flow.FlowSolution]
    thermal: Optional[thermal.ThermalSolution]
    w: np.ndarray
    x: np.ndarray
    history: List[Dict[str, float]] = field(default_factory=list)
    converged: bool = False
    termination: str = ""
    iterations: int = 0
    thermal_theta_bar: Optional[np.ndarray] = None

    def metrics(self, cfg: Dict[str, Any]) -> Dict[str, float]:
        g, s, op = cfg["geometry"], cfg["solid"], cfg["operating"]
        out: Dict[str, float] = {}
        if self.flow is not None:
            out.update({f"flow_{k}": v for k, v in flow.flow_metrics(self.flow, cfg).items()})
        if self.wall is not None:
            st = self.wall
            out["w_max"] = st.w_max
            out["w_max_over_H0"] = st.w_max / g["H0"]
            out["x_at_wmax"] = st.x_at_wmax
            out["slope_max"] = st.slope_max
            out["M_mid"] = float(np.interp(0.5 * g["L"], st.x, st.moment))
            out["sigma_bend_max"] = float(np.max(st.bending_stress(g["d"])))
            theta_mean = (float(np.mean(self.thermal_theta_bar))
                          if self.thermal_theta_bar is not None else float("nan"))
            out["sigma_memb"] = -s["E"] * s["alpha"] * theta_mean / (1.0 - s["nu"])
            out["N_membrane"] = st.N
            out["N_theta"] = st.N_theta
            Ds = config.derived(cfg)["Ds"]
            out["N_over_Ncr"] = abs(st.N) / (np.pi**2 * Ds / g["L"]**2)
            out["arc"] = st.arc
            out["eps_fibre"] = float(np.max(st.surface_strain_bending(g["d"])))
        if self.thermal is not None:
            bal = thermal.enthalpy_balance(self.thermal, cfg)
            out["Q_in"] = bal["Q_in"]
            out["Q_out"] = bal["Q_out"]
            out["energy_imbalance"] = bal["rel_imbalance"]
            out["interface_flux_jump"] = thermal.interface_flux_jump(self.thermal, cfg)
            nu = thermal.nusselt_profile(self.thermal, cfg)
            out["Nu_inlet"] = float(nu["Nu"][1])
            out["Nu_mean"] = float(np.nanmean(nu["Nu"]))
            out["Nu_outlet"] = float(nu["Nu"][-2])
            out["h_mean"] = float(np.nanmean(nu["h"]))
            out["T_wall_max"] = float(np.max(self.thermal.T))
            if self.thermal_theta_bar is not None:
                tb = np.asarray(self.thermal_theta_bar)
                out["theta_bar_mean"] = float(np.mean(tb))
                out["theta_bar_max"] = float(np.max(tb))
        if self.w is not None:
            out["w_max_fraction_of_H0"] = float(np.max(np.abs(self.w)) / g["H0"])
        return {k: float(v) for k, v in out.items()}


def _wall_profile_arrays(therm: thermal.ThermalSolution, cfg: Dict[str, Any]):
    data = fem.element_data(therm.solid, therm.solid.p2_coordinates(therm.n_global))
    return thermal.wall_profile(therm.solid, data, therm.T, cfg)


def solve_coupled(cfg: Dict[str, Any], verbose: bool = False,
                  w_init: Optional[np.ndarray] = None,
                  stop_after: int = 0) -> CoupledResult:
    """Run the partitioned fixed-point coupling for the baseline configuration."""
    g, s, num = cfg["geometry"], cfg["solid"], cfg["numerics"]
    L, H0, d = g["L"], g["H0"], g["d"]
    nxd = int(num["nx_heated"])
    x = np.linspace(0.0, L, nxd + 1)
    coup = num["coupling"]
    max_it = int(coup.get("max_iter", 25))
    tol = float(coup.get("tol_rel", 1e-6))
    relax = float(coup.get("relaxation", 0.5))
    max_bow = float(coup.get("max_bow_fraction", 0.45))

    Ds = config.derived(cfg)["Ds"]

    w = np.zeros(nxd + 1) if w_init is None else np.asarray(w_init, dtype=float).copy()
    if w.size != nxd + 1:
        raise ValueError(f"w_init must have nx_heated+1 = {nxd + 1} entries")

    history: List[Dict[str, float]] = []
    result = CoupledResult(wall=None, flow=None, thermal=None, w=w.copy(), x=x)
    state = None
    flow_sol = None
    therm = None
    theta_bar = None
    for it in range(1, max_it + 1):
        fluid = fem.fluid_mesh(cfg, w)
        solid = fem.solid_mesh(cfg, fluid)
        n_global = fem.bind_shared(fluid, solid)

        flow_sol = flow.solve_flow(fluid, cfg)
        therm = thermal.solve_thermal(fluid, solid, flow_sol, cfg, n_global)
        prof = _wall_profile_arrays(therm, cfg)
        theta_bar = prof["theta_bar"]
        kappa = prof["kappa_th"]

        p_iface = flow.interface_pressure(flow_sol, x)
        # the fluid pressure acts on the wetted face and pushes the wall away from the
        # passage; with w positive into the passage the transverse load is -p
        state = wall.self_consistent(x, Ds, kappa, theta_bar, cfg, p=-p_iface)

        w_new = state.w
        scale = max(float(np.max(np.abs(w_new))), 1e-30)
        delta = float(np.max(np.abs(w_new - w)) / scale)
        history.append({
            "iteration": it,
            "w_max": state.w_max,
            "w_max_over_H0": state.w_max / H0,
            "delta_rel": delta,
            "N": state.N,
            "dp": float(np.mean(flow_sol.p[fluid.boundary_vertices("inlet")])
                        - np.mean(flow_sol.p[fluid.boundary_vertices("outlet")])),
            "theta_bar_mean": float(np.mean(theta_bar)),
            "energy_imbalance": thermal.enthalpy_balance(therm, cfg)["rel_imbalance"],
        })
        if verbose:
            print(f"  coupling it {it:2d}: w_max/H0={state.w_max / H0:.4f} "
                  f"delta={delta:.2e} N={state.N:9.2f} "
                  f"dT={np.mean(theta_bar):7.2f} K")

        result.iterations = it
        result.wall, result.flow, result.thermal = state, flow_sol, therm
        result.thermal_theta_bar = theta_bar
        result.history = history
        result.w = w_new.copy()

        if delta < tol:
            result.converged = True
            result.termination = "converged"
            break
        if state.w_max / H0 > max_bow:
            result.termination = (
                f"stopped: predicted bow {state.w_max / H0:.3f} H0 exceeds the kinematic "
                f"limit {max_bow:.2f} H0 of the reduced model")
            if verbose:
                print("  " + result.termination)
            break
        if stop_after and it >= stop_after:
            result.termination = f"stopped after {stop_after} iterations by request"
            break
        w = (1.0 - relax) * w + relax * w_new
        result.w = w.copy()
    else:
        result.termination = f"not converged in {max_it} iterations"

    result.history = history
    return result
