# Stage 17 — repair of the independent Stage 16 findings

**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix` (the only push target; `origin/main`
stays at `5a255212`, `claude/independent-audit-7c9749f` is untouched).
**Parent:** `dc29b3d` (the Stage 16 audit commit).
**Status:** repair implemented and mutation-tested; **not** independently verified, and the coupled
production solver remains **NOT READY**. Commit hashes are recorded in §8.

This report states what was claimed, what the source now says, what was recomputed, and what remains
open. Everything below is checkable in the tree: the numbers come from
`python3 audit_stage15/regression.py --chain`, the mutation results from
`python3 audit_stage15/mutation_campaign_stage17.py` (full log in
`audit_stage15/mutation_stage17_results.txt`).

---

## 1. P1 — NEW-01: the solid thermal subproblem was ill-posed

### 1.1 What was claimed

Stage 16 wrote the stagger as: fluid first with a Dirichlet interface temperature `T_Γ` → extract the
flux `q_Γ` → **solid with `q_Γ` as a Neumann datum** → extract `T_Γ^{k+1}`. The text then asserted
that the prescribed outer-face flux `q''` "fixes the temperature level" of the solid.

### 1.2 Derivation of the solid problem and the uniqueness question

The steady solid problem, as the model states it, is

    ∇·(k_s ∇T_s) = 0            in Ω_s
    T_s = T_Γ                    on Γ_if      (temperature continuity, eq:iftemp)
    +k_s ∇T_s·n_out = q''        on Γ_h⁰      (prescribed flux, B6)
    k_s ∇T_s·n = 0               on Γ_end, Γ_h^out, Γ_c⁰ (B7, B8)

If instead the interface datum is the conjugate flux, every boundary condition is of Neumann type:
the bilinear form has the constant in its kernel, so **the solution set is a line**, and it is
non-empty only when `∮ (k_s∇T_s·n) = ∫q'' + ∫q_Γ + 0 = 0`. At an intermediate iterate the fluxes do
not balance, so the iterate is not merely non-unique — it is **unsolvable**. That is a stronger
statement than "the level is free", and it is the statement the chapter now makes.

With one Dirichlet surface (`Γ_if`) the problem is uniquely solvable for every admissible flux data
(Lax–Milgram; the trace `T_Γ ∈ H^{1/2}(Γ_if)`). Uniqueness is therefore decided by *which* datum is
transferred, not by any additional condition.

### 1.3 Is there a legitimate interface/reference condition?

Yes, and it was already in the model: `eq:iftemp` (temperature continuity) together with the inflow
datum `T_in` of B1. In the *model* neither side alone fixes the level; the conjugated pair does.
In the *algorithm* the level is inherited through `T_Γ^{(k)}`, i.e. it is an **output** of the
conjugate problem, not a datum. Accordingly:

* **no reference temperature was introduced;**
* **no gauge, no mean-zero projection, no "set the average to zero" device was added to `T_s`;**
* the model is unchanged — only the order in which the two subproblems are solved.

This satisfies the instruction not to set a datum merely to force uniqueness: the physical condition
that determines the level (`T_in` through the interface equation) is the one the manuscript already
had, and it is now stated where it bites.

### 1.4 What changed in the sources

| Location | Before | Now |
|---|---|---|
| `ch08` `sec:iteration` step 1 | solid receives `q_Γ` (Neumann) | solid receives `T_Γ^{(k)}` (Dirichlet) on `Γ_if`, `+k_s∇T_s·n=q''` on `Γ_h⁰`; extracts `q_Γ^{(k)}` |
| `ch08` step 2 | fluid receives `T_Γ` (Dirichlet) | fluid receives `q_Γ^{(k)}` (Neumann), level anchored by `T_in` (B1); extracts `T_Γ^{(k+1)}` |
| `ch08`, new paragraph | "flux fixes the level" | kernel/compatibility argument: constant in the kernel, solvability requires balanced fluxes, "doubly inadmissible"; no reference temperature invented |
| `ch05` `sec:datamodel` | ambiguous data flow | pure-Neumann inadmissibility stated as a property of the *model*, then the unique algorithm that avoids it; pointer to D-32 |
| register | — | **D-32** added (32 rows now) |
| solver spec §12 | — | corrected order, code-level requirements, verification hooks |

### 1.5 Trace into the results (the chain the instruction asked for)

Level of `T_s` → `θ̄` → `N_θ` (eq:ntheta) → `κ_geo`, `w_max` → `M_mid`, `σ_bend` → `Γ_p`.
Recomputed from inputs parsed out of `ch02`/`ch09`:

| Quantity | Recomputed | Printed |
|---|---|---|
| `θ̄` | `32.2652 K` | `32.3` |
| `N_θ` | `−2.9039×10⁴ N/m` | `−2.91×10⁴` |
| `N_cr` | `1.05746×10⁵ N/m` | `1.057×10⁵` |
| `μ`, `μL` | `54.876 m⁻¹`, `1.64629` | `55`, `1.65` |
| `w_max` | `2.18858×10⁻⁴ m` | `2.19×10⁻⁴` |
| `M_mid` | `−6.35535 N·m/m` | `−6.4` |
| `σ_bend` | `4.2369 MPa` | `4.2` |
| `Γ_p` mixed / like-for-like | `2382.1` / `1726.3` | `2.4×10³` / `1.73×10³` |
| self-consistent `w_max` | `2.13988×10⁻⁴ m` | `2.14×10⁻⁴` |

**No printed number changed.** That is the correct outcome: the physical level was always the one set
by `T_in`; the defect was that the stated algorithm could not reach it.

---

## 2. P2 — NEW-02: expected value versus manuscript rounding

The recomputation layer parses the inputs (`E`, `ν`, `α`, `k_s`, `ρ`, `μ`, `c_p`, `k_f`, `H₀`, `L`,
`d`, `U`, `q''`, `L_o`, `Nu_H1`) out of the manuscript and recomputes every printed result instead of
comparing text with text. Internal precision is kept at full double precision and the comparison is
made at the precision the manuscript actually prints:

* the exact `θ̄ = 32.26516…` K is printed as `32.3` K; the check allows `0.05` K, i.e. the printed
  3-significant-figure rounding, and would fail on `32.2` or `32.4`;
* `N_cr = 1.057 46×10⁵` is printed `1.057×10⁵` (4 s.f.) — tolerance `0.5 %`;
* `w_max = 2.188 58×10⁻⁴` is printed `2.19×10⁻⁴` — tolerance `1 %`;
* `σ_bend = 4.2369` is printed `4.2` — tolerance `2 %`;
* `Γ_p` mixed `2382.1` is printed `2.4×10³` (−0.75 %), like-for-like `1726.3` printed `1.73×10³`
  (+0.21 %) — tolerance `1–2 %`.

The rounding is stated separately from the arithmetic, so a value that is *correct but printed with
too few digits* is distinguished from a value that is wrong. Mutation A5 (`32.3 → 34.3`) and A7
(`q'' 5.0 → 6.0 kW/m²`) both fail the check, so a corrupted input or a corrupted printed value is
caught rather than tolerated by a loose band.

---

## 3. P3 — NEW-05: the end effect is 0.2 %, not "a few per cent"

| Claim | Where it stood | Now |
|---|---|---|
| "a few per cent" end stiffening | `ch04`, `ch11` | deleted; replaced by the measured `0.2 %` |
| "one-time numerical check" still outstanding | `ch04`, `ch11` | deleted; the check is complete and its result is quoted |
| "closing the residual" | `ch11` | deleted |
| measured values | — | `1.0000` (point pins), `0.998` (full-edge support, free axial mean), `−0.02…−0.06` (clamp), register **D-26** |

Neither the admissibility argument (A-3 mesh bound, A-6 stress cap) nor any printed result moves: the
penalty is an order of magnitude below the bound it was invoked for. The `ch07` caveat that the base
case is a conservative *idealisation* is retained — it never claimed a per-cent figure.

---

## 4. P4 — mutation campaign: 25 independent mutants reproduced, plus 9 new ones

    $ python3 audit_stage15/mutation_campaign_stage17.py
    base PASS
    ...
    DETECTED 34 / 34, SURVIVING 0  (caught by a numeric/identity check: 25;
                                    caught only by the equation fingerprint: 9)

Isolated copies under `/tmp/hff_mut17/`; the harness aborts if the baseline fails and reports
`ANCHOR COUNT ≠ 1` instead of silently skipping, so no mutant can pass vacuously.

### 4.1 The 25 Stage 16 mutants

**Detected 25/25.** Three had to be **re-anchored** because the Stage 17 repair rewrote the sentence
they attacked (recorded in the campaign file and in §4 of `06_regression_results.md`):

| Mutant | Why re-anchored |
|---|---|
| A8 (hidden pressure gauge) | the `D-25` sentence now reads "corrected in D-30" |
| A15 ("few per cent") | that claim was withdrawn — the mutant now *restores* it |
| A17 (loop closure removed) | the loop sentence was rewritten for D-32 |

No survivor remains, so no explanation of a survivor is owed. What *is* owed is the honest caveat in
§4.3.

### 4.2 The 9 new mutants (they attack the Stage 17 repairs)

| ID | Mutation | Caught by |
|---|---|---|
| B1 | step 1 reverts to the solid flux datum | `step 1 gives the solid T_s = T_Gamma^{(k)} …` |
| B2 | deletes the kernel/compatibility argument | `the kernel/compatibility argument is spelled out` |
| B3 | `ch05` claims the flux datum is well posed | `ch05 and ch08 agree that a solid flux datum is inadmissible` |
| B4 | `0.2 % → 2 %` | `ch04 states the measured 0.2 % with its Q8 evidence` |
| B5 | drops `(mixed)` from the `Γ_p` row | `ch07 table labels Gamma_p mixed` |
| B6 | like-for-like `1.73 → 1.93` | `appendix A8 like-for-like Gamma_p matches` |
| B7 | renumbers `D-32 → D-33` | `no equation or register row removed` |
| B8 | doubles `N_θ^c/d` in `eq:weaks` | `geometric term present, negative, with N/d` |
| B9 | `ch05` pointer `D-32 → D-31` | `ch05 and ch08 agree …` |

### 4.3 What the campaign does and does not prove

* Nine mutants are caught **only** by the equation-fingerprint layer. That layer hashes every display
  equation and every register row, so it detects *any* edit to an equation — including a legitimate
  one. It is a change detector, not a proof of correctness, and it is reported as such.
* The other 25 are caught by a check that recomputes the quantity from parsed inputs or verifies an
  exact identity (`κ_geo = κ_th sec(μL/2)`, `(κ+κ_th)/(κ−κ_th) = cot²(μL/4)`, the beam–column ODE and
  its four boundary conditions).
* Passing 34/34 therefore does **not** mean "the equations are right". It means "no single-token
  corruption of these sources survives this suite". Semantic errors that are internally consistent —
  e.g. a wrong constitutive assumption carried consistently through every printed number — would
  still pass, and only the independent audit can address that class.

---

## 5. P5 — I-11 closed at the presentation level, I-13/I-15 stay open, I-15 not claimed

### 5.1 I-11 (`Γ_p` mixed versus like-for-like) — five presentation sites + the A-5 statement

| # | Site | Now |
|---|---|---|
| 1 | `ch04` prose | mixed `2.4×10³` labelled; like-for-like `w_p(N_θ^c)=1.27×10⁻⁷ m → 1.73×10³` given |
| 2 | `ch07` results table | row reads `Γ_p = w_max/w_p`, "(mixed)", `2.4×10³` (`≥5`, A-5 met) |
| 3 | `ch07` prose | both ratios quoted with their definitions |
| 4 | appendix A8 | `Γ_p = 2.19×10⁻⁴/9.2×10⁻⁸ = 2.4×10³` labelled *mixed*; the like-for-like value follows with D-29 |
| 5 | appendix dictionary | the `Γ_p` row records `(mixed; like-for-like 1.73×10³, D-29)` |
| — | `ch06` A-5 | evaluated on the like-for-like ratio, which is the stricter of the two; A-5 is met either way |

The **author's** choice of a headline ratio remains `OPEN-AD` — it is a reporting decision, not an
error, and both numbers are now visible wherever one is quoted.

### 5.2 I-13 (provenance/staleness)

Reassessed, **not closed**: `main.pdf` still predates every modified source; `regression.py` §7 and
`README.md` say so. A rebuild is required and cannot be executed here (no `pdflatex`, `latex`,
`tectonic` or `lualatex`). The claim "the package is current" is not made anywhere.

### 5.3 I-15 (figure collisions)

**Left OPEN by instruction.** The figure sources are checked for brace/label structure only. No
visual check was performed and none is claimed; a TikZ build plus a rendered-page inspection is
required.

---

## 6. Dependencies rechecked after the thermal fix

See `07_final_consistency_audit.md` §"Stage 17 recheck": the chain `θ̄ → N_θ → κ_geo → w_max →
M_mid → σ → Γ_p` was recomputed, and the model/algorithm/solver-spec triple was read side by side.
Five consistency statements were checked: one assignment (solid Dirichlet → fluid Neumann) in all
three places; both interface equations still enforced as the two halves of the loop; no datum
invented; the level traced to `θ̄`/`N_θ`/geometric stiffness; and no printed result changed.

---

## 7. Test suite v3 (I-07) — what it adds

| Layer | Purpose |
|---|---|
| structural | braces, environments, 89 labels, no dangling references, citations, 32 register rows |
| claims | sign conventions, BCs, function spaces, thermal well-posedness (D-32), `Γ_p` labelling, 0.2 % wording |
| fingerprints | SHA-256 of 76 canonicalised equation/register bodies |
| inputs | every material and operating input parsed from the manuscript |
| recompute | 43 printed results recomputed from those inputs |
| identities | `κ_geo = κ_th sec(μL/2)`, `(κ+κ_th)/(κ−κ_th) = cot²(μL/4)`, ODE + 4 BC residuals |

    $ python3 audit_stage15/regression.py
    ALL 109 CHECKS PASSED

---

## 8. Commit record

| Commit | Contents |
|---|---|
| `dc29b3d` | parent: Stage 16 audit artefacts (unchanged) |
| *(this commit)* | Stage 17 source corrections (D-32, D-26/NEW-05, D-29/I-11, `sec:iteration` label), `regression.py` v3 + `equation_fingerprints.json`, `mutation_campaign_stage17.py` + results log, updates to `01`, `05`, `06`, `07`, `08`, `09`, `10`, this report and `13_…`, rebuilt ZIP + manifest |

The commit hash cannot be written into a file inside that same commit; it is recorded in the commit
message and in `git log`, and the pushed tip of `arena/c875f9b3-hff-final-overleaf-package-fix` is the
authoritative pointer. Evidence hashes: the ZIP's SHA-256, its size, its member count and the SHA-256
of every member are in `audit_stage15/package_manifest.txt`, regenerated with the archive.

## 9. What is still wrong or unresolved

1. **RU-01 / B-7** — casing clearance, contact law, vented vs sealed cavity: not in the source.
   Three branches and their consequences are enumerated in `02_…` §4. Minimum author decision: state
   the standoff and whether the cavity is vented.
2. **RU-03** — the `1.4377 H₀` mid-span height is a consequence of the adopted convention, not a
   measurement; it needs the same author decision.
3. **Headline `Γ_p`** — which of `2.4×10³` (mixed) and `1.73×10³` (like-for-like) the paper leads
   with.
4. **I-13 / I-15** — no build, no render, no visual check.
5. **Independence** — none of the above is self-approved. A fresh independent audit is requested in
   `13_stage17_audit_request.md`.
