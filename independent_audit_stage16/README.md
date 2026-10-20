# Independent audit of the HFF Stage 16 implementation

Audited branch: `arena/c875f9b3-hff-final-overleaf-package-fix`
Audited commit: `b63d34c145428ec7a07642fe5d551f34f50f2f14` (verified before and after the audit)
Previous audit: `claude/independent-audit-7c9749f` at baseline `7c9749f`

## Contents

| File | Purpose |
|---|---|
| `HFF_Claude_Independent_Audit_Stage16.md` | the audit report: per-item verdicts, derivations, source locations, smallest corrections, gate verdicts |
| `evidence/verify_numerics.py`, `evidence/output_numerics.txt` | independent re-derivation of every printed baseline number from the printed inputs |
| `evidence/q8_pin_verification.py`, `evidence/output_q8_pin.txt` | independent Q8 plane-strain FE: point pin / full-edge pin / clamp, with derivative, patch and exact-field tests |
| `evidence/gauge_and_geometric_term.py`, `evidence/output_gauge_geom.txt` | discrete pressure-gauge functional and the 2-D -> 1-D reduction of the geometric term |
| `evidence/mutation_campaign.py`, `evidence/output_mutations.txt` | 25 adversarial source mutations scored against `audit_stage15/regression.py` |

All four scripts run from the repository root with the standard library only:

    python3 independent_audit_stage16/evidence/verify_numerics.py
    python3 independent_audit_stage16/evidence/q8_pin_verification.py
    python3 independent_audit_stage16/evidence/gauge_and_geometric_term.py
    python3 independent_audit_stage16/evidence/mutation_campaign.py   # writes isolated copies under /tmp

`mutation_campaign.py` copies the repository into `/tmp/audit16/m/<id>` for each mutant; it never
writes into the working tree.

## Provenance note

This directory is committed on the Arena working branch because that is the only branch the tooling
used here is permitted to write to. It is the auditor's deliverable, not part of the author's Stage 16
submission, and nothing under `chapters/`, `figures/` or `audit_stage15/` was modified by the audit.
To publish it on the dedicated audit branch while preserving history:

    git checkout claude/independent-audit-7c9749f
    git checkout <this-commit> -- independent_audit_stage16
    git commit -m "Independent audit of Stage 16 (b63d34c)"
    git push origin claude/independent-audit-7c9749f

(or create `claude/independent-audit-b63d34c` from it in the same way).
