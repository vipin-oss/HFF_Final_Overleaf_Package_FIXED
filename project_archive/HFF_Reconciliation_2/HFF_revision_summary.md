# Revision summary — Stage 4 (final Overleaf package)

**Input:** repository state `cd05983` (Stage 3). **No change to:** the research objective, the
governing model, geometry, material parameters, the baseline operating point, the reconciled
beam–column formulation (frozen-force reduction, `eq:nupdate`, 2.3 % conservative limitation),
the corrected dimensionless groups (Ri definitions and values untouched), the baseline
assumptions, or any resolved audit decision. **No solver code written; no coupled simulation
started.**

## What changed (exactly)

1. **Rounding harmonizations** (identified by the final consistency pass; justified in
   `HFF_source_pdf_consistency_report.md` §2):
   `M_b = 117.5/32.3 = 3.64` everywhere (was 3.7 via rounded inputs in Table 7.1, cell A5,
   dictionary); θ̄ ceiling `58.8 K` (was 58.7); cell A5 recomputed at θ̄ = 32.3 K
   (N_θ = −2.91×10⁴ N/m; N_cr = 1.057×10⁵ N/m). Reconciliation row R-14 annotated.
2. **Presentation fixes:** `tab:bcs` (ch05) and `tab:geometry` (ch02) set in p-columns;
   the long archive path in Appendix B set as breakable `\path` — removes the 200 pt / 159 pt
   margin overruns. No content change.
3. **New deliverables (this stage):** `HFF_final_pre_coding_checklist.md` (evidence-based
   closure table: requirement / evidence / status / action / two gating columns);
   `HFF_final_reference_status.csv` (+ notes file) consolidating the stage-1/2 reference
   verification — 18/18 entries verified at the level stated, 2 residual actions (C-1, hood1974
   page range); `HFF_source_pdf_consistency_report.md`; this summary.
4. **`HFF_Final_Overleaf_Package.zip`:** Overleaf-ready — ZIP **root** contains `main.tex`,
   `references.bib`, `chapters/`, `figures/`, and the freshly compiled `main.pdf` (49 pages,
   0 undefined references/citations, 0 LaTeX warnings); the full audit trail
   (`audit/`, `HFF_Independent_Audit_2/`, `HFF_Reconciliation_2/`, `REVISION_SUMMARY.md`,
   README) is preserved under `project_archive/`. The PDF is built from exactly the sources in
   the ZIP root.

## What did not change

All mathematical content, citations, equations, tables, scholarly text, admissibility bounds,
audit registers D-1…D-20, and the four implementation decisions below (which restate the
standing staged-decision record).

## Implementation decisions (separate, per component)

1. **Fluid solver verification (V-A): PROCEED.** Ready: complete specification (rigid slit,
   analytic targets f_D Re = 96, profile to machine precision), mesh/GCI plan, per-run checks.
   Check first: outflow-sensitivity flag (C-9) applies to any V-B-coupled use, not to V-A
   itself.
2. **Solid thermoelastic solver + stress post-processing (V-C): PROCEED, conditional.** Ready:
   unit-test anchors V-C1a/b, V-C2 (corrected identities, D-2/D-12), V-C3(i)/(ii) including the
   beam–column target (amplification 1.39 at μL = 1.65) and the optional consistent-update
   check (0.428 H₀); mean-stress identity as runtime assertion. Condition: property inputs carry
   the C-6 freeze qualifier until the datasheet is frozen.
3. **Thermal solver verification (V-B): PROCEED, conditional.** Ready: specification with SUPG
   at Pe = 348 and acceptance criteria (tolerance + no over/undershoot > 0.1 % + stabilized
   −Galerkin report); Nu_T/H2/H1 anchored. Conditions: T1 quotations carry the corroboration
   note until C-1 closes; quadrature-consistency audit items assigned here for the conjugate
   case are recorded but only bite at the coupled stage.
4. **Fully coupled fluid–thermal–structural solver: HOLD (unchanged).** Conditions to release:
   C-2 (V-D matched case extracted), C-3 (V-E data set constructed), C-6 (property freeze),
   regime guards A-1…A-6 as runtime assertions, V-G executed, C-9 sensitivity study, C-12
   (second-solver platform) committed, replication of one anchor point at field level.
   **Beginning an isolated verification solver is not approval for the coupled solver. No
   solver has been validated; no validation claim may be made until code, verification
   results, and identified experimental data exist.**

## What remains unresolved

C-1 (T1 primary-table digits), C-2 (V-D digit-level matching), C-3 (V-E data set), C-6
(property freeze), C-7 (systematic originality search), C-9 (outflow sensitivity), C-12
(platform commitment); validation data set unidentified (the programme is verification-only as
specified); hood1974 page range. All are recorded with named actions and gating columns in
`HFF_final_pre_coding_checklist.md`.
