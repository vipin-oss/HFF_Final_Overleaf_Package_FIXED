"""Finite-element primitives: P2-P1 Taylor--Hood triangles and structured meshes.

The discretisation follows the specification of the manuscript:

* continuous piecewise-quadratic velocity and temperature (six-node triangles),
* continuous piecewise-linear pressure (three-node triangles) - the Taylor--Hood pair,
* a body-fitted mesh of the fluid domain whose upper boundary is the deformed
  interface,
* a conforming solid block whose interface nodes coincide, node for node, with those of
  the fluid, and share their global degree-of-freedom numbers.  Temperature and
  tractions are therefore transferred between the two subdomains without projection or
  mortar operators, which is the condition under which the interface boundary terms of
  the weak form cancel exactly (Section 5.2 of the manuscript).

Global P2 numbering
-------------------
A mesh numbers its vertices ``0 .. n_vertices-1`` and its mid-side nodes
``mid_offset + edge_id``.  For a coupled fluid/solid pair, ``bind_shared`` sets
``mid_offset = n_global_vertices`` for both meshes, so that a shared interface edge -
which carries the same edge id in both meshes - also carries the same global midpoint
number.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import scipy.sparse as sp

# ---------------------------------------------------------------------------
#  Degree-5, seven-point quadrature on the reference triangle (Dunavant)
# ---------------------------------------------------------------------------
_A = 0.059715871789770
_B = 0.470142064105115
_C = 0.797426985353087
_D = 0.101286507323456
_QP = np.array([
    [1 / 3, 1 / 3],
    [_A, _B], [_B, _A], [_B, _B],
    [_C, _D], [_D, _C], [_D, _D],
])
# The published weights are normalised to unity over a reference triangle of area one;
# the reference triangle used here has area 1/2, hence the factor 1/2.
_QW = 0.5 * np.array([0.225,
                      0.132394152788506, 0.132394152788506, 0.132394152788506,
                      0.125939180544827, 0.125939180544827, 0.125939180544827])
assert abs(_QW.sum() - 0.5) < 1e-14


def p2_basis(r: np.ndarray, s: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """P2 shape functions and reference-coordinate gradients.

    Returns ``N`` of shape ``(nqp, 6)`` and ``dN`` of shape ``(nqp, 6, 2)``.
    Vertex order 0,1,2; mid-side order 3=(0,1), 4=(1,2), 5=(2,0).
    """
    r = np.atleast_1d(r).astype(float)
    s = np.atleast_1d(s).astype(float)
    L = np.stack([1.0 - r - s, r, s], axis=1)
    G = np.array([[-1.0, -1.0], [1.0, 0.0], [0.0, 1.0]])
    N = np.empty((L.shape[0], 6))
    dN = np.empty((L.shape[0], 6, 2))
    for i in range(3):
        N[:, i] = L[:, i] * (2.0 * L[:, i] - 1.0)
        dN[:, i, :] = (4.0 * L[:, i] - 1.0)[:, None] * G[i][None, :]
    for k, (i, j) in enumerate([(0, 1), (1, 2), (2, 0)]):
        N[:, 3 + k] = 4.0 * L[:, i] * L[:, j]
        dN[:, 3 + k, :] = 4.0 * (L[:, i][:, None] * G[j][None, :]
                                 + L[:, j][:, None] * G[i][None, :])
    return N, dN


def p1_basis(r: np.ndarray, s: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """P1 shape functions and reference-coordinate gradients (nqp, 3) / (nqp, 3, 2)."""
    r = np.atleast_1d(r).astype(float)
    s = np.atleast_1d(s).astype(float)
    N = np.stack([1.0 - r - s, r, s], axis=1)
    dN = np.broadcast_to(np.array([[-1.0, -1.0], [1.0, 0.0], [0.0, 1.0]]),
                         (N.shape[0], 3, 2)).copy()
    return N, dN


# ---------------------------------------------------------------------------
#  Meshes
# ---------------------------------------------------------------------------
@dataclass
class TriMesh:
    """Structured triangular mesh with P2/P1 connectivity and boundary tags."""

    xy: np.ndarray                 # (n_vertices, 2)
    tris: np.ndarray               # (n_elem, 3), counter-clockwise
    edges: np.ndarray              # (n_elem, 3) global edge ids for (0,1),(1,2),(2,0)
    edge_nodes: np.ndarray         # (n_edges, 2) vertex pairs, ascending global ids
    boundary: Dict[str, np.ndarray] = field(default_factory=dict)
    n_vertices: int = 0
    n_edges: int = 0
    mid_offset: Optional[int] = None
    grid: Optional[np.ndarray] = None      # structured (ny+1, nx+1) vertex map

    def __post_init__(self):
        if self.mid_offset is None:
            self.mid_offset = int(self.n_vertices)

    @property
    def n_p2(self) -> int:
        return int(self.mid_offset) + int(self.n_edges)

    @property
    def p2(self) -> np.ndarray:
        return np.hstack([self.tris, self.mid_offset + self.edges])

    def p2_coordinates(self, n_global: Optional[int] = None) -> np.ndarray:
        """Coordinates of the P2 nodes in the global numbering (zeros elsewhere)."""
        n = int(self.n_p2 if n_global is None else n_global)
        out = np.zeros((n, 2))
        out[: self.n_vertices] = self.xy
        mid = 0.5 * (self.xy[self.edge_nodes[:, 0]] + self.xy[self.edge_nodes[:, 1]])
        out[int(self.mid_offset):int(self.mid_offset) + self.n_edges] = mid
        return out

    def p2_boundary_dofs(self, tag: str) -> np.ndarray:
        pairs = self.boundary.get(tag, np.zeros((0, 2), dtype=int))
        if pairs.size == 0:
            return np.zeros(0, dtype=int)
        lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(self.edge_nodes, axis=1))}
        verts = np.unique(pairs.ravel())
        mids = np.array([self.mid_offset + lut[tuple(sorted((int(a), int(b))))]
                         for a, b in pairs], dtype=int)
        return np.unique(np.concatenate([verts, mids]))

    def p2_boundary_coordinates(self, tag: str) -> Tuple[np.ndarray, np.ndarray]:
        """Return (dofs, coordinates) of the P2 nodes lying on a boundary tag."""
        pairs = self.boundary.get(tag, np.zeros((0, 2), dtype=int))
        if pairs.size == 0:
            return np.zeros(0, dtype=int), np.zeros((0, 2))
        lut = {tuple(sorted(p)): k for k, p in enumerate(np.sort(self.edge_nodes, axis=1))}
        verts = np.unique(pairs.ravel())
        dofs = list(verts)
        coords = [self.xy[verts]]
        mids = np.array([self.mid_offset + lut[tuple(sorted((int(a), int(b))))]
                         for a, b in pairs], dtype=int)
        # de-duplicate midpoints (interior corners of a tag appear once)
        if mids.size:
            _, first = np.unique(mids, return_index=True)
            keep = np.sort(first)
            mids = mids[keep]
            coords.append(0.5 * (self.xy[pairs[keep, 0]] + self.xy[pairs[keep, 1]]))
        dofs = np.concatenate([np.asarray(dofs, dtype=int)] +
                              ([mids] if mids.size else []))
        coords = np.vstack(coords)
        _, first = np.unique(dofs, return_index=True)
        keep = np.sort(first)
        return dofs[keep], coords[keep]

    def boundary_vertices(self, tag: str) -> np.ndarray:
        pairs = self.boundary.get(tag, np.zeros((0, 2), dtype=int))
        return np.zeros(0, dtype=int) if pairs.size == 0 else np.unique(pairs.ravel())


def _edge_table(tris: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    pairs = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    key = np.sort(pairs, axis=1)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = np.asarray(inv).ravel()
    ne = tris.shape[0]
    edges = inv.reshape(3, ne).T
    return uniq.astype(int), edges.astype(int)


def _structured_block(nx: int, ny: int, nid: np.ndarray) -> np.ndarray:
    quads = []
    for j in range(ny):
        for i in range(nx):
            quads.append((nid[j, i], nid[j, i + 1], nid[j + 1, i + 1], nid[j + 1, i]))
    tris = []
    for a, b, c, d in quads:
        tris.append((a, b, c))
        tris.append((a, c, d))
    return np.asarray(tris, dtype=int)


def fluid_mesh(cfg: Dict, w_profile: Optional[np.ndarray] = None) -> TriMesh:
    """Body-fitted mesh of the fluid passage.

    ``w_profile`` is the interface deflection on the ``nx_heated + 1`` nodes of the
    heated segment (positive into the passage).  The displacement is blended across the
    passage with ``y = eta*H0 - w(x)*eta**2``, so the lower wall stays fixed and the
    mesh lines follow the deformed interface smoothly.
    """
    g, num = cfg["geometry"], cfg["numerics"]
    H0, L, Le, Lo = g["H0"], g["L"], g["Le"], g["Lo"]
    nxe, nxd, nxo = int(num["nx_entrance"]), int(num["nx_heated"]), int(num["nx_exit"])
    ny = int(num["ny_fluid"])
    cluster = float(num.get("wall_clustering", 1.0))

    xs = np.concatenate([np.linspace(-Le, 0.0, nxe + 1)[:-1],
                         np.linspace(0.0, L, nxd + 1)[:-1],
                         np.linspace(L, L + Lo, nxo + 1)])
    nx = xs.size - 1
    eta = np.linspace(0.0, 1.0, ny + 1)
    if cluster != 1.0:
        eta = 0.5 * (1.0 - np.cos(np.pi * eta))
        eta = eta ** cluster
    if w_profile is None:
        wp = np.zeros(nxd + 1)
    else:
        wp = np.asarray(w_profile, dtype=float)
        if wp.size != nxd + 1:
            raise ValueError(f"w_profile must have nx_heated+1 = {nxd + 1} entries")

    nid = np.arange((ny + 1) * (nx + 1)).reshape(ny + 1, nx + 1)
    xy = np.zeros(((ny + 1) * (nx + 1), 2))
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = xs[i]
            disp = np.interp(x, np.linspace(0.0, L, nxd + 1), wp) if 0.0 <= x <= L else 0.0
            xy[nid[j, i]] = (x, eta[j] * H0 - disp * eta[j] ** 2)

    tris = _structured_block(nx, ny, nid)
    top = [(nid[ny, i], nid[ny, i + 1]) for i in range(nx)]
    bottom = [(nid[0, i], nid[0, i + 1]) for i in range(nx)]
    inlet = [(nid[j, 0], nid[j + 1, 0]) for j in range(ny)]
    outlet = [(nid[j, nx], nid[j + 1, nx]) for j in range(ny)]
    iface = [top[nxe + k] for k in range(nxd)]
    lids = [top[k] for k in range(nxe)] + [top[nxe + nxd + k] for k in range(nxo)]
    boundary = {
        "inlet": np.array(inlet), "outlet": np.array(outlet),
        "wall_bottom": np.array(bottom), "interface": np.array(iface),
        "lids": np.array(lids, dtype=int).reshape(-1, 2) if lids else np.zeros((0, 2), int),
    }
    edge_nodes, edges = _edge_table(tris)
    return TriMesh(xy=xy, tris=tris, edges=edges, edge_nodes=edge_nodes, boundary=boundary,
                   n_vertices=xy.shape[0], n_edges=edge_nodes.shape[0], grid=nid)


def solid_mesh(cfg: Dict, fluid: Optional[TriMesh] = None) -> TriMesh:
    """Structured mesh of the wall strip on the reference configuration.

    With ``fluid`` supplied, the bottom row of the solid re-uses the fluid interface
    vertices and the interface edges re-use the fluid edge numbers; call
    :func:`bind_shared` afterwards to fix the global midpoint numbering.
    """
    g, num = cfg["geometry"], cfg["numerics"]
    H0, L, d = g["H0"], g["L"], g["d"]
    nxd, ny = int(num["nx_heated"]), int(num["ny_solid"])
    xs = np.linspace(0.0, L, nxd + 1)
    ys = H0 + d * np.linspace(0.0, 1.0, ny + 1)

    if fluid is None:
        nid = np.zeros((ny + 1, nxd + 1), dtype=int)
        xy = np.zeros(((ny + 1) * (nxd + 1), 2))
        for j in range(ny + 1):
            for i in range(nxd + 1):
                nid[j, i] = j * (nxd + 1) + i
                xy[nid[j, i]] = (xs[i], ys[j])
        tris = _structured_block(nxd, ny, nid)
        boundary = {
            "interface": np.array([(nid[0, i], nid[0, i + 1]) for i in range(nxd)]),
            "outer": np.array([(nid[ny, i], nid[ny, i + 1]) for i in range(nxd)]),
            "end_left": np.array([(nid[j, 0], nid[j + 1, 0]) for j in range(ny)]),
            "end_right": np.array([(nid[j, nxd], nid[j + 1, nxd]) for j in range(ny)]),
        }
        edge_nodes, edges = _edge_table(tris)
        return TriMesh(xy=xy, tris=tris, edges=edges, edge_nodes=edge_nodes,
                       boundary=boundary, n_vertices=xy.shape[0],
                       n_edges=edge_nodes.shape[0], grid=nid)

    iface_pairs = np.asarray(fluid.boundary["interface"], dtype=int)
    if iface_pairs.shape[0] != nxd:
        raise ValueError("fluid interface discretisation does not match nx_heated")
    iface_verts = np.unique(iface_pairs.ravel())
    iface_verts = iface_verts[np.argsort(fluid.xy[iface_verts, 0])]
    if iface_verts.size != nxd + 1:
        raise ValueError("interface vertex count mismatch")

    base = int(fluid.n_vertices)
    nid = np.zeros((ny + 1, nxd + 1), dtype=int)
    nid[0, :] = iface_verts
    xy_full = np.zeros((base + ny * (nxd + 1), 2))
    xy_full[:base] = fluid.xy
    for j in range(1, ny + 1):
        for i in range(nxd + 1):
            k = base + (j - 1) * (nxd + 1) + i
            nid[j, i] = k
            xy_full[k] = (xs[i], ys[j])

    tris = _structured_block(nxd, ny, nid)
    pairs = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    key = np.sort(pairs, axis=1)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = np.asarray(inv).ravel()
    edges_local = inv.reshape(3, tris.shape[0]).T

    fluid_edge = {tuple(sorted((int(a), int(b)))): k
                  for k, (a, b) in enumerate(np.sort(fluid.edge_nodes, axis=1))}
    edges = np.empty_like(edges_local)
    new_pairs: List[np.ndarray] = []
    remap: Dict[int, int] = {}
    for e in range(tris.shape[0]):
        for k in range(3):
            lid = int(edges_local[e, k])
            a, b = uniq[lid]
            fe = fluid_edge.get(tuple(sorted((int(a), int(b)))))
            if fe is not None:
                edges[e, k] = fe
            else:
                if lid not in remap:
                    remap[lid] = int(fluid.n_edges) + len(new_pairs)
                    new_pairs.append(uniq[lid])
                edges[e, k] = remap[lid]
    edge_nodes = (np.vstack([fluid.edge_nodes, np.asarray(new_pairs, dtype=int)])
                  if new_pairs else fluid.edge_nodes.copy())
    boundary = {
        "interface": iface_pairs,
        "outer": np.array([(nid[ny, i], nid[ny, i + 1]) for i in range(nxd)]),
        "end_left": np.array([(nid[j, 0], nid[j + 1, 0]) for j in range(ny)]),
        "end_right": np.array([(nid[j, nxd], nid[j + 1, nxd]) for j in range(ny)]),
    }
    return TriMesh(xy=xy_full, tris=tris, edges=edges, edge_nodes=edge_nodes,
                   boundary=boundary, n_vertices=xy_full.shape[0],
                   n_edges=edge_nodes.shape[0], grid=nid)


def bind_shared(fluid: TriMesh, solid: TriMesh) -> int:
    """Adopt the joint global P2 numbering; returns the global P2 dimension."""
    if solid.n_vertices <= fluid.n_vertices:
        raise ValueError("solid mesh must contain the fluid vertices (conforming build)")
    fluid.mid_offset = int(solid.n_vertices)
    solid.mid_offset = int(solid.n_vertices)
    n_global = int(solid.n_vertices) + int(solid.n_edges)
    # the two meshes must agree on the interface dofs
    a = np.sort(fluid.p2_boundary_dofs("interface"))
    b = np.sort(solid.p2_boundary_dofs("interface"))
    if not np.array_equal(a, b):
        raise RuntimeError("interface degree-of-freedom mismatch: meshes are not conforming")
    return n_global


# ---------------------------------------------------------------------------
#  Element data
# ---------------------------------------------------------------------------
@dataclass
class ElementData:
    detJ: np.ndarray        # (ne, nqp)
    dNdx: np.ndarray        # (ne, nqp, 6, 2)
    N: np.ndarray           # (nqp, 6) shape functions (shared by all elements)
    w: np.ndarray           # (ne, nqp) detJ * quadrature weight
    centroids: np.ndarray   # (ne, nqp, 2)
    hsize: np.ndarray       # (ne,)
    x: np.ndarray           # (ne, 6, 2) vertex coordinates of the element


def element_data(mesh: TriMesh, xy_p2: Optional[np.ndarray] = None) -> ElementData:
    ne = mesh.tris.shape[0]
    p2 = mesh.p2
    coords_all = mesh.p2_coordinates() if xy_p2 is None else xy_p2
    if coords_all.shape[0] <= int(p2.max()):
        raise ValueError("coordinate array does not cover the P2 numbering")
    coords = coords_all[p2]                       # (ne, 6, 2)
    N, dN = p2_basis(_QP[:, 0], _QP[:, 1])        # (nqp,6), (nqp,6,2)
    J = np.einsum("gak,eab->egbk", dN, coords)    # J[e,g,b,k] = dx_b/dxi_k
    detJ = J[:, :, 0, 0] * J[:, :, 1, 1] - J[:, :, 0, 1] * J[:, :, 1, 0]
    if np.any(detJ <= 0.0):
        bad = int(np.argwhere(detJ <= 0)[0][0])
        raise ValueError(f"non-positive Jacobian in element {bad}: mesh inverted")
    inv = np.empty_like(J)
    inv[:, :, 0, 0] = J[:, :, 1, 1] / detJ
    inv[:, :, 0, 1] = -J[:, :, 0, 1] / detJ
    inv[:, :, 1, 0] = -J[:, :, 1, 0] / detJ
    inv[:, :, 1, 1] = J[:, :, 0, 0] / detJ
    dNdx = np.einsum("gak,egkb->egab", dN, inv)   # (ne,nqp,6,2) = dN_a/dx_b
    w = detJ * _QW[None, :]
    centroids = np.einsum("gb,eba->ega", N, coords)
    area = 0.5 * np.abs((coords[:, 1, 0] - coords[:, 0, 0]) * (coords[:, 2, 1] - coords[:, 0, 1])
                        - (coords[:, 2, 0] - coords[:, 0, 0]) * (coords[:, 1, 1] - coords[:, 0, 1]))
    hsize = np.sqrt(2.0 * area)
    return ElementData(detJ=detJ, dNdx=dNdx, N=N, w=w, centroids=centroids,
                       hsize=hsize, x=coords)


# ---------------------------------------------------------------------------
#  Assembly helpers
# ---------------------------------------------------------------------------
def scatter(rows: np.ndarray, cols: np.ndarray, vals: np.ndarray, n: int) -> sp.csr_matrix:
    return sp.coo_matrix((np.asarray(vals).ravel(),
                          (np.asarray(rows).ravel(), np.asarray(cols).ravel())),
                         shape=(n, n)).tocsr()


def element_matrix(dofs: np.ndarray, Ke: np.ndarray, n: int) -> sp.csr_matrix:
    """Assemble element matrices ``Ke`` of shape (ne, m, m) with dof map (ne, m)."""
    m = dofs.shape[1]
    rows = np.repeat(dofs, m, axis=1)
    cols = np.tile(dofs, (1, m))
    return scatter(rows, cols, Ke, n)


def element_vector(dofs: np.ndarray, fe: np.ndarray, n: int) -> np.ndarray:
    out = np.zeros(n)
    np.add.at(out, np.asarray(dofs).ravel(), np.asarray(fe).ravel())
    return out


def solve_dirichlet(A: sp.spmatrix, b: np.ndarray, dofs: np.ndarray,
                    values: np.ndarray, n_refine: int = 4,
                    return_residual: bool = False):
    """Solve ``A x = b`` with Dirichlet data by elimination, with iterative refinement.

    The saddle-point systems of the flow problem are ill-conditioned (the discrete
    inf-sup constant enters squared), so the sparse LU factorisation is refined by
    residual correction; the achieved relative residual is returned when requested.
    """
    n = A.shape[0]
    dofs = np.asarray(dofs, dtype=int).ravel()
    values = np.asarray(values, dtype=float).ravel()
    fixed = np.zeros(n, dtype=bool)
    fixed[dofs] = True
    free = np.flatnonzero(~fixed)
    x = np.zeros(n)
    x[dofs] = values
    if free.size == 0:
        return (x, 0.0) if return_residual else x
    A = A.tocsr()
    rhs = (b - A @ x)[free]
    A_ff = A[free][:, free].tocsc()
    lu = sp.linalg.splu(A_ff)
    xf = lu.solve(rhs)
    scale = np.linalg.norm(rhs)
    res = np.inf
    for _ in range(n_refine):
        r = rhs - A_ff @ xf
        res = np.linalg.norm(r) / scale if scale > 0 else np.linalg.norm(r)
        if res < 1e-13:
            break
        xf = xf + lu.solve(r)
    x[free] = xf
    if return_residual:
        return x, float(res)
    return x


def integrated_nodal_gradient(mesh: TriMesh, data: ElementData, values: np.ndarray
                              ) -> np.ndarray:
    """Lumped L2 projection of the gradient of a P2 field onto the P2 nodes."""
    grad = np.einsum("egba,eb->ega", data.dNdx, values[mesh.p2])   # (ne,nqp,2)
    w = data.w
    num = np.zeros((mesh.p2.max() + 1, 2))
    den = np.zeros(mesh.p2.max() + 1)
    for a in range(6):
        num[:, a] += 0.0  # placeholder to keep shape explicit
    for a in range(6):
        np.add.at(num, mesh.p2[:, a], np.einsum("eg,egk->ek", w, grad))
        np.add.at(den, mesh.p2[:, a], w.sum(axis=1))
    den[den == 0] = 1.0
    return num / den[:, None]
