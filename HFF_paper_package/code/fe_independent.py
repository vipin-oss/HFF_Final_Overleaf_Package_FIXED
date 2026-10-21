#!/usr/bin/env python3
"""Independent finite-element check of the restrained, geometrically nonlinear wall (scikit-fem).

Purpose
-------
q8_nonlinear.py is a hand-written Q8 quadrilateral code.  This script solves the *same boundary-value
problem* with a different code base and a different discretisation: scikit-fem, six-node quadratic
triangles (P2), a different mesh topology and different assembly, constraint handling (Lagrange
multipliers) and quadrature.  Agreement therefore tests the implementation and the mesh/element
dependence; it does not test the governing equations themselves (St Venant-Kirchhoff kinematics,
eigenstrain model), which are the same in both codes and are the assumptions of the paper.

Problem: plane-strain strip 0<=X<=L, 0<=Y<=d,  theta(Y) = theta_bar + dT_t (Y/d - 1/2),
in-plane eigenstrain (1+nu) alpha theta, u_y = 0 on both end edges, zero mean axial displacement on each
end edge (Lagrange multipliers), no mechanical load.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from skfem import (Basis, BilinearForm, ElementTriP2, ElementVector, FacetBasis, LinearForm, MeshTri,
                   asm)

import hff_model as hm

P = hm.Params()
E, NU, AL, L = P.E, P.nu, P.alpha, P.L
LAM = E * NU / ((1 + NU) * (1 - 2 * NU))
G = E / (2 * (1 + NU))


def stress_tensor(Ee, th):
    """S = C:(E - (1+nu) alpha theta I) in plane strain; Ee shape (2,2,...), th shape (...)."""
    eth = (1 + NU) * AL * th
    e11, e22, e12 = Ee[0, 0] - eth, Ee[1, 1] - eth, Ee[0, 1]
    tr = e11 + e22
    S = np.empty_like(Ee)
    S[0, 0] = LAM * tr + 2 * G * e11
    S[1, 1] = LAM * tr + 2 * G * e22
    S[0, 1] = S[1, 0] = 2 * G * e12
    return S


def solve(d, thbar, dtt, nx, ny, nsteps=4, verbose=False):
    xs = np.linspace(0.0, L, nx + 1)
    ys = np.linspace(0.0, d, ny + 1)
    mesh = MeshTri.init_tensor(xs, ys)
    basis = Basis(mesh, ElementVector(ElementTriP2()))
    I2 = np.eye(2)[:, :, None, None]

    def kin(w):
        F = I2 + w["u"].grad                     # F_ij = delta_ij + du_i/dX_j
        Ee = 0.5 * (np.einsum("kiab,kjab->ijab", F, F) - I2)
        return F, Ee

    def theta(Y):
        return thbar + dtt * (Y / d - 0.5)

    @LinearForm
    def residual(v, w):
        F, Ee = kin(w)
        S = stress_tensor(Ee, w["s"] * theta(w.x[1]))
        dE = 0.5 * (np.einsum("kiab,kjab->ijab", F, v.grad) + np.einsum("kiab,kjab->ijab", v.grad, F))
        return np.einsum("ijab,ijab->ab", S, dE)

    def tangent_form(geometric):
        @BilinearForm
        def tangent(du, v, w):
            F, Ee = kin(w)
            S = stress_tensor(Ee, w["s"] * theta(w.x[1]))
            dEv = 0.5 * (np.einsum("kiab,kjab->ijab", F, v.grad) + np.einsum("kiab,kjab->ijab", v.grad, F))
            dEu = 0.5 * (np.einsum("kiab,kjab->ijab", F, du.grad) + np.einsum("kiab,kjab->ijab", du.grad, F))
            tr = dEu[0, 0] + dEu[1, 1]
            dS = np.empty_like(dEu)
            dS[0, 0] = LAM * tr + 2 * G * dEu[0, 0]
            dS[1, 1] = LAM * tr + 2 * G * dEu[1, 1]
            dS[0, 1] = dS[1, 0] = 2 * G * dEu[0, 1]
            out = np.einsum("ijab,ijab->ab", dS, dEv)
            if geometric:
                out = out + np.einsum("ijab,kiab,kjab->ab", S, du.grad, v.grad)
            return out
        return tangent

    tan_geo, tan_mat = tangent_form(True), tangent_form(False)

    left = mesh.facets_satisfying(lambda x: x[0] < 1e-12)
    right = mesh.facets_satisfying(lambda x: x[0] > L - 1e-12)
    # u_y = 0 on end edges: component 1 only (vertex and mid-edge dofs)
    fixed = np.unique(np.concatenate([basis.get_dofs(left).nodal["u^2"], basis.get_dofs(right).nodal["u^2"],
                                      basis.get_dofs(left).facet["u^2"], basis.get_dofs(right).facet["u^2"]]))

    @LinearForm
    def axial(v, w):
        return v.value[0]

    cons = []
    for facets in (left, right):
        fb = FacetBasis(mesh, ElementVector(ElementTriP2()), facets=facets)
        cons.append(asm(axial, fb))
    Cm = sp.csr_matrix(np.vstack(cons))
    nd = basis.N
    free = np.setdiff1d(np.arange(nd), fixed)
    xq = basis.global_coordinates()
    S_load = lambda s: s * np.ones_like(xq.value[0])

    def assemble(u, s, tangent=True, geometric=True, linear_strain=False):
        w = {"u": basis.interpolate(u), "s": S_load(s)}
        R = asm(residual, basis, **w)
        K = asm(tan_geo if geometric else tan_mat, basis, **w) if tangent else None
        return R, K

    def bordered(u, lam, s, geometric=True, tangent=True):
        R, K = assemble(u, s, tangent, geometric)
        g = np.concatenate([R[free] + Cm[:, free].T @ lam, Cm[:, free] @ u[free]])
        if not tangent:
            return g, None
        J = sp.bmat([[K[free][:, free], Cm[:, free].T], [Cm[:, free], None]], format="csc")
        return g, J

    # linear solution (material stiffness, one exact step from u=0)
    u0, lam0 = np.zeros(nd), np.zeros(2)
    g, J = bordered(u0, lam0, 1.0, geometric=False)
    z = spla.spsolve(J, -g)
    u_lin = np.zeros(nd)
    u_lin[free] = z[: len(free)]

    # nonlinear solution: Newton with thermal load steps
    u = np.zeros(nd)
    lam = np.zeros(2)
    hist = []
    for k in range(1, nsteps + 1):
        s = k / nsteps
        for it in range(30):
            g, J = bordered(u, lam, s)
            if it == 0:
                gref = np.linalg.norm(bordered(np.zeros(nd), np.zeros(2), s, tangent=False)[0])
            rel = np.linalg.norm(g) / max(gref, 1.0)
            if rel < 1e-10 and it > 0:
                break
            dz = spla.spsolve(J, -g)
            u[free] += dz[: len(free)]
            lam += dz[len(free):]
        hist.append((s, it, float(rel)))
        if verbose:
            print("   step", s, "iters", it, "rel.res", rel)

    # mid-span, mid-surface vertex
    p = mesh.p
    k0 = int(np.argmin((p[0] - L / 2) ** 2 + (p[1] - d / 2) ** 2))
    assert abs(p[0, k0] - L / 2) < 1e-12 and abs(p[1, k0] - d / 2) < 1e-12, "mid-surface vertex needed"
    dof_uy = basis.nodal_dofs[1, k0]

    def force_band(u_, linear_strain=False):
        """Compressive membrane force from the band |x - L/2| < L/8: -(integral of S11 dA)/(band length)."""
        gu = basis.interpolate(u_).grad
        if linear_strain:
            Ee = 0.5 * (gu + gu.transpose(1, 0, 2, 3))
        else:
            F = I2 + gu
            Ee = 0.5 * (np.einsum("kiab,kjab->ijab", F, F) - I2)
        S = stress_tensor(Ee, theta(xq.value[1]))
        sel = np.abs(xq.value[0].mean(axis=1) - L / 2) < L / 8
        band_length = basis.dx[sel].sum() / d
        return -(S[0, 0] * basis.dx)[sel].sum() / band_length

    return {
        "w_lin": float(u_lin[dof_uy]), "w_nl": float(u[dof_uy]),
        "Nc_lin": float(force_band(u_lin, linear_strain=True)), "Nc_nl": float(force_band(u)),
        "newton": hist, "ndof": int(nd), "elements": int(mesh.t.shape[1]),
    }


def main(argv):
    quick = "--quick" in argv
    r0 = hm.compute(P)
    out = {"baseline_beam": {"w_lin": r0["w_lin"], "w_frozen": r0["w_frozen"], "w_sc": r0["w_sc"],
                             "Nc_frozen": r0["N_c"], "Nc_sc": r0["N_c_sc"]}, "runs": []}
    meshes = [(48, 4)] if quick else [(48, 4), (96, 4), (96, 8), (192, 8)]
    for nx, ny in meshes:
        r = solve(P.d, r0["theta_bar"], r0["dT_t"], nx, ny)
        r.update(nx=nx, ny=ny)
        out["runs"].append(r)
        print(f"{nx:4d}x{ny:<2d} P2 tri el={r['elements']:6d}  w_lin={r['w_lin']:.5e} w_NL={r['w_nl']:.5e} "
              f"N_lin={r['Nc_lin']:.0f} N_NL={r['Nc_nl']:.0f}", flush=True)
    name = "fe_independent_quick.json" if quick else "fe_independent.json"
    (pathlib.Path(__file__).resolve().parent / "results" / name).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
