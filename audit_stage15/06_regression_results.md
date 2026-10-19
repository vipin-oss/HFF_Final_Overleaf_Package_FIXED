# Stage 15 — Regression results

**Executable:** `audit_stage15/regression.py` — run from the repository root:
`python3 audit_stage15/regression.py`. Exit status 0 iff every check passes.
**Result at `e8ef0d7`:** `ALL CHECKS PASSED` — 37/37.

Nothing here is asserted from memory; each line is the program's own output.

---

## 1. Structural integrity (7 checks)

| Check | Result |
|---|---|
| Braces balanced, all 16 `.tex` files | PASS (0 unbalanced) |
| `\begin` / `\end` balanced | PASS |
| Labels unique | PASS — 87 labels, 87 distinct, no duplicates |
| No dangling `\ref`/`\eqref` targets | PASS — 0 missing |
| All `\cite` keys resolve in `references.bib` | PASS — 19 cited, 18 entries, 0 missing |
| No uncited bib entries | PASS |
| No undefined shorthand macros | PASS (`\ie` removed — see §7) |

**Note on the cite count.** The static check originally reported the pseudo-key
`"%\nsaleh2025laminar"`. This was a **false positive** from a regex spanning a `%` line
continuation inside `\cite{...,%` at `ch01:64`. In LaTeX the `%` suppresses the newline and the key
list continues correctly, so `\cite{soti2015steady,alsabery2019numerical,saleh2025laminar}` is what
is actually read. The checker now strips comments; the count is 19 cited keys over 18 entries with
one entry (`saleh2025laminar`) cited from four places. **Not a defect.**

## 2. Absence of superseded material (4 checks)

| Pattern | Expected | Result |
|---|---|---|
| `1.8\times10^{-4}` in body text | absent | PASS — 0 hits (survives only in the historical register rows D-11/D-23) |
| `w=-d_2` | absent | PASS — 0 hits |
| "positive into the channel" | absent | PASS — 0 hits |
| `w^{''''}(x)= -\,p` | absent | PASS — 0 hits |

## 3. Convention markers present (7 checks)

`w=+d_2` stated · pressure term `+p` · geometric-stiffness term in `eq:weaks` · `eq:supg` defined ·
`V_g`/`S_s` defined · outlet pressure gauge stated · `Γ_p` defined as `w_max/w_p`. All PASS.

## 4. Numerical reproduction (20 checks)

Every value recomputed from the printed design point (`ch02:40–46`, `ch02:169–180`) **without**
using any manuscript result as an input.

| Quantity | Recomputed | Tolerance | Result |
|---|---|---|---|
| `D_s` | `9.642857143 N·m` | `5×10⁻¹⁰` | PASS |
| `κ_th` | `1.400000000 m⁻¹` | `1×10⁻¹²` | PASS |
| `μL` | `1.646414286` | `5×10⁻¹⁰` | PASS |
| `w_max` | `2.188704727879×10⁻⁴ m` | `5×10⁻¹⁶` | PASS |
| `w_max/H₀` | `0.437740946` | `5×10⁻¹⁰` | PASS |
| `κ_geo` | `2.059208681 m⁻¹` | `5×10⁻¹⁰` | PASS |
| `M_mid` | `−6.356655141 N·m` | `5×10⁻¹⁰` | PASS |
| `σ_bend` | `4.237770 MPa` | `5×10⁻⁷` | PASS |
| fibre strain | `9.888130219613×10⁻⁴` | `5×10⁻¹⁶` | PASS |
| `eq:beamcolsol` vs printed ODE | max residual `1.46×10⁻¹¹` | `<10⁻⁹` | PASS |
| `eq:beamcolsol` vs all four BCs | `0` to machine precision | `<10⁻¹²` | PASS |
| arc term (analytic) | `1.388009729196×10⁻⁴` | `5×10⁻¹⁶` | PASS |
| arc term: analytic vs Simpson | rel. `7.8×10⁻¹⁶` | `<10⁻¹⁰` | PASS |
| relaxation | `6.1446 %` (printed `6.1 %`) | `±0.05` | PASS |
| circular-arc estimate | `1.590×10⁻⁴` (printed `1.6×10⁻⁴`) | `<0.005` | PASS |
| `κ_geo = κ_th sec(μL/2)` | identity to `2×10⁻¹⁶` | `<10⁻¹⁵` | PASS |
| `(κ_geo+κ_th)/(κ_geo−κ_th) = cot²(μL/4)` | `5.247516878033` | `<10⁻¹⁴` | PASS |
| closed form | `1714.285714` | `5×10⁻⁷` | PASS |
| `w_max/w_p` | `2382.263649` | `5×10⁻⁶` | PASS |
| amplification `= w_max/w_lin` | `1.389654` both ways | `<10⁻⁹` | PASS |
| frozen stress column | `13.9188 MPa` (printed `13.9`) | `10⁻³` | PASS |
| self-consistent column | `13.6143 MPa` (printed `13.6`) | `10⁻³` | PASS |

## 5. Cross-document value reuse

Every headline value is used more than once and the uses agree:

| Value | Sites | Chapters |
|---|---|---|
| `w_max = 2.19×10⁻⁴ m` | 7 | ch04, ch07(×2), appendix(×3), register |
| `w_max = 2.14×10⁻⁴ m` (self-consistent) | 4 | ch04, ch07, appendix(×2) |
| `0.438` / `0.428` | 10 / 7 | ch04, ch06, ch07, ch11, appendix |
| `0.315` (linear) | 6 | ch04, ch06, ch07(×2), appendix |
| fibre `9.9×10⁻⁴` | 6 | ch02, ch04, ch07(×2), appendix |
| arc `1.39×10⁻⁴` | 7 | ch02, ch04, ch07(×2), appendix(×2) |
| arc estimate `1.6×10⁻⁴` | 5 | ch04, appendix(×2), register(×2) |
| `6.1 %` / `5.9 %` | 5 / 3 | ch04, appendix |
| `Γ_p = 2.4×10³` | 6 | ch04, ch07(×2), register(×3) |
| `13.9` / `13.6` MPa | 2 / 2 | ch07(×2) / ch07, appendix |

No conflicting value of any of these quantities exists anywhere in the tree.

## 6. What this suite does **not** cover

Stated explicitly so that a green run is not over-read:

1. **It does not compile.** There is no TeX engine (`pdflatex`, `latexmk`, `bibtex`, `biber`,
   `tectonic`, `lualatex`, `xelatex` all absent). Overfull boxes, TikZ geometry errors, float
   placement failures and bibliography-style breakage can only be found by a real build.
2. **It does not render the figure.** The `fig_geometry` changes are verified for brace balance and
   macro existence only. Whether the bow reads correctly at final scale is a visual judgement.
3. **It does not validate physics.** It validates arithmetic and internal consistency. The choice of
   deflection direction is justified in `02_…` §2–§3 from the printed kinematics and the heating
   side; that argument is checked by hand, not by the program.
4. **It does not exercise RU-01.** The casing/clearance question cannot be tested — the parameter
   does not exist in the source.

## 7. Defects this suite caught during Stage 15

Recorded because a regression suite that never fails anything is not evidence:

| Defect | How caught | Fix |
|---|---|---|
| `\ie` used in new register text but **not defined** in this preamble | macro-existence sweep | replaced with `i.e.\ ` |
| `w_{\mathrm{th}}` orphaned by the D-22 redefinition (referenced but no longer defined anywhere) | follow-up grep of the changed block | replaced by `w_{\max}` |
| Register D-11 still asserted the superseded arc value `1.8×10⁻⁴` as current | stale-value sweep across register rows | annotated "superseded by D-23" |
| ch05 thermal rewrite initially contradicted `ch08:108` (Dirichlet datum vs shared unknown) | cross-check of the edited paragraph against the chapter it must agree with | rewritten to the shared-unknown formulation |
| ch08 claimed the reduction "recovers `eq:beamcol`" although `eq:beamcol` is the zero-load problem | re-derivation of the reduction | qualified: `eq:beamcol` with no transverse load, `eq:beam` with no membrane force |
| Formatter precedence bug in the register generator (`"%.9e"%-D_s*(...)`) | generator crash | parenthesised |
