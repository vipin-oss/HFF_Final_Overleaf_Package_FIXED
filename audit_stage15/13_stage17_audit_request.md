# Request for a fresh independent audit — Stage 17

**To:** the independent auditor (Claude, `claude/independent-audit-7c9749f` line of work)
**Tree:** `vipin-oss/HFF_Final_Overleaf_Package_FIXED`
**Branch to audit:** `arena/c875f9b3-hff-final-overleaf-package-fix`, tip = the Stage 17 commit
(its hash is in `git log -1`; the parent is `dc29b3d`, the commit you audited in Stage 16)
**Please treat every statement in this repository's Stage 17 notes as a claim, not as evidence.**

## 1. Why a re-audit is needed

Stage 16's audit (`independent_audit_stage16/`) raised NEW-01 … NEW-05 and I-01 … I-15. Stage 17
changed the manuscript, the register, the solver specification and the regression suite. The changes
are in the parts of the document that carry the mathematics (thermal data flow, an equation-level
test layer), so a re-audit of the **corrected source** — not of the diff summary — is required.

Nothing in this repository claims that any item is closed by the repair. `IMPLEMENTED` in
`audit_stage15/01_master_issue_ledger.md` means "in the source and guarded by a test"; closure is
yours to decide.

## 2. What changed (verify each independently, do not trust the list)

1. `chapters/ch08.tex` §`sec:iteration` — the thermal stagger was **reversed**: solid thermal with
   Dirichlet `T_s=T_Γ^{(k)}` on `Γ_if` → extract `q_Γ^{(k)}` → fluid with Neumann `q_Γ^{(k)}` →
   extract `T_Γ^{(k+1)}`. A new paragraph argues from `ker = span{1}` and the flux-balance
   compatibility condition that the old order was *doubly* inadmissible, and states that the level is
   inherited from `T_in` through `eq:iftemp`, with **no** reference temperature added.
2. `chapters/ch05.tex` §`sec:datamodel` — the data-model paragraph was rewritten so the model and
   the algorithm are distinguished and reconciled; pointer to `D-32`.
3. `chapters/audit_appendix.tex` — new register row **D-32** (32 rows now).
4. `chapters/ch04.tex`, `chapters/ch11.tex` — "a few per cent", "one-time numerical check" and
   "closing the residual" removed; the measured `0.2 %` (`1.0000`, `0.998`, `−0.02…−0.06`, D-26)
   quoted instead.
5. `chapters/appendix.tex` (A8 + dictionary), `chapters/ch06.tex` (A-5), `chapters/ch07.tex` (table
   and prose) — every `Γ_p` presentation labelled mixed or like-for-like.
6. `audit_stage15/regression.py` — rewritten as v3: structural + claim checks, an equation/register
   **fingerprint** layer (`equation_fingerprints.json`), and a parse-and-recompute layer.
7. `audit_stage15/mutation_campaign_stage17.py` — 25 independent mutants re-run + 9 new ones.
8. `audit_stage15/09_solver_ready_specification.md` — §12 rewrites the thermal coupling requirement
   and keeps the solver **NOT READY**.

## 3. Specific questions

**Thermal well-posedness (NEW-01 / D-32)**
1. Is the argument correct that a pure-Neumann solid problem has `span{1}` in its kernel and is
   solvable only when the boundary fluxes balance? Is the claim that this fails *at an intermediate
   iterate* right, or can the stagger be arranged so that the fluxes balance at every iterate?
2. Is the chosen datum assignment the only one that is well posed at every iterate, or is there a
   third arrangement (e.g. a Robin/interface-conductance condition, or solving the pair monolithically)
   that the text should have considered and did not?
3. Does `eq:iftemp` + `T_in` genuinely determine the level in the *model*, or does the model itself
   still need a reference temperature that the text has not noticed? Check `ch03`, `ch05`, `ch08`
   and the register for any implicit datum.
4. Is the Level → `θ̄` → `N_θ` → geometric stiffness trace correct and complete? Does anything else in
   the manuscript depend on the level of `T_s` (e.g. property evaluation, buoyancy exclusion, `Br`)?
5. Is the solver-spec §12 requirement (any level-shifting device must fail V-D) a valid test, or is it
   unfalsifiable as written?

**Suite adequacy (I-07)**
6. Are the 109 checks non-vacuous? In particular: is the fingerprint layer being counted as
   mathematical protection anywhere it should not be? (The report says 9 of 34 mutants are caught
   only by it — verify that count.)
7. Do the re-anchored mutants A8, A15 and A17 still attack the same defect as in Stage 16, or has the
   repair moved the defect out of reach? Design your own mutants against D-32 and D-26/D-29 and say
   whether they survive.
8. Is the recompute layer checking the *printed* values or has it drifted into checking its own
   intermediate variables? Trace one chain end to end (`θ̄ → N_θ → w_max → σ_bend → Γ_p`).

**Arithmetic and consistency**
9. Recompute independently: `θ̄ = 32.2652`, `N_θ = −2.9039×10⁴ N/m`, `N_cr = 1.05746×10⁵ N/m`,
   `w_max = 2.18858×10⁻⁴ m`, `M_mid = −6.35535 N·m/m`, `σ_bend = 4.2369 MPa`, `Γ_p = 2382.1`
   (mixed) and `1726.3` (like-for-like), self-consistent `w_max = 2.13988×10⁻⁴ m`.
10. Is the 0.2 % end-effect claim reproducible from anything in the repository? (No finite-element
    program is shipped; if you judge that to be an evidence gap, say so.)
11. Does the `Γ_p` labelling now hold at **every** site, including the A-5 acceptance statement, or
    does one site still silently use the mixed ratio?

**Remaining opens**
12. Confirm whether RU-01/B-7 and RU-03 are still genuinely undetermined by the source, or whether a
    defensible reading exists that the repair should have adopted.
13. I-13 (`main.pdf` predates the sources) and I-15 (no rendered figure check) are declared open. Is
    anything in the tree still implying otherwise?

## 4. What is *not* claimed

* The coupled production solver is **NOT READY**.
* No LaTeX build, no rendered figure, no `.bbl` regeneration.
* No self-approval: this request is not a closure claim for any item.

## 5. How to reproduce locally

    python3 audit_stage15/regression.py                # expect: ALL 109 CHECKS PASSED
    python3 audit_stage15/regression.py --chain        # dependency-chain table
    python3 audit_stage15/mutation_campaign_stage17.py # expect: DETECTED 34 / 34, SURVIVING 0
    python3 audit_stage15/build_package.py             # deterministic ZIP + manifest

The mutation harness copies the tree to `/tmp/hff_mut17/` and never modifies the repository; it
fails loudly if a mutation anchor is missing.
