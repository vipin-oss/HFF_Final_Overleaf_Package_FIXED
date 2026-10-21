#!/usr/bin/env python3
"""Consistency checks for the manuscript.  Run from anywhere:  python3 code/check_manuscript.py

The checks are cumulative: sections that exist are all checked every time.

  C1  LaTeX log: no undefined citations; undefined references only to labels that are not
      defined yet in the sources (forward references while sections are being written).
  C2  Bibliography: every \\cite key exists in references.bib; every bib entry is cited.
  C3  Sign language: required phrases present, forbidden phrases absent.
  C4  No hand-typed duplicate of a computed number: every value in numbers.tex that appears
      as a literal in the section sources is reported.
  C5  Independent numerical cross-check of the closed forms, using a different code path from
      hff_model.py (finite-difference boundary-value solve, direct 2-D fixed point, direct
      closed-form arithmetic).
  C6  Figures: PDF and EPS exist for every figure used.
  C7  Length: abstract <= 250 words including keywords and classification; manuscript body plus
      280 words per figure and table <= 10000 (Emerald research-article limit).
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_bvp

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEC = ROOT / "sections"
RES = ROOT / "code" / "results"
fails: list[str] = []
notes: list[str] = []


def ok(cond: bool, msg: str) -> None:
    (notes if cond else fails).append(("PASS  " if cond else "FAIL  ") + msg)


def strip_comments(t: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", t)


def sources() -> dict[str, str]:
    d = {"main.tex": (ROOT / "main.tex").read_text()}
    for f in sorted(SEC.glob("*.tex")):
        d[f"sections/{f.name}"] = f.read_text()
    return d


SRC = sources()
BODY = "\n".join(strip_comments(v) for k, v in SRC.items() if k != "main.tex")

# ---------------------------------------------------------------------------------------------
# C1 log
log = (ROOT / "main.log").read_text(errors="ignore") if (ROOT / "main.log").exists() else ""
defined = set(re.findall(r"\\label\{([^}]+)\}", BODY))
undef_refs = set(re.findall(r"Reference `([^']+)' on page \d+ undefined", log))
real_undef = sorted(r for r in undef_refs if r in defined)
fwd = sorted(r for r in undef_refs if r not in defined)
ok(not real_undef, f"C1 no undefined references to existing labels {real_undef}")
if fwd:
    notes.append(f"NOTE  C1 forward references to labels not yet written: {fwd}")
ok("Citation" not in "".join(re.findall(r"LaTeX Warning: Citation[^\n]*undefined", log)),
   "C1 no undefined citations")
ok("Overfull \\hbox" not in log or len(re.findall(r"Overfull \\hbox \((\d+\.\d+)pt", log)) == 0
   or max(float(x) for x in re.findall(r"Overfull \\hbox \((\d+\.\d+)pt", log)) < 20,
   "C1 no badly overfull boxes (< 20 pt)")

# ---------------------------------------------------------------------------------------------
# C2 bibliography
bib = (ROOT / "references.bib").read_text()
bib_keys = re.findall(r"^@\w+\{([^,]+),", bib, re.M)
cited = set()
for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", BODY):
    cited |= {k.strip() for k in m.group(1).split(",")}
ok(cited <= set(bib_keys), f"C2 all cited keys exist in references.bib (missing: {sorted(cited - set(bib_keys))})")
ok(set(bib_keys) <= cited,
   f"C2 every bib entry is cited (uncited: {sorted(set(bib_keys) - cited)})")

# ---------------------------------------------------------------------------------------------
# C3 sign language
t = re.sub(r"\s+", " ", BODY)
must = ["away from the channel", "passage widens", "outer face", "heat supplied to the solid",
        "pin and not a clamp", "no contact between the deformed strip and the casing"]
if "s4_baseline.tex" in " ".join(SRC) and len(SRC.get("sections/s4_baseline.tex", "")) > 200:
    must += ["not a prescribed clearance"]
for ph in must:
    ok(ph.lower() in t.lower(), f"C3 required phrase present: '{ph}'")
forbidden = [
    (r"bows? into the (passage|channel|flow)", "bow direction must be away from the channel"),
    (r"positive into the channel", "w is positive away from the channel"),
    (r"-\s*k_s\s*\\nabla T_s\s*\\!?\\cdot\\!?\s*\\bn_\{\\mathrm\{out\}\}\s*=\s*\\qpp", "old B6 sign (-k_s grad T . n_out = q'')"),
    (r"fluid-side heating|heated from the fluid", "fluid-side heater is not modelled"),
    (r"embedded in a rigid casing", "casing wording must not imply contact"),
    (r"\bconverged strip solution\b", "avoid unqualified convergence claims"),
    (r"2382", "mixed Gamma_p value must not appear as a literal"),
    (r"coupled (solver|simulation|computation)s? (show|demonstrate|confirm)", "no coupled-result claims"),
]
for pat, why in forbidden:
    hits = re.findall(pat, t, re.I)
    ok(not hits, f"C3 forbidden pattern absent: {why}")
# any mention of bowing "into the passage" must be hypothetical: allow only inside the sign-chain sentence
ok(len(re.findall(r"into the passage", t)) <= 1, "C3 'into the passage' appears at most once (hypothetical in sign chain)")

# ---------------------------------------------------------------------------------------------
# C4 literals that duplicate computed numbers
nums_tex = (ROOT / "numbers.tex").read_text() if (ROOT / "numbers.tex").exists() else ""
dups = []
for name, val in re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", nums_tex):
    lit = val.strip()
    if re.fullmatch(r"[-+]?\d+\.\d+", lit) and len(lit.replace(".", "").lstrip("+-0")) >= 3:   # >= 3 significant digits
        if re.search(r"(?<![\w.\\])" + re.escape(lit.lstrip("+-")) + r"(?![\w])", BODY):
            dups.append((name, lit))
ok(not dups, f"C4 no hand-typed duplicates of computed decimals {dups}")

# ---------------------------------------------------------------------------------------------
# C5 independent cross-check (different code path)
B = json.loads((RES / "baseline.json").read_text())
P, R = B["params"], B["baseline"]
E, nu, a, ks, d, L, H0, q = P["E"], P["nu"], P["alpha"], P["ks"], P["d"], P["L"], P["H0"], P["q"]
mu_f, U, kf, cp, rho = P["mu"], P["U"], P["kf"], P["cp"], P["rho"]

ok(abs(q * d / ks - 60.0) < 1e-12, "C5 dT_t = q'' d / k_s = 60 K")
kap = (1 + nu) * a * q / ks
ok(abs(kap - 1.4) < 1e-12 and abs(R["kappa_th"] - kap) < 1e-12, "C5 kappa_th = (1+nu) alpha q''/k_s = 1.4 1/m")
Ds = E * d**3 / (12 * (1 - nu**2))
th = q * d / ks / 2 + q / (5.385 * kf / (2 * H0)) + q * L / (rho * U * H0 * cp) / 2
Nc = E * d * a * th / (1 - nu)
ok(abs(R["theta_bar"] - th) < 1e-9 and abs(R["N_c"] - Nc) < 1e-6, "C5 theta_bar and N_c recomputed directly")
ok(abs(R["N_cr"] - math.pi**2 * Ds / L**2) < 1e-6, "C5 N_cr = pi^2 D_s / L^2")
# (a) finite-difference-free BVP: solve  D w'''' + N w'' = 0, w(0)=w(L)=0, w''(0)=w''(L)=-kappa
def _solve_scaled(m2, load, bc_pp):
    # Scaled BVP on xi in [0,1] for the fourth-order beam-column equation
    # (4th derivative of W) + m2 * (2nd derivative of W) = load, W(0)=W(1)=0, W''(0)=W''(1)=bc_pp.
    # Independent of the closed forms and of hff_model.py (collocation solver; no formulas shared).
    def f(x, y):
        return np.vstack([y[1], y[2], y[3], load - m2 * y[2]])
    def bc(ya, yb):
        return np.array([ya[0], yb[0], ya[2] - bc_pp, yb[2] - bc_pp])
    x = np.linspace(0, 1, 201)
    guess = np.zeros((4, x.size))
    guess[0] = 0.5 * x * (1 - x)
    guess[1] = 0.5 * (1 - 2 * x)
    guess[2] = -0.5 * np.ones_like(x)
    sol = solve_bvp(f, bc, x, guess, tol=1e-10, max_nodes=200000)
    assert sol.success, sol.message
    return sol


def bvp_wmax(Nval):
    sol = _solve_scaled(Nval * L**2 / Ds, 0.0, -1.0)
    class S:  # unscale: w = kappa L^2 W,  w' = kappa L W'
        def __init__(self, sol):
            self.sol = lambda xs: np.vstack([kap * L**2 * sol.sol(np.asarray(xs) / L)[0],
                                             kap * L * sol.sol(np.asarray(xs) / L)[1]])
    return float(kap * L**2 * sol.sol(0.5)[0]), S(sol)


w_bvp, sol = bvp_wmax(Nc)
ok(abs(w_bvp - R["w_frozen"]) / R["w_frozen"] < 1e-6, f"C5 beam-column w_max: BVP {w_bvp:.6e} vs closed form {R['w_frozen']:.6e}")
mu = math.sqrt(Nc / Ds)
w_closed = kap / mu**2 * (1 / math.cos(mu * L / 2) - 1)
ok(abs(w_closed - R["w_frozen"]) / R["w_frozen"] < 1e-9, "C5 w_max = kappa/mu^2 (sec(mu L/2) - 1)")
# (b) self-consistent N via BVP + direct fixed-point with relaxation, independent of hff_model
k_arc = E * d / (2 * (1 - nu**2))
N = Nc
for _ in range(100):
    _, s = bvp_wmax(N)
    xs = np.linspace(0, L, 4001)
    slope = s.sol(xs)[1]
    msq = np.trapezoid(slope**2, xs) / L if hasattr(np, "trapezoid") else np.trapz(slope**2, xs) / L
    Nn = Nc - k_arc * msq
    if abs(Nn - N) < 1e-9 * Nc:
        N = Nn
        break
    N = Nn
w_sc_bvp, _ = bvp_wmax(N)
ok(abs(w_sc_bvp - R["w_sc"]) / R["w_sc"] < 1e-5, f"C5 self-consistent w_max: BVP fixed point {w_sc_bvp:.6e} vs model {R['w_sc']:.6e}")
ok(abs(w_sc_bvp / H0 - 0.428) < 5e-4 and abs(R["w_frozen"] / H0 - 0.4377) < 5e-4, "C5 w/H0 = 0.428 (self-consistent), 0.4377 (frozen)")
ok(R["w_frozen"] > R["w_sc"] > R["w_lin"], "C5 ordering w_lin < w_sc < w_frozen")
ok(abs(R["H_mid_frozen_over_H0"] - (1 + R["w_frozen"] / H0)) < 1e-12, "C5 H_mid/H0 = 1 + w_max/H0 (dimensionally consistent)")
# (c) Gamma_p: closed form and two independent numerical beam solves
pbar = 0.5 * (12 * mu_f * U / H0**2 * (0.02 + 0.03) + 12 * mu_f * U / H0**2 * 0.02)
ok(abs(pbar - 84.0) < 1e-9, "C5 p_bar = 84 Pa")
Gl = 48 * kap * Ds / (5 * pbar * L**2)
ok(abs(Gl - R["Gamma_p_lin"]) < 1e-9 and abs(Gl - 1714.2857142857) < 1e-6, f"C5 Gamma_p^lin = 48 kappa D_s/(5 p L^2) = {Gl:.4f}")
def bvp_load(Nval, p):
    sol = _solve_scaled(Nval * L**2 / Ds, 1.0, 0.0)      # W = w D / (p L^4)
    return float(p * L**4 / Ds * sol.sol(0.5)[0])


wp0, wpN = bvp_load(0.0, pbar), bvp_load(Nc, pbar)
ok(abs(wp0 - 5 * pbar * L**4 / (384 * Ds)) / wp0 < 1e-8, "C5 uniform-load w_p = 5 p L^4/(384 D_s) (BVP)")
ok(abs(wpN - R["w_p_bc"]) / wpN < 1e-6, f"C5 pressure deflection with N_c: BVP {wpN:.5e} vs series {R['w_p_bc']:.5e}")
ok(abs(w_bvp / wpN - R["Gamma_p_bc"]) < 0.5, f"C5 Gamma_p^Nc = {w_bvp / wpN:.1f}")
ok(abs(R["Gamma_p_lin"] / R["Gamma_p_bc"] - 1) < 0.01, "C5 the two like-for-like Gamma_p forms agree within 1 %")
# (d) guard fluxes
for key, target in (("q_w_guard", 5.5e3), ("q_stress_guard", 5.95e3), ("q_buckling_guard", 9.1e3)):
    ok(abs(B["ceilings"][key] - target) / target < 0.01, f"C5 {key} = {B['ceilings'][key]:.0f} W/m^2 (~{target:.0f})")
# (e) Q8
Q = json.loads((RES / "q8_study.json").read_text())
runs = Q["runs"]
ok(max(r["patch"] for r in runs) < 1e-10, "C5 Q8 patch test < 1e-10 on every mesh")
ok(all(abs(r["POINT"]["d/2"] - 1.0) < 1e-4 for r in runs), "C5 Q8 point-pin ratio = 1.0000 on every mesh")
pin = {(r["nx"], r["ny"]): r["PIN"]["d/2"] for r in runs}
ok(abs(pin[(192, 8)] - pin[(96, 8)]) < 1e-6 and abs(pin[(192, 8)] - pin[(192, 4)]) < 1e-5, "C5 Q8 full-edge pin ratio is mesh-converged (<1e-5)")
ok(all(r["CLAMP"]["d/2"] < 0 and abs(r["CLAMP"]["d/2"]) < 0.1 for r in runs), "C5 Q8 clamp ratio small and negative on every mesh")
for k in ("a)",):
    pass

# ---------------------------------------------------------------------------------------------
# C6 figures
figs = re.findall(r"includegraphics(?:\[[^\]]*\])?\{figures/([^}]+)\}", BODY)
for f in figs:
    stem = pathlib.Path(f).stem
    ok((ROOT / "figures" / f"{stem}.pdf").exists() and (ROOT / "figures" / f"{stem}.eps").exists(),
       f"C6 figure {stem}: PDF and EPS present")

# C8 every figure/table label is referenced in the text
labels = re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", BODY)
unref = [l for l in labels if not re.search(r"\\(?:ref|eqref)\{" + re.escape(l) + r"\}", BODY)]
ok(not unref, f"C8 every figure/table label is referenced in the text (unreferenced: {unref})")

# ---------------------------------------------------------------------------------------------
# C7 length
ab = SRC.get("sections/abstract.tex", "")
ab_txt = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})?", " ", strip_comments(ab))
for name, val in re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", nums_tex):
    pass
def expand_macros(txt: str) -> str:
    for name, val in re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", nums_tex):
        txt = txt.replace("\\" + name, val)
    return txt
ab_exp = expand_macros(strip_comments(ab))
ab_exp = re.sub(r"\\(textbf|emph|noindent|begin|end)\{?[a-z]*\}?", " ", ab_exp)
ab_exp = re.sub(r"[\\${}^_~]", " ", ab_exp)
words_ab = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9.,\-/%×]*", ab_exp))
if len(ab) > 200:
    ok(words_ab <= 250, f"C7 abstract + keywords + classification = {words_ab} words (limit 250)")
# Emerald counting: running text plus captions; display maths, table/figure bodies and inline maths are
# excluded; every figure and table counts as 280 words.
def words_of(txt: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z'\-]*", txt))
total_words = 0
for k, v in SRC.items():
    if k == "main.tex":
        continue
    tt = strip_comments(v)
    caps = re.findall(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", tt)
    tt = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", " ", tt, flags=re.S)
    tt = re.sub(r"\\begin\{(equation|align|equation\*|align\*)\}.*?\\end\{\1\}", " ", tt, flags=re.S)
    tt = re.sub(r"\$[^$]*\$", " ", tt)
    tt = re.sub(r"\\(citep|citet|cite|ref|eqref|label)\{[^}]*\}", " ", tt)
    tt = re.sub(r"\\[a-zA-Z]+\*?", " ", tt)
    total_words += words_of(tt) + sum(words_of(re.sub(r"\$[^$]*\$|\\[a-zA-Z]+", " ", c_)) for c_ in caps)
nfig = len(re.findall(r"\\begin\{figure\}", BODY))
ntab = len(re.findall(r"\\begin\{table\}", BODY))
total = total_words + 280 * (nfig + ntab)
ok(total <= 10000, f"C7 length (Emerald counting): {total_words} words + 280 x ({nfig} figures + {ntab} tables) = {total} (limit 10000)")

print("\n".join(notes))
print("\n".join(fails))
print(f"\n{len(notes) - sum(n.startswith('NOTE') for n in notes)} checks passed, {len(fails)} failed")
sys.exit(1 if fails else 0)
