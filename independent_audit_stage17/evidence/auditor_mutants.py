#!/usr/bin/env python3
"""Independent auditor mutation campaign (Stage 17 audit).

Runs against ISOLATED COPIES under /tmp/audit17/am; the repository is never modified.
Each mutant records: anchor multiplicity (must be 1), the suite's exit code, and the first
failing check.  A mutant that leaves the suite at 109/109 is reported as ESCAPED.

Three mutants (G1,G2,G3) restore or invent defects of the kind Stage 17 repaired; four
(T1,T2,N1,S1) attack printed derivations and claims; F1 combines a display-equation edit with
the suite's own documented `--update-fingerprints` workflow.  C1..C3 are positive controls.
"""
import os, shutil, subprocess, sys

ROOT = os.path.abspath('.')
BASE = '/tmp/audit17/am'
BS = chr(92)

M = [
 ("G1", "chapters/ch08.tex",
  "inject a spurious outlet mass source (register D-25, corrected in D-30).",
  "inject a spurious outlet mass source (register D-25, corrected in D-30); the level is fixed by "
  "imposing $" + BS + "int_{" + BS + "Ga_{" + BS + "mathrm{out}}}p" + BS + "," + BS + "mathrm dY=0$, which removes the gauge freedom.",
  "gauge constraint re-inserted next to its own explanation (keeps the D-30 pointer)"),
 ("G2", "chapters/ch05.tex",
  "Because no gauge freedom exists, nothing is imposed to fix it; the",
  "The gauge is fixed by imposing $" + BS + "int_{" + BS + "Ga_{" + BS + "mathrm{out}}}p" + BS + "," + BS + "mathrm dY=0$; the",
  "gauge constraint invented in ch05 (contradicts B2 and ch08)"),
 ("G3", "chapters/ch08.tex",
  "as a " + BS + "emph{Dirichlet datum}: $T_s=T_" + BS + "Gamma^{(k)}$ on $" + BS + "Ga_{" + BS + "mathrm{if}}$,",
  "as a " + BS + "emph{Dirichlet datum}: $T_s=T_" + BS + "Gamma^{(k)}$ on $" + BS + "Ga_{" + BS + "mathrm{if}}$, "
  "with the interface flux also prescribed there as $k_s" + BS + "nabla T_s" + BS + "cdot" + BS + "bn=q_" + BS + "Gamma^{(k-1)}$,",
  "step 1 over-determined: Dirichlet and Neumann on the same surface"),
 ("T1", "chapters/ch07.tex",
  "$" + BS + "Delta T_t/2+q^{''}/h+" + BS + "Delta T_b/2$",
  "$" + BS + "Delta T_t/3+q^{''}/(2h)+" + BS + "Delta T_b/2$",
  "theta-bar formula cell corrupted (both coefficients), printed total untouched"),
 ("T2", "chapters/ch07.tex",
  "(9" + BS + "times10^{-4})]=117$ K",
  "(9" + BS + "times10^{-4})]=130$ K",
  "critical temperature 117 K -> 130 K (underpins M_b >= 2)"),
 ("N1", "chapters/appendix.tex",
  "$" + BS + "Gamma_p$ & thermal-to-pressure deflection ratio & -- " + BS + BS,
  "$" + BS + "Gamma_p$ & deflection ratio & -- " + BS + BS,
  "nomenclature entry left unlabelled (mixed vs like-for-like)"),
 ("S1", "chapters/ch04.tex",
  "is superseded by that measurement, the check is complete",
  "is superseded by that measurement; note that the pin idealization still stiffens the ends by "
  "about two per cent, the check is complete",
  "a NEW stale end-stiffening claim re-added in different words"),
 ("C1", "chapters/appendix.tex", "$" + BS + "bar" + BS + "theta=32.3$ K",
  "$" + BS + "bar" + BS + "theta=32.4$ K", "positive control: printed theta-bar shifted by 0.1 K"),
 ("C2", "chapters/appendix.tex", "K: $-2.91" + BS + "times10^4$ N/m",
  "K: $-2.71" + BS + "times10^4$ N/m", "positive control: membrane force changed by 7 %"),
 ("C3", "chapters/ch05.tex",
  "-k_f" + BS + "nabla T_f" + BS + "cdot" + BS + "bn &= -k_s" + BS + "nabla T_s" + BS + "cdot" + BS + "bn",
  "-k_f" + BS + "nabla T_f" + BS + "cdot" + BS + "bn &= +k_s" + BS + "nabla T_s" + BS + "cdot" + BS + "bn",
  "positive control: interface flux-continuity sign flipped (display equation)"),
]

def clone(dst):
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', 'project_archive',
                                                            'independent_audit_stage17'))

def run(dst):
    p = subprocess.run([sys.executable, 'audit_stage15/regression.py'], cwd=dst,
                       capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return p.returncode, fails

def main():
    os.makedirs(BASE, exist_ok=True)
    base = os.path.join(BASE, 'baseline'); clone(base)
    rc, fails = run(base)
    print("baseline: %s" % ("PASS (109/109)" if rc == 0 else "FAIL %s" % fails[:3]))
    if rc != 0: return 1
    det = esc = skip = 0
    rows = []
    for mid, rel, old, new, desc in M:
        dst = os.path.join(BASE, mid); clone(dst)
        p = os.path.join(dst, rel); t = open(p, encoding='utf-8').read()
        n = t.count(old)
        if n != 1:
            print("%-3s SKIP      anchor count %d  -- %s" % (mid, n, desc)); skip += 1; continue
        open(p, 'w', encoding='utf-8').write(t.replace(old, new, 1))
        rc, fails = run(dst)
        if rc == 0:
            print("%-3s ESCAPED   109/109 pass -- %s" % (mid, desc)); esc += 1
            rows.append((mid, "ESCAPED", desc, ""))
        else:
            print("%-3s detected  %-52s | %s" % (mid, fails[0][:52], desc)); det += 1
            rows.append((mid, "detected", desc, fails[0]))
    # F1: display-equation edit followed by the suite's documented fingerprint regeneration
    dst = os.path.join(BASE, 'F1'); clone(dst)
    p = os.path.join(dst, 'chapters/ch04.tex'); t = open(p, encoding='utf-8').read()
    old = BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8} ."
    new = BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{12} ."
    if t.count(old) == 1:
        open(p, 'w', encoding='utf-8').write(t.replace(old, new, 1))
        rc1, f1 = run(dst)
        subprocess.run([sys.executable, 'audit_stage15/regression.py', '--update-fingerprints'],
                       cwd=dst, capture_output=True, text=True)
        rc2, f2 = run(dst)
        print("\nF1  linear bow 1/8 -> 1/12 : before regeneration rc=%d (%s) ; after "
              "--update-fingerprints rc=%d (%s)" % (rc1, f1[0][:40] if f1 else '-', rc2,
                                                    "109/109 PASS" if rc2 == 0 else f2[:2]))
        rows.append(('F1', 'ESCAPED-after-regen' if rc2 == 0 else 'detected',
                     'display equation corrupted, fingerprints regenerated', ''))
    print("\nescaped %d ; detected %d ; skipped %d" % (esc, det, skip))
    return 0

if __name__ == '__main__':
    sys.exit(main())
