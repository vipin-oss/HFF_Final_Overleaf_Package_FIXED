#!/usr/bin/env python3
"""One-shot restructuring of journal_submission/main.tex.

Re-orders the v2 manuscript into the section tree used by the 2023 HFF
reference paper (Gupta, Kumar, Kumar & Barak, HFF 33(6), 2250-2277):

    1. Introduction                     (flat, no subsections)
    2. Field equations                  (2.5 Limiting cases, 2.6 Regime bounds)
       Nomenclature                     (after section 2, as in the journal)
    3. Problem formulation              (configuration, assumptions, reduced
                                         wall model as 3.3.1-3.3.7, boundary
                                         conditions as 3.4)
    4. Solution of the problem          (discretisation -> verification)
    5. Numerical results and discussion
    6. Discussion
    7. Limitations
    8. Conclusions                      (bullet takeaways)
       Declarations
       References                       (\\input{references}, thebibliography)
       Appendix A-C
       Corresponding author

The source is the v2 manuscript as delivered on ``main``; it is read from git
(``git show main:journal_submission/main.tex``) so the script stays re-runnable
after main.tex has been overwritten with its own output.  Pass --source PATH
to read a file instead.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "journal_submission" / "main.tex"
DST = ROOT / "journal_submission" / "main.tex"

MARKER = re.compile(r"^\\(?:section\*?\{[^}]*\}|appendix\s*$|bibliographystyle\{(?:[^}]*)\})")

# --------------------------------------------------------------------- blocks
def split_blocks(lines: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    starts = [i for i, ln in enumerate(lines) if MARKER.match(ln)]
    preamble = lines[: starts[0]]
    blocks = []
    for k, start in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        blocks.append((lines[start].strip(), lines[start:end]))
    return preamble, blocks

def find(blocks, head: str) -> list[str]:
    for h, body in blocks:
        if h == head:
            return list(body)
    raise SystemExit(f"block not found: {head}")

def retitle(body: list[str], old: str, new: str) -> list[str]:
    out = []
    for ln in body:
        if ln.strip() == old:
            out.append(new)
        else:
            out.append(ln)
    return out

def drop_label(body: list[str], label: str) -> list[str]:
    return [ln for ln in body if ln.strip() != f"\\label{{{label}}}"]

def flatten(body: list[str], labels: list[str]) -> list[str]:
    """Remove \\subsection lines whose \\label is in `labels` (intro only)."""
    out, skip = [], False
    for ln in body:
        if ln.startswith("\\subsection{") and not skip:
            skip = "pending"
            continue
        if skip == "pending":
            if ln.startswith("\\label{") and ln[7:-1] in labels:
                skip = False
                continue
            # not one of ours: restore the heading we swallowed
            out.append("\\subsection{" + "SUBPLACEHOLDER" + "}")
            skip = False
        out.append(ln)
    return out

# ----------------------------------------------------------------- transformations
def source_text() -> str:
    if "--source" in sys.argv:
        return Path(sys.argv[sys.argv.index("--source") + 1]).read_text(encoding="utf-8")
    import subprocess

    return subprocess.run(
        ["git", "show", "main:journal_submission/main.tex"],
        cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


SRC_TEXT = source_text()
PREAMBLE, BLOCKS = split_blocks(SRC_TEXT.splitlines())

nomenclature = find(BLOCKS, "\\section*{Nomenclature}")
# close the \small scope of the nomenclature table
nomenclature = [ln for ln in nomenclature if ln.strip() != "\\normalsize"]
for _i, _ln in enumerate(nomenclature):
    if _ln.strip() == "\\end{longtable}":
        nomenclature.insert(_i + 1, "\\normalsize")
        break

intro = find(BLOCKS, "\\section{Introduction}")
intro = flatten(intro, ["sec:context", "sec:litfsi", "sec:litconj", "sec:gap", "sec:contrib"])

field = find(BLOCKS, "\\section{Governing equations}")
field = retitle(field, "\\section{Governing equations}", "\\section{Field equations}")
field = retitle(field, "\\subsection{Field equations}",
                "\\subsection{Field equations and kinematics}")

limiting_cases = r"""
\subsection{Limiting cases}
\label{sec:limits}

Four limits of the formulation set out in equations
\\eqref{eq:continuity}--\\eqref{eq:ifthermal} and \\eqref{eq:beamdim} are used
later as checks and as the reference states against which the coupled solution
is read.

\emph{Rigid wall.} For $w\equiv0$ the passage is plane and the flow reduces to
Poiseuille flow with $f\,Re_{D_h}=96$, while the energy equation reduces to the
thermal-entry problem of a parallel-plate channel with a uniform wall flux. This
limit is reproduced to round-off by the present solvers (\S\ref{sec:benchmarks})
and supplies the denominators of every normalised quantity reported below.

\emph{One-dimensional wall conduction.} When $k_s d\ll k_f L$, equation
\eqref{eq:solidenergy} collapses to $\dd^2T_s/\dd y^2=0$ and the wall
temperature rise becomes $q''(d/k_s+1/h)$; the through-thickness profile
\eqref{eq:theta_profile} then reduces to a straight line and the eigen-curvature
\eqref{eq:kappa} to its linear-in-$q''$ form. The departure of the coupled
solution from this estimate is the $6.2\%$ reported in \S\ref{sec:thermalresults}.

\emph{Frozen membrane force.} Setting $N=N_\theta$ in equation
\eqref{eq:beam} removes the axial-compatibility equation \eqref{eq:nupdate} and
leaves a linear bending problem. The resulting over-prediction of the bow is the
model-form error quantified in \S\ref{sec:modform}; it vanishes as $q''\to0$.

\emph{Euler column.} With $q''=0$ the strip carries no thermal load, and the
eigenvalue problem implied by equation \eqref{eq:beamdim} at $\lambda=\pi$
returns $N_{cr}=\pi^2D_s/L^2$, the classical pinned--pinned result that the
thermal resultant must reach for buckling to occur. The working point at
$0.283\,N_{cr}$ therefore sits below, but not far below, that limit.

"""

field = retitle(field, "\\subsection{Regime bounds}",
                "\\subsection{Regime bounds}")
# insert the limiting-case subsection immediately before the regime bounds
idx = field.index("\\subsection{Regime bounds}")
field = field[:idx] + limiting_cases.strip("\n").splitlines() + [""] + field[idx:]

wall = find(BLOCKS, "\\section{Reduced wall model and its derivation}")
wall = [re.sub(r"^\\subsection\{", r"\\subsubsection{", ln) for ln in wall]
wall = retitle(wall, "\\section{Reduced wall model and its derivation}",
               "\\subsection{Reduced wall model and its derivation}\n\\label{sec:wall}")
wall = [ln.replace("This section derives the wall model",
                   "This subsection derives the wall model") for ln in wall]

model = find(BLOCKS, "\\section{Physical model and assumptions}")
model = retitle(model, "\\section{Physical model and assumptions}",
                "\\section{Problem formulation}")

bcs = find(BLOCKS, "\\section{Boundary conditions and closure of the problem}")
bcs = retitle(bcs, "\\section{Boundary conditions and closure of the problem}",
              "\\subsection{Boundary conditions and closure of the problem}")

numerics = find(BLOCKS, "\\section{Computational formulation}")
numerics = retitle(numerics, "\\section{Computational formulation}",
                   "\\section{Solution of the problem}")

grid = find(BLOCKS, "\\section{Grid independence}")
grid = retitle(grid, "\\section{Grid independence}",
               "\\subsection{Mesh independence and the grid-convergence index}")
grid = retitle(grid, "Table~\\ref{tab:mesh} lists the levels and the",
               "Table~\\ref{tab:mesh} lists the levels and the")

verif = find(BLOCKS, "\\section{Verification}")
verif = [re.sub(r"^\\subsection\{", r"\\subsubsection{", ln) for ln in verif]
verif = retitle(verif, "\\section{Verification}",
                "\\subsection{Verification of the implementation}")

results = find(BLOCKS, "\\section{Results}")
results = retitle(results, "\\section{Results}",
                  "\\section{Numerical results and discussion}")

discussion = find(BLOCKS, "\\section{Discussion}")
limitations = find(BLOCKS, "\\section{Limitations}")
conclusions = find(BLOCKS, "\\section{Conclusions}")
declarations = find(BLOCKS, "\\section*{Declarations}")
_all = SRC_TEXT.splitlines()
_start = next(i for i, ln in enumerate(_all) if ln.strip() == "\\appendix")
appendix = _all[_start:]

# ------------------------------------------------------------------ conclusions
conclusions = retitle(
    conclusions,
    "here {---} a plane channel of $0.5$~mm undeformed height with a $3$~mm strip",
    "here {---} a plane channel of $0.5$~mm undeformed height with a $3$~mm strip",
)

pairs = [
    ("\\item The strip bows", "\\item It is shown that the strip bows"),
    ("\\item The bow more than doubles", "\\item It is shown that the bow more than doubles"),
    ("\\item The conjugate wall temperature rise", "\\item It is shown that the conjugate wall temperature rise"),
    ("\\item The frozen-force closure", "\\item It is shown that the frozen-force closure"),
    ("\\item The binding constraint", "\\item It is shown that the binding constraint"),
    ("\\item Thermal--hydraulic performance", "\\item It is shown that thermal--hydraulic performance"),
]
lead = [ln for ln in conclusions]
conclusions = []
for ln in lead:
    for old, new in pairs:
        if ln.strip().startswith(old):
            ln = new + ln.strip()[len(old):]
            break
    conclusions.append(ln)

# ---------------------------------------------------------------- declarations
declarations = retitle(
    declarations,
    "\\noindent\\textbf{Competing interests.}\nThe author declares no competing interests.",
    "\\noindent\\textbf{Disclosure statement.}\nThe author declares no conflict of interest.",
)
declarations = [
    ln.replace("\\noindent\\textbf{Competing interests.}",
               "\\noindent\\textbf{Disclosure statement.}")
    .replace("The author declares no competing interests.",
             "The author declares no conflict of interest.")
    for ln in declarations
]

# ------------------------------------------------------------------- preamble
preamble = list(PREAMBLE)
src_preamble = "\n".join(preamble)
src_preamble = src_preamble.replace(
    "%  Build (Overleaf or local):\n"
    "%      pdflatex main ; bibtex main ; pdflatex main ; pdflatex main\n",
    "%  Build (Overleaf or local) -- two passes, no BibTeX run:\n"
    "%      pdflatex main ; pdflatex main\n"
    "%  The bibliography is generated from references.bib by\n"
    "%      python3 tools/make_references.py\n"
    "%  and is read from references.tex.\n",
)
src_preamble = src_preamble.replace(
    "\\vspace{2pt}\n\\noindent\\textbf{Article classification:} Research paper\n"
    "\\end{structuredabstract}\n\n\\vspace{4pt}\n\\noindent\\rule{\\textwidth}{0.4pt}",
    "\\vspace{2pt}\n\\noindent\\textbf{Paper type:} Research paper\n"
    "\\end{structuredabstract}\n\n"
    "\\vspace{2pt}\n\\noindent\\textit{Disclosure statement:} the author declares no\n"
    "conflict of interest and no specific funding was received for this work.\n\n"
    "\\vspace{4pt}\n\\noindent\\rule{\\textwidth}{0.4pt}",
)
preamble = src_preamble.splitlines()

# --------------------------------------------------------------- references + end
references = [
    "",
    "% ===========================================================================",
    "\\section*{References}",
    "\\addcontentsline{toc}{section}{References}",
    "\\IfFileExists{references.tex}{\\input{references}}%",
    "  {\\input{journal_submission/references}}",
    "",
]

corresponding = [
    "",
    "\\vspace{10pt}",
    "\\noindent\\rule{\\textwidth}{0.4pt}\n",
    "\\noindent\\textbf{Corresponding author}\\\\[2pt]",
    "\\noindent Author name can be contacted at: \\texttt{author@institution.edu}",
    "",
]

# ------------------------------------------------------------------- assemble
out: list[str] = []
out += preamble
out += [""]
out += intro
out += [""]
out += field
out += [""]
out += nomenclature
out += [""]
out += model
out += [""]
out += wall
out += [""]
out += bcs
out += [""]
out += numerics
out += [""]
out += grid
out += [""]
out += verif
out += [""]
out += results
out += [""]
out += discussion
out += [""]
out += limitations
out += [""]
out += conclusions
out += [""]
out += declarations
out += references
while appendix and appendix[-1].strip() in ("", "\\end{document}"):
    appendix.pop()
out += appendix
out += corresponding
out += ["", "\\end{document}", ""]

text = "\n".join(out)
# --------------------------------------------------------------- section leads
SOLUTION_LEAD = r"""The problem posed in Section~\ref{sec:model} is solved as three coupled
blocks: a velocity--pressure problem in the deformed passage, a conjugate
conduction problem in the strip and its surroundings, and the nonlinear
beam--column equation of the strip itself. Sections~\ref{sec:fe}--\ref{sec:coupling}
define the discretisation, the weak forms and the coupling; Sections
\ref{sec:grid} and \ref{sec:verification} report the mesh-independence study and
the verification of the implementation."""
RESULTS_LEAD = r"""The coupled solution is reported in the order in which the loop closes. The
closed-form baseline comes first (Section~\ref{sec:baseline}), then the flow in
the deformed passage (Section~\ref{sec:flowresults}), the conjugate temperature
field (Section~\ref{sec:thermalresults}) and the wall response that produces
them (Section~\ref{sec:wall}). Sections~\ref{sec:convresults}--\ref{sec:modform}
quantify the convergence of the coupling, the sensitivity to the imposed flux,
the wall thickness, the Reynolds number and two material properties, and the
model-form error of the frozen-force closure."""
text = text.replace(
    "\\section{Solution of the problem}\n\\label{sec:numerics}\n\n",
    "\\section{Solution of the problem}\n\\label{sec:numerics}\n\n" + SOLUTION_LEAD + "\n\n",
)
text = text.replace(
    "\\section{Numerical results and discussion}\n\\label{sec:results}\n\n",
    "\\section{Numerical results and discussion}\n\\label{sec:results}\n\n" + RESULTS_LEAD + "\n\n",
)
ROADMAP = r"""The paper is organised as follows. Section~\ref{sec:equations} sets out the field
equations, the dimensionless groups and the limits against which the solution is later
checked, and the nomenclature follows it. Section~\ref{sec:model} poses the problem: the
configuration, the ten assumptions with their quantitative support, the derivation of the
reduced wall model and the boundary data. Section~\ref{sec:numerics} describes how the
coupled problem is solved, including the monolithic conjugate assembly, the coupling
algorithm, the mesh-independence study and the verification of the implementation.
Section~\ref{sec:results} reports the coupled solution and its sensitivity to five
parameters, Section~\ref{sec:discussion} discusses what the results mean and
Section~\ref{sec:limitations} states what the model excludes. Section~\ref{sec:conclusions}
concludes. Three appendices record the closed-form algebra, the weak forms and the
reproduction record."""
text = text.replace(
    "structural model is the most consequential of those exclusions and it is not\n"
    "presented as a substitute for a two-dimensional thermoelastic continuum.",
    "structural model is the most consequential of those exclusions and it is not\n"
    "presented as a substitute for a two-dimensional thermoelastic continuum.\n\n"
    + ROADMAP,
)
text = re.sub(r"\n{3,}", "\n\n", text)
text = text.replace("\\label{sec:wall}\n\\label{sec:wall}", "\\label{sec:wall}")
text = text.replace("\\eqref{eq:thermalboundary}", "\\eqref{eq:ifthermal}")
if DST.exists() and "--force" not in sys.argv:
    raise SystemExit(f"{DST} exists; pass --force to overwrite")
DST.write_text(text, encoding="utf-8")
print(f"wrote {DST} ({len(text.splitlines())} lines)")
