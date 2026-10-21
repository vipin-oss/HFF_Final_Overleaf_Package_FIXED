#!/usr/bin/env python3
"""Geometrically nonlinear plane-strain Q8 strip with axially restrained pinned ends.

Why this script exists
----------------------
q8_strip.py verifies the *free* bow kappa_th L^2/8 (zero membrane force: zero-mean temperature,
axial slip allowed).  The baseline of the paper, however, has axially restrained ends (A7, B6) and
a mean wall temperature rise, so a compressive membrane force N_c acts and the bow is amplified
by the beam-column effect (Section 3).  A linear finite-element model cannot show this effect.
This script solves the baseline wall problem with a total-Lagrangian St Venant-Kirchhoff solid
(Green-Lagrange strain, moderate rotations) and compares with the beam-column predictions.

Problem (identical data to hff_model.Params, baseline)
    plane strain, theta(Y) = theta_bar + dT_t (Y/d - 1/2)  [K],  eigenstrain (1+nu) alpha theta I
    ends X=0,L :  u_y = 0 on the whole edge, mean axial displacement over the edge = 0
                  (eliminated exactly by a linear constraint), no applied moment.
    no mechanical load (the fluid pressure is treated separately in the paper).

Method: Q8 serendipity, 3x3 Gauss, Newton iteration with exact tangent (material + geometric),
thermal load applied in steps.  Checks before use: tangent vs finite-difference of the residual.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

import hff_model as hm
from q8_strip import shape, mesh, validate_shapes, GP, GW

P = hm.Params()
R0 = hm.compute(P)
E, NU, AL, D, L = P.E, P.nu, P.alpha, P.d, P.L
THBAR, DTT = R0["theta_bar"], R0["dT_t"]
LAM = E * NU / ((1 + NU) * (1 - 2 * NU))
G = E / (2 * (1 + NU))
C = np.array([[LAM + 2 * G, LAM, 0.0], [LAM, LAM + 2 * G, 0.0], [0.0, 0.0, G]])


class Model:
    def __init__(self, nx, ny):
        self.nx, self.ny = nx, ny
        self.lat, self.xy, self.el = mesh_dims(nx, ny)
        self.ndof = 2 * len(self.xy)
        xe = self.xy[self.el, 0]
        ye = self.xy[self.el, 1]
        self.xe, self.ye = xe, ye
        self.gp = [(GP[a], GP[b], GW[a] * GW[b]) for a in range(3) for b in range(3)]
        self.sh = [shape(s, t) for s, t, _ in self.gp]
        # geometry factors per Gauss point (reference configuration)
        self.geo = []
        for (s, t, w), (N, Ns, Nt) in zip(self.gp, self.sh):
            xs, ys = xe @ Ns, ye @ Ns
            xt, yt = xe @ Nt, ye @ Nt
            det = xs * yt - xt * ys
            gx = (yt[:, None] * Ns[None, :] - ys[:, None] * Nt[None, :]) / det[:, None]
            gy = (-xt[:, None] * Ns[None, :] + xs[:, None] * Nt[None, :]) / det[:, None]
            Y = ye @ N
            self.geo.append((w * det, gx, gy, Y))
        dofs = np.empty((len(self.el), 16), dtype=int)
        dofs[:, 0::2] = 2 * self.el
        dofs[:, 1::2] = 2 * self.el + 1
        self.dofs = dofs
        self.rows = np.repeat(dofs, 16, axis=1).ravel()
        self.cols = np.tile(dofs, (1, 16)).ravel()
        self._reduction()

    def _reduction(self):
        nx, ny, lat = self.nx, self.ny, self.lat
        nd = self.ndof
        fixed = set()
        elim = {}   # eliminated dof -> {dof: coeff}
        for iend in (0, 2 * nx):
            col = [(j, lat[(iend, j)]) for j in range(2 * ny + 1)]
            for _, n in col:
                fixed.add(2 * n + 1)
            h = D / ny
            wts = {}
            for j, n in col:
                wts[n] = 0.0
            for f in range(ny):          # Simpson on each element edge
                for jj, c in ((2 * f, 1.0), (2 * f + 1, 4.0), (2 * f + 2, 1.0)):
                    wts[lat[(iend, jj)]] += c * h / 6.0
            m = lat[(iend, ny)]
            cm = wts[m]
            elim[2 * m] = {2 * n: -w / cm for n, w in wts.items() if n != m}
        free = [d for d in range(nd) if d not in fixed and d not in elim]
        idx = {d: i for i, d in enumerate(free)}
        rows, cols, vals = [], [], []
        for d in free:
            rows.append(d); cols.append(idx[d]); vals.append(1.0)
        for d, terms in elim.items():
            for dd, c in terms.items():
                rows.append(d); cols.append(idx[dd]); vals.append(c)
        self.T = sp.csr_matrix((vals, (rows, cols)), shape=(nd, len(free)))
        self.nred = len(free)

    def residual_tangent(self, u, s, tangent=True, geometric=True, linear_strain=False):
        """Internal-force residual (thermal eigenstrain scaled by s) and tangent, full space."""
        ue = u[self.dofs]
        ux, uy = ue[:, 0::2], ue[:, 1::2]
        nel = len(self.el)
        fe = np.zeros((nel, 16))
        ke = np.zeros((nel, 16, 16)) if tangent else None
        Nbar = 0.0
        eN = np.zeros(nel)
        for (wd, gx, gy, Y) in self.geo:
            F11 = 1 + (gx * ux).sum(1); F12 = (gy * ux).sum(1)
            F21 = (gx * uy).sum(1);     F22 = 1 + (gy * uy).sum(1)
            if linear_strain:      # small-strain measure, used only to post-process the linear solution
                E11, E22, G12 = F11 - 1, F22 - 1, F12 + F21
            else:
                E11 = 0.5 * (F11**2 + F21**2 - 1)
                E22 = 0.5 * (F12**2 + F22**2 - 1)
                G12 = F11 * F12 + F21 * F22
            th = THBAR + DTT * (Y / D - 0.5)
            eth = s * (1 + NU) * AL * th
            Ev = np.stack([E11 - eth, E22 - eth, G12], axis=1)
            S = Ev @ C.T                                   # (nel,3): S11,S22,S12
            B = np.zeros((nel, 3, 16))
            B[:, 0, 0::2] = F11[:, None] * gx; B[:, 0, 1::2] = F21[:, None] * gx
            B[:, 1, 0::2] = F12[:, None] * gy; B[:, 1, 1::2] = F22[:, None] * gy
            B[:, 2, 0::2] = F11[:, None] * gy + F12[:, None] * gx
            B[:, 2, 1::2] = F21[:, None] * gy + F22[:, None] * gx
            fe += wd[:, None] * np.einsum("eij,ei->ej", B, S)
            Nbar += (wd * S[:, 0]).sum()
            eN += wd * S[:, 0]
            if tangent:
                ke += wd[:, None, None] * np.einsum("eji,jk,ekl->eil", B, C, B)
                Gm = (gx[:, :, None] * (S[:, 0, None, None] * gx[:, None, :] + S[:, 2, None, None] * gy[:, None, :])
                      + gy[:, :, None] * (S[:, 2, None, None] * gx[:, None, :] + S[:, 1, None, None] * gy[:, None, :]))
                if geometric:
                    ke[:, 0::2, 0::2] += wd[:, None, None] * Gm
                    ke[:, 1::2, 1::2] += wd[:, None, None] * Gm
        self.last_eN = eN
        R = np.zeros(self.ndof)
        np.add.at(R, self.dofs.ravel(), fe.ravel())
        K = None
        if tangent:
            K = sp.csr_matrix((ke.ravel(), (self.rows, self.cols)), shape=(self.ndof, self.ndof))
        return R, K, Nbar / L

    def solve(self, nsteps=4, geometric=True, tol=1e-10, verbose=False):
        z = np.zeros(self.nred)
        info = []
        for step in range(1, nsteps + 1):
            s = step / nsteps
            for it in range(30):
                u = self.T @ z
                R, K, Nb = self.residual_tangent(u, s)
                if not geometric:      # linear: drop geometric stiffness and use u=0 kinematics
                    raise NotImplementedError
                Rr = self.T.T @ R
                if it == 0:
                    r0 = max(np.linalg.norm(Rr), 1e-30)
                    ref = np.linalg.norm(self.T.T @ self.residual_tangent(np.zeros(self.ndof), s, False)[0])
                if np.linalg.norm(Rr) < tol * max(ref, 1.0) and it > 0:
                    break
                Kr = (self.T.T @ K @ self.T).tocsc()
                z -= spla.spsolve(Kr, Rr)
            info.append((s, it, float(np.linalg.norm(Rr) / max(ref, 1e-30))))
            if verbose:
                print("   step", s, "iters", it, "rel.res", info[-1][2])
        return self.T @ z, info

    def linear_solution(self):
        """Linear thermoelastic solution with the same restraints: material stiffness only, one step from u=0
        (R is linear in u at F=I, so the step is exact)."""
        u0 = np.zeros(self.ndof)
        R, K, _ = self.residual_tangent(u0, 1.0, True, geometric=False)
        Kr = (self.T.T @ K @ self.T).tocsc()
        z = -spla.spsolve(Kr, self.T.T @ R)
        return self.T @ z


def mesh_dims(nx, ny):
    """mesh() of q8_strip uses its own module-level L and D; both equal the baseline values."""
    assert abs(L - 3.0e-2) < 1e-12 and abs(D - 3.0e-3) < 1e-12
    return mesh(nx, ny)


def tangent_check(m, s=1.0):
    """Central finite difference of the residual against the analytic tangent (error is O(h^2))."""
    rng = np.random.default_rng(1)
    z = 1e-5 * rng.standard_normal(m.nred)
    u = m.T @ z
    _, K, _ = m.residual_tangent(u, s)
    Kr = m.T.T @ K @ m.T
    dz = 1e-7 * rng.standard_normal(m.nred)
    Rp = m.residual_tangent(u + m.T @ dz, s, False)[0]
    Rm = m.residual_tangent(u - m.T @ dz, s, False)[0]
    num = m.T.T @ (Rp - Rm) / 2
    return float(np.linalg.norm(Kr @ dz - num) / np.linalg.norm(num))


def summary(m, u, Nb):
    """w at the mid-surface node of mid-span; mean axial force over the length and the force in
    the two element columns adjacent to mid-span (membrane force N_c = -integral of S11 over Y)."""
    w = float(u[2 * m.lat[(m.nx, m.ny)] + 1])
    col = m.last_eN.reshape(m.nx, m.ny).sum(1) / (L / m.nx)
    mid = -0.5 * (col[m.nx // 2 - 1] + col[m.nx // 2])
    return {"w_mid": w, "Nc_mean": float(-Nb), "Nc_mid": float(mid)}


def main(argv):
    validate_shapes()
    quick = "--quick" in argv
    meshes = [(24, 2), (48, 4)] if quick else [(24, 2), (48, 4), (96, 4), (96, 8), (192, 8)]
    # convergence in the thermal membrane state first: check against the analytic frozen force
    out = {"theta_bar": THBAR, "dT_t": DTT, "w_lin_beam": R0["w_lin"], "w_frozen_beam": R0["w_frozen"],
           "w_sc_beam": R0["w_sc"], "Nc_frozen_beam": R0["N_c"], "Nc_sc_beam": R0["N_c_sc"], "runs": []}
    for nx, ny in meshes:
        t0 = time.time()
        m = Model(nx, ny)
        tc = tangent_check(m)
        assert tc < 1e-4, f"tangent check failed {tc}"
        ul = m.linear_solution()
        _, _, Nbl = m.residual_tangent(ul, 1.0, False, linear_strain=True)
        rl = summary(m, ul, Nbl)
        un, info = m.solve(nsteps=4)
        R, _, Nb = m.residual_tangent(un, 1.0, False)
        rn = summary(m, un, Nb)
        if (nx, ny) == meshes[-1]:
            ii = range(2 * nx + 1)
            rn["profile_x"] = [L * i / (2 * nx) for i in ii]
            rn["profile_w"] = [float(un[2 * m.lat[(i, ny)] + 1]) for i in ii]
            rl["profile_w"] = [float(ul[2 * m.lat[(i, ny)] + 1]) for i in ii]
            m.residual_tangent(un, 1.0, False)
            rn["col_x"] = [L * (i + 0.5) / nx for i in range(nx)]
            rn["col_N"] = [float(-v) for v in m.last_eN.reshape(nx, ny).sum(1) / (L / nx)]
            m.residual_tangent(ul, 1.0, False, linear_strain=True)
            rl["col_N"] = [float(-v) for v in m.last_eN.reshape(nx, ny).sum(1) / (L / nx)]
        rec = {"nx": nx, "ny": ny, "elements": nx * ny, "tangent_check": tc,
               "linear": rl, "nonlinear": rn, "newton": info}
        out["runs"].append(rec)
        print(f"{nx:4d}x{ny:<2d} tangent {tc:.1e}  linear w={rl['w_mid']:.5e} Nmid={rl['Nc_mid']:.0f} | "
              f"NL w={rn['w_mid']:.5e} Nmean={rn['Nc_mean']:.0f} Nmid={rn['Nc_mid']:.0f}  ({time.time()-t0:.1f}s)", flush=True)
    print(f"beam: w_lin={R0['w_lin']:.5e} w_frozen={R0['w_frozen']:.5e} w_sc={R0['w_sc']:.5e} "
          f"Nc_frozen={R0['N_c']:.1f} Nc_sc={R0['N_c_sc']:.1f}")
    name = "q8_nl_quick.json" if quick else "q8_nl.json"
    (pathlib.Path(__file__).resolve().parent / "results" / name).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
