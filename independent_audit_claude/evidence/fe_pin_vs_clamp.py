#!/usr/bin/env python3
"""Independent 2-D plane-strain thermoelastic FE test (Q8 serendipity, 3x3 Gauss) of the HFF strip.
Question: does 'd1=d2=0 on the full end edge' (source B7 / V_s) reproduce the pinned-pinned bowing kappa L^2/8
that the beam model assumes, or does it behave as a clamp?  Inputs = printed design point; theta_bar = 0
(pure through-thickness gradient, so no membrane force and the beam benchmark is exactly kappa_th L^2/8)."""
import numpy as np, sympy as sp, scipy.sparse as sps, scipy.sparse.linalg as spl, sys

E, nu, al, ks, q = 3.6e9, 0.4, 5e-5, 0.25, 5e3
L, d = 3e-2, 3e-3
Gam = q / ks                                    # dT/dy = q''/ks = 2e4 K/m (heated face on top, y up)
kth = (1 + nu) * al * Gam                       # 1.4 1/m
w_beam = kth * L**2 / 8                         # 1.575e-4 m (pinned-pinned, zero membrane force)
lam = E * nu / ((1 + nu) * (1 - 2 * nu)); mu = E / (2 * (1 + nu))
D = np.array([[lam + 2 * mu, lam, 0], [lam, lam + 2 * mu, 0], [0, 0, mu]])

xi, eta = sp.symbols('xi eta')
Ns = [-(1-xi)*(1-eta)*(1+xi+eta)/4, -(1+xi)*(1-eta)*(1-xi+eta)/4, -(1+xi)*(1+eta)*(1-xi-eta)/4, -(1-xi)*(1+eta)*(1+xi-eta)/4,
      (1-xi**2)*(1-eta)/2, (1+xi)*(1-eta**2)/2, (1-xi**2)*(1+eta)/2, (1-xi)*(1-eta**2)/2]
Nf = sp.lambdify((xi, eta), Ns, 'numpy')
dNx = sp.lambdify((xi, eta), [sp.diff(n, xi) for n in Ns], 'numpy')
dNe = sp.lambdify((xi, eta), [sp.diff(n, eta) for n in Ns], 'numpy')
g = np.sqrt(3 / 5); gp = [(-g, 5 / 9), (0.0, 8 / 9), (g, 5 / 9)]
loc = [(-1, -1), (1, -1), (1, 1), (-1, 1), (0, -1), (1, 0), (0, 1), (-1, 0)]   # node natural coords

def run(nx, ny, bc):
    # lattice of (2nx+1)x(2ny+1) points, centre points of elements (both indices odd) are not nodes
    idx = {}; coords = []
    for j in range(2 * ny + 1):
        for i in range(2 * nx + 1):
            if i % 2 == 1 and j % 2 == 1: continue
            idx[(i, j)] = len(coords); coords.append((i * L / (2 * nx), -d / 2 + j * d / (2 * ny)))
    coords = np.array(coords); nn = len(coords); ndof = 2 * nn
    hx, hy = L / nx, d / ny
    rows, cols, vals = [], [], []; F = np.zeros(ndof)
    for ey in range(ny):
        for ex in range(nx):
            conn = [idx[(2 * ex + 1 + a, 2 * ey + 1 + b)] for a, b in loc]
            Ke = np.zeros((16, 16)); fe = np.zeros(16)
            ycen = -d / 2 + (ey + 0.5) * hy
            for gx, wx in gp:
                for gy, wy in gp:
                    dx = np.array(dNx(gx, gy)) * 2 / hx; dy = np.array(dNe(gx, gy)) * 2 / hy
                    B = np.zeros((3, 16)); B[0, 0::2] = dx; B[1, 1::2] = dy; B[2, 0::2] = dy; B[2, 1::2] = dx
                    J = hx * hy / 4 * wx * wy
                    Ke += B.T @ D @ B * J
                    Nv = np.array(Nf(gx, gy)); yy = ycen + gy * hy / 2
                    th = Gam * yy                                    # theta_bar = 0
                    fe += B.T @ (D @ (np.array([1, 1, 0]) * (1 + nu) * al * th)) * J
            dofs = np.array([[2 * c, 2 * c + 1] for c in conn]).ravel()
            for a in range(16):
                for b in range(16): rows.append(dofs[a]); cols.append(dofs[b]); vals.append(Ke[a, b])
                F[dofs[a]] += fe[a]
    K = sps.csr_matrix((vals, (rows, cols)), shape=(ndof, ndof))
    fixed = {}
    mid = ny                                   # j index of the mid-plane (2*ny lattice rows -> mid row = ny)
    for j in range(2 * ny + 1):
        for i in (0, 2 * nx):
            n = idx[(i, j)]
            if bc == 'clamp_full_edge':   fixed[2 * n] = 0; fixed[2 * n + 1] = 0           # B7 / V_s as written
            if bc == 'roller_edge_uy':    fixed[2 * n + 1] = 0                            # v=0 on edge, rotation free
    nL, nR = idx[(0, mid)], idx[(2 * nx, mid)]
    if bc in ('pin_midpoint', 'roller_edge_uy'):
        fixed[2 * nL] = 0; fixed[2 * nR] = 0
        if bc == 'pin_midpoint': fixed[2 * nL + 1] = 0; fixed[2 * nR + 1] = 0
    free = np.array([k for k in range(ndof) if k not in fixed])
    u = np.zeros(ndof); u[free] = spl.spsolve(K[free][:, free].tocsc(), F[free])
    nm = idx[(nx, mid)]; nb = idx[(nx, 0)]; nt = idx[(nx, 2 * ny)]
    return u[2 * nm + 1], u[2 * nb + 1], u[2 * nt + 1], K[free][:, free].shape[0]

print("beam benchmark (pinned-pinned, zero membrane force): kappa_th = %.6f 1/m, w_max = kappa L^2/8 = %.6e m" % (kth, w_beam))
print("%-18s %-9s %-14s %-14s %-12s" % ("end condition", "mesh", "w_mid-plane", "w_interface", "ratio to beam"))
for (nx, ny) in ((60, 4), (90, 6)):
    for bc in ('pin_midpoint', 'roller_edge_uy', 'clamp_full_edge'):
        wm, wb, wt, nd = run(nx, ny, bc)
        print("%-18s %3dx%-5d %+.6e   %+.6e   %.4f   (interface = bottom/fluid face; +y = away from channel)" % (bc, nx, ny, wm, wb, wm / w_beam))
