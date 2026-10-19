# Final packaging report — `HFF_Final_Overleaf_Package.zip`

**Package built:** 19 October 2026 (this report is part of the package it describes).
**Provenance:** the ZIP root is the compilation directory. `main.pdf` was produced by
pdfLaTeX → bibtex8 → pdfLaTeX ×2 from **exactly** the root-level sources in this archive —
no older PDF was reused.

## Compilation facts

| Item | Value |
|---|---|
| Output | `main.pdf`, 49 pages, 469,859 bytes |
| `main.pdf` SHA-256 | `59916a98cc082ded19c96d97b603797088b0ee865b654fa602373afa07939dba` |
| Errors / undefined refs / citations | 0 / 0 / 0 |
| LaTeX warnings | 0 |
| Toolchain | TeX Live 2026 engine (BusyTeX/wasm build, Overleaf-pdfLaTeX-compatible package set); `bibtex8` interchangeable with Overleaf's `bibtex` for this all-ASCII bibliography |

## ZIP structure (actual entries at build time)

ZIP **root** (Overleaf project root — upload the ZIP directly):

```
main.tex                                  <- Overleaf main document
references.bib                            <- 18 entries
README.md                                 <- upload + compile instructions (matches this package)
main.pdf                                  <- compiled from the sources above (hash above)
chapters/ch01.tex ... ch11.tex            <- 11 chapters
chapters/appendix.tex                     <- Appendix A (notation, arithmetic cells, dictionary)
chapters/audit_appendix.tex               <- Appendix B (register D-1...D-20, evidence, open checks)
figures/fig_geometry.tex                  <- TikZ (no external graphics)
figures/fig_signs.tex                     <- TikZ
HFF_final_pre_coding_checklist.md         <- evidence-based closure table (18 requirements)
HFF_final_reference_status.csv            <- per-entry verification status (+ _notes.txt companion)
HFF_source_pdf_consistency_report.md      <- final consistency check (checks, findings, fixes)
HFF_revision_summary.md                   <- what changed / what did not / what remains open
HFF_final_packaging_report.md             <- this report
project_archive/audit/                    <- 6 source documents of the first audit chain (verbatim)
project_archive/HFF_Independent_Audit_2/  <- 6 second-stage audit deliverables
project_archive/HFF_Reconciliation_2/     <- reconciliation + correction records (incl. this file's
                                             siblings and the beam-column consistency audit)
project_archive/REVISION_SUMMARY.md       <- revision history (Revisions 1, 2, 2a, 3, 4)
```

48 files total. No enclosing project folder: `main.tex` and `references.bib` are at the ZIP root
(requirement verified by listing the archive before delivery).

## Reference status (explicitly open — not claimed fully verified)

All 18 bibliography entries were verified against Crossref/DOI or publisher records during the
audit stages (per-entry basis in `HFF_final_reference_status.csv`). Two items remain
**explicitly open**:

1. **C-1 — Shah & London (1978), Nu_T1 = 4.861:** the digit-level confirmation from the primary
   table is outstanding; the value is corroborated by three independent reproductions recorded
   in the reference-status CSV.
2. **Hood & Taylor (1974):** the page range is not machine-verified and is retained as an
   explicit `note` in the bib entry.

## Contents unchanged from the approved formulation

The mathematical model, geometry, material parameters, baseline operating point, reconciled
frozen-force beam–column formulation (with `eq:nupdate` and the quantified 2.3 % conservative
limitation), corrected dimensionless groups (Ri single-basis definitions and values), all
admissibility bounds, registers D-1…D-20, and the four component implementation decisions
(V-A/V-B/V-C proceed under stated conditions; fully coupled solver on HOLD) are exactly as
approved at Stage 3 and audited at Stage 4. No solver code exists or is included.

## Delivery identity

The delivered archive is the file `HFF_Final_Overleaf_Package.zip` created together with this
report (48 files, ≈0.68 MB, ZIP/DEFLATE, integrity-tested). Its SHA-256 is quoted in the
delivery message that transmits it, so the received file can be checked against the build.
