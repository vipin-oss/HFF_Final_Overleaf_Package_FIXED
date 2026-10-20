# Stage 15 — Master issue ledger

**Tree:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Baseline at start of Stage 15:** `9066c3b`
**Correction commit:** `e8ef0d7`
**Register:** Appendix B of the manuscript now carries D-1 … D-25.

Status vocabulary. `CLOSED` — corrected in source at `e8ef0d7` and re-verified against source.
`CLOSED (no action)` — verified correct, no change needed. `OPEN-AD` — author decision required;
work that does not depend on it has proceeded. `OPEN-TECH` — technical blocker not yet resolvable
in this environment. `CARRIED` — accepted limitation, correctly disclosed in the manuscript.

Priority tiers: **RB** = required before coding; **CC** = claim-check (verify, usually no edit);
**RU** = requires author resolution; **B** = blocker.

---

## 1. Required-before-coding (RB)

| ID | Location | Defect | Action taken | Status |
|---|---|---|---|---|
| RB-01 | `ch02:129–133` | `w = −d₂`, "positive into the channel" | `w = +d₂`, "away from the channel" | **CLOSED** |
| RB-02 | `appendix` glossary | same definition, second wording | aligned | **CLOSED** |
| RB-03 | `ch02:27` figure caption | "positive into the channel" | "away from the channel" | **CLOSED** |
| RB-04 | `ch02:131` | "bows into the channel" | "bows away"; `κ=−w''` unchanged | **CLOSED** |
| RB-05 | `ch03:140` | `D_s w'''' = −p` — sole A-consistent equation | `D_s w'''' = +p` | **CLOSED** |
| RB-06 | `ch03:144` | "`w` measured positive into the channel" | "away from" | **CLOSED** |
| RB-07 | `ch04` pin relation | phrase only | aligned; equation unchanged | **CLOSED** |
| RB-08 | `ch04:190–192` | `M` unnamed, equals `−M_phys` | declared sagging-positive, `M = −∫σ_xx y dy` | **CLOSED** |
| RB-09 | `ch04:296` | load "opposing" the bow | "acting in the same sense" | **CLOSED** |
| RB-10 | `ch04:309–310` | "thermally **rather than** hydraulically driven" | ratio of co-directional contributions | **CLOSED** |
| RB-11 | `ch01:10` | "bows toward the interior" | "away from the interior" | **CLOSED** |
| RB-12 | `main.tex:54` | "deflects **into** the flow passage" | "away from"; "widened passage" | **CLOSED** |
| RB-13 | `fig_geometry.tex:18–22, 36–38` | bow drawn 6 pt **into** the fluid; outer face straight; arrow 11 pt against a 6 pt bow | bow reversed, **both faces** displaced by the same amount, flux arrows lifted clear, `w` arrow spans the drawn bow | **CLOSED**; conformal redraw to a real measured profile remains **OPEN-AD** under RU-01 |
| RB-14 | `ch09` V-C2, V-C3 | expectations carried no sign | `κ > 0` (hot face convex); `w_max > 0` away from the channel | **CLOSED** |
| RB-15 | six sites | `½⟨w'²⟩ = 1.8×10⁻⁴` not reproducible | `1.39×10⁻⁴`; recomputed `1.388009729196×10⁻⁴` | **CLOSED** |
| RB-16 | `appendix:130` | row printed `2.4×10³` against a closed form that evaluates to `1.714×10³` (+40.00 %) | row re-expressed as `w_max/w_p` | **CLOSED** |
| RB-17 | `ch04:299–308`, `ch06:83` | sentence named `w_th` of `eq:beamcolbase` but equated `Γ_p` to the *linear* closed form | `Γ_p = w_max/w_p` with the linear limit and the amplification `1.389654` shown explicitly | **CLOSED** |

**RB-15 provenance (closes B-11).** The error is isolated: it is a single transcription, propagating
verbatim through six sites, of the value that a *different* formula would give. The printed
first-iterate relaxation of `6.1 %` is exactly `1.388×10⁻⁴ / e₀ = 6.1446 %`, whereas `1.8×10⁻⁴`
would give `7.968 %`. So `1.8×10⁻⁴` was never a later revision of the model — it is inconsistent
with a number in the same paragraph. B-11 is therefore **CLOSED**, not merely displaced.

## 2. Claim-checks (CC) — verified against source, no edit

| ID | Verdict |
|---|---|
| CC-01 | `κ_th>0 ⇒ w=κ_th x(L−x)/2 ≥ 0` — true under B; became correct with RB-04. **CLOSED** |
| CC-02 | "fixed so that the bowing is positive" — true under B. **CLOSED** |
| CC-03 | clamped strip: `D_s κ_th = 13.500000 N·m` — correct. **CLOSED (no action)** |
| CC-04 | `2.19×10⁻⁴`, `0.438 H₀`, `0.315` — all reproduced to 3 s.f. **CLOSED (no action)** |
| CC-05 | `(κ_geo−κ_th)d/2 = 9.8881×10⁻⁴` — correct under B; **must not be flipped**. Explains B-3 in closed form (§5 of `02_…`). **CLOSED** |
| CC-06 | `M = −6.356655 N·m`, `σ_bend = 4.237770 MPa`, `9.000 MPa` restrained scale — reproduced. **CLOSED (no action)** |
| CC-07 | `(1+ν)Σ_κΛ²/8 = 0.315` — exact. **CLOSED (no action)** |
| CC-08 | `ch07` magnitudes — correct; only the arc cell changed. **CLOSED** |
| CC-09 | appendix A3, A9 — correct once the arc term was fixed; **the arc formula `κ_geo²L²/24` is correct** (−0.62 %), not an error. **CLOSED** |
| CC-10 | `fig_signs.tex` has no `w`/`κ` content; is 20 lines, not 17. **CLOSED (no action)** |
| CC-11 | `ch10`, `ch11` direction-neutral. **CLOSED (no action)** |
| CC-12 | `eq:nupdate` carries `⟨w'²⟩` only — sign-invariant. **CLOSED (no action)** |
| CC-13 | slope `0.03` → `0.027` rad (precision drift, `0.027516`). **CLOSED** |
| CC-14 | "pressure dominates by about two orders": `84/0.6 = 140`. **CLOSED (no action)** |

## 3. Author-resolution items (RU)

| ID | Question | Status |
|---|---|---|
| RU-01 | Is the strip's outer face **free**, **backed by a vented cavity**, or **in contact** with the rigid casing? No standoff distance is stated anywhere in the source. Under the adopted convention the strip bows **towards** the casing by `0.4377 H₀ = 0.219 mm`, so this is now load-bearing. Three branches with distinct consequences are enumerated in `02_derivation_and_sign_convention.md` §4. | **OPEN-AD** |
| RU-02 | Report the sagging-positive `M` or the physical first moment `M_phys = −M`? Both vanish at the pins, so **no result changes**; only the mid-span sign convention is at stake. Disposition taken: keep `M` as printed and state `M_phys = −M` once (RB-08), so no reader can mis-sign it. | **CLOSED by disclosure** (author may still prefer the opposite label) |
| RU-03 | Should the mid-span passage height be stated? No gap sentence exists in the source. Under the adopted convention the mid-span height is `H₀ + w_max = 1.4377 H₀` (i.e. **the passage widens**), the mirror value being `0.5623 H₀`. | **OPEN-AD**, coupled to RU-01 |

## 4. Blockers (B)

| ID | Blocker | Status |
|---|---|---|
| B-1 | Function spaces and interface traces undefined (`ch08`) | **CLOSED** — `V_g, Q, S_f, V_s, S_s` defined with `H^{1/2}(Γ_if)` traces |
| B-2 | Pressure gauge unenforced | **CLOSED** — outlet mean-pressure datum stated and its algebraic form given |
| B-3 | Geometric stiffness missing from `eq:weaks` | **CLOSED** — `−∫ N_θ^c ∂_X d₂ ∂_X φ₂ dX` added, reduction to `eq:beamcol` stated |
| B-4 | Thermal data-flow contradiction | **CLOSED** — restated as a shared interface unknown carrying the flux balance; `ch08:108` governs and is now consistent with `ch05` |
| B-5 | Monolithic cancellation vs staggered iteration | **CLOSED** — assembled-system cancellation distinguished from its limit-wise recovery; V-B flux-jump norm cited as acceptance criterion |
| B-6 | SUPG `τ` unspecified | **CLOSED** — `τ_K` with `Pe_K`, units, and the `Pe≫1` limit written out as `eq:supg` |
| B-7 | Rigid casing / clearance / contact | **OPEN-AD** — same item as RU-01 |
| B-8 | LaTeX build of current source | **OPEN-TECH** — no engine in this environment (see `08_…`) |
| B-9 | Audit-artefact provenance | **CLOSED** — Stage 15 artefacts committed under `audit_stage15/`; earlier Stage 11–14 reports remain outside the tree and are cited as external, not claimed as present |
| B-10 | Reference/deformed interface `O(ε)` | **CLOSED (verified)** — the stated `5.4×10⁻³` is the total mechanical surface strain `e₀ + κ_geo d/2 = 5.347713×10⁻³`, recomputed. The disclosure is correct and appropriately placed |
| B-11 | Is the `1.8×10⁻⁴` error isolated? | **CLOSED** — see RB-15 provenance |

## 5. Tally

| Tier | Count | Closed | Open |
|---|---|---|---|
| RB | 17 | 17 | 0 (RB-13 has an author-gated remainder) |
| CC | 14 | 14 | 0 |
| RU | 3 | 1 (by disclosure) | 2 |
| B | 11 | 8 | 3 (B-7 = RU-01, B-8 toolchain) |

Two open items are **not** technical defects: RU-01/B-7 and RU-03 are unstated physical
configuration, and B-8 is the absence of a compiler. No item was closed by moving it into a report;
each `CLOSED` above was rechecked against the tree at `e8ef0d7`.

---

# Stage 16 status update (Claude audit I-01 … I-15)

Status vocabulary used below: **IMPLEMENTED** = the source now contains the correction and a
regression check would fail if it were reverted; **PARTIAL** = the implementable part is done and
something remains for the author; **OPEN (author decision)** = not implementable without inventing
physics. Nothing here is marked "verified closed" by me: closure requires a fresh independent audit.

| ID | Status after Stage 16 | Where it now lives | What the regression suite checks |
|---|---|---|---|
| I-01 pin treated as clamp | **IMPLEMENTED** | `ch02` A9, `ch05` B7, `ch08` `V_s` | B7 must contain `d_2=0` and `⟨d_1⟩=0` and must **not** contain `d_1=d_2=0`; `V_s` must contain `φ₂=0` and must not be the `φ=0` clamp |
| I-02 casing clearance / RU-01 | **OPEN (author decision)** | `ch07` RU-01 | not testable — the parameter does not exist in the source |
| I-03 missing `1/d` in geometric term | **IMPLEMENTED** | `ch08` `eq:weaks` | the term must be present as `−(N_θ^c/d)∂_X d_2`; the old dimensionless-less form must be absent; a flipped sign must be absent |
| I-04 pressure gauge | **IMPLEMENTED** | `ch08` spaces paragraph | the constraint `∫p ds = 0` must be absent; the no-gauge argument must be present |
| I-05/I-06 SUPG + stagger | **IMPLEMENTED** | `ch08` `eq:supgwf`, `ch05` | `eq:supgwf` must exist; `h_K → h_K/p` must be addressed; the Dirichlet/Neumann split must be stated |
| I-07 vacuous mutation tests | **IMPLEMENTED** | `audit_stage15/regression.py`, `mutation_test.py` | six mutations, each in an isolated copy; baseline must pass, every mutant must fail |
| I-08 stress inconsistency | **IMPLEMENTED** | `ch04`, `ch07`, appendix | self-consistent `σ_max` must match recomputation; frozen must exceed it; frozen must stay under the `0.2σ_y` cap |
| I-09 strain envelope | **IMPLEMENTED** | `ch02`, `ch04`, `ch07`, `ch08`, appendix | printed `3.25e-3` must match `max|ε_mech|` recomputed from the inputs |
| I-10 θ̄ rounding | **IMPLEMENTED** | `ch04` | θ̄ recomputed from its own components must agree with the printed 32.27 K to 0.05 K |
| I-11 Γ_p like-for-like | **PARTIAL** | `ch04` D-29 | both ratios checked (`2.4e3` mixed, `1.7e3` like-for-like); which one the author *intends* to headline is still open |
| I-12 stale package | **IMPLEMENTED** | `README.md`, ZIP, manifest | every `.zip` named in `README.md` must exist; per-member hashes recorded |
| I-13 provenance | **IMPLEMENTED** | `README.md` build note | `main.pdf` staleness is *reported* (see §7 of the suite); a rebuild is still required |
| I-15 figure collisions | **IMPLEMENTED** | `figures/fig_geometry.tex` | brace/label structure only — rendering is a visual judgement, not a test |
| I-14 (report-only items) | **n/a** | — | no source change required |

---

# Stage 17 status update (repair of the Stage 16 audit)

None of these is marked `VERIFIED CLOSED`: closure needs a fresh independent audit of the new
commit. `IMPLEMENTED` means the source contains the correction **and** a regression check fails if it
is reverted (mutation-tested). `OPEN-AD` means the physics is not determined by the source.

| ID | Item | Status after Stage 17 | Evidence in the tree | Guarding test(s) |
|---|---|---|---|---|
| NEW-01 | Solid thermal subproblem ill-posed (pure Neumann) | **IMPLEMENTED** — iteration reordered, solid Dirichlet first, level inherited from `T_in`, no datum invented | `ch08` `sec:iteration` steps 1–2 + well-posedness paragraph; `ch05` `sec:datamodel`; register `D-32`; solver spec §12 | 9 structural checks + mutation B1/B2/B3/B9 (all detected) |
| NEW-02 | Expected value vs printed rounding | **IMPLEMENTED** — `θ̄` true `32.2652` vs printed `32.3`; tolerance stated as the printed 3 s.f. | `ch04`, appendix A5 | `printed theta-bar equals the recomputed value to its 3-s.f. rounding` |
| NEW-03 | Dangling pointer after the D-25/D-30 split | **IMPLEMENTED** — `D-25 → D-30` in `ch08` | `ch08:94` | `register pointer corrected to D-30` |
| NEW-05 | "Few per cent" / "one-time numerical check" end effect | **IMPLEMENTED** — measured `0.2 %` (`1.0000`, `0.998`, `−0.02…−0.06`), D-26 | `ch04`, `ch11` | 5 checks + mutation B4 (detected) |
| I-01 | Pin vs clamp | IMPLEMENTED (Stage 16), re-verified | `ch02` A9, `ch05` B7, `ch08` `V_s` | B7/A9/`V_s` checks + mutation A21 (detected) |
| I-02 | Casing clearance / contact | **OPEN-AD** (RU-01) | `ch07` RU-01 | not testable — no parameter in source |
| I-03 | Missing `1/d` in the geometric term | IMPLEMENTED, re-verified | `ch08` `eq:weaks` | 4 checks + mutation B8 (detected) |
| I-04 | Pressure gauge | IMPLEMENTED, re-verified | `ch08` spaces paragraph | gauge scan + mutation A8 (detected) |
| I-05/I-06 | SUPG, stagger | IMPLEMENTED, re-verified | `ch08` `eq:supgwf`, `sec:iteration` | SUPG checks + NEW-01 checks |
| I-07 | Vacuous mutation tests | **IMPLEMENTED** — suite v3, 34/34 detected | `regression.py`, `mutation_campaign_stage17.py`, `mutation_stage17_results.txt` | campaign exits 0 only with zero survivors |
| I-08 | Stress inconsistency | IMPLEMENTED, re-verified | `ch04`, `ch07`, appendix | recompute + ch07 stress whitelist + mutation A19 (detected) |
| I-09 | Strain envelope | IMPLEMENTED, re-verified | `ch02`, `ch04`, `ch07`, `ch08`, appendix | `appendix envelope matches`, `…mechanical surface strain…` |
| I-10 | `θ̄` rounding | IMPLEMENTED, re-verified | `ch04` | 0.05 K tolerance check |
| I-11 | `Γ_p` like-for-like | **IMPLEMENTED** (5 sites labelled, A-5 on the like-for-like ratio); headline choice **OPEN-AD** | `ch04`, `ch07`, appendix A8 + dictionary, `ch06` A-5 | 6 checks + mutations B5/B6 (detected) |
| I-12 | Stale package | IMPLEMENTED — deterministic ZIP rebuilt, hash recorded | `README.md`, `package_manifest.txt` | manifest check (§8 of the suite) |
| I-13 | Provenance / staleness of `main.pdf` | **OPEN** — the PDF still predates the modified sources; no TeX engine here | `08_build_and_packaging_report.md` | suite §7 reports, does not assert |
| I-14 | Report-only items | n/a | — | — |
| I-15 | Figure collision / visual check | **OPEN** — structure only; no renderer, no visual check | `figures/fig_geometry.tex` | brace/label structure only |

**Tally after Stage 17:** 13 items implemented (12 of them mutation-tested), 1 open author decision
on the `Γ_p` headline, 2 open environment items (I-13 rebuild, I-15 visual check), 1 open physics
item (RU-01/B-7) plus RU-03. The coupled production solver remains **NOT READY**.

---

## Stage 18 — verification defects repaired (implementation, not audit)

Parent on entry: `a61837e` (Stage 18 acceptance audit: no Stage 18 existed; implementation still
`211f751`, suite v3 = 109 assertions). Stage commit: the commit that adds this section (hash in the
commit message; it cannot be written into a file that the shipped ZIP contains — see
`14_stage18_repair_report.md` §15). Full detail: `14_stage18_repair_report.md`; raw mutation evidence:
`stage18_mutation_results.txt`.

| ID | Original claim / defect | Why it needed repair | Old source | New source | Dependencies | Recalculation / check | Mutation |
|---|---|---|---|---|---|---|---|
| S18-1 | `regression.py` asserted the I-15 figure item with `… or True` | an unconditional pass is not a test | `check("figure fix is not claimed as visually verified", … or True)` | two assertions: no positive visual-verification claim in any source; ledger I-15 still `**OPEN**`; missing required files now exit non-zero with a named FAIL instead of a traceback | `FIGCLAIM` scan, `LEDGER` regex, `REQUIRED` guard | `no chapter claims a visual verification of a figure (I-15 remains open)`, `the ledger still records I-15 as OPEN` | V1 (insert a positive claim in `ch09`) → detected |
| S18-2 | A pressure constraint was forgiven when its explanation was within ±260 characters | the exemption, not the condition, decided the outcome | `explained = [i for i in gauge_hits if 'over-determine' in C8[i-260:i+260]]` | `P_NORM` (5 notations) × sentence-scoped `REJECT` and no-`ADOPT` test, no exemption window; register row handled separately (must call it an error) | `ch08` gauge paragraph; register D-30 | `a pressure normalisation occurs only as an explicitly rejected counterfactual`; two occurrences reported (ch08 = rejected counterfactual, D-30 row = removed error) | G1, G2, A8 → detected; G1/G2 pass v3 |
| S18-3 | `tab:bcs` was never parsed; a solid Γ_if with two thermal data was unrepresentable | the interface data are the core of the conjugate problem | string checks only (`B7 found` …) | `tab:bcs` parsed row by row; Γ_if row may carry neither a solid flux datum nor Dirichlet+Neumann at once; prose data are located **with their surface** by `DATUM` | `ch05` `tab:bcs`, `ch08` step 1–2 | `no Gamma_if row gives the solid a Dirichlet AND a Neumann temperature datum`; `no solid flux datum is imposed on Gamma_if anywhere in the formulation`; exactly one solid Dirichlet datum found (`ch08` step 1) | G3 → detected; passes v3 |
| S18-4 | `θ̄` was compared only as a total, from a hard-typed chain | the table cell could say anything | one check, `abs(thbar-thp) <= 0.05` | cell formula and three components parsed; each recomputed at its displayed precision (30.0 / 1.55 / 0.72 vs 30.000 / 1.548 / 0.718) and the total compared with 32.2652 | `ch02` inputs, `Nu_H1`, `ch07` cell | `each component printed in the theta-bar cell is its recomputed value at 2 dp`, `the theta-bar cell total is the recomputed theta-bar` | T1 → detected; passes v3 |
| S18-5 | `T̄_cr` was never recomputed; `M_b ≥ 2` was not tied to it | the buckling margin is an admissibility claim | `M_b` compared with a hard-coded `117.5/θ̄` | `eq:tcr` coefficient parsed (12), `T̄_cr = 117.495 K` recomputed, thickness catalogue recomputed, `M_b = 3.6415` and the two `M_b=2` consequences (`58.75 K`, `9104 W/m²`) recomputed | `eq:tcr`, A4, A5, `ch07` rows | `ch07 table T_cr is the recomputed threshold`, `the T_cr versus thickness catalogue matches eq:tcr`, `the M_b numerator is the recomputed T_cr`, `bound A-2 (M_b >= 2) is met by the recomputed margin` | T2 → detected; `117→130` passes v3, fails v4 |
| S18-6 | `eq:wmax` was checked only through the printed `w_max/H_0` | the display could be corrupted with the printed result untouched (A4-class) | `cmp("ch04 printed linear w/H0 matches", …)` | constants of `eq:wmax` parsed; mid-span = stated maximum; `w''=−κ_th`; `μL→0` limit of `eq:beamcolsol`; printed `1.575×10⁻⁴` reproduced | `eq:wmax`, `eq:beamcolsol`, appendix A3, `ch07` | four assertions incl. `eq:wmax is the mu -> 0 limit of eq:beamcolsol` | F1 (`8→16` **with** `--update-fingerprints`) → exit 1 on four substantive assertions |
| S18-7 | The `Γ_p` nomenclature entry was unchecked (only the dictionary and A8 were) | nomenclature is the definition readers take away | `$\Gamma_p$ & thermal-to-pressure deflection ratio & --` | `$\Gamma_p$ & deflection ratio $w_{\max}/w_p$, \eqref{eq:gammap}; mixed and like-for-like presentations & --` (headline still an author decision) | `eq:gammap`, A8, dictionary row | three assertions on the entry itself | N1 → detected |
| S18-8 | Stale end-condition magnitudes were matched only as “a few per cent” with a ±200-character exemption | reworded claims escaped; scope of the scan was unstated | `stale_few()` on `ch04`/`ch11` | sentence-scoped scan of 22 files (16 sources + 6 reports), magnitudes `one|two|three|few|couple|1|2|3` + `per cent`/`%`, exemption only for an explicit supersession marker in the same sentence; locations printed by the suite | `ch04`, `ch11`, register D-26, README/reports | `no stale end-effect percentage survives in the 22 scanned files` | S1, S2 (+2 probes) → detected; all pass v3 |
| S18-9 | Nothing said that well-posedness ≠ convergence of the staggered iteration; no thermal stopping measure | the audit's §8 requirement | the iteration section stopped at subproblem well-posedness and a displacement-based criterion | `ch08` paragraph: no contraction/energy proof claimed; `ΔT_Γ^{(k)}` and `‖ΔT_Γ^{(k)}‖ = max_{Γ_if}|T_Γ^{(k)}−T_Γ^{(k−1)}|` defined; acceptance rule stated with the tolerance **left to the mesh/iteration study**, no value asserted; flux-jump criterion named as a-posteriori only | `sec:iteration`, `sec:quality` | none (prose; inline math only, so the 76 fingerprints are unchanged) | — |

**Note on a withdrawn suspicion.** An internal note during this stage suspected the `q''/h` component
of `θ̄` of being inconsistent; it used `D_h = 6 mm` instead of `D_h = 2H_0 = 1 mm`. The suspicion was
wrong and is withdrawn (`h = 3231 W/m²K`, `q''/h = 1.548 K`, `θ̄ = 32.2652 K`). Only a display
rounding (`1.6` for `1.548` at one decimal) was corrected, with no change of value.

**Tally after Stage 18.** Suite v4 = 144 assertions, all passing. Mutation campaign: 44 cases
executed, 44 detected, **36 substantive**, **8 fingerprint-only**, 0 escapes, 0 invalid, 0 anchors
missing. Unchanged and still **OPEN**: RU-01, RU-03, heater mounting/heated-face interpretation, the
contact law, the intended headline definition of `Γ_p`, **I-13** (no TeX engine; `main.pdf` stale),
**I-15** (no renderer; no visual check). The coupled production solver remains **NOT READY**; no
convergence of the staggered iteration is claimed or demonstrated.

---

## Stage 19 — targeted verification hardening after conditional acceptance (implementation, not audit)

Parent on entry: `39ef118` (the independent Stage 18 acceptance audit, verdict *conditional
acceptance*, five suite blind spots and two manuscript defects). Stage commit: the commit that adds
this section (its hash is in the commit message; it cannot be written into a file that the shipped
ZIP contains — see `15_stage19_repair_report.md` §12). Full detail:
`15_stage19_repair_report.md`; raw mutation evidence: `stage19_mutation_results.txt`; before/after
evidence for the five blind spots: `stage19_before_after.txt`.

The five blind spots were **reproduced first** on `5741d36` with the new campaign (5 escapes,
0 false detections), and only then closed. Suite v4 (144 assertions) → **v5 (156 assertions)**.
Fingerprints were regenerated once, deliberately: 78 entries, `reg:D-26` changed, `reg:D-33` and
`reg:D-34` added, nothing removed, and **no display-equation fingerprint changed**.

| ID | Original claim / defect | Why it needed repair | Old source | New source | Dependencies | Recalculation / check | Mutation |
|---|---|---|---|---|---|---|---|
| S19-1 | The gauge test matched integral/mean forms only | `p(\mathbf 0)=0` is the same normalisation in another notation; it passed suite v4 | `P_NORM` without pointwise forms | `P_NORM` adds `p(\mathbf 0)=0`, `p(0)=0`, `p(\mathbf x_0)=0`, `p\big|_{x_0}=0`; clause-scoped verdict | `ch08` gauge paragraph; D-30 row | `a pressure normalisation occurs only as an explicitly rejected counterfactual`; positive control that the legitimate outflow datum is the boundary value `p\to0` (B2) | M3c (`p(\mathbf 0)=0`) → detected (was ESCAPED) |
| S19-2 | Rejection was judged on the whole sentence, and adoption by a fixed verb list | "we choose X for the level **rather than** rely on the outflow condition" passed v4: "rather than" excused the adoption, and "choose" was not in the vocabulary | sentence-scoped `REJECT`, `ADOPT` without `choose/pin/anchor` | clause-scoped verdict: `CLAUSE_SPLIT` treats `rather than`, `instead of`, `although`, `but`, `while`, `;`, `:` as boundaries; negation may now reach the verb across a noun ("no normalisation is imposed") | `ch08`, `ch05` | same check name; the rejecting alternative is no longer part of the clause that carries the constraint | M6b ("we choose … rather than …") → detected (was ESCAPED); control P1 (legitimate "no normalisation is imposed: … would over-determine") → now PASSES (v4 wrongly rejected it) |
| S19-3 | `tab:bcs` rows were selected by the Boundary cell before being tested | a double thermal datum in a Condition column of a row whose Boundary cell omits `Γ_if` was never looked at | `IFACE = rows containing 'Ga_{\mathrm{if}}'` | every row is tested: solid Dirichlet + solid Neumann ⇒ double datum; a non-zero solid flux datum is admissible only on the heated face (zero flux stays admissible on ends/faces); the `Γ_if`-row check is kept under its Stage 18 name | `ch05` `tab:bcs` | `no tab:bcs row gives any surface a solid Dirichlet AND a solid Neumann thermal datum`; `no Gamma_if row gives …` (unchanged); `no tab:bcs row puts a non-zero solid flux datum on a surface other than the heated face` | M7 (B9 = `T_s=T_h` on `Γ_h^0` **plus** `∂_nT_s=q''/k_s`) → detected (was ESCAPED) |
| S19-4 | The prose datum test required the phrase `<datum> … on <surface>` | a double datum written "together with its interface temperature" passed v4 | `DATUM` regex requiring `on $Γ$` | datum-shape rule per sentence: solid Dirichlet (`T_s=`) **and** a non-zero solid flux (`∇T_s·n=`, `∂_nT_s=`) that is not placed on `Γ_h^0` ⇒ failure; tables removed before scanning; zero-flux (adiabatic) data ignored | `ch08` steps 1–2 | `no prose datum gives the solid a temperature AND a non-heated-face heat flux in one sentence`; `no prose sentence puts a non-zero solid flux datum on a surface other than the heated face`; Stage 18 names kept | M8 (flux "together with its interface temperature", no "on") → detected (was ESCAPED); control P2 (Dirichlet + heated-face flux in one sentence) → passes |
| S19-5 | The stale-magnitude scan accepted `per cent` and `%` only | "about two pct" passed v4 | `STALE` without `pct` | `STALE` adds `pct`, `percentage points`, hyphenated `per-cent` | `ch04`, `ch11`, 20 other scanned files | `no stale end-effect percentage survives in the 22 scanned files` | M10 ("two pct") → detected (was ESCAPED) |
| S19-6 | An expression the parser could not read caused the dependent numeric checks to be **skipped** (`if _w1 and _wq:`) | a format mismatch, not a wrong value, was the only reason for failure — the audit's A2 weakness | `if _w1 and _wq:` / `if _tcr:` | explicit failing assertions `the eq:wmax constants are parseable …` and `the eq:tcr denominator coefficient is parseable …` before the conditional block | `eq:wmax`, `eq:tcr` | the parse guard fails, and the substantive check names stay in the output | W3 (`eq:wmax` → `/(2(1−ν))` with regenerated fingerprints) → detected |
| S19-7 | `ch06` claimed `T_ref` and `T_in` enter "exclusively through property values" | false for `T_in`, which is the inflow Dirichlet datum; the quoted `θ̄` silently assumes `T_ref = T_in` | `Only temperature differences … exclusively through property values` | `T_ref` enters through properties and through `T_in − T_ref`; `T_in` is the B1 datum and the anchor of the level via `eq:iftemp`; the convention `T_ref = T_in` behind the quoted `θ̄` is stated, with the offset a solver must carry if it differs (D-33) | `ch06`, `eq:iftemp`, `ch02` table row | `ch06 states that T_in is the inflow datum, not a property input`; `ch06 states the T_ref = T_in convention behind the quoted theta-bar` | none needed (prose); no printed value changes |
| S19-8 | The `M_b = 2` ceiling was printed `58.8 K` | double rounding: `117.5/2 = 58.75 → 58.8`, while the exact `117.4953/2 = 58.7476 → 58.7` | `\bar\theta\le58.8` K | `\bar\theta\le58.7` K (register D-34) | `ch07` ceiling sentence, `eq:tcr` | `the M_b = 2 ceiling is the correctly rounded T_cr/2 (58.7 K)` — exact `abs(printed − round(T_cr/2,1)) < 1e-12`, i.e. **no tolerance**; the dependent `q'' ≈ 9.1×10³` is unchanged | reverting to 58.8 fails the rounding assertion |
| S19-9 | The single 24-element Q8 comparison was described as if it settled the strip solution | the six-mesh study shows the point-pin ratio is independent of axial refinement while the clamp magnitude falls under refinement; absolute ratios move with the through-thickness discretisation | `… the check is complete …`, `D-26 … resolved (Stage 16)` | `ch04`, `ch11`, `ch02` A9 and `D-26` state: values on **one** 24-element mesh, the `0.2 %` pin difference reproduced at two and four elements through the thickness, clamp band is finite-mesh evidence only, not a converged penalty. Measured values (`1.0000`, `0.998`, `−0.02…−0.06`) preserved | `independent_audit_stage16/evidence/q8_pin_verification.py`, six-mesh study (`15_stage19_repair_report.md` §5) | `ch04 scopes the Q8 values to one finite mesh …`, `ch11 scopes …`, `the D-26 register row states the Q8 finite-mesh scope` | scope-text removal is caught by the three pins |

**Positive controls (permanent, in `mutation_campaign_stage19.py`).** P1 a legitimately reworded
rejection ("No normalisation is imposed: constraining `∫p ds=0` would over-determine the system")
must pass — it is valid because the constraint is named and rejected in the same clause with no
adopting verb, and it exposed a **v4 false positive** that Stage 19 fixes. P2 a sentence that states
the interface Dirichlet datum and the heated-face flux together must pass — it is valid because the
flux is explicitly placed on `Γ_h^0`, which is exactly the distinction the M8 rule relies on. P3 a
legitimately added display equation must pass — a fingerprint **addition** is reported, never failed.

**Tally after Stage 19.** Suite v5 = **156 assertions, all passing**. Stage 18 campaign: **44/44
detected (36 substantive, 8 fingerprint-only)**, 0 escapes, 0 invalid, 0 anchor. Stage 19 campaign:
**10/10 detected** (the five required classes + G5, T3, T4, W2, W3), 0 escapes, 0 invalid, 0
anchor, **all substantive**; **3/3 positive controls pass**. Non-vacuity probes 6/6. Fingerprints:
78 entries, stable on a clean tree. Package rebuilt deterministically; archive SHA-256 in
`package_manifest.txt`.

**Unchanged and still OPEN:** RU-01 (casing clearance / contact interpretation / vented-or-sealed
cavity), RU-03 (`1.4377 H₀`), heater mounting and heated-face interpretation, the contact law, and
the intended headline definition of `Γ_p`. **I-13** (no TeX engine: `main.pdf` predates the sources)
and **I-15** (no renderer: no figure check) remain **OPEN**. The coupled production solver remains
**NOT READY**: no convergence of the staggered iteration is demonstrated, and no interface
temperature history has been computed.
