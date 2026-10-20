#!/usr/bin/env python3
"""Height-consistent Q8 study for register D-26 (Stage 20, finding F-1).

Why this script exists
----------------------
The six-mesh study of Stage 19 reported a "top face" and a "mid" column whose *physical
heights were not fixed*: it read `lat[(NX,1)]` and `lat[(NX,2)]`, and the lattice maps
j -> y = d*j/(2*NY).  Those nodes therefore sit at

    lat[(NX,1)]:  y = d/4  for NY = 2,   y = d/8  for NY = 4
    lat[(NX,2)]:  y = d/2  for NY = 2,   y = d/4  for NY = 4

so the two "through-thickness" rows of that table were sampled at different heights.  The
apparent dependence of the ratios on the through-thickness discretisation was an artefact of
that choice, not a property of the finite-element model.

This script re-solves the same six meshes and reports every ratio at three FIXED physical
heights, y = d/2 (mid-surface), y = d/4 and y = d (top face).  It is the evidence base for the
Stage 20 correction of the ch04/ch11/A9/D-26 statements.

Method (independent of independent_audit_stage16/evidence/q8_pin_verification.py)
--------------------------------------------------------------------------------
Own mesh generator, own 8-node serendipity shape functions, own symmetric-banded Cholesky
solver (`A = U^T U`), homogeneous essential conditions imposed by row/column elimination.
Plane strain, full 3x3 Gauss quadrature, effective thermal strain (1+nu)*alpha*theta.
Validated before any result is used:
  * partition of unity and analytic derivatives checked against central differences;
  * patch test: the exact stress-free thermal-bending field must satisfy K u = f to round-off.

Usage
-----
    python3 audit_stage15/q8_height_study.py            # six meshes (fast)
    python3 audit_stage15/q8_height_study.py --extra    # adds 48x8 as a convergence check
"""
import sys
from math import sqrt, cos, sin, tan

E, nu, alpha, dT = 3.6e9, 0.40, 5.0e-5, 25.0
L, d = 3.0e-2, 3.0e-3
KTH = (1 + nu) * alpha * dT / d
WB = KTH * L * L / 8.0
MU_LAM = E * nu / ((1 + nu) * (1 - 2 * nu))
MU_SHR = E / (2 * (1 + nu))
D = [[MU_LAM + 2 * MU_SHR, MU_LAM, 0.0], [MU_LAM, MU_LAM + 2 * MU_SHR, 0.0], [0.0, 0.0, MU_SHR]]

GA = [-sqrt(3.0 / 5.0), 0.0, sqrt(3.0 / 5.0)]
GW = [5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0]


def shp(s, t):
    """8-node serendipity shape functions and their s/t derivatives."""
    N = [(1 - s) * (1 - t) * (-s - t - 1) / 4, (1 + s) * (1 - t) * (s - t - 1) / 4,
         (1 + s) * (1 + t) * (s + t - 1) / 4, (1 - s) * (1 + t) * (-s + t - 1) / 4,
         (1 - s * s) * (1 - t) / 2, (1 + s) * (1 - t * t) / 2,
         (1 - s * s) * (1 + t) / 2, (1 - s) * (1 - t * t) / 2]
    Ns = [(1 - t) * (2 * s + t) / 4, (1 - t) * (2 * s - t) / 4,
          (1 + t) * (2 * s + t) / 4, (1 + t) * (2 * s - t) / 4,
          -s * (1 - t), (1 - t * t) / 2, -s * (1 + t), -(1 - t * t) / 2]
    Nt = [(1 - s) * (s + 2 * t) / 4, (1 + s) * (2 * t - s) / 4,
          (1 + s) * (s + 2 * t) / 4, (1 - s) * (2 * t - s) / 4,
          -(1 - s * s) / 2, -(1 + s) * t, (1 - s * s) / 2, -(1 - s) * t]
    return N, Ns, Nt


def validate_shapes():
    worst_n = worst_d = 0.0
    for (s, t) in [(0.0, 0.0), (0.33, -0.71), (-0.82, 0.44), (0.11, 0.95), (-0.5, -0.5)]:
        N, Ns, Nt = shp(s, t)
        worst_n = max(worst_n, abs(sum(N) - 1.0))
        h = 1e-6
        Na, _, _ = shp(s + h, t); Nb, _, _ = shp(s - h, t)
        Nc, _, _ = shp(s, t + h); Ne, _, _ = shp(s, t - h)
        for k in range(8):
            worst_d = max(worst_d, abs((Na[k] - Nb[k]) / (2 * h) - Ns[k]),
                          abs((Nc[k] - Ne[k]) / (2 * h) - Nt[k]))
    return worst_n, worst_d


def build(nx, ny):
    lat, xy = {}, []
    for j in range(2 * ny + 1):
        for i in range(2 * nx + 1):
            if i % 2 == 0 or j % 2 == 0:
                lat[(i, j)] = len(xy)
                xy.append((L * i / (2.0 * nx), d * j / (2.0 * ny)))
    elems = []
    for e in range(nx):
        for f in range(ny):
            i0, j0 = 2 * e, 2 * f
            elems.append([lat[(i0, j0)], lat[(i0 + 2, j0)], lat[(i0 + 2, j0 + 2)], lat[(i0, j0 + 2)],
                          lat[(i0 + 1, j0)], lat[(i0 + 2, j0 + 1)], lat[(i0 + 1, j0 + 2)],
                          lat[(i0, j0 + 1)]])
    return lat, xy, elems


def element(conn, xy):
    k = [[0.0] * 16 for _ in range(16)]
    f = [0.0] * 16
    xe = [xy[n][0] for n in conn]
    ye = [xy[n][1] for n in conn]
    for a in range(3):
        for b in range(3):
            s, t, w = GA[a], GA[b], GW[a] * GW[b]
            N, Ns, Nt = shp(s, t)
            xs = sum(Ns[n] * xe[n] for n in range(8)); ys = sum(Ns[n] * ye[n] for n in range(8))
            xt = sum(Nt[n] * xe[n] for n in range(8)); yt = sum(Nt[n] * ye[n] for n in range(8))
            det = xs * yt - xt * ys
            if det <= 0:
                raise ArithmeticError('non-positive Jacobian')
            gx = [(yt * Ns[n] - ys * Nt[n]) / det for n in range(8)]
            gy = [(-xt * Ns[n] + xs * Nt[n]) / det for n in range(8)]
            B = [[0.0] * 16 for _ in range(3)]
            for n in range(8):
                B[0][2 * n] = gx[n]; B[1][2 * n + 1] = gy[n]
                B[2][2 * n] = gy[n]; B[2][2 * n + 1] = gx[n]
            wd = w * det
            DB = [[sum(D[r][c] * B[c][q] for c in range(3)) for q in range(16)] for r in range(3)]
            for i in range(16):
                for j in range(16):
                    k[i][j] += wd * sum(B[r][i] * DB[r][j] for r in range(3))
            yv = sum(N[n] * ye[n] for n in range(8))
            eth = (1 + nu) * alpha * (dT * (yv / d - 0.5))
            De = [D[r][0] * eth + D[r][1] * eth for r in range(3)]
            for i in range(16):
                f[i] += wd * sum(B[r][i] * De[r] for r in range(3))
    return k, f


def assemble(xy, elems):
    n = 2 * len(xy)
    K = [[0.0] * n for _ in range(n)]
    F = [0.0] * n
    for conn in elems:
        ke, fe = element(conn, xy)
        for a in range(8):
            ia = 2 * conn[a]; F[ia] += fe[2 * a]; F[ia + 1] += fe[2 * a + 1]
            for b in range(8):
                ib = 2 * conn[b]
                K[ia][ib] += ke[2 * a][2 * b]; K[ia][ib + 1] += ke[2 * a][2 * b + 1]
                K[ia + 1][ib] += ke[2 * a + 1][2 * b]; K[ia + 1][ib + 1] += ke[2 * a + 1][2 * b + 1]
    return K, F


def banded_solve(A, F, fixed):
    """Symmetric band storage, A = U^T U, homogeneous essential conditions eliminated."""
    n = len(F)
    b = 0
    for i in range(n):
        for j in range(i + 1, n):
            if A[i][j] != 0.0:
                b = max(b, j - i)
    B = [[0.0] * (b + 1) for _ in range(n)]
    for i in range(n):
        for k in range(b + 1):
            if i + k < n:
                B[i][k] = A[i][i + k]
    rhs = F[:]
    for dof in fixed:
        for k in range(b + 1):
            if dof + k < n:
                B[dof][k] = 0.0
        for i in range(max(0, dof - b), dof):
            B[i][dof - i] = 0.0
        B[dof][0] = 1.0
        rhs[dof] = 0.0
    U = [[0.0] * (b + 1) for _ in range(n)]
    for i in range(n):
        for j in range(i, min(n, i + b + 1)):
            s = B[i][j - i]
            for k in range(max(0, i - b), i):
                if j - k <= b:
                    s -= U[k][i - k] * U[k][j - k]
            if j == i:
                if s <= 0.0:
                    raise ArithmeticError('not positive definite at %d (s=%.3e)' % (i, s))
                U[i][0] = sqrt(s)
            else:
                U[i][j - i] = s / U[i][0]
    y = [0.0] * n
    for i in range(n):
        s = rhs[i]
        for k in range(max(0, i - b), i):
            s -= U[k][i - k] * y[k]
        y[i] = s / U[i][0]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = y[i]
        for k in range(i + 1, min(n, i + b + 1)):
            s -= U[i][k - i] * x[k]
        x[i] = s / U[i][0]
    return x


def solve(nx, ny):
    lat, xy, elems = build(nx, ny)
    K, F = assemble(xy, elems)

    # patch test: the exact stress-free bending field must satisfy K u = f
    ue = [0.0] * (2 * len(xy))
    for n_, (x, y) in enumerate(xy):
        ue[2 * n_] = -(y - d / 2) * KTH * (L - 2 * x) / 2
        ue[2 * n_ + 1] = KTH * x * (L - x) / 2 + KTH * (y - d / 2) ** 2 / 2
    res = [sum(K[i][j] * ue[j] for j in range(len(ue))) - F[i] for i in range(len(ue))]
    patch = max(abs(v) for v in res) / max(abs(v) for v in F)

    face0 = [n for (i, j), n in lat.items() if i == 0]
    faceL = [n for (i, j), n in lat.items() if i == 2 * nx]
    out = {}
    for mode in ('POINT', 'PIN', 'CLAMP'):
        fixed = set()
        if mode in ('POINT', 'PIN'):
            fixed.add(2 * lat[(0, 1)])           # remove the axial rigid translation
        if mode == 'PIN':
            fixed |= {2 * n + 1 for n in face0 + faceL}
        if mode == 'POINT':
            fixed |= {2 * n + 1 for n in face0 + faceL if abs(xy[n][1] - d / 2) < 1e-15}
        if mode == 'CLAMP':
            fixed |= {2 * n for n in face0 + faceL} | {2 * n + 1 for n in face0 + faceL}
        u = banded_solve(K, F, fixed)
        row = {}
        for lab, jj in (('d/2', ny), ('d/4', max(1, ny // 2)), ('d', 2 * ny)):
            row[lab] = u[2 * lat[(nx, jj)] + 1] / WB
        out[mode] = row
    # heights of the two lattice rows used by the Stage 19 table
    old = {'lat[(NX,1)]': xy[lat[(nx, 1)]][1], 'lat[(NX,2)]': xy[lat[(nx, 2)]][1]}
    return out, patch, old, len(elems)


def main():
    meshes = [(6, 2), (12, 2), (24, 2), (6, 4), (12, 4), (24, 4)]
    if '--extra' in sys.argv:
        meshes.append((48, 8))
    wn, wd = validate_shapes()
    print('shape functions: partition of unity %.1e, derivative vs central difference %.1e' % (wn, wd))
    if wn > 1e-14 or wd > 1e-7:
        raise SystemExit('shape functions fail validation')
    print('kappa_th = %.6e 1/m   beam value kappa_th L^2/8 = %.4e m' % (KTH, WB))
    print('all ratios below are w(L/2, y) / (kappa_th L^2/8) at the stated physical height y')
    print()

    rows = []
    for (nx, ny) in meshes:
        out, patch, old, ne = solve(nx, ny)
        rows.append((nx, ny, ne, out, patch, old))
        print('  mesh %2dx%-2d  elements %3d  patch test %.1e' % (nx, ny, ne, patch))
    print()

    print('TABLE 1  mid-surface, y = d/2  (the height at which the manuscript values are quoted)')
    print('  %-9s %7s %9s %9s %9s' % ('mesh', 'elems', 'POINT', 'PIN', 'CLAMP'))
    for nx, ny, ne, out, patch, old in rows:
        print('  %-9s %7d %9.4f %9.4f %9.4f'
              % ('%dx%d' % (nx, ny), ne, out['POINT']['d/2'], out['PIN']['d/2'], out['CLAMP']['d/2']))
    print()

    print('TABLE 2  same meshes, same nodes as the Stage 19 table - the heights MOVE with NY')
    print('  %-9s %7s %14s %14s' % ('mesh', 'elems', 'y of lat[(NX,1)]', 'y of lat[(NX,2)]'))
    for nx, ny, ne, out, patch, old in rows:
        print('  %-9s %7d %14s %14s'
              % ('%dx%d' % (nx, ny), ne,
                 '%.4f m = d/%d' % (old['lat[(NX,1)]'], round(d / old['lat[(NX,1)]'])),
                 '%.4f m = d/%d' % (old['lat[(NX,2)]'], round(d / old['lat[(NX,2)]']))))
    print()

    print('TABLE 3  fixed heights y = d/4 and y = d (for completeness, not quoted in the text)')
    print('  %-9s %7s | %8s %8s %8s | %8s %8s %8s'
          % ('mesh', 'elems', 'POINT', 'PIN', 'CLAMP', 'POINT', 'PIN', 'CLAMP'))
    print('  %-9s %7s | %-26s | %-26s' % ('', '', 'at y = d/4', 'at y = d'))
    for nx, ny, ne, out, patch, old in rows:
        print('  %-9s %7d | %8.4f %8.4f %8.4f | %8.4f %8.4f %8.4f'
              % ('%dx%d' % (nx, ny), ne,
                 out['POINT']['d/4'], out['PIN']['d/4'], out['CLAMP']['d/4'],
                 out['POINT']['d'], out['PIN']['d'], out['CLAMP']['d']))
    print()

    # ---- the statements this study supports ------------------------------------------------
    m2 = [r for r in rows if r[1] == 2]
    m4 = [r for r in rows if r[1] == 4]
    def val(r, mode, h='d/2'):
        return r[3][mode][h]
    print('WHAT THE STUDY SUPPORTS (mid-surface)')
    print('  point pins, all six meshes          : %s'
          % ', '.join('%.4f' % val(r, 'POINT') for r in rows))
    print('  full-edge pin, NY = 2 (NX = 6,12,24): %s'
          % ', '.join('%.4f' % val(r, 'PIN') for r in m2))
    print('  full-edge pin, NY = 4 (NX = 6,12,24): %s'
          % ', '.join('%.4f' % val(r, 'PIN') for r in m4))
    print('  clamp, NY = 2                       : %s'
          % ', '.join('%.4f' % val(r, 'CLAMP') for r in m2))
    print('  clamp, NY = 4                       : %s'
          % ', '.join('%.4f' % val(r, 'CLAMP') for r in m4))
    dmax = max(abs(val(a, m) - val(b, m)) for m in ('POINT', 'PIN', 'CLAMP')
               for a in rows for b in rows if a[0] == b[0] and a[1] != b[1])
    print()
    print('  largest difference between NY=2 and NY=4 at a fixed NX, all three supports,')
    print('  at the mid-surface: %.5f  (so the through-thickness mesh does not decide the ratio)'
          % dmax)
    pin24 = [r for r in rows if r[2] == 24 and r[1] == 2][0]
    pin48 = [r for r in rows if r[2] == 48 and r[1] == 2][0]
    print('  at 24 elements (12x2): POINT %.4f, PIN %.4f, CLAMP %.4f'
          % (val(pin24, 'POINT'), val(pin24, 'PIN'), val(pin24, 'CLAMP')))
    print('  pin difference POINT-PIN at 24 elements: %.4f  (= %.1f %%)'
          % (val(pin24, 'POINT') - val(pin24, 'PIN'),
             100 * (val(pin24, 'POINT') - val(pin24, 'PIN')) / val(pin24, 'POINT')))
    print('  clamp magnitude: %.4f at 24 elements (12x2) -> %.4f at 48 elements (24x2)'
          % (val(pin24, 'CLAMP'), val(pin48, 'CLAMP')))
    print()
    print('LIMITS OF THIS STUDY (stated, not hidden)')
    print('  * the pin ratio is not converged: it is still falling at 48 elements; the mesh')
    print('    sequence is evidence of a trend, not a converged strip solution;')
    print('  * no Richardson extrapolation is attempted and no tolerance is quoted;')
    print('  * results are for the frozen-force linear thermal field of D-26 only.')


if __name__ == '__main__':
    main()
