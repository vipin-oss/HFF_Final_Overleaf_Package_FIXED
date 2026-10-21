#!/usr/bin/env python3
"""Plane-strain Q8 thermoelastic strip: end-support and mesh-sensitivity study.

Purpose
-------
The reduced-order wall model of the paper predicts that a strip with a linear through-thickness
temperature profile and ideal pinned ends bows to  w_max = kappa_th L^2 / 8  at negligible
membrane force.  This script solves the corresponding two-dimensional plane-strain thermoelastic
problem with 8-node serendipity (Q8) elements, and reports

    ratio = w(L/2, y*) / (kappa_th L^2 / 8)            at the FIXED height y* = d/2 (mid-surface)

for three idealisations of the ends:

    POINT : u_y = 0 at the single mid-surface node of each end edge (ideal point pin)
    PIN   : u_y = 0 on the whole end edge, mean axial displacement free (the pin of the paper)
    CLAMP : u_x = u_y = 0 on the whole end edge (a clamp; beam theory predicts w = 0)

Why the height is fixed
-----------------------
A sampling height that moves with the mesh (e.g. "the second lattice row") changes with the
through-thickness refinement and is not a mesh property.  Every value below is sampled at the
same physical point, the mid-surface y = d/2, on every mesh.

Method
------
Own mesh generator, own serendipity shape functions, 3x3 Gauss quadrature, sparse direct solve.
Plane strain with the effective in-plane thermal strain (1+nu) alpha theta.  Before any result is
used: partition of unity and shape-function derivatives are checked, and the patch test (the exact
stress-free thermal-bending field must satisfy K u = f to round-off) is run on every mesh.

This script is independent of the earlier pure-Python audit scripts (own implementation).
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

E, NU, ALPHA, DT = 3.6e9, 0.40, 5.0e-5, 25.0
L, D = 3.0e-2, 3.0e-3
KTH = (1 + NU) * ALPHA * DT / D
WB = KTH * L * L / 8.0
LAM = E * NU / ((1 + NU) * (1 - 2 * NU))
G = E / (2 * (1 + NU))
CMAT = np.array([[LAM + 2 * G, LAM, 0.0], [LAM, LAM + 2 * G, 0.0], [0.0, 0.0, G]])
GP = np.array([-math.sqrt(0.6), 0.0, math.sqrt(0.6)])
GW = np.array([5 / 9, 8 / 9, 5 / 9])


def shape(s, t):
    N = np.array([
        (1 - s) * (1 - t) * (-s - t - 1) / 4, (1 + s) * (1 - t) * (s - t - 1) / 4,
        (1 + s) * (1 + t) * (s + t - 1) / 4, (1 - s) * (1 + t) * (-s + t - 1) / 4,
        (1 - s * s) * (1 - t) / 2, (1 + s) * (1 - t * t) / 2,
        (1 - s * s) * (1 + t) / 2, (1 - s) * (1 - t * t) / 2])
    Ns = np.array([
        (1 - t) * (2 * s + t) / 4, (1 - t) * (2 * s - t) / 4,
        (1 + t) * (2 * s + t) / 4, (1 + t) * (2 * s - t) / 4,
        -s * (1 - t), (1 - t * t) / 2, -s * (1 + t), -(1 - t * t) / 2])
    Nt = np.array([
        (1 - s) * (s + 2 * t) / 4, (1 + s) * (2 * t - s) / 4,
        (1 + s) * (s + 2 * t) / 4, (1 - s) * (2 * t - s) / 4,
        -(1 - s * s) / 2, -(1 + s) * t, (1 - s * s) / 2, -(1 - s) * t])
    return N, Ns, Nt


def validate_shapes() -> tuple[float, float]:
    worst_n = worst_d = 0.0
    h = 1e-6
    for s, t in [(0, 0), (0.33, -0.71), (-0.82, 0.44), (0.11, 0.95), (-0.5, -0.5)]:
        N, Ns, Nt = shape(s, t)
        worst_n = max(worst_n, abs(N.sum() - 1.0))
        ds = (shape(s + h, t)[0] - shape(s - h, t)[0]) / (2 * h)
        dt = (shape(s, t + h)[0] - shape(s, t - h)[0]) / (2 * h)
        worst_d = max(worst_d, np.abs(ds - Ns).max(), np.abs(dt - Nt).max())
    return worst_n, worst_d


def mesh(nx: int, ny: int):
    lat: dict[tuple[int, int], int] = {}
    xy = []
    for j in range(2 * ny + 1):
        for i in range(2 * nx + 1):
            if i % 2 == 0 or j % 2 == 0:
                lat[(i, j)] = len(xy)
                xy.append((L * i / (2 * nx), D * j / (2 * ny)))
    el = []
    for e in range(nx):
        for f in range(ny):
            i0, j0 = 2 * e, 2 * f
            el.append([lat[(i0, j0)], lat[(i0 + 2, j0)], lat[(i0 + 2, j0 + 2)], lat[(i0, j0 + 2)],
                       lat[(i0 + 1, j0)], lat[(i0 + 2, j0 + 1)], lat[(i0 + 1, j0 + 2)],
                       lat[(i0, j0 + 1)]])
    return lat, np.array(xy), np.array(el)


def assemble(xy, el):
    ndof = 2 * len(xy)
    rows, cols, vals = [], [], []
    F = np.zeros(ndof)
    # precompute shape data at Gauss points
    gp = [(GP[a], GP[b], GW[a] * GW[b]) for a in range(3) for b in range(3)]
    sh = [shape(s, t) for s, t, _ in gp]
    for conn in el:
        xe, ye = xy[conn, 0], xy[conn, 1]
        ke = np.zeros((16, 16))
        fe = np.zeros(16)
        for (s, t, w), (N, Ns, Nt) in zip(gp, sh):
            xs, ys, xt, yt = Ns @ xe, Ns @ ye, Nt @ xe, Nt @ ye
            det = xs * yt - xt * ys
            if det <= 0:
                raise ArithmeticError("non-positive Jacobian")
            gx = (yt * Ns - ys * Nt) / det
            gy = (-xt * Ns + xs * Nt) / det
            B = np.zeros((3, 16))
            B[0, 0::2] = gx
            B[1, 1::2] = gy
            B[2, 0::2] = gy
            B[2, 1::2] = gx
            wd = w * det
            ke += wd * (B.T @ CMAT @ B)
            yv = N @ ye
            eth = (1 + NU) * ALPHA * DT * (yv / D - 0.5)
            fe += wd * (B.T @ (CMAT @ np.array([eth, eth, 0.0])))
        dofs = np.empty(16, dtype=int)
        dofs[0::2] = 2 * conn
        dofs[1::2] = 2 * conn + 1
        rows.append(np.repeat(dofs, 16))
        cols.append(np.tile(dofs, 16))
        vals.append(ke.ravel())
        F[dofs] += fe
    K = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(ndof, ndof))
    return K, F


def patch_test(K, F, xy) -> float:
    u = np.zeros(2 * len(xy))
    x, y = xy[:, 0], xy[:, 1]
    u[0::2] = -(y - D / 2) * KTH * (L - 2 * x) / 2
    u[1::2] = KTH * x * (L - x) / 2 + KTH * (y - D / 2) ** 2 / 2
    return float(np.abs(K @ u - F).max() / np.abs(F).max())


def solve_case(K, F, fixed):
    ndof = len(F)
    free = np.setdiff1d(np.arange(ndof), np.fromiter(fixed, dtype=int))
    u = np.zeros(ndof)
    u[free] = spla.spsolve(K[free][:, free].tocsc(), F[free])
    return u


def run_mesh(nx: int, ny: int) -> dict:
    lat, xy, el = mesh(nx, ny)
    K, F = assemble(xy, el)
    patch = patch_test(K, F, xy)
    face0 = [n for (i, j), n in lat.items() if i == 0]
    faceL = [n for (i, j), n in lat.items() if i == 2 * nx]
    mid0, midL = lat[(0, ny)], lat[(2 * nx, ny)]
    res = {"nx": nx, "ny": ny, "elements": nx * ny, "patch": patch}
    for mode in ("POINT", "PIN", "CLAMP"):
        fixed = set()
        if mode == "POINT":
            fixed |= {2 * lat[(0, ny)] + 1, 2 * lat[(2 * nx, ny)] + 1, 2 * lat[(0, ny)]}
        if mode == "PIN":
            fixed |= {2 * n + 1 for n in face0 + faceL}
            fixed.add(2 * lat[(0, ny)])         # remove the axial rigid-body translation only
        if mode == "CLAMP":
            fixed |= {2 * n for n in face0 + faceL} | {2 * n + 1 for n in face0 + faceL}
        u = solve_case(K, F, fixed)
        # fixed physical sampling heights at mid-span x = L/2 (node i = nx)
        row = {}
        for lab, frac in (("d/2", 0.5), ("d/4", 0.25), ("d", 1.0)):
            j = int(round(2 * ny * frac))
            row[lab] = float(u[2 * lat[(nx, j)] + 1] / WB)
        res[mode] = row
    return res


def main(argv) -> None:
    quick = "--quick" in argv
    wn, wd = validate_shapes()
    print(f"shape functions: partition of unity {wn:.1e}, derivatives vs central differences {wd:.1e}")
    assert wn < 1e-14 and wd < 1e-7
    print(f"kappa_th = {KTH:.6e} 1/m,  beam value kappa_th L^2/8 = {WB:.6e} m")
    nxs = [6, 12, 24, 48] if quick else [6, 12, 24, 48, 96, 192]
    nys = [2, 4] if quick else [2, 4, 8]
    out = []
    for ny in nys:
        for nx in nxs:
            r = run_mesh(nx, ny)
            out.append(r)
            print(f"  {nx:4d} x {ny:<2d} el={r['elements']:5d} patch={r['patch']:.1e} "
                  f"POINT={r['POINT']['d/2']:.5f} PIN={r['PIN']['d/2']:.5f} "
                  f"CLAMP={r['CLAMP']['d/2']:+.5f}", flush=True)
    resdir = pathlib.Path(__file__).resolve().parent / "results"
    resdir.mkdir(exist_ok=True)
    name = "q8_study_quick.json" if quick else "q8_study.json"
    (resdir / name).write_text(json.dumps({"kappa_th": KTH, "w_beam": WB, "runs": out}, indent=2))
    print("written", resdir / name)


if __name__ == "__main__":
    main(sys.argv[1:])
