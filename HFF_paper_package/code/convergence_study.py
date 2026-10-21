#!/usr/bin/env python3
"""h-convergence of the restrained, geometrically nonlinear wall (baseline), two independent codes.

Both codes are refined simultaneously in x and y (N_x, N_y) = (12,2), (24,4), (48,8), (96,16), (192,32)
(refinement ratio 2).  The mid-span, mid-surface deflection is compared with the Richardson extrapolation
of the last three levels.  Observed order p, extrapolated value and the grid-convergence index (GCI,
safety factor 1.25) follow Celik et al. (2008).  Codes: q8_nonlinear.Model (Q8 quadrilaterals) and
fe_independent.solve (scikit-fem, P2 triangles).
"""
from __future__ import annotations

import json
import math
import pathlib

import fe_independent as fe
import hff_model as hm
import q8_nonlinear as qn

P = hm.Params()
R0 = hm.compute(P)
LEVELS = [(12, 2), (24, 4), (48, 8), (96, 16), (192, 32)]


def richardson(f3, f2, f1, r=2.0):
    """f3 coarse, f2 medium, f1 fine.  Returns (p, f_ext, GCI_fine) or None."""
    e32, e21 = f2 - f3, f1 - f2
    if e32 * e21 <= 0 or e21 == 0:
        return None
    p = math.log(abs(e32 / e21)) / math.log(r)
    f_ext = f1 + e21 / (r**p - 1)
    gci = 1.25 * abs(e21 / f1) / (r**p - 1)
    return p, f_ext, gci


def main():
    out = {"levels": [], "method": "simultaneous h-refinement, ratio 2"}
    for nx, ny in LEVELS:
        m = qn.Model(nx, ny)
        u, _ = m.solve(nsteps=4)
        wq = float(u[2 * m.lat[(nx, ny)] + 1])
        rp = fe.solve(P.d, R0["theta_bar"], R0["dT_t"], nx, ny)
        out["levels"].append({"nx": nx, "ny": ny, "h_x": P.L / nx, "q8_elements": nx * ny,
                              "p2_elements": rp["elements"], "w_q8": wq, "w_p2": rp["w_nl"]})
        print(f"{nx:4d}x{ny:<3d} Q8 w={wq:.6e}  P2 w={rp['w_nl']:.6e}", flush=True)
    for key in ("w_q8", "w_p2"):
        v = [x[key] for x in out["levels"]]
        out[key + "_richardson"] = richardson(v[-3], v[-2], v[-1])
        print(key, out[key + "_richardson"])
    (pathlib.Path(__file__).resolve().parent / "results" / "convergence.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
