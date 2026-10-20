# Stage 19 — Targeted verification hardening after conditional acceptance

**Stage commit:** the commit that adds this report. Its hash is in the commit message and cannot be
written here: this file is a member of the ZIP that the same commit ships, so a literal self-hash
would be wrong the moment it was written (the same constraint recorded in `14_stage18_repair_report.md`
§15). Verify with `git log -1 -- audit_stage15/15_stage19_repair_report.md`.
**Parent on entry:** `39ef118` (the independent Stage 18 acceptance audit).
**Audited implementation baseline:** `5741d36d6f0f9911bfe3f338fb5f77ba94e1d7ea`.
**Scope:** bounded repair of the five verification blind spots and the two manuscript defects named
by that audit, plus the Q8 evidence scope. No new physics, no changed physical assumption, no changed
numerical result except the one display rounding the audit identified.

This report separates three things that must not be conflated: **implementation success** (§10), the
**acceptance decision** (§11, which is *not* mine to make — a fresh independent audit is requested),
and **production-solver readiness** (§12, unchanged: NOT READY).

---

## 0. Headline

| Item | Before (`5741d36`) | After (this commit) |
|---|---|---|
| Regression suite | v4, **144** assertions, all passing | v5, **156** assertions, all passing |
| Five audited blind spots | **5 escapes** (M3c, M6b, M7, M8, M10) | **0 escapes** |
| Stage 18 campaign | 44/44 (36 substantive + 8 fingerprint-only) | 44/44 (36 + 8), re-run unchanged |
| Stage 19 campaign | — | **10/10 detected**, all substantive; **3/3 controls pass** |
| Positive controls | P1 **wrongly rejected** by v4 (a false positive) | P1, P2, P3 all pass |
| Fingerprints | 76 entries | 78 entries, byte-stable; 1 changed key (D-26), 2 added (D-33, D-34), 0 display equations |
| `ch06` `T_in` clause | "exclusively through property values" (false for `T_in`) | `T_in` stated as the B1 datum and the level anchor; `T_ref = T_in` convention stated (D-33) |
| `M_b = 2` ceiling | 58.8 K (double rounding) | **58.7 K** (correct rounding of 58.7476 K), register D-34 |
| Q8 claim | "the check is complete" | values stated as **one 24-element mesh**, finite-mesh evidence, not converged |
| Package | 78 members, `d7b80365…` | rebuilt deterministically; count/hash in `package_manifest.txt` |
| I-13, I-15 | OPEN | **OPEN** (no TeX engine, no renderer) |
| Solver | NOT READY | **NOT READY** |

---

## 1. What was reproduced before anything was changed

The instruction was to inspect the auditor's prototype rather than trust it, and to reproduce every
finding first. The prototype was read; its approach was **not** adopted wholesale (its stale-magnitude
and prose rules depend on phrase lists, and it did not test the pointwise `\mathbf 0` spelling that the
audit's own mutation used). Instead, the five classes were re-derived from the audit's mutation
descriptions and re-run against the untouched baseline.

**Evidence `stage19_before_after.txt`, first block.** A pristine `git archive 5741d36` tree plus the
Stage 19 campaign script:

```
REQUIRED CLASSES 5 (M3c M6b M7 M8 M10): detected 0 of 5
ALL MUTANTS 10: detected 5, escaped 5, invalid 0, anchor not applied 0
CONTROLS 3: 2 passed as intended        <-- P1, a legitimate rejection, was REJECTED by v4
```

So the audit's five findings are exact, and suite v4 additionally had a **false positive**: a
correctly worded rejection ("No normalisation is imposed: constraining `∫ p ds = 0` would
over-determine the system") was rejected because the negation did not reach "is imposed" across the
noun "normalisation". Closing the holes without fixing that would have made the check a phrase trap.

### 1.1 The two manuscript defects, reproduced independently

Computed from the manuscript's own inputs with independent parsers (`d = 3 mm`, `α = 5×10⁻⁵ K⁻¹`,
`ν = 0.4`, `L = 9 mm`, `q'' = 5 kW m⁻²`):

```
T_cr  (full precision)        = 117.4952904892 K
T_cr/2 (full precision)       = 58.7476452446 K
one-decimal display           = 58.7 K        <-- correct
printed route 117.5/2         = 58.75 -> 58.8 K  <-- rounds twice
q'' at the ceiling            = 9103.87 W/m2 -> 9.1e3 (unchanged)
M_b                           = 3.641547 (unchanged)
theta-bar                     = 32.26521 K (unchanged)
```

and for the reference-temperature defect: `θ̄ = ΔT_t/2 + q''/h + ΔT_b/2` with
`ΔT_b = q''L/(ρUH₀c_p) = 1.4354 K` measured from the **inlet** plane, so
`θ̄ = T̄_wall − T_in`, i.e. the quoted value assumes `T_ref = T_in`. `T_in` is the B1 Dirichlet datum,
not a property input.

---

## 2. The five classes, closed — rule, evidence, and what remains heuristic

Each case is applied to a fresh isolated copy after a clean baseline run; a case counts only if the
suite completes, exits non-zero, and the **declared intended assertion** is among the failures.

| Class | v5 rule (structural, not a phrase list) | Exit | Failing check (intended) |
|---|---|---|---|
| **M3c** pointwise gauge `p(\mathbf 0)=0` | `P_NORM` gains pointwise notations (`p(\mathbf 0)=0`, `p(0)=0`, `p(\mathbf x_0)=0`, `p\big|_{x_0}=0`); verdict scoped to the clause carrying the constraint | 1 | `a pressure normalisation occurs only as an explicitly rejected counterfactual` |
| **M6b** "we choose … rather than …" | `CLAUSE_SPLIT` treats `rather than`, `instead of`, `although`, `but`, `while`, `;`, `:` as clause boundaries, so the rejection attached to the *alternative* cannot launder the adoption clause; `ADOPT` also gains `choose/pin/anchor/…` as a second line of defence | 1 | same gauge assertion |
| **M7** double datum, `Condition` column, Boundary cell without `Γ_if` | `tab:bcs` is tested **row by row for every surface**: solid Dirichlet + solid Neumann ⇒ failure; a non-zero solid flux datum is admissible only on the heated face (zero flux stays admissible on ends/faces) | 1 | `no tab:bcs row gives any surface a solid Dirichlet AND a solid Neumann thermal datum` (plus the flux-surface assertion) |
| **M8** prose double datum without "on surface" | datum-**shape** rule per sentence: a solid Dirichlet datum (`T_s=`) together with a non-zero solid flux datum (`∇T_s·n=`, `∂_nT_s=`) that is not placed on `Γ_h^0` | 1 | `no prose datum gives the solid a temperature AND a non-heated-face heat flux in one sentence` (plus the flux-surface assertion) |
| **M10** stale magnitude "2 pct" | `STALE` accepts `pct`, `percentage points`, hyphenated `per-cent` in addition to `per cent`/`%` | 1 | `no stale end-effect percentage survives in the 22 scanned files` |

Reproduced-notation variants checked by hand during development (each fails the gauge assertion,
none is a required campaign case): `p(\mathbf 0)=0`, `p(\mathbf{0})=0`, `p(0)=0`, `p\big|_{x_0}=0`.
A legitimate boundary value (`p(0)=120` Pa at the inlet end, `p→0` at the outlet) does **not** fire.

### 2.1 Known limitations of the heuristic parts (stated, not hidden)

These are the honest boundaries of the new rules; they are not claims of completeness.

1. **Clause splitting is lexical.** It recognises the connectives listed above. A rejection expressed
   with a connective outside that list (e.g. "except that", "save for") in the same clause as an
   adopting verb could still be mis-scored — in either direction. The rule is stricter than v4
   (a normalisation clause now needs its own rejection), so the failure mode is a false rejection,
   which is visible immediately, not a silent pass.
2. **The pointwise notation list is finite.** `p` fixed at a point written in an unanticipated form
   (e.g. an index set `p|_{i=0}=0`, or "the pressure vanishes at the origin" in words) is not
   recognised. The list covers the algebraic notations in use in this manuscript.
3. **The prose datum rule needs the datum to be written as an equation.** "The solid is held at the
   interface temperature" (words, no `T_s =`) is not seen. It also assumes that a non-zero solid flux
   belongs on the heated face; a future second heated surface would need the rule extended.
4. **The table rule tests rows, not the physical set.** It cannot know that two *different* rows
   impose incompatible data on the same surface unless both rows are written in datum form.
5. **The stale scan is a magnitude scan.** It catches the numbers `1/2/3/one/two/three/few/couple`
   before a percentage word. A stale magnitude written "0.5 pct" or "ten per cent" is not caught
   (it was not caught before either); extending it would risk false positives on legitimate values.
6. **All of these are regression pins on statements, not proofs of the physics.** Passing suite v5
   means the manuscript still says what it is supposed to say; it does not mean the physics is right.

---

## 3. Positive controls (permanent, in `mutation_campaign_stage19.py`)

| Control | Text added to a clean copy | Why it is a valid control | Result |
|---|---|---|---|
| **P1** | "No normalisation is imposed: constraining `∫_{Γ_out} p ds = 0` would over-determine the system." | A legitimate rejection: the constraint is named **and** rejected in the same clause, with no adopting verb. It is exactly the kind of sentence the check must allow — and it was **wrongly rejected by v4**, so it guards against over-correction. | **PASS** (rc 0) |
| **P2** | "Equivalently, one statement prescribes `T_s = T_Γ^{(k)}` on `Γ_if` and `+k_s∇T_s·n_out = q''` on `Γ_h^0`, so no second thermal datum is introduced." | A legitimate combined statement: it carries a Dirichlet interface datum **and** a flux, but the flux is explicitly on the heated face. It is the exact discrimination the M8 rule relies on; if the rule were "any sentence with both", every correct description of step 1 would fail. | **PASS** (rc 0) |
| **P3** | A new display equation `a² + b² = c²` added to `ch10` | A legitimate addition must be *reported*, never failed: fingerprints are change detectors, and an addition is not an edit of an existing expression. Verifies the fingerprint layer's semantics. | **PASS** (rc 0), `new fingerprint keys (deliberate additions)` printed as INFO |

`CONTROLS 3: 3 passed as intended`, exit 0 for the campaign.

---

## 4. Manuscript corrections

### 4.1 `ch06` — `T_in` is a datum, not a property input (register D-33)

Replaced the clause "Only temperature differences appear … so `T_ref` and `T_in` enter the solution
exclusively through property values" with a statement that `T_ref` enters through property values and
through `T_in − T_ref`, that **`T_in` is the inflow Dirichlet datum of B1 and the anchor of the
interface temperature level via `eq:iftemp`**, that the quoted `θ̄` is measured from the inlet bulk
temperature and therefore uses **`T_ref = T_in`**, and that a solver taking `T_in ≠ T_ref` must carry
the offset explicitly. No physical model changes; no printed value changes.

### 4.2 `ch07` — the `M_b = 2` ceiling is 58.7 K (register D-34)

`\bar\theta \le 58.8` K → **`58.7` K**, with a pointer to D-34. The dependent flux ceiling
(`q'' ≈ 9.1×10³ W m⁻²`), `M_b = 3.64`, the thickness catalogue and every other printed value are
unchanged. The regression assertion compares the displayed value with `round(T_cr/2, 1)` at `1e-12`
(**no tolerance**), so reverting to 58.8 fails.

### 4.3 Q8 evidence scope (ch04, ch11, ch02 A9, register D-26)

The six-mesh study was re-run on this tree (§5). The measured values are preserved
(`1.0000`, `0.998`, `−0.02 … −0.06`), and all four sites now state that they are values on **one
24-element mesh** (twelve elements along, two through the thickness), that the `0.2 %` difference
between the two pin idealizations is reproduced at two and four elements through the thickness, that
the absolute ratios shift with the through-thickness discretisation, and that the clamp band is
**finite-mesh evidence, not a converged penalty**. `ch04` now quotes the difference as
`0.0019` of `κ_thL²/8` to keep the claim numerical and to avoid a second "0.2 %" claim in the same
paragraph (which would also have broken the Stage 18 mutation B4's unique anchor).

---

## 5. Q8 six-mesh study (re-run in Stage 19)

Only `NX, NY` are changed in each variant; the shipped verifier
`independent_audit_stage16/evidence/q8_pin_verification.py` is otherwise untouched.

| mesh | elements | POINT mid/top | PIN mid/top | CLAMP mid/top |
|---|---|---|---|---|
| 6×2 | 12 | 1.0025 / 1.0000 | 1.0024 / 0.9999 | −0.0761 / −0.0803 |
| 12×2 | 24 | 1.0025 / 1.0000 | 1.0006 / 0.9981 | −0.0408 / −0.0450 |
| 24×2 | 48 | 1.0025 / 1.0000 | 1.0004 / 0.9979 | −0.0245 / −0.0288 |
| 6×4 | 24 | 1.0056 / 1.0025 | 1.0054 / 1.0023 | −0.0564 / −0.0617 |
| 12×4 | 48 | 1.0056 / 1.0025 | 1.0037 / 1.0006 | −0.0284 / −0.0336 |
| 24×4 | 96 | 1.0056 / 1.0025 | 1.0036 / 1.0005 | −0.0159 / −0.0211 |

Reading: the point-pin ratio does not move with axial refinement (it depends on the through-thickness
discretisation); the pin ratio approaches 1 as the axial mesh is refined; the clamp magnitude falls
monotonically under every refinement. The quoted `1.0000`/`0.998` pair is therefore a finite-mesh
pair, and the `0.2 %` **difference** between them is the part that is stable across meshes
(0.0019 at 12×2 and at 12×4). This is exactly what the manuscript now says.

Shipped-script diagnostics re-confirmed: shape-derivative check `4.5×10⁻¹¹`, exact-field residual
`1.4×10⁻⁹` against a load scale of `1.9×10⁴`.

---

## 6. Stage 18 protection preserved

The 44-case campaign was re-run **unchanged** against suite v5:

```
TOTAL CASES 44: detected 44, escaped 0, invalid 0, anchor not applied 0
  of the 44 detections, 36 are supported by the substantive layer and 8 are FINGERPRINT-ONLY
```

That includes the cases the audit asked to preserve: `eq:wmax` corruption with and without
`--update-fingerprints` (F1), the `θ̄` table cell (T1), `T̄_cr` and the `M_b ≥ 2` claim (T2, A5–A7),
gauge reintroduction (G1, G2, A8), double thermal boundary data (G3, B1, B3, B9), the `Γ_p`
nomenclature (N1, B5, B6, A12), and stale end-effect claims (S1, S2, A15).

No tolerance was loosened (the ceiling assertion was **tightened** from a 0.5 % tolerance to exact
rounding), and the Stage 18 check names are retained so the campaign's declared assertions still
resolve. One Stage 18 assertion was **subsumed, not dropped**: `no Gamma_if row prescribes a solid
flux datum` tested only `Γ_if` rows, and is replaced by `no tab:bcs row puts a non-zero solid flux
datum on a surface other than the heated face`, which fails on the same mutation (a `Γ_if` row is not
the heated face) and additionally covers every other surface. The `Γ_if` double-datum assertion from
Stage 18 is kept verbatim under its original name.

**Two deliberate test changes, both documented:**

1. `register rows present and counted` now expects **34** rows (two Stage 19 register entries added).
2. `the M_b = 2 ceiling reproduces the quoted 58.8 K` became
   `the M_b = 2 ceiling is the correctly rounded T_cr/2 (58.7 K)` with an exact-rounding criterion.

One campaign anchor was repaired in the *case list*, not in the suite: `mutation_campaign_stage19.py`
initially declared M8 against the prototype's check name; the suite's name differs, and the campaign
correctly refused to count it as detected (`INVALID`) until the declaration was corrected. That is the
campaign's intended behaviour and is recorded here rather than quietly patched.

---

## 7. Fingerprints: what changed, what it proves

* **76 → 78 entries.** Regenerated once, deliberately, because content changed:
  `reg:D-26` **changed** (scope sentence), `reg:D-33` and `reg:D-34` **added**, **nothing removed**,
  and **no display-equation fingerprint changed** — confirming that the manuscript corrections were
  prose and table work, not equation changes.
* **Stability:** regenerating on a pristine copy of the tree reproduces the committed file
  **byte-for-byte** (`b5e9be8e…`, 78 entries).
* **What they prove:** that an expression or register row is unchanged since the file was written.
  **What they do not prove:** that it is correct. F1 is re-verified in the Stage 19 campaign (W2:
  `eq:wmax` denominator 8 → 7 **with** `--update-fingerprints` still fails the substantive
  denominator check), and the parse guards added in §8 close the "unparseable expression silently
  skips its numeric checks" weakness the audit flagged as A2.
* No fingerprint was regenerated to hide a substantive failure: the regeneration is a consequence of
  two new register rows and one edited register row, all described above and in the ledger.

---

## 8. Suite v5: what was added beyond the five classes

| Addition | Why |
|---|---|
| `the eq:wmax constants are parseable (so the value can be checked at all)` | v4 silently skipped the numeric block when the parser failed (audit A2); now the run fails with a reason that names the cause |
| `the eq:tcr denominator coefficient is parseable (so T_cr can be checked at all)` | same |
| `the outflow pressure datum is a boundary value, not an interior point constraint` | positive control inside the suite: the gauge test must not be satisfied by deleting the legitimate `p → 0` datum |
| `no tab:bcs row puts a non-zero solid flux datum on a surface other than the heated face` | the M7 class, stated as a property of the data set rather than of one row; **subsumes** the Stage 18 `Γ_if`-only flux assertion (verified: the M7 mutation and a `Γ_if` flux mutation both fail this one) |
| `ch06 states that T_in is the inflow datum, not a property input`; `ch06 states the T_ref = T_in convention …` | pins the §4.1 correction |
| `ch04 scopes the Q8 values to one finite mesh …`; `ch11 scopes …`; `the D-26 register row states the Q8 finite-mesh scope` | pins the §4.3 correction |
| `the ledger records the Stage 19 repairs` | the ledger is the provenance of record; it must not silently drop the stage |

Suite size: **156 assertions** (`ALL 156 CHECKS PASSED`, exit 0, `stage19_regression_results.txt`).

---

## 9. Validation runs — exact commands, counts, exit codes

All mutation runs used isolated copies (`/tmp/hff_mut19/...`, `/tmp/hff_mut18/...`), each cloned from
the tree, with a clean baseline run first. The repository was never mutated by a test.

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `python3 audit_stage15/regression.py` | **156/156 PASS** | 0 |
| 2 | `python3 audit_stage15/mutation_campaign_stage18.py --results audit_stage15/stage19_campaign44_rerun.txt` | **44/44 detected** (36 substantive, 8 fingerprint-only) | 0 |
| 3 | `python3 audit_stage15/mutation_campaign_stage19.py` | **10/10 detected**, 0 escapes, 0 invalid, 0 anchor; **5/5 required classes** | 0 |
| 4 | same script, controls P1/P2/P3 | **3/3 passed** | 0 |
| 5 | `python3 independent_audit_stage18/evidence_stage18_final/nonvacuity_probe.py "$PWD"` | **6/6 probes caught, 0 vacuous** (`stage19_nonvacuity.txt`) | 0 |
| 6 | `python3 audit_stage15/regression.py --update-fingerprints` on a pristine copy | **byte-identical** fingerprints, 78 entries (`stage19_fingerprint_stability.txt`) | 0 |
| 7 | `python3 audit_stage15/build_package.py` twice from independent clean copies | identical archives; manifest/digests/order/CRC verified (§13) | 0 |
| 8 | Campaign against a pristine `5741d36` tree (before/after evidence) | **5 escapes reproduced**, 0/5 required classes (`stage19_before_after.txt`) | 1 (expected) |

**Not executed, and why:**

| Not executed | Reason |
|---|---|
| LaTeX build (`pdflatex` ×4, `bibtex`) | no TeX engine in this environment — **I-13 stays OPEN** |
| Figure render / visual collision check | no renderer — **I-15 stays OPEN** |
| Any coupled solver run, interface-temperature history, convergence rate | no solver exists; **NOT READY** |
| PDF text/page verification | no `pdftotext`/`pypdf` |

---

## 10. Implementation success (this stage only)

**Successful, within the stated scope.** The five audited classes are closed with structural rules
(§2), the two manuscript defects are corrected with independent recomputation (§1.1, §4), the Q8
claims are scoped to the evidence actually available (§4.3, §5), Stage 18 protection is preserved
unchanged (§6), and every validation in §9 was executed with the recorded counts. Two test-side
defects were found and fixed during the work and are disclosed rather than hidden: the v4 false
positive on legitimate rejection prose (P1), and the stale M8 expectation in the new campaign.

**What this does not establish:** that the suite is complete. It now resists five specific
constructions; §2.1 lists where it is still heuristic. The audit's own standard — *passing the suite
is necessary but not sufficient* — still applies.

---

## 11. Acceptance decision (not mine to make)

This stage is an **implementation** stage. It does not accept its own work. A fresh independent audit
against the exact Stage 19 commit is requested; the following are the questions it should put to this
commit:

1. Re-run suite v5 and both campaigns from a pristine `git archive` of the Stage 19 commit; confirm
   156/156, 44/44 (36+8), 10/10 with 3/3 controls.
2. Re-derive the five rules independently and attempt to evade them again — in particular: a
   normalisation with a connective outside the split list; a pointwise datum in words; a datum split
   across two sentences; a table row whose two data are on different surfaces.
3. Recompute `T̄_cr/2` and check the displayed 58.7 K is the one-decimal rounding of the exact value.
4. Check that the `T_ref = T_in` convention is what the quoted `θ̄` actually uses, and that no printed
   number changes under it.
5. Decide whether the Q8 scope statements are sufficient, or whether the manuscript should also state
   the through-thickness sensitivity of the absolute ratios.
6. Confirm that the fingerprint regeneration contains exactly the three register-row changes claimed
   and no equation change.
7. Verify package determinism and the member set independently.

**Conditions carried forward from Stage 18, still open:** C2 (LaTeX rebuild + visual check), C3
(author decisions on RU-01, RU-03, heater mounting, contact law, headline `Γ_p`), C4 (do not read the
Q8 numbers as converged), C5 (keep "well-posedness is not convergence" and the undemonstrated
tolerance), C6 (reference-temperature convention — **now done**, register D-33).

---

## 12. Production-solver readiness

**NOT READY — unchanged.** No subproblem was solved, no staggered iteration was run, no interface
temperature history exists, and no convergence rate or stagnation evidence has been produced. The
manuscript's convergence paragraph (well-posedness is not convergence; `‖ΔT_Γ^{(k)}‖` monitored with
the tolerance left to a mesh/iteration study; the flux-jump criterion is a-posteriori only) remains
correct and remains the whole of what is claimed. RU-01, RU-03, the heater mounting and the contact
law are unresolved and change the geometry and load path; they are the author's to decide and have not
been decided here.

---

## 13. Package

`python3 audit_stage15/build_package.py` writes `HFF_Final_Overleaf_Package.zip` with fixed member
order, fixed timestamps and no byte-code caches, then `audit_stage15/package_manifest.txt` with the
archive SHA-256, its size, its member count and every member's digest. The manifest is **not** a
member (it cannot hash itself), which is why the authoritative hash lives there and not in this
report.

Verification performed (evidence `stage19_package_verify.txt`):

* two independent rebuilds from two clean copies produce **identical bytes**;
* member count, order and every member digest recomputed from the archive match the manifest;
* every member is byte-identical to the file on disk;
* `ZipFile.testzip()` → no CRC error; all timestamps `2026-10-19 00:00:00`; deflate level 9;
* no `__pycache__`/`.pyc` members.

The member set gains `audit_stage15/15_stage19_repair_report.md`, `mutation_campaign_stage19.py`,
`stage19_mutation_results.txt`, `stage19_before_after.txt`, `stage19_nonvacuity.txt`,
`stage19_fingerprint_stability.txt`, `stage19_regression_results.txt`,
`stage19_campaign44_rerun.txt` and `stage19_package_verify.txt`, and loses nothing.

---

## 14. Files changed in this stage

| File | Change |
|---|---|
| `chapters/ch06.tex` | `T_in` / `T_ref` clause corrected (D-33) |
| `chapters/ch07.tex` | ceiling 58.8 → 58.7 K, pointer to D-34 |
| `chapters/ch04.tex` | Q8 scope; `0.0019` difference; clamp band as finite-mesh evidence |
| `chapters/ch11.tex` | Q8 scope |
| `chapters/ch02.tex` | A9: Q8 scope sentence |
| `chapters/audit_appendix.tex` | D-26 scope; **D-33**, **D-34** added (32 → 34 register rows) |
| `audit_stage15/regression.py` | v5: five classes closed, parse guards, Stage 19 pins, ceiling tightening, register count |
| `audit_stage15/mutation_campaign_stage19.py` | **new**: 10 mutants (5 required) + 3 controls, fresh copies, declared assertions, `--results` |
| `audit_stage15/mutation_campaign_stage18.py` | `--results` option only, so a re-run cannot overwrite the Stage 18 record |
| `audit_stage15/equation_fingerprints.json` | regenerated once: 78 entries, `reg:D-26` changed, `reg:D-33/34` added |
| `audit_stage15/01_master_issue_ledger.md` | Stage 19 section (S19-1 … S19-9, controls, tally) |
| `audit_stage15/05_correction_log.md` | Stage 19 section (S19-A … S19-D) |
| `audit_stage15/stage19_*.txt` | raw logs: regression, campaigns, before/after, non-vacuity, fingerprints, package |
| `HFF_Final_Overleaf_Package.zip`, `audit_stage15/package_manifest.txt` | rebuilt deterministically |

Nothing in `main.tex`, `references.bib`, the figures, or any display equation was touched. The
audited commit `5741d36` and the audit commit `39ef118` are unchanged; `origin/main` and the
`claude/…` branch were not modified.
