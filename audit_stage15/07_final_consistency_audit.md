# Stage 15 — Final cross-document consistency audit

An independent pass over the corrected tree, checking the things an arithmetic suite cannot:
that the chapters agree with each other, that prose agrees with equations, that the figure agrees
with the convention, and that nothing was "fixed" that should have been left alone.

---

## 1. Direction language, whole tree

Swept for nine direction stems (`into the channel`, `into the flow`, `into the passage`,
`toward the interior`, `towards the interior`, `into the fluid`, `narrow`, `constrict`, `inward`)
across `main.tex`, `chapters/*.tex` and `figures/*.tex`.

**Result: zero hits in body text.** The only survivors are inside register rows D-21 and D-23, where
they are *quotations of the superseded claim* — which is their purpose. The abstract's
"the widened passage modifies …" (`main.tex:54`) now agrees with a wall moving away from the
channel, which widens the passage.

## 2. Prose vs equations in the wall chapter

| Claim | Equation | Agrees? |
|---|---|---|
| `κ = −w''`, `w` positive away from the channel (`ch02:131`) | `ch04:186` `w'' = −κ_th` | **yes** — see §2 of `02_…` |
| `κ_th > 0` gives `w = κ_th x(L−x)/2 ≥ 0` (`ch03:145–146`) | `eq:wmax` | **yes** |
| `M = D_s(w''+κ_th)` vanishes at pins (`ch04:189`) | `eq:beamcol` BC | **yes**, and `M_phys = −M` is stated once |
| pressure "acting in the same sense as the thermal bowing" (`ch04:296`) | `D_s w'''' = +p` (`ch03:140`) | **yes** — `p > 0` pushes the wall away, same sign as `w > 0` |
| "co-directional deflection" (`ch04:309`) | `Γ_p` ratio | **yes** — a ratio of two same-sign contributions |
| thermal bow is positive on the heated wall (`ch02:135`) | `+k_f∇T_f·n` | **yes** — flux into the fluid is positive on `Γ`, consistent with heat entering through `Γ_h` |

**The pressure-direction check is the one worth stating.** Under the old convention the text had
pressure *opposing* the bow (`ch04:275` old) and `D_s w'''' = −p`. Flipping `w` flips both, so the
corrected pair `+p` with "same sense" is the one that preserves the *physics* (fluid pressure and
thermal bow both act outward from the channel). Flipping only one of them would have inverted the
sign of the hydraulic contribution and made `Γ_p` a ratio of opposing contributions — which is
exactly what the old text implied and what RB-09/RB-10 removed.

## 3. Figure vs convention

`fig_geometry.tex` now shows: interface `Γ` at `\Hf`, wall from `\Hf` to `\Hf+\ds`, both faces
displaced upward by the same quadratic bow (control `+12` ⟹ mid-span `+6` pt), `q''` arrows above
the wall clearing the bow, and a `w` arrow spanning exactly the drawn bow.

- Same displacement on both faces: **required**, since a strip of constant thickness cannot have one
  face move and the other not. The old figure had the interface bowed and the outer face straight —
  kinematically impossible.
- Direction: **away** from the channel, consistent with `w > 0` and with `ch02:131`.
- **Still open:** the bow magnitude is a schematic `6` pt and is unrelated to `0.4377 H₀`. A
  conformal redraw to the measured profile is gated on RU-01 because under reading `R3` (contact)
  the drawn bow would be physically impossible.

## 4. The two stress columns

Requirement: keep `13.9 MPa` (frozen force) and `13.6 MPa` (self-consistent) as two valid columns,
not a contradiction.

- `ch07:95` states `13.9` as the frozen-force value the bound is enforced against, and `13.6` as the
  self-consistent comparison, with a pointer to Appendix B. They are now explicitly **two model
  levels of one quantity**, adjacent in one sentence.
- `appendix:109` gives the self-consistent column with `M_mid = −5.9 N·m` and `0.151σ_y`.
- **Verified arithmetic:** `|σ_memb| + 6|M|/d²` = `9.681 + 4.2378 = 13.9188 MPa` (frozen);
  `9.681 + 3.9333 = 13.6143 MPa` (self-consistent). `0.151σ_y = 13.59 MPa`. All reproduce.
- The 2.2 % spread is the *expected* frozen-force error, not a discrepancy: `ch04:236–240` states
  the frozen force overpredicts by 2.3 % in `w_max` and that the mid-span moment shifts by under
  8 % (actual: `−7.2 %` in `σ_bend`). **Consistent.**

## 5. Items deliberately NOT changed

Per the standing instruction not to repair what the evidence supports:

| Item | Why untouched |
|---|---|
| `1.6×10⁻⁴` circular-arc estimate | `κ_geo²L²/24` is **exact** for a constant-curvature parabolic arc; the `0.62 %` gap from the beam–column value is a real difference between profiles, not an error |
| `6.1 %` relaxation | exactly `1.388×10⁻⁴/e₀ = 6.1446 %` |
| `0.438 H₀` | `0.437740946`, rounding correct |
| `1.39` amplification | `1.389654`; also verified equal to `(w_max/w_p)/(w_lin/w_p)` |
| `H1` / `H2` nomenclature | resolved in a prior stage against Shah & London and the parallel-plate tables; the manuscript's usage is correct and is not re-litigated here |
| `ch07:46` `Ri = 3.4×10⁻³` | the `D_h`-basis value, explicitly labelled as such by a preceding decision; retained |
| `eq:nupdate`, `eq:ntheta`, `eq:tcr`, `eq:mf`, `eq:wpdef` | verified unchanged and correct |
| material properties, `references.bib` | untouched by this stage |

## 6. Residual inconsistencies that remain, by design

These are **recorded, not repaired**, because repairing them would require inventing physics:

1. **RU-01 casing/clearance (OPEN).** Under the adopted convention the strip bows toward the rigid
   casing by `0.219 mm`. No standoff is stated anywhere in the source. Three readings with distinct
   consequences are enumerated in `02_…` §4. Under `R2` or `R3` the baseline mechanics change.
2. **RU-03 passage height (OPEN).** No sentence anywhere states the deformed mid-span height. Under
   the adopted convention it is `1.4377 H₀` — the passage **widens**; the mirror value would have
   been `0.5623 H₀`. Coupled to RU-01.
3. **`h_K` for anisotropic elements (disclosed).** Defined as "element length in the mean-flow
   direction"; not unique for graded elements. A coding decision, flagged in the solver spec.
4. **Regularity assumptions (disclosed).** `V_g = [H¹]²` implies a regularity the manuscript asserts
   rather than proves. Correctly stated as an assumption.

## 7. Chapter-to-chapter interfaces

| Interface | Check |
|---|---|
| ch02 (conventions) → ch03/ch04 (derivation) | `w`, `κ`, `M`, `p` all consistent; verified by re-deriving `M_phys` |
| ch04 (baseline) → ch07 (table) | all 16 table rows reproduce; 3 rounding-level differences only (`1.575→1.58`, `2.905e4→2.9e4`, `9.643→9.6`) |
| ch04 → appendix B (arithmetic) | cells A3, A8, A9 agree with ch04 including the corrected arc term |
| ch05 (BCs) → ch08 (weak form) | the thermal data flow now agrees; the four interface conditions `eq:ifkin`–`eq:ifflux` are the ones the weak form consumes |
| ch08 (discretization) → ch09 (tests) | V-C2/V-C3 carry signs; V-B flux-jump norm is cited as an acceptance criterion for the staggered path |
| ch06 (dimensionless) → ch04 | `Γ_p` definition now single-sourced from `eq:gammap` |
| main.tex (abstract) → ch04 | "widened passage" agrees |

## 8. Verdict on consistency

**The manuscript is internally consistent**, with two exceptions that are *external* to the text
rather than contradictions inside it: the casing standoff (RU-01) and the passage-height statement
(RU-03) are unstated physical configuration. No sentence in the tree contradicts another sentence
in the tree after `e8ef0d7`.

---

# Stage 16 consistency re-audit (separate pass, after the edits)

Checked after all six correction batches, not during them — the point of a separate pass is to catch
what a batch broke.

| Cross-check | Result |
|---|---|
| the pin description in `ch02` A9, `ch05` B7 and `ch08` `V_s` agree | yes, all three now `d₂=0` + `⟨d₁⟩=0` |
| no remaining claim that `Γ_p` "exceeds" without saying which ratio | yes, both labelled |
| no remaining `13.6 MPa` outside the withdrawal note | yes |
| `13.9` and `13.0` never presented as the same quantity | yes, frozen vs self-consistent columns |
| every `N_θ^c` occurrence that should carry `/d` does | checked in `eq:weaks` and its explanation |
| no `∫p ds=0` left anywhere | yes |
| SUPG label `eq:supgwf` referenced, not orphaned | yes |
| register D-25 annotated as partly superseded | yes (D-26, D-27, D-30) |
| 31 register rows, 88 unique labels, no dangling refs | yes |
| README names exactly the files the ZIP contains | yes (every member is a file, no directory entries; counts and hashes are in the manifest, not repeated here) |

Defects introduced by the batches themselves, caught on this pass and fixed:

- an accidental `\Nth` macro (a "nicer" name for `N_θ`) appeared during the batch and was replaced
  with `|N_θ|` after a macro sweep — recorded because it is exactly the failure mode a batch creates;
- the first attempt to append D-26 … D-29 used a stale anchor and asserted on a row that no longer
  existed; the retry targeted the real D-25 row and the count was verified (31 rows, not 30).
