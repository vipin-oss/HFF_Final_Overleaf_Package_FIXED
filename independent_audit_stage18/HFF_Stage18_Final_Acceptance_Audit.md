# HFF Stage 18 — Final Independent Acceptance Audit

**Target (frozen):** `5741d36d6f0f9911bfe3f338fb5f77ba94e1d7ea` — "Stage 18: repair of the verification
defects (suite v4, 44-case campaign)", parent `a61837ef4b93ec9fe74802ef161f6f3cc1c586b6`.
Branch `arena/c875f9b3-hff-final-overleaf-package-fix`; local HEAD = remote head at freeze time.
**Auditor role:** independent. Nothing in the audited commit was modified: every mutation and every
test run was executed in a fresh isolated copy, and the only addition to the repository is this
directory (`independent_audit_stage18/`).
**Audit date:** 2026-10-20 (UTC). **Environment:** Python 3.11.2, no TeX engine, no PDF rasteriser.

---

## 0. Headline

| Question | Answer |
|---|---|
| Is `5741d36` the commit that was audited? | **Yes** — local HEAD = `origin` head = `5741d36`, tree clean at freeze; all runs from `git archive HEAD`. |
| Do the claimed suite and campaign figures reproduce? | **Yes.** Suite v4: **144/144 pass, exit 0**. Campaign: **44/44 executed, 44 detected, 36 substantive + 8 fingerprint-only, 0 escaped, 0 invalid, 0 anchor-missing** (re-executed by the auditor). |
| Is every printed number independently reproduced? | **Yes**, to the precision at which it is printed (θ̄, `T̄_cr`, `M_b`, `w_max`, `Γ_p` both definitions, stresses, `w_p`, `N_θ`, `N_cr`, `μL`, the `M_b = 2` ceiling). Identities are exact; see §3. |
| Is the verification layer sufficient? | **No.** Five adversarial mutations survive suite v4 (§7.2): a pointwise pressure datum, an adopting "we choose … rather than" gauge, a double thermal datum in a `tab:bcs` *Condition* column, a prose double datum, and a stale magnitude written `pct`. The "no constraint can be smuggled in beside its explanation" property is therefore **not established**. |
| Fingerprints: do they prove correctness? | **No.** They detect change only. `--update-fingerprints` does not short-circuit the run (F1 fix verified), and corrupting `eq:wmax` then regenerating still fails **four substantive** checks. 76 fingerprints are stable on a clean tree (regeneration reproduces the file byte-for-byte). |
| Package integrity | **Verified by replay**: 78 members, 78/78 member digests, member order, CRC, fixed timestamps; rebuilt archive hash `d7b80365…` (833 423 B) is **byte-identical** to the shipped archive. |
| Build/render (I-13, I-15) | **NOT EXECUTED** — no TeX engine. The shipped `main.pdf` (embedded `CreationDate D:20261019055805Z`) predates the Stage 18 sources. |
| **Final decision** | **CONDITIONAL ACCEPTANCE** — of the *manuscript content and package*, conditional on C1–C5 in §10. |
| **Production solver** | **NOT READY** (separate verdict, §11). |

---

## 1. Target, environment, and what was executed

### 1.1 Freeze

| Item | Value |
|---|---|
| Commit | `5741d36d6f0f9911bfe3f338fb5f77ba94e1d7ea` |
| Parent | `a61837ef4b93ec9fe74802ef161f6f3cc1c586b6` |
| Local HEAD / `git ls-remote origin` | identical (`5741d36…`) |
| Working tree at freeze | clean; no staged or unstaged change |
| Frozen copy used for every run | `git archive HEAD` extraction (no `.git`, no working-tree artefacts) |
| `regression.py` | `0eeb63a7…` (sha256), 730 lines |
| `mutation_campaign_stage18.py` | `f40b712d…`, 250 lines |
| `stage18_mutation_results.txt` | `c4ea93ef…` |
| `equation_fingerprints.json` | `c599ff48…` (76 entries) |
| `package_manifest.txt` | `9566ff93…` |
| Shipped ZIP | `d7b80365e090a37095248147cc86139ee41ddfd041fac19eddb236c1b2886e94`, 833 423 B |
| Repair report | `audit_stage15/14_stage18_repair_report.md` (`b1f41a4a…`) |

Evidence: `evidence_stage18_final/frozen_commit.txt`.

### 1.2 Toolchain (this matters for what could *not* be done)

`pdflatex`, `latexmk`, `bibtex`, `xelatex`, `lualatex`, `pdftoppm`, `pdftotext`, `gs`, `qpdf`,
`magick` are all **absent**; ImageMagick's `convert` is present but refuses PDF by security policy.
Consequently: no LaTeX rebuild, no page render, no figure inspection, no PDF text extraction. Every
statement below about the PDF is a *provenance* statement derived from the file's bytes, not a
content statement. See `evidence_stage18_final/gates.txt`.

### 1.3 Ran / did not run

| Executed | Result |
|---|---|
| `python3 audit_stage15/regression.py` (fresh extraction of `5741d36`) | **144/144 PASS, rc 0** (`evidence_stage18_final/suite_v4_run.txt`) |
| `python3 audit_stage15/mutation_campaign_stage18.py` (same extraction) | **44/44 detected, rc 0** (`campaign_v4_run.txt`) |
| `independent_audit_stage16/evidence/q8_pin_verification.py` + 6 mesh variants | reproduced; mesh study (`q8_mesh_study.txt`) |
| Auditor numerics `auditor_numerics18.py` (own regex parsers, from ch02/ch09 inputs) | all headline values reproduced (`numerics.txt`) |
| 22 fresh adversarial mutations + 6 non-vacuity probes | §7 (`fresh_mutations.txt`, `nonvacuity.txt`) |
| ZIP replay + manifest/digest/order/CRC verification | §4 (`package_verify.txt`) |
| **NOT executed** | LaTeX build, PDF render, figure visual check (I-15), any coupled solver run, any interface-temperature history |

No value in this report was taken from a fingerprint match, from the repair report's prose, or from
the campaign's own summary. Where a claim is arithmetic, the arithmetic was redone from the inputs
parsed out of `ch02.tex`/`ch09.tex` with independent regular expressions.

---

## 2. Gate A — formulation and mathematical correctness

**Verdict: PASS** (with one author decision left open, RU-01/RU-03, and one definitional decision,
the `Γ_p` headline).

### 2.1 The solid/fluid thermal data assignment is forced and correctly argued (D-32, NEW-01)

`ch08` (§ "Why the solid receives the temperature and not the flux") states, and the text supports,
the following chain, which I checked line by line:

* **Solid.** Dirichlet datum `T_s = T_Γ^{(k)}` on `Γ_if`; prescribed flux `+k_s∇T_s·\bn_out = q''`
  on the heated outer face `Γ_h^0`; zero flux on `Γ_end` and the remaining faces (B6–B8). A
  Dirichlet surface plus flux data on the complement is coercive: **unique** solution, and the flux
  through `Γ_if` is an *output*.
* **Fluid.** Neumann datum `k_f∇T_f·\bn = q_Γ^{(k)}` on `Γ_if`, inflow datum `T_f = T_in` at B1,
  do-nothing outflow at B2. One Dirichlet surface (inflow) ⇒ **unique**; the level is anchored by
  `T_in`, not free.
* **Why the alternative fails.** Handing the *conjugate flux* to the solid instead would make the
  solid problem pure-Neumann: the constant is in the kernel (level free) **and** a solution exists
  only if the boundary fluxes sum to zero — true at the fixed point, generally false at an
  intermediate iterate. Both statements are correct as written ("doubly inadmissible"), and the
  compatibility argument is spelled out rather than asserted.
* **No invented datum.** The model's level is set by `T_in` through `eq:iftemp`; no reference
  temperature is introduced. `T_ref` does cancel from every equation that uses it (`θ = T_s − T_ref`,
  `θ_f = T_f − T_ref`, and `N_θ` depend on differences only), so the claim "the level is inherited,
  not invented" is sound **for `T_ref`**. It is *not* sound for `T_in`: `T_in` is a Dirichlet datum,
  and the quoted `θ̄ = 32.3 K` is measured from the inlet bulk temperature, i.e. the baseline
  implicitly adopts `T_ref = T_in`. `ch06:111` says both "enter the solution exclusively through
  property values", which is wrong for `T_in` (see A5 in §2.6).

### 2.2 No pressure gauge, and the argument for it is correct

`ch08:90–93` argues that `b(\cdot,1)` does not annihilate constants for the adopted traction/outflow
pair, so `p` is determined absolutely; the natural outflow condition leaves `p → 0` across that
section; adding `∫_{Γ_out} p ds = 0` as an extra equation would over-determine the system and, with
a Lagrange multiplier, inject a spurious outlet mass source (D-25 → D-30). I checked the weak form:
the constant is indeed *not* in the kernel of `b(·,1)` when the traction is prescribed on the
outflow, and the reported `p̄ = 84 Pa` follows from the datum, not from a normalisation. `ch05:63`
("no gauge freedom … nothing is imposed to fix it") is consistent with `ch08`.

### 2.3 Boundary-condition set (`tab:bcs`) — consistent and complete

All nine rows parsed and checked as a *set*, not as strings: each field on `Γ_if` receives exactly
one thermal datum (B5 = conjugate pair `eq:ifkin`–`eq:ifflux`); the solid's flux datum sits on
`Γ_h^0` (B6, regime N) with the `T_s = T_h` alternative on the same surface (B9, regime D); the
ends are pinned, not clamped (B7 / A9: `d_2 = 0`, `⟨d_1⟩ = 0`, zero applied moment, zero flux); the
remaining faces are traction- and flux-free (B8). The mechanical and thermal data do not conflict at
any row. The prose statement of step 1 matches the table.

### 2.4 `Γ_p`: definitions, locations, and what remains undecided

`eq:gammap` defines `Γ_p = w_max/w_p` with `w_max` from the *beam–column* solution (amplified) and
`w_p` from the *linear* uniform-load formula — a deliberately **mixed** ratio — and gives the
like-for-like alternative `w_max/w_p(N_θ^c)` in which the same compressive force amplifies both
responses. Both are computed independently (§3.4) and both are labelled at every presentation site:

| Site | Content | Label |
|---|---|---|
| `ch04:307` | `eq:gammap`, closed form `48κ_th D_s/(5p̄L²)·w_max/w_max^lin` | "mixed" stated in the following sentence |
| `ch04:318` | like-for-like `w_p(N_θ^c) = 1.27×10⁻⁷ m`, `1.73×10³` | "mixed" vs "like-for-like" explained |
| `ch06:83` | `Γ_p = w_max/w_p`, `eq:gammap` + `M_b` | definition pointer |
| `ch06:101` | A-5 `Γ_p ≥ 5` evaluated on the **like-for-like** ratio | explicit |
| `ch07:41` | table row `w_max/w_p (mixed)`, `2.4×10³` | "(mixed)" + eqref |
| `ch07:87` | prose: mixed `2.4×10³`, like-for-like `1.73×10³` | both |
| `appendix:49` | nomenclature: `w_max/w_p`, `eqref{eq:gammap}`, "mixed and like-for-like presentations" | both (Stage 18 repair) |
| `appendix:94–96` | A8 arithmetic for both ratios | both |
| `appendix:136` | table `Γ_p` row: mixed `2.4×10³`, like-for-like `1.73×10³` | both |

**Open (author decision):** which definition is the *headline* `Γ_p`. The audit does not choose one;
both are now correct and labelled, and A-5 is explicitly evaluated on the conservative (like-for-like)
value. This is the RU-01-adjacent `Γ_p` item and stays open.

### 2.5 `T̄_cr`, `M_b`, and `eq:wmax` as *mathematical* objects

* `eq:tcr`: `T̄_cr = π²d²/(12α(1+ν)L²)`, derived from `|N_θ| = N_cr = π²D_s/L²` with wide-plate
  `D_s`. I re-derived it: `N_θ = Edαθ̄/(1−ν)` ⇒ `θ̄_cr = N_cr(1−ν)/(Edα) = π²d²/(12α(1+ν)L²)`
  **exactly**; the printed 12 and the identity agree to 2.5×10⁻⁶ relative.
* `M_b = T̄_cr/θ̄` with the stated requirement `M_b ≥ 2`; the `M_b = 2` rule is used consistently to
  bound `θ̄ ≤ T̄_cr/2` and `q''`.
* `eq:wmax`: `w_max = κ_th L²/8` with `κ_th = (1+ν)αq''/k_s`, and the parabola
  `w(x) = κ_th x(L−x)/2`. Checked three ways: mid-span value `1/(4·2) = 1/8` (exact), the second
  derivative is `−κ_th` with `w(0)=w(L)=0` (residual 1.5×10⁻⁷ against κ_th = 1.4), and it is the
  `μL → 0` limit of the beam–column solution `eq:beamcolsol` (ratio − 1 = 1.1×10⁻⁸).

### 2.6 Gate A defects found

**A5 (new, LOW–MEDIUM).** `ch06:111` — "Only temperature differences appear in the equations, so
`T_ref` and `T_in` enter the solution exclusively through property values" — is true for `T_ref` but
**false for `T_in`**. `T_in` is the inflow Dirichlet datum of B1 (and the anchor of the interface
level via `eq:iftemp`); it enters the solution as a *temperature difference* `T_in − T_ref`, not as a
property value. The quoted `θ̄`, `N_θ` and `M_b` are measured from the inlet bulk temperature, so
**the baseline implicitly sets `T_ref = T_in`** (a stress-free strip at the coolant inlet
temperature). That convention is nowhere stated, and `ch02:47` lists both as "to be fixed at data
freeze" with the same "temperature differences only enter" note. No printed number changes under the
adopted convention, but an independent solver that takes `T_in` and `T_ref` separately will obtain a
different `N_θ` (the offset `T_in − T_ref` adds directly to `θ̄`). This is a formulation-clarity
defect and a data-freeze item, not an arithmetic error.

Otherwise, none. Two presentational repairs were made in Stage 18 and are confirmed: the θ̄ cell now prints its
components at a precision that matches their recomputation (`30.0+1.55+0.72 ≈ 32.3`), and the
nomenclature entry for `Γ_p` is no longer a bare "thermal-to-pressure deflection ratio".

*Retraction of a Stage 19 working note (recorded for honesty):* an early suspicion that `q''/h` was
inconsistent with `θ̄` came from using a wrong hydraulic diameter in my own check
(`D_h = 2H_0 = 1 mm`, not `6 mm`). With `D_h = 2H_0`, `h = Nu_{H1}k_f/D_h = 3231 W m⁻²K⁻¹` and
`q''/h = 1.548 K`, which is exactly what the manuscript prints. There is **no** numerical defect;
the only issue was display rounding ("1.6" for 1.548 at one decimal), repaired in Stage 18.

---

## 3. Gate B (part 1) — independent numerical reproduction

All values below were recomputed from inputs parsed out of `ch02.tex` and `ch09.tex`
(`q'' = 5000 W m⁻²`, `d = 3 mm`, `H_0 = 0.5 mm`, `L = 9 mm`, `U = 0.05 m s⁻¹`,
`E = 3.6 GPa`, `ν = 0.4`, `α = 5×10⁻⁵ K⁻¹`, `k_s = 0.25`, `k_f = 0.6`, `ρ = 1000`,
`μ = 1×10⁻³`, `c_p = 4180`, `Nu_{H1} = 5.385`). Evidence: `evidence_stage18_final/numerics.txt`,
produced by `auditor_numerics18.py`, which uses its own parsers and does not import the suite.

### 3.1 Temperature level and buckling chain

| Quantity | Independent | Printed | Site | Rel. dev. |
|---|---|---|---|---|
| `ΔT_t/2 = q''d/(2k_s)` | 30.0000 K | 30.0 | ch07:34 | 0 |
| `q''/h`, `h = Nu_{H1}k_f/(2H_0)` | 1.547509 K | 1.55 | ch07:34 | 1.6×10⁻³ |
| `ΔT_b/2 = q''L/(2ρUH_0c_p)` | 0.717703 K | 0.72 | ch07:34 | 3.2×10⁻³ |
| **`θ̄`** | **32.26521 K** | 32.3 | ch07:34, A5 | 1.1×10⁻³ |
| `T̄_cr = π²d²/(12α(1+ν)L²)` | 117.4953 K | 117.5 | ch07:39, A5 | 4.0×10⁻⁵ |
| same, 3 s.f. cell | 117.4953 K | 117 | ch07:38 | 4.2×10⁻³ |
| `M_b = T̄_cr/θ̄` | **3.641547** | 3.64 | ch07:39, A5 | 4.3×10⁻⁴ |
| `θ̄` at `M_b = 2` | 58.7477 K | 58.8 | ch07:100 | 8.9×10⁻⁴ |
| `q''` at `M_b = 2` | 9103.9 W m⁻² | 9.1×10³ | ch07:101 | 4.3×10⁻⁴ |

`M_b ≥ 2` is **met** by the computed margin (3.6415), and the two derived consequences follow from
the same `T̄_cr`: `117.4953/2 = 58.7477 K` and `5000 × 58.7477/32.2652 = 9103.9 W m⁻²`.

*Display-rounding note.* The exact ceiling is 58.7477 K, which rounds to **58.7** K at one decimal;
`ch07:100` prints **58.8** K, which is the rounding of the *already-rounded* `117.5/2 = 58.75`. The
two routes differ by 0.05 K (one unit in the last printed place). No conclusion depends on it, and
the suite's 0.5 % tolerance accepts it, but the cell is inconsistent with full-precision rounding.

The `T̄_cr` versus thickness catalogue is reproduced: `{13.06, 29.37, 52.22, 81.59, 117.50}` K for
`d = {1, 1.5, 2, 2.5, 3}` mm against the printed `{13, 29, 52, 82, 117}` K (max deviation 0.5 K,
which is the printed rounding).

### 3.2 Deflection, amplification, stress

| Quantity | Independent | Printed | Site |
|---|---|---|---|
| `κ_th = (1+ν)αq''/k_s` | 1.4000 m⁻¹ | 1.4 | ch07:30 |
| `w_max^lin = κ_thL²/8` | 1.57500×10⁻⁴ m | 1.575×10⁻⁴ / 1.58×10⁻⁴ | A3 / ch07:30 |
| `w_max^lin/H_0` | 0.31500 | 0.315 | ch07:32 |
| beam–column `w_max` (frozen force, `μL = 1.6463`) | 2.18858×10⁻⁴ m | 2.19×10⁻⁴ | ch07:31, ch04 |
| `w_max/H_0` | 0.437716 | 0.438 | ch07:31 |
| amplification | 1.38957 | 1.39 | ch04:314 |
| `σ_bend = 6|M_mid|/d²` | 4.2369 MPa | 4.2 | ch07:42 |
| `σ_memb = −Eαθ̄/(1−ν)` | 9.6796 MPa | 9.6 | ch07:43 |
| `σ_max` (worst fibre) | 13.916 MPa | 13.9 | ch07:95, 97 |
| stress fraction | 0.1546 | 0.15 | ch07:44 |
| self-consistent `w_max` | 2.13988×10⁻⁴ m (0.4280 H₀) | 2.14×10⁻⁴ (0.428 H₀) | ch07:31 |
| force relaxation, first iterate | 6.1446 % | 6.1 % | ch04:238 |
| force relaxation, self-consistent | 5.882 % | 5.9 % | ch04:241, appendix:107 |
| circular-arc / exact | 1.1456 | "10–20 % above" | ch04 |

The beam–column solution satisfies the printed ODE to 7.3×10⁻¹² and all four BCs to <10⁻¹²; the
identity `κ_geo = κ_th sec(μL/2)` holds to 10⁻¹², and `(κ_geo+κ_th)/(κ_geo−κ_th) = cot²(μL/4)` to
10⁻¹⁰. The `μ → 0` limit of `eq:beamcolsol` is `κ_thL²/8` (ratio − 1 = 1.1×10⁻⁸), which is what
`eq:wmax` claims. The parabola's `w'' = −κ_th` is verified to 3.2×10⁻⁷ absolute (2.3×10⁻⁷ relative)
by central differences — round-off level for a quadratic.

### 3.3 `N_θ`, `N_cr`, `μL`, `w_p`

`N_θ = −Eαθ̄d/(1−ν) = −2.90387×10⁴` N m⁻¹ (printed 2.91×10⁴); `N_cr = π²D_s/L² = 1.057458×10⁵`
N m⁻¹ (printed 1.057×10⁵); `μL = L√(−N_θ/D_s) = 1.64629` (printed 1.65);
`p̄ = 12μU(L+L_o)/H_0²` with the datum consistent split `= 84 Pa`; `w_p = 5p̄L⁴/(384D_s) =
9.1875×10⁻⁸ m` (printed 9.2×10⁻⁸ m); `w_p(N_θ^c) = 1.2678×10⁻⁷ m` (printed 1.27×10⁻⁷ m).

### 3.4 `Γ_p` both definitions

* mixed: `w_max/w_p = 2.18858×10⁻⁴/9.1875×10⁻⁸ = 2382.1` → printed `2.4×10³` (7.4×10⁻³ relative,
  i.e. 2 s.f.).
* like-for-like: `w_max/w_p(N_θ^c) = 1726.3` → printed `1.73×10³` (2.2×10⁻³).
* linear-limit closed form `48κ_thD_s/(5p̄L²) = 1714.3` → printed `1.7×10³`.
* consistency: `48κ_thD_s/(5p̄L²) × 1.38957 = 2382.1` ✓ (the amplification does exactly what the
  text says it does).
* A-5 (`Γ_p ≥ 5`): met on **both** definitions by two orders of magnitude.

### 3.5 Q8 evidence (D-26 / NEW-05) and the limits of a single mesh

The shipped verification script reproduces the committed acceptance values at its own mesh
(`NX, NY = 12, 2`, 24 Q8 elements):

| Case | mid-surface ratio to `κL²/8` | top-face ratio | committed value |
|---|---|---|---|
| POINT (ideal point pins) | 1.0025 | 1.0000 | 1.0025 / 1.0000 |
| PIN (full-edge pin) | 1.0006 | 0.9981 | 1.0006 / 0.9981 |
| CLAMP | −0.0408 | −0.0450 | −0.0408 / −0.0450 |

Exact-field residual `max|Ku_ex − f| = 1.4×10⁻⁹` (scale 1.9×10⁴); shape-derivative check 4.5×10⁻¹¹.
Auditor mesh study (only `NX, NY` changed):

| mesh | elements | POINT mid/top | PIN mid/top | CLAMP mid/top |
|---|---|---|---|---|
| 6×2 | 12 | 1.0025 / 1.0000 | 1.0024 / 0.9999 | −0.0761 / −0.0803 |
| 12×2 | 24 | 1.0025 / 1.0000 | 1.0006 / 0.9981 | −0.0408 / −0.0450 |
| 24×2 | 48 | 1.0025 / 1.0000 | 1.0004 / 0.9979 | −0.0245 / −0.0288 |
| 6×4 | 24 | 1.0056 / 1.0025 | 1.0054 / 1.0023 | −0.0564 / −0.0617 |
| 12×4 | 48 | 1.0056 / 1.0025 | 1.0037 / 1.0006 | −0.0284 / −0.0336 |
| 24×4 | 96 | 1.0056 / 1.0025 | 1.0036 / 1.0005 | −0.0159 / −0.0211 |

Reading, and its limits:

1. The POINT ratio is **mesh-independent in `NX`** and only `NY`-dependent (1.0000 at `NY = 2`,
   1.0025 at `NY = 4`) — a through-thickness/element-type effect, not an axial discretisation error.
2. The PIN ratio converges monotonically toward 1 with axial refinement (1.0024 → 1.0006 → 1.0004);
   the quoted 0.2 % end-effect is therefore a property of the **discretisation** at the shipped mesh
   (24 elements), not a converged continuum value.
3. The CLAMP suppression is strongly mesh-dependent (−0.076 → −0.041 → −0.025 at `NY = 2`, and
   −0.056 → −0.028 → −0.016 at `NY = 4`): its magnitude decreases under every refinement, so the
   quoted band "−0.02 to −0.06" is a *coarse-mesh* band. The manuscript uses it only to establish that the clamped
   alternative is not the measured configuration, which survives; it does **not** establish a
   converged clamp penalty, and the text should not be read as doing so.
4. The evidence is a single model (curvature-only energy, one element through the thickness at
   `NY = 2`), not a study; a converged statement would need a proper `h`/`p` study with a
   thickness-resolved model. This is a **limitation**, not a numerical error in what is claimed.

---

## 4. Gate C — package, build, and visual integrity

### 4.1 ZIP replay (executed, twice, from independent clean extractions)

| Check | Result |
|---|---|
| Members | **78** (matches `package_manifest.txt`) |
| Archive SHA-256 | `d7b80365e090a37095248147cc86139ee41ddfd041fac19eddb236c1b2886e94` — recomputed from the file, equal to the manifest line |
| Size | 833 423 B (manifest equal) |
| Member digests | **78/78** recomputed and equal to the manifest |
| Member order | identical to the manifest order |
| CRC of every member | **ok** (`ZipFile.testzip()` → `None`) |
| Timestamps | all `2026-10-19 00:00:00` (normalised; reproducible) |
| Compression | deflate (8) for all members |
| Byte-code / stray artefacts | none (`__pycache__` excluded) |
| Members differing from the committed tree | **none** |
| Rebuild determinism | two rebuilds from two copies → the **same** SHA-256 as the shipped archive |

Evidence: `evidence_stage18_final/package_verify.txt`.

### 4.2 Build and visual gates — NOT EXECUTED

The shipped `main.pdf` carries `/Producer (pdfTeX-1.40.29)` and
`/CreationDate (D:20261019055805Z)` (2026-10-19 05:58:05 UTC). The Stage 18 sources were committed
2026-10-20 07:00 UTC. **The PDF therefore cannot contain the Stage 18 corrections.** No engine is
available, so no rebuild and no render were attempted; no page count, layout, float placement,
overfull box, or figure appearance is audited here. Section 7 of the suite reports mtimes ("REPORTED,
NOT ASSERTED"); mtimes in a fresh checkout are set by extraction and cannot establish provenance —
this is exactly why I-13 remains **OPEN**. I-15 (figure collision / visual check) also remains
**OPEN**: the figure files are brace- and label-structured, and nothing in the suite tests how they
render.

---

## 5. Actual 144-check outcome

Command, from a fresh `git archive HEAD` extraction:
`python3 audit_stage15/regression.py` → **`ALL 144 CHECKS PASSED`**, exit 0 (`suite_v4_run.txt`,
log `1d7f38ea…`-independent; the auditor's own log is `suite_v4_run.txt`).

Composition (static classification of the source, 106 `check()` call sites expanding to 144
assertions through loops):

| Layer | Share | Notes |
|---|---|---|
| Structural (files, braces, labels, citations, macros, register row count) | ~10 | fails loudly on a missing required file (verified, §7.4) |
| Claim/presence or claim/absence on source strings | ~70 | e.g. `w = +d_2`, no `1/(2d)`, no reversed bow, `Γ_p` labels |
| Semantic prose tests (sentence-scoped) | ~12 | gauge counterfactual, BC double datum, stale end-effect scan, figure-verification claims |
| Numeric recomputation from parsed inputs | **29 call sites** | θ̄, `T̄_cr`, catalogue, `M_b`, ceilings, `w_max`, stresses, `Γ_p` both, `w_p`, `N_θ`, `N_cr`, amplification, arc estimate, strain envelope |
| Fingerprint assertions | 3 | equation changed / register row changed / nothing removed |

**Discrepancies found in the claim of 144:** none — the count is exactly 144 and every one passes.
Note, however, that a passing count is not evidence of strength: §7 shows four mutations that this
144-check suite does not detect.

**Non-vacuity probes** (`nonvacuity.txt`, 6/6 caught, 0 vacuous): deleting `chapters/ch07.tex` stops
the run with an explicit "required source files missing" failure; blanking the θ̄ cell, removing the
`12` from `eq:tcr`, giving `eq:wmax` a non-integer denominator, adding a bare pressure normalisation
to `ch04`, and changing a stress quoted in `ch07` prose are each caught by a check that names the
edited object.

---

## 6. Actual 44-case campaign outcome

Command: `python3 audit_stage15/mutation_campaign_stage18.py` → exit 0 (`campaign_v4_run.txt`).

| Result | Count |
|---|---|
| Cases attempted | **44** |
| Detected (suite exits non-zero with the declared intended check among the failures) | **44** |
| … substantive | **36** |
| … **fingerprint-only** (`A1 A2 A3 A10 A11 A18 A22 B7`) | **8** |
| Escaped | 0 |
| Invalid (wrong failure, crash, syntax error) | 0 |
| Anchor not applied | 0 |
| Baseline (clean copy) | exit 0, 144/144 |

I checked the 44-case list against the intended assertions case by case: each `detected` line names
the check that targets its defect (not a syntax error, not a missing file, not an unrelated string
check). The eight fingerprint-only detections are exactly the cases whose only observable effect is
"an expression changed" — they are correctly reported as *not* evidence of substantive detection, and
the campaign does not count them as such.

**Limits of this result:** 44/44 is a *closed-world* result. It shows that the 44 known defects are
caught; it cannot show that the suite catches an unknown defect class. §7 supplies the counterexample
class: four mutations that survive while the campaign reports 44/44.

---

## 7. Fresh adversarial mutations (auditor-authored, fresh isolated copies)

Each case: fresh `git archive` copy → clean baseline run (exit 0) → one edit → run. "Intended
reason" means the failing check name matches the defect class by design, not by accident.

### 7.1 Matrix against suite v4

| # | Mutation | rc | First failing check (intended reason) | Verdict |
|---|---|---|---|---|
| M1 | θ̄ cell 32.3 → 32.4 (components kept) | 1 | `each component printed in the theta-bar cell is its recomputed value at 2 dp` | detected |
| M1b | θ̄ cell formula loses a `1/2`, numbers kept | 1 | `the theta-bar cell quotes its three components and the total` | detected |
| M1c | θ̄ cell formula terms swapped, numbers kept | 1 | same as M1b | detected |
| M2 | ch07 `T̄_cr` 117 → 130 K | 1 | `ch07 table T_cr is the recomputed threshold` | detected |
| M3a | gauge re-inserted as a gerund, beside its explanation | 1 | `a pressure normalisation occurs only as an explicitly rejected counterfactual` | detected |
| M3b | gauge re-inserted with "we impose", same sentence | 1 | same | detected |
| **M3c** | **pointwise gauge `p(\mathbf 0)=0`** | **0** | — | **ESCAPED** |
| M4 | double datum added to row B10 | 1 | `no Gamma_if row prescribes a solid flux datum` (+ double-datum) | detected |
| M5 | end-effect 0.2 % → 1.5 % | 1 | `no stale end-effect percentage survives in the 22 scanned files` | detected |
| M6 | gauge re-inserted after a correct rejection sentence | 1 | gauge counterfactual check | detected |
| **M6b** | gauge with "choose … rather than" wording | **0** | — | **ESCAPED** |
| **M7** | **double datum in a `Condition` column whose `Boundary` cell omits `Γ_if`** | **0** | — | **ESCAPED** |
| **M8** | **prose double datum without the "on surface" clause** | **0** | — | **ESCAPED** |
| M9 | stale magnitude as "percentage points" | 1 | stale end-effect check | detected |
| **M10** | **stale magnitude written "2 pct"** | **0** | — | **ESCAPED** |
| M11 | `Γ_p` label removed from the dictionary (`appendix:136`) | 1 | `dictionary labels Gamma_p` | detected |
| M12 | `Γ_p` label removed from the ch07 prose site | 1 | `ch07 prose gives both ratios` | detected |
| M13 | `w_max = κL²/(8(1−ν))` + `--update-fingerprints` | 1 | `eq:wmax states a parabola and a w_max with explicit constants` | detected |
| M13b | parabola `/(2(1+ν))` + regen | 1 | same | detected |
| M14 | `eq:tcr` coefficient 12 → 14, printed values kept, regen | 1 | `ch07 table T_cr is the recomputed threshold` (+catalogue) | detected |
| M14b | coefficient 12 → 14 **and** every printed `M_b`/catalogue value updated consistently, regen | 1 | `appendix M_b matches` (5 fails) | detected |
| M15 | `q''` 5.0 → 6.0 kW m⁻² with θ̄ updated consistently | 1 | `appendix N_theta matches` (37 fails) | detected |

`M14b` was **not** a fully consistent rewrite (some `3.64` occurrences were left behind); it is
reported as detected but must not be described as "fully consistent yet still caught". `M15` *was*
consistent in the θ̄ cell and still fails, because the upstream input change propagates into 37
downstream assertions — this is the desired "validate against inputs, not against internal
consistency" behaviour.

For reference, the same seven cases against the **predating** suite v3 (`a61837e`) all returned
exit 0: `M1, M2, M3a, M3b, M3c, M4, M5` escaped v3 entirely (`mutation_matrix_v3_v4.txt`). Stage 18
therefore fixed real blindness; the four v4 escapes above are the *residue* of that class.

### 7.2 The five surviving mutations (reported, not hidden)

| ID | What survives | Why it survives | Severity |
|---|---|---|---|
| **M3c** | a pressure datum imposed at a single interior point (`p(\mathbf 0) = 0`) | the gauge test matches integral/mean forms only; a pointwise datum is the same normalisation in another notation | **MEDIUM** — exactly the smuggling class the check claims to close |
| **M6b** | "we choose the extra equation `∫` p dx = 0 for the level **rather than** rely on the outflow condition" | the rejecting token `rather than` satisfies the rejection test while the finite adopting vocabulary (`impose/fix/set/enforce/adopt/normalise/require`) misses `choose` | **MEDIUM** — adopting language with a rejection token is not discriminated |
| **M7** | `T_s` Dirichlet **and** `∂_nT_s` Neumann in the `Condition` column of a row whose `Boundary` cell omits `Γ_if` | rows are selected by the string `Γ_if` in the *Boundary* column before the double-datum test runs | **MEDIUM** — the BC-set check is not row-independent |
| **M8** | prose giving the solid both an interface temperature and an interface heat flux, without the "on `Γ_if`" clause | the prose test requires the `<datum> … on <surface>` pattern | **MEDIUM** — same class as M7 |
| **M10** | a stale end-effect magnitude written "2 pct" | the stale-magnitude regex accepts `per cent`/`%` but not `pct` | **LOW** — a spelling variant of a defect that *is* detected when spelled normally |

Consequence for the acceptance question: the claim that "no constraint can be smuggled in beside its
own explanation" (the reason G1/G2 were introduced) is **not yet true for all notations**. Four of the
five escapes (M3c, M6b, M7/M8) are precisely the *same* smuggling pattern in another notation. The
suite must not be described as closing that class.

### 7.3 Fingerprint behaviour under adversarial use

* `eq:wmax` denominator 8 → 16 **with** `--update-fingerprints`: `WROTE … (76 entries)`, the
  comparison is reported as `SKIPPED`, and the run still exits **1** with four substantive failures
  (`the parabola's mid-span value …`, both `the eq:wmax denominator reproduces the printed linear
  w_max …` checks, and `eq:wmax is the mu -> 0 limit of eq:beamcolsol`). The F1 loophole is closed.
* A display-equation edit **without** regeneration: exit 1 on `no display equation has changed` only
  — a fingerprint-only detection, correctly not counted as substantive.
* A legitimate new display equation: exit 0 in both modes; `76 → 77` keys with
  `new fingerprint keys (deliberate additions)` reported as INFO. An addition is therefore not a
  failure, which is the right semantics.
* Cosmetic defect: generated keys render as `eq:eq:auditprobe` (the `eq:` prefix is added to a label
  that already contains it). Harmless for comparison, confusing for a human reader.

### 7.4 Non-vacuity probes (do the checks read the file?)

Six probes, all caught, none vacuous; details in `nonvacuity.txt`. Notably, deleting a required
chapter file stops the suite with `the suite cannot read … NO check below this line was executed`
rather than silently passing, and each semantic check fails with the *edited object* in its detail
string.

---

## 8. Fingerprint mechanism review

**What the 76 fingerprints are:** `sha256(canonical body)[:16]` for 44 display equations (keyed by
`\label`) and 32 register rows (keyed by `D-nn`), stored in `equation_fingerprints.json`. On a clean
tree they are stable: regeneration reproduces the file **byte-for-byte** (76 entries), and the
manuscript edits of Stage 18 changed no display equation and no register row. Verified by
`--update-fingerprints` in a clean copy followed by a byte comparison.

**What they prove:** that a canonicalised expression or register row is *unchanged* since the file was
written. That is a tamper-evidence mechanism for accidental edits, and it is effective for that.

**What they cannot prove:** that an expression is *correct*. A wrong expression with a regenerated
fingerprint passes the fingerprint layer by construction. Correctness rests entirely on the
substantive layer, which is why F1 mattered: regeneration used to `sys.exit(0)` before any substantive
check ran. It no longer does.

**Residual weaknesses, stated plainly:**

1. **Regeneration is unguarded by design.** There is no second reviewer, no signature, no
   append-only log: anyone who edits an equation and runs `--update-fingerprints` gets a green
   fingerprint layer. The only defence is the substantive layer, which §7 shows is incomplete for
   four classes. The docstring ("change detection, never a correctness proof") is accurate, and the
   suite prints a `WARNING` block on regeneration, but nothing prevents the workflow.
2. **A parse-breaking edit is caught only by a format check.** `eq:wmax` with a non-integer
   denominator fails `eq:wmax states a parabola and a w_max with explicit constants` and the
   downstream numerical checks are *skipped* rather than failed (`if _w1 and _wq:`). Detection is
   real, but the reported reason is weaker than "the value is wrong". A guard that fails when a
   parsed quantity is unavailable would be stronger than a silent `if`.
3. **Key namespace.** Duplicate `eq:` prefixes (cosmetic, above).
4. **Coverage is per display equation, not per claim.** Prose that quotes a derived quantity is
   protected only where a dedicated check exists (`_allowed_stress` is the one systematic instance).

---

## 9. Remaining defects, limitations, and author decisions

| ID | Item | Status | Consequence |
|---|---|---|---|
| **A1** | Five suite blind spots (M3c, M6b, M7, M8, M10) | **OPEN** | the anti-smuggling property is not established; fix before citing the suite as closure |
| **A5** | `ch06:111` says `T_in` enters "exclusively through property values"; it is a Dirichlet datum, and the baseline implicitly assumes `T_ref = T_in` | **OPEN (prose + data freeze)** | an independent solver taking `T_in ≠ T_ref` shifts `θ̄` and hence `N_θ`, `M_b` |
| **A2** | Unparseable expression ⇒ downstream numerical checks skipped, not failed | **OPEN (design)** | detection reason is a format mismatch, not a wrong value |
| **A3** | Regeneration cannot be prevented by the suite itself | **OPEN (design)** | fingerprints are tamper-evident, not tamper-proof |
| **A4** | Fingerprint key `eq:eq:*` duplication | **OPEN (cosmetic)** | readability only |
| **I-13** | `main.pdf` predates the Stage 18 sources; no TeX engine here | **OPEN** | PDF must be rebuilt (4 passes) before circulation; page count/layout unaudited |
| **I-15** | figure render/collision check | **OPEN** | figure appearance unaudited |
| **RU-01** | casing clearance / contact interpretation / vented-vs-sealed cavity | **OPEN-AD** | the 0.4377 H₀ bow towards the casing is load-bearing; no standoff is stated in the source |
| **RU-03** | mid-span passage height `1.4377 H₀` (or mirror `0.5623 H₀`) | **OPEN-AD** | not stated in the manuscript; coupled to RU-01 |
| **D-?** | heater mounting / heated-face interpretation | **OPEN-AD** | the `q''` datum is applied on `Γ_h^0`; the physical mounting is an assumption |
| **D-?** | contact law | **OPEN-AD** | no contact model; the strip is assumed free to bow |
| **RU** | headline definition of `Γ_p` (mixed vs like-for-like) | **OPEN-AD** | both are correct and labelled; A-5 uses the conservative one |
| **L1** | Q8 evidence: single 24-element mesh, curvature-only energy, thickness dependence | **LIMITATION** | the 0.2 % end-effect and the −0.02…−0.06 clamp band are mesh quantities; not converged |
| **L2** | coupled solid–fluid iteration: convergence not demonstrated | **LIMITATION** | see §10; well-posedness ≠ convergence, correctly stated in `ch08` |
| **L3** | `T_in`, `T_ref` values still "to be fixed at data freeze" in `ch02` | **DATA GAP** | no printed number depends on `T_ref`; `T_in` sets the level but not any quoted magnitude |

The convergence limitation paragraph in `ch08` was read in full and is correctly scoped: it states
that well-posedness of the four subproblems establishes uniqueness at every iterate and **nothing**
about convergence of the alternation; it explicitly declines to give a contraction or energy-stability
proof; it defines the thermal monitor
`‖ΔT_Γ^{(k)}‖ = max_{Γ_if} |T_Γ^{(k)} − T_Γ^{(k−1)}|` (kelvin, on the current mesh, reported per run)
and says the tolerance will be fixed *by* the mesh-refinement and iteration study, asserting **no**
numerical tolerance; and it names stagnation of `‖ΔT_Γ^{(k)}‖` as a trigger for the monolithic path.
The discretised stopping criterion `‖δ^{(k+1)} − δ^{(k)}‖_∞ ≤ 10⁻⁶ w_max` is a *criterion*, not a
proof, and the text does not present it as one.

---

## 10. Final decision

**CONDITIONAL ACCEPTANCE** of commit `5741d36` as a *manuscript and package* submission.

Justification, on independent evidence only:

* **Gate A (formulation): pass.** The thermal data assignment is forced and correctly argued; no
  gauge is required and none is imposed; the BC set is consistent; `T̄_cr`, `M_b`, `eq:wmax` and both
  `Γ_p` definitions are mathematically correct.
* **Gate B (numerics): pass for every printed quantity.** Every headline number reproduces to its
  printed precision from independently parsed inputs; the identities are exact; the Q8 acceptance
  values reproduce. **But Gate B fails on the verification claim:** four adversarial mutations
  survive a suite that reports 144/144 and a campaign that reports 44/44.
* **Gate C (package): pass by replay.** Archive hash, 78 members, 78/78 digests, order, CRC, fixed
  timestamps, and byte-identical rebuild. **Build/render: NOT EXECUTED.**

Conditions (all must hold before the submission is called accepted without qualification):

* **C1.** Close the five suite blind spots (M3c pointwise/other-notation normalisation; M6b adopting
  verbs that are not in the vocabulary; row- and sentence-level double thermal data independent of the
  `Boundary` cell and of the "on surface" phrase; `pct`/`percentage-point` spellings). Until then, the suite must not be described as
  preventing constraint smuggling. (An auditor prototype that closes all four is supplied,
  *not applied*, under `proposed_repair_not_applied/`; it reproduces 148/148 on the current sources
  and turns all four escapes into intended-reason failures. It is a proposal for the next
  implementation cycle, not part of this audit.)
* **C2.** Rebuild `main.pdf` with the four LaTeX passes and confirm the page count (I-13), then
  perform the figure/collision visual check (I-15). Until then the shipped PDF is stale by
  construction.
* **C3.** State, or explicitly defer with an owner, the author decisions: RU-01 (vented/contact/free
  casing and clearance), RU-03 (`1.4377 H₀`), heater mounting, contact law, and the headline `Γ_p`
  definition.
* **C4.** Do not cite the Q8 end-effect magnitude or the clamp band as converged values (L1).
* **C5.** Keep the convergence statement as written (no proof, tolerance undemonstrated) and do not
  upgrade the monolithic path from "fallback" to "validated".
* **C6.** State the reference-temperature convention (the quoted `θ̄` assumes `T_ref = T_in`) and
  correct the `ch06:111` clause about `T_in` entering "through property values" (A5).

What this audit did **not** find: any wrong printed number, any sign error, any unit error, any
inconsistent BC set, any missing reference, any label/reference breakage, any package inconsistency,
or any fingerprint drift.

---

## 11. Production-solver readiness (separate verdict)

**NOT READY.** Nothing in this audit demonstrates a working coupled solver:

* no solid, fluid, thermoelastic or mesh-extension solve was executed (no mesh generator, no linear
  algebra, no nonlinear loop available here);
* no interface-temperature history, no residual history, no convergence rate, no stagnation
  evidence, and no monolithic path was exercised;
* the stopping criteria are *specified* but no tolerance is demonstrated (correctly so, per `ch08`);
* RU-01, RU-03, the heater mounting and the contact law are unresolved and change the geometry and
  the load path;
* the Q8 evidence is a single-mesh verification, not a solver validation; the benchmark hierarchy in
  `ch09` is a specification of acceptance tests, not a record of runs.

The verification package is suitable for *pre-coding* work and for manuscript review; it is not
evidence of solver readiness.

---

## 12. Reproducible evidence

All paths are relative to this directory; all runs used `git archive HEAD` extractions of
`5741d36` in `/tmp`, never the repository itself.

| File | Content |
|---|---|
| `evidence_stage18_final/frozen_commit.txt` | commit/parent/remote, tree status, environment, sha256 of every audited file |
| `evidence_stage18_final/suite_v4_run.txt` | full 144-check log, exit 0 |
| `evidence_stage18_final/campaign_v4_run.txt` | 44-case campaign log, exit 0, raw evidence tail |
| `evidence_stage18_final/mutation_matrix_v3_v4.txt` | the seven shared mutations under v3 and v4 |
| `evidence_stage18_final/fresh_mutations.txt` | 22 auditor mutations (M1…M15, incl. escapes) |
| `evidence_stage18_final/fingerprints.txt` | F1 reproduction, fingerprint-only edit, legitimate addition |
| `evidence_stage18_final/numerics.txt` | independent recomputation of every headline number |
| `evidence_stage18_final/q8_mesh_study.txt` | Q8 acceptance values + 6-mesh study |
| `evidence_stage18_final/package_verify.txt` | archive hash, members, digests, order, CRC, determinism |
| `evidence_stage18_final/nonvacuity.txt` | 6 non-vacuity probes, 0 vacuous |
| `evidence_stage18_final/gates.txt` | toolchain inventory, PDF provenance, convergence claims, ledger statuses |
| `evidence_stage18_final/nonvacuity_probe.py` | the probe script itself (re-runnable) |
| `proposed_repair_not_applied/` | auditor prototype closing the four blind spots — **not applied**, not part of `5741d36` |

Commands:

```
git archive HEAD | tar -x -C /tmp/frozen
cd /tmp/frozen && python3 audit_stage15/regression.py                  # 144/144, rc 0
cd /tmp/frozen && python3 audit_stage15/mutation_campaign_stage18.py   # 44/44, rc 0
python3 evidence_stage18_final/nonvacuity_probe.py /tmp/frozen         # 6/6 caught
cd /tmp/clean && python3 audit_stage15/build_package.py                # reproduces d7b80365…
```

**Publication:** this report is committed and pushed to
`arena/c875f9b3-hff-final-overleaf-package-fix`; `git log -1 -- independent_audit_stage18/`
identifies the audit commit, and `git rev-parse origin/arena/c875f9b3-hff-final-overleaf-package-fix`
after the push identifies the published head. The audit commit adds only this directory — the
audited commit `5741d36` is unchanged.
