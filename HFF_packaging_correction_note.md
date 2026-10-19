# Packaging correction note

The previous archive contained the entire project inside an enclosing directory despite the README claiming the source files were at ZIP root. This package removes that enclosing directory. `main.tex`, `references.bib`, `chapters/`, `figures/`, and `main.pdf` now sit at the ZIP root. Prior audit records are preserved under `project_archive/`.

No mathematical source files were edited during this packaging correction. The bundled PDF is the same PDF that was included in the source archive; its SHA-256 is recorded in `HFF_final_packaging_report.md`. The LaTeX source bytes are unchanged.
