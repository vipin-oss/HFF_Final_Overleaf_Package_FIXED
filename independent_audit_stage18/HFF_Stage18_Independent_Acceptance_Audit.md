# HFF Stage 18 — Independent Acceptance Audit

**Status: STOPPED AT §1 — NO STAGE 18 SUBMISSION EXISTS.**
The audit instruction (§1) requires: *"If the expected Stage 18 commit or required artefacts cannot
be located, stop and report the limitation. Do not silently audit a different commit."* That is what
this report does.

**Auditor role:** independent auditor. No manuscript, figure, test, package or commit content was
modified. The only addition is `independent_audit_stage18/` (this report and its evidence).
**Audit date:** 2026-10-20 (UTC); user time zone Asia/Kolkata.

---

## 0. Headline

| Question | Answer |
|---|---|
| Is there a Stage 18 commit? | **No.** Newest implementation commit is Stage 17 `211f751`; newest commit of any kind is the Stage 17 audit `4f54aa8`. |
| Is there a Stage 18 repair report / suite / campaign / raw results? | **No.** `audit_stage15/` ends at `13_stage17_audit_request.md`; the suite self-identifies as *"version 3 (Stage 17)"*. |
| Can the §2 acceptance test be executed? | **No** — there is no Stage 18 test command to run. |
| Final decision (§8) | **REJECT Stage 18 as an acceptance request** — there is no submission to accept. This is *not* a judgement of Stage 18 code, because no Stage 18 code exists. |
| Solver readiness (§9) | **NOT READY** (unchanged). |

**Supplementary evidence, clearly labelled:** because the only suite in the tree is the Stage 17
suite, I re-ran the seven counterexamples and F1 against **HEAD as it stands**. All seven still pass
the suite (exit code 0, 109/109) and F1 is still accepted after `--update-fingerprints`. These runs
are labelled **current-state (suite v3, Stage 17)** everywhere and are *not* presented as a Stage 18
audit.

---

## 1. Freeze and target search

### 1.1 Repository state at audit time

| Item | Value |
|---|---|
| Branch | `arena/c875f9b3-hff-final-overleaf-package-fix` |
| HEAD | `4f54aa88e1b605f8f37645254ca57d56f34f5f2c` — "Independent Stage 17 audit of 211f751: report + reproducible evidence" |
| HEAD's parent (Stage 17 implementation) | `211f75163485a2b209b79fb3e22ecb0d7227d342` |
| `origin/<session branch>` | `4f54aa8…` (same as HEAD) |
| `origin/main` | `5a255212a51374f7eb178647eb12b0a9c2b67ded` (untouched) |
| Working tree | clean (`git status --porcelain` empty before the audit; only `?? independent_audit_stage18/` after) |
| Remote refs (`git ls-remote origin`) | `HEAD`, `refs/heads/main`, `refs/heads/arena/c875f9b3-…`, `refs/heads/claude/independent-audit-7c9749f` (`227f749`) |
| Interpreter | Python 3.11.2 |
| TeX toolchain | `pdflatex`, `latex`, `lualatex`, `xelatex`, `latexmk`, `tectonic`, `bibtex`, `biber`, `pdftoppm`, `pdftotext`, `gs`, `qpdf`, `inkscape` — **all MISSING** |

Evidence: `evidence/target_search.txt`, `evidence/toolchain_and_tree.txt`.

### 1.2 Searches performed for a Stage 18 submission

| Search | Result |
|---|---|
| `git log --all --oneline --grep="Stage 18" -i` | **no commits** |
| `git ls-remote origin` (all branch heads) | three branches only: `main`, session branch (`4f54aa8`), `claude/independent-audit-7c9749f` (`227f749` — the Stage 15-era Claude audit, inspected: no Stage 18 content) |
| `git for-each-ref` (tags, all refs) | no tags; no additional refs |
| `find . -iname '*18*'` outside `.git` | only the directory this audit created |
| `grep -rIl "Stage 18"` over the whole tree | **no files** |
| `audit_stage15/` listing | `01…13` only — no `14_stage18_*`, no `*_stage18_*` |
| `git diff --stat 211f751 HEAD -- chapters audit_stage15 figures main.tex references.bib` | **empty** — no implementation file has changed since Stage 17 |

### 1.3 Required Stage 18 artefacts versus what exists

| Required artefact (§1) | Status | Nearest thing in the tree |
|---|---|---|
| Stage 18 commit hash | **ABSENT** | `211f751` (Stage 17 implementation) and `4f54aa8` (Stage 17 audit) |
| Stage 18 repair report | **ABSENT** | `audit_stage15/12_stage17_repair_report.md` |
| Stage 18 regression suite | **ABSENT** | `audit_stage15/regression.py`, header: *"HFF regression suite, version 3 (Stage 17)"*, 109 assertions |
| Stage 18 mutation definitions | **ABSENT** | `audit_stage15/mutation_campaign_stage17.py`, 34 mutants (A1–A25, B1–B9) |
| Stage 18 raw results | **ABSENT** | `audit_stage15/mutation_stage17_results.txt` |
| Package manifest | present, **unchanged** | `audit_stage15/package_manifest.txt`; ZIP `8f67ef7c…d5d1`, 802 932 B, 75 members |
| Stage 17 baseline `211f751` | **present** ✓ | ancestor of HEAD |
| Stage 17 audit report | **present** ✓ | `independent_audit_stage17/HFF_Stage17_Independent_Audit.md` (49 917 B) |

**Conclusion of §1:** the Stage 18 target does not exist in this repository or on any remote ref.
The seven defects that Stage 18 is supposed to repair are therefore necessarily unrepaired — not
because of a coding failure I can inspect, but because no repair was submitted.

---

## 2. The seven counterexamples and F1

### 2.1 Why this cannot be an acceptance run

§2 requires: *"Run the actual Stage 18 test command"*. There is no Stage 18 test command. Running
`audit_stage15/regression.py` and reporting its behaviour as "Stage 18 detection" would be exactly
the silent substitution §1 forbids. I therefore split the evidence:

- **§2.2 (current-state, not Stage 18):** what the only suite in the tree does with the seven
  defects today. This is recorded so that the acceptance question has a factual baseline, and so
  that no reader can mistake "109/109 passing" for evidence of repair.
- **§2.3 (the acceptance protocol):** the exact commands, expected assertions and expected exit
  codes that must hold for the *next* submission to be accepted (or rejected) on evidence.

### 2.2 Current-state reproduction — **suite v3 (Stage 17), HEAD `4f54aa8`**

Command: `python3 independent_audit_stage18/evidence/seven_cases_rc.py`
(fresh isolated copy per case under `/tmp/audit18/cases`; one anchor replacement each; repository
never modified). Raw output: `evidence/seven_cases_rc.txt`.

Baseline first: `exit=0 PASS=109 FAIL=0 clean`.

| Case | Defect injected | Suite exit | PASS | Verdict | First failing assertion |
|---|---|---|---|---|---|
| **G1** | gauge constraint re-inserted immediately beside its own explanation (keeps the "corrected in D-30" pointer) | **0** | **109** | **ESCAPE** | *(none)* |
| **G2** | gauge constraint invented in `ch05` (`∫_{Γ_out}p dY = 0`) | **0** | **109** | **ESCAPE** | *(none)* |
| **G3** | `Γ_if` given Dirichlet temperature **and** Neumann flux in step 1 (over-determined solid subproblem) | **0** | **109** | **ESCAPE** | *(none)* |
| **T1** | `θ̄` cell corrupted: `ΔT_t/3 + q''/(2h) + ΔT_b/2` | **0** | **109** | **ESCAPE** | *(none)* |
| **T2** | `T̄_cr` 117 K → 130 K (the `M_b ≥ 2` bound depends on it) | **0** | **109** | **ESCAPE** | *(none)* |
| **N1** | label removed from the actual `Γ_p` nomenclature entry (`appendix:49`) | **0** | **109** | **ESCAPE** | *(none)* |
| **S1** | stale end-stiffening claim re-added in alternative wording ("about two per cent") | **0** | **109** | **ESCAPE** | *(none)* |
| **F1 step 1** | `eq:wmax` `κ_thL²/8 → κ_thL²/12` | **1** | 108 | detected | `no display equation has changed \| ['eq:eq:wmax']` |
| **F1 step 2** | …then `--update-fingerprints` and re-run | **0** | **109** | **ESCAPE** | *(none)* |

Summary line from the run: `escapes 7 / 7 cases; F1 accepted-after-regen=True`.

Interpretation (strictly about the current tree):
- None of the seven defects is detected, and each run is a **clean** 109/109 (no unrelated failure,
  no syntax error, no missing file), so these are genuine blind spots, not artefacts.
- The fingerprint layer detects the corrupted display equation **only until the fingerprint file is
  regenerated by the suite's own documented flag**; after that the mathematically corrupted
  `eq:wmax` is accepted at 109/109.
- The controls in the same harness are detected (`θ̄ 32.3→32.4`, `N_θ` shifted 7 %, `eq:ifflux` sign
  flip), which shows the suite is not simply inert.

### 2.3 Acceptance protocol for a future Stage 18 submission

A submission is acceptable only if, in a clean copy of the submitted commit, each of the following
fails **for the intended reason** (named assertion referring to the edited artefact), with a
non-zero exit code, and with the baseline passing first:

| Case | Required detection (intended reason) | Minimum acceptable assertion shape |
|---|---|---|
| G1 | the inserted gauge relation is flagged as a gauge constraint, *not* as a lost pointer | an occurrence-level assertion on `∫p…=0` relations that is not disabled by nearby explanatory text |
| G2 | same, with `ch05` in scope | the assertion must scan at least `ch05`, `ch08`, appendix |
| G3 | the boundary-condition **set** on `Γ_if` is rejected | per-boundary count of thermal data: exactly one of Dirichlet/Neumann for a given field |
| T1 | the `θ̄` table cell is rejected | the formula cell (or its canonical fingerprint) must be covered |
| T2 | `T̄_cr` recomputed and compared; `M_b` recomputed from it | numeric recomputation from `π²d²/[12α(1+ν)L²]`, not a hard-coded 117.5 |
| N1 | the nomenclature entry itself is checked | assertion anchored at `appendix:49`, not at the table row |
| S1 | the stale claim class is rejected regardless of wording | claim-level test (value/magnitude), not a phrase match |
| F1 | corruption survives `--update-fingerprints` or regeneration is itself guarded | either a numeric/semantic check of the equation's consequence, or a fingerprint-update guard that refuses silently legitimising an edit |

Anything less — including "the mutant now fails because a register pointer moved" — does not count.

---

## 3. Test-suite audit (the only suite present: v3, Stage 17)

Because no Stage 18 suite exists, this section audits the current suite as it stands and records the
residual blind spots that a Stage 18 submission would have to close. Classification is by what each
assertion actually does (AST extraction, `independent_audit_stage17/evidence/check_classification.py`;
the file is unchanged since `211f751`, so the Stage 17 taxonomy applies verbatim):

| Class | Count | Comment |
|---|---|---|
| Independent numerical recomputation | **42** | 34 `cmp` calls + 8 `check`s; inputs parsed from `ch02`/`ch09`, results compared with printed values |
| Prose-value consistency | 4 | `circular-arc` band, `σ_fr > σ_sc`, `0.2σ_y`, `ch07` stress set |
| Structural / semantic assertion | 8 | braces, environments, labels, refs, citations, macros, register-row count |
| Fingerprint-based change detection | 3 | aggregates over 44 equation entries + 32 register rows |
| File / text-presence (claim string) | **50** | substring presence/absence; no recomputation |
| Vacuous or ineffective | **1** | `regression.py:174–175`, `check(..., ('I-15' in read(...)) or True)` — constant PASS |

**Count integrity:** 77 static `check` sites, of which 2 are the body of `cmp`, plus 34 `cmp`
invocations → **109 executed assertions**, and the suite reports **109**. The reported count matches
what is genuinely executed. ✔

**Required properties of §3, checked against the current suite:**

| Property | Result |
|---|---|
| No unconditional-success expressions remain | **FAIL** — `or True` still present at `regression.py:175` |
| Missing targets cannot silently pass | **PASS** — emptying `appendix.tex` gives 89 PASS / 20 FAIL, exit 1, and every appendix-dependent numeric check fails with `printed=None`; deleting `ch08.tex` aborts with `KeyError` (exit 1) — safe, but not a graceful diagnostic (evidence: `missing_target_probe.txt`) |
| A fingerprint update cannot make a corrupted equation acceptable | **FAIL** — proved by F1 (accepted at 109/109 after `--update-fingerprints`) |
| Table cells covered | **FAIL** — `θ̄` cell (`ch07:34`) and `T̄_cr` row (`ch07:38`) are neither fingerprinted nor recomputed (T1, T2) |
| Nomenclature entries covered | **FAIL** — the "dictionary" assertion matches the table row at `appendix:136`, not the entry at `appendix:49` (N1) |
| Boundary-condition sets covered | **FAIL** — no assertion enumerates conditions per boundary; G3 passes |
| Dependent claims covered | **FAIL** — `M_b = 117.5/32.3` uses a hard-coded 117.5; nothing recomputes `T̄_cr` |
| Rounding tolerances justified by displayed precision | **PASS** — e.g. `θ̄` uses ±0.05 K against a one-decimal print (half-ULP); the 0.1 K positive control is caught |
| Reported count matches executed count | **PASS** — 109 = 109 |

**Residual blind spots (explicit, not claimed complete):** the seven cases above; plus the
±260-character "explained" exemption window around the gauge test; plus the fact that 50 of 109
assertions are string-presence checks (12 of the campaign's 25 "non-fingerprint" kills are of that
kind). A passing count is not evidence of semantic coverage.

---

## 4. Thermal formulation and numerical consistency

| Check (§4) | Finding |
|---|---|
| Solid Dirichlet on `Γ_if` + prescribed heater flux on `Γ_h⁰` | **Preserved** — `ch08:174–180` unchanged (`git diff 211f751 HEAD` empty for `chapters/`) |
| Fluid Neumann interface flux with inlet datum `T_in` | **Preserved** — `ch08:181–187`, `ch05:46` unchanged |
| Sign/normal/unit consistency of the interface coupling | **Preserved** — Stage 17 audit's Gate A verification stands; sources byte-identical |
| Level dependence through `θ̄ → N_θ →` geometric stiffness | **Preserved** — same equations, same dependence |
| **Documentation adds the limitation that well-posed subproblems do not prove convergence** | **NOT MET** — no such sentence exists (`grep` for "not proved / not shown to converge / no convergence proof" in `ch08.tex`: no hits). This was required correction **C2** of the Stage 17 audit and remains open |
| **`‖ΔT_Γ‖` defined and used in the stopping criterion** | **NOT MET** — no `ΔT_Γ` increment appears in `ch08.tex`; the stopping rule (`ch08:199–203`) remains displacement-based (`‖Δd‖_∞ ≤ 10⁻⁶ w_max`) |
| Numerical values and rounding unchanged without justification | **PASS** — unchanged, and no justification is needed because nothing changed. Re-running my independent recomputation reproduces the Stage 17 audit's numbers byte-for-byte (`diff` empty: `evidence/numerics_rerun.txt`) |
| Convergence proof or adequate coupled numerical study | **ABSENT** — none exists in the tree; a stopping criterion is not a convergence proof |

I did **not** infer a convergence proof from the stopping criterion, and I did **not** treat the
absence of a Stage 18 commit as evidence that convergence was addressed.

---

## 5. Mutation campaign

**Documented Stage 18 campaign: ABSENT.** The only campaign is
`audit_stage15/mutation_campaign_stage17.py` (34 mutants: A1–A25 from the Stage 16 audit, B1–B9 for
the Stage 17 repairs). I re-executed it at HEAD (`evidence/current_state_campaign34.txt`):

```
baseline ... PASS
DETECTED 34 / 34, SURVIVING 0
(caught by a numeric/identity check: 25; caught only by the equation fingerprint: 9)
exit 0
```

| Metric | Value | Note |
|---|---|---|
| Total mutants attempted | 34 | all anchors found (`count == 1`); no SKIPs |
| Detected | 34 | suite exit ≠ 0 |
| Detected by **numeric** check | **10** | re-classified in the Stage 17 audit (`evidence/check_classification.txt`) |
| Detected by **claim string** | **12** | A8, A9, A16, A17, A21, A23, B1, B2, B3, B5, B8, B9 |
| Detected by **pattern guard** | 3 | A15, A19, B4 |
| **Fingerprint-only** | **9** | A1–A4, A10, A11, A18, A22, B7 |
| Unrelated failures | 0 | each failure names the edited artefact |
| Surviving mutants in this campaign | 0 | — |
| Surviving defects from the *independent* set | **7 of 7** | §2.2 |
| Commands | `python3 audit_stage15/mutation_campaign_stage17.py`; `python3 independent_audit_stage18/evidence/seven_cases_rc.py` | both executed in this audit |

So: the campaign's own 34/34 claim reproduces, but it is not evidence that Stage 18 fixed anything —
there is no Stage 18, and the seven defects the campaign never contained are still alive.

---

## 6. Unresolved release gates

| Gate | State | Evidence |
|---|---|---|
| **I-13** fresh LaTeX/TikZ build + package freshness | **OPEN** | no TeX engine of any kind (`pdflatex`, `latex`, `lualatex`, `xelatex`, `latexmk`, `tectonic`, `bibtex`, `biber` all MISSING); the suite still reports `main.pdf predates 15 source file(s)` as a *warning only* |
| **I-15** figure rendering and visual validation | **OPEN** | no renderer (`pdftoppm`, `gs`, `inkscape` MISSING); ImageMagick's PDF coder is policy-disabled; no PDF reader library |
| Coupled thermal-loop convergence / escalation | **OPEN** | no convergence statement, no `‖ΔT_Γ‖` criterion, no coupled run |
| **RU-01** casing clearance / contact / vented vs sealed | **OPEN-AD** | no standoff distance; outer face mechanically free (B8) while the strip bows 0.219 mm toward the casing |
| **RU-03** `1.4377 H₀` mid-span height | **OPEN-AD** | value appears only in `audit_stage15/`, never in `chapters/` |
| Heater mounting / heated-face interpretation | **OPEN-AD** | `q''` on `Γ_h⁰` is a design choice; no mounting/contact-resistance model |
| Contact law | **OPEN-AD** | A8 perfect contact assumed, no resistance/gap conductance |
| Headline `Γ_p` definition | **OPEN-AD** | mixed (2382) reported, like-for-like (1726) disclosed (D-29) |

No part of this audit marks any of these closed, and no improved test count is presented as
validating any of this physics.

---

## 7. Package and repository integrity

| Check | Result |
|---|---|
| Shipped ZIP unchanged | `8f67ef7c03e8d4e138383d87e9b7237c994c51125f959dc3981c77f5d6f5d5d1`, 802 932 B, 75 members |
| Manifest | 75 rows; **75/75 member digests match**; no extra members; CRC (`testzip`) ok; fixed timestamps `2026-10-19 00:00:00` |
| Deterministic rebuild | **PASS, executed here**: `git archive HEAD` into an empty directory, `python3 audit_stage15/build_package.py` → `8f67ef7c…d5d1`, 802 932 B, 75 members — byte-identical to the shipped ZIP |
| Implementation unchanged except declared Stage 18 modifications | **no Stage 18 modifications exist**; `git diff 211f751 HEAD` over `chapters audit_stage15 figures main.tex references.bib` is **empty** |
| `origin/main` untouched | `5a255212…` locally and in `git ls-remote` |
| Audit did not modify the implementation | working tree clean apart from `?? independent_audit_stage18/`; all mutation runs in `/tmp`, one fresh copy per case |
| Build / render / push claims | none made beyond the audit commit itself |

Evidence: `evidence/package_verify.txt`, `evidence/rebuild_determinism.txt`,
`evidence/target_search.txt`, `evidence/toolchain_and_tree.txt`.

---

## 8. Findings and final decision

### 8.1 Findings

| ID | Severity | Finding | Status |
|---|---|---|---|
| **AU18-01** | **BLOCKER (for the acceptance question)** | No Stage 18 commit, repair report, suite, campaign, raw results or manifest update exists on any local or remote ref. HEAD is the Stage 17 audit commit; the newest implementation commit is `211f751` | **OPEN** |
| AU18-02 | HIGH | The seven Stage 17 counterexamples (G1, G2, G3, T1, T2, N1, S1) pass the only suite in the tree at 109/109, exit 0 | **OPEN (unrepaired)** |
| AU18-03 | HIGH | F1 still accepted: `eq:wmax` corrupted to `κL²/12` is rejected only until `--update-fingerprints`, after which it passes 109/109 | **OPEN (unrepaired)** |
| AU18-04 | MEDIUM | The convergence limitation sentence (Stage 17 audit C2) was never added | **OPEN** |
| AU18-05 | MEDIUM | `‖ΔT_Γ‖` is neither defined nor used in the stopping criterion | **OPEN** |
| AU18-06 | LOW | The vacuous `or True` assertion remains (`regression.py:174–175`) | **OPEN** |
| AU18-07 | MEDIUM | Table cells (`θ̄`, `T̄_cr`), the nomenclature entry and the boundary-condition set remain uncovered | **OPEN** |
| AU18-08 | — | I-13 and I-15 remain OPEN; no build or render was possible or claimed | **OPEN-ENV** |
| AU18-09 | — | RU-01, RU-03, heater face, contact law, headline `Γ_p` remain author decisions | **OPEN-AD** |

### 8.2 Final decision

**REJECT — Stage 18 is not accepted.**

Not because its code is wrong (there is none), but because **the object of the audit does not
exist**: the acceptance criteria of §2 cannot be satisfied by a submission that was never made, and
an "ACCEPT" recorded against `211f751`/`4f54aa8` would be a silent substitution of a different
commit — precisely what §1 prohibits.

The formal status is therefore: **no Stage 18 submission; acceptance refused; the Stage 17 defects
are unrepaired.**

### 8.3 Solver readiness

**NOT READY** — unchanged from the Stage 17 audit. Well-posed subproblems do not prove convergence
of the staggered iteration; no coupled run exists; RU-01/RU-03, the heater face, the contact law and
the `Γ_p` headline remain undecided; and no build of the manuscript can be produced or inspected in
this environment.

---

## 9. What would make the next audit auditable

1. A **commit** on a reachable ref, quoted by hash, containing:
   - a Stage 18 repair report (`audit_stage15/14_stage18_repair_report.md` or similar) that states,
     for each of G1, G2, G3, T1, T2, N1, S1, F1: the assertion added, the file/line range it reads,
     and the expected exit code for the mutant;
   - the updated suite, with a version string identifying Stage 18 (the current header still says
     *"version 3 (Stage 17)"*);
   - the permanent mutation definitions including the seven cases, and raw results for the full
     campaign (including the controls);
   - an updated manifest/ZIP **only if** the package changes, with the member list and digests.
2. The suite must show, per §2.3, that each case fails **for its intended reason**, not through a
   moved pointer, a missing anchor, or a fingerprint regeneration.
3. The manuscript-side items (C2 convergence-limitation sentence, `‖ΔT_Γ‖` criterion) must be in
   `chapters/ch08.tex`, since they are documentation, not test infrastructure.
4. Until then, no acceptance claim should be made, and `34/34` or `109/109` should not be quoted as
   evidence of repair.

---

## 10. Discipline and limitations of this audit

- No source, figure, test, package or commit was modified. The only addition is
  `independent_audit_stage18/`.
- Every mutation ran in a fresh isolated copy under `/tmp/audit18/cases`; the repository's
  `regression.py` and `equation_fingerprints.json` were never regenerated in place.
- I did not audit a different commit as if it were Stage 18. The only suite runs reported are
  explicitly labelled **current-state (suite v3, Stage 17)** and are supplementary.
- No build, render, PDF inspection, deterministic-rebuild or coupled-solver run is claimed in this
  audit.
- **Branch limitation (documented, not worked around):** this session is bound to
  `arena/c875f9b3-hff-final-overleaf-package-fix`. I could not publish on a separate independent
  audit branch. The report is committed on the session branch under `independent_audit_stage18/`;
  `origin/main` and `claude/independent-audit-7c9749f` were not touched.

---

## Appendix A — reproduction

```bash
cd /home/user/HFF_Final_Overleaf_Package_FIXED        # HEAD 4f54aa8, tree clean

# target search (all of these return nothing for Stage 18)
git log --all --oneline --grep="Stage 18" -i
git ls-remote origin
find . -path ./.git -prune -o -iname '*18*' -print
git diff --stat 211f751 HEAD -- chapters audit_stage15 figures main.tex references.bib

# current-state suite and campaign (suite v3 = Stage 17)
python3 audit_stage15/regression.py                              # 109/109, exit 0
python3 audit_stage15/mutation_campaign_stage17.py               # 34/34, exit 0
python3 independent_audit_stage18/evidence/seven_cases_rc.py     # 7 escapes + F1 accepted
python3 independent_audit_stage17/evidence/verify_package.py     # 75/75 digests
python3 independent_audit_stage17/evidence/auditor_numerics4.py  # identical to Stage 17 output

# determinism (working tree untouched)
rm -rf /tmp/audit18/rebuild && mkdir -p /tmp/audit18/rebuild
git archive HEAD | tar -x -C /tmp/audit18/rebuild
cd /tmp/audit18/rebuild && python3 audit_stage15/build_package.py
sha256sum HFF_Final_Overleaf_Package.zip      # 8f67ef7c…d5d1, 802932 bytes, 75 members
```

Evidence files: `evidence/{target_search,toolchain_and_tree,suite_v3_run,seven_cases_rc,
current_state_g1_g3_t1_t2_n1_s1_f1,current_state_campaign34,package_verify,numerics_rerun,
missing_target_probe,rebuild_determinism}.txt`.
