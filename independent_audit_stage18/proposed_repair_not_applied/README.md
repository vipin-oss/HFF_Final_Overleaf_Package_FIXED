# Auditor prototype — **NOT APPLIED** to the audited commit

This directory is *not* part of commit `5741d36` and was **not applied** to it. It is a reviewer's
prototype, recorded so that the next implementation cycle does not have to rediscover the four/five
blind spots reported in `../HFF_Stage18_Final_Acceptance_Audit.md` §7.

While auditing, the reviewer developed and ran the hardening below on a scratch copy of the tree,
then **reverted every change to `audit_stage15/`** so that the audited commit and the shipped package
remain exactly as delivered. `git status` on the audit branch shows no modification under
`audit_stage15/`; the patches here are the complete record of what was tried.

## Contents

| File | What it is |
|---|---|
| `regression_stage19_hardening.patch` | `git diff` of `audit_stage15/regression.py` (v4 → prototype v5, 144 → 148 assertions) |
| `mutation_campaign_stage18_results_option.patch` | adds `--results PATH` so a re-run cannot overwrite the committed Stage 18 record |
| `mutation_campaign_stage19.py` | 8 permanent cases for the escaped classes + 2 controls (P1 legitimate rewording, F2 legitimate equation addition) |
| `stage19_mutation_results.txt` | raw results of that campaign |
| `stage18_campaign_rerun_stage19.txt` | the 44-case Stage 18 campaign re-run against the prototype suite |
| `suite_stage19_148.txt` | prototype suite log, `ALL 148 CHECKS PASSED` |

## What the prototype changes

1. **Gauge (M3c).** Adds pointwise/other-notation pressure normalisations
   (`p(\mathbf 0)=0`, `p|_{x_0}=0`, `p(0)=0`) to the normalisation detector, and adds a positive
   control that the *legitimate* outflow datum is still a boundary value `p → 0` on B2, so the check
   cannot pass vacuously.
2. **Adopting verbs (M6b).** Extends the adopting vocabulary (`pin`, `pinned by`, `anchored`,
   "level … is set by"), so "we choose … **rather than** …" is no longer read as a rejection.
3. **`tab:bcs` rows (M7).** The double-datum test no longer selects rows by `Γ_if` in the Boundary
   cell: any row carrying a solid Dirichlet **and** a solid Neumann datum fails, and a non-zero solid
   flux datum is admissible only on the heated outer face (zero-flux end/face data stay allowed).
   The original `Γ_if`-row check is kept unchanged, so the Stage 18 campaign's declared assertion
   still exists.
4. **Prose (M8).** Sentence-level detection of a solid Dirichlet datum together with a non-zero solid
   flux datum that is not explicitly placed on the heated face; `longtable` bodies are removed before
   the scan so table rows are not flattened into one "sentence".
5. **Stale magnitudes (M10).** Accepts `pct`, `percentage points`, `per-cent` as spellings of a stale
   end-effect claim.
6. **I-13 provenance (§7 of the suite).** Reports the PDF's embedded `CreationDate` and states that
   mtimes in a fresh checkout cannot establish provenance; adds a README provenance assertion.
7. **§7 wording.** Replaces "the tracked main.pdf does NOT contain the Stage 18 corrections" with the
   stage-neutral "current source corrections".

## Evidence produced by the prototype (on a scratch copy, not on `5741d36`)

* prototype suite on the current sources: **148/148, exit 0**;
* 8/8 new mutants detected for their intended assertion, 0 escaped, 0 invalid, 0 anchor-missing;
* 2/2 controls behaved as intended (a reworded rejection and a legitimate new display equation both
  pass, the latter reporting a new fingerprint key as INFO);
* the Stage 18 campaign re-run against the prototype: **44/44, 36 substantive + 8 fingerprint-only**;
* registering the fingerprints on a clean tree reproduces `equation_fingerprints.json`
  **byte-for-byte** (76 entries);
* 6 non-vacuity probes still caught.

These numbers describe the prototype. They are **not** claims about `5741d36`, whose own suite is
144/144 and which still contains the five blind spots.
