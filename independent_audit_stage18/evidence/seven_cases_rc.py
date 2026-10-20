#!/usr/bin/env python3
"""Stage 18 audit — exact exit codes for the seven Stage 17 counterexamples and F1.

IMPORTANT: no Stage 18 suite exists. This script therefore runs the ONLY suite in the tree
(audit_stage15/regression.py, v3, Stage 17) against a fresh isolated copy for every case.
Results are labelled 'current-state', not 'Stage 18'.

Each case: fresh clone -> exactly one anchor replacement -> run -> record exit code and every
FAIL line. A case with exit code 0 is an ESCAPE.
"""
import os, shutil, subprocess, sys

ROOT = os.path.abspath('.')
BASE = '/tmp/audit18/cases'
BS = chr(92)

CASES = [
 ("G1", "chapters/ch08.tex",
  "inject a spurious outlet mass source (register D-25, corrected in D-30).",
  "inject a spurious outlet mass source (register D-25, corrected in D-30); the level is fixed by "
  "imposing $" + BS + "int_{" + BS + "Ga_{" + BS + "mathrm{out}}}p" + BS + "," + BS + "mathrm dY=0$, which removes the gauge freedom.",
  "gauge constraint beside its explanation"),
 ("G2", "chapters/ch05.tex",
  "Because no gauge freedom exists, nothing is imposed to fix it; the",
  "The gauge is fixed by imposing $" + BS + "int_{" + BS + "Ga_{" + BS + "mathrm{out}}}p" + BS + "," + BS + "mathrm dY=0$; the",
  "gauge constraint invented in ch05"),
 ("G3", "chapters/ch08.tex",
  "as a " + BS + "emph{Dirichlet datum}: $T_s=T_" + BS + "Gamma^{(k)}$ on $" + BS + "Ga_{" + BS + "mathrm{if}}$,",
  "as a " + BS + "emph{Dirichlet datum}: $T_s=T_" + BS + "Gamma^{(k)}$ on $" + BS + "Ga_{" + BS + "mathrm{if}}$, "
  "with the interface flux also prescribed there as $k_s" + BS + "nabla T_s" + BS + "cdot" + BS + "bn=q_" + BS + "Gamma^{(k-1)}$,",
  "Gamma_if over-determined (Dirichlet + Neumann)"),
 ("T1", "chapters/ch07.tex",
  "$" + BS + "Delta T_t/2+q^{''}/h+" + BS + "Delta T_b/2$",
  "$" + BS + "Delta T_t/3+q^{''}/(2h)+" + BS + "Delta T_b/2$",
  "theta-bar formula cell corrupted"),
 ("T2", "chapters/ch07.tex",
  "(9" + BS + "times10^{-4})]=117$ K",
  "(9" + BS + "times10^{-4})]=130$ K",
  "T_cr 117 K -> 130 K (M_b >= 2 depends on it)"),
 ("N1", "chapters/appendix.tex",
  "$" + BS + "Gamma_p$ & thermal-to-pressure deflection ratio & -- " + BS + BS,
  "$" + BS + "Gamma_p$ & deflection ratio & -- " + BS + BS,
  "Gamma_p nomenclature label removed"),
 ("S1", "chapters/ch04.tex",
  "is superseded by that measurement, the check is complete",
  "is superseded by that measurement; note that the pin idealization still stiffens the ends by "
  "about two per cent, the check is complete",
  "stale end claim in alternative wording"),
]

def clone(dst):
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        '.git', 'project_archive', 'independent_audit_stage17', 'independent_audit_stage18'))

def run(dst, *args):
    p = subprocess.run([sys.executable, 'audit_stage15/regression.py', *args], cwd=dst,
                       capture_output=True, text=True)
    fails = [l[6:].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    passes = sum(1 for l in p.stdout.splitlines() if l.startswith('PASS'))
    return p.returncode, fails, passes

os.makedirs(BASE, exist_ok=True)
b = os.path.join(BASE, 'baseline'); clone(b)
rc, fails, npass = run(b)
print("baseline: exit=%d PASS=%d FAIL=%d  %s" % (rc, npass, len(fails), "clean" if rc == 0 else fails[:3]))
if rc != 0:
    print("BASELINE NOT CLEAN — aborted"); sys.exit(1)

rows = []
for cid, rel, old, new, desc in CASES:
    d = os.path.join(BASE, cid); clone(d)          # fresh clean copy per case
    path = os.path.join(d, rel); t = open(path, encoding='utf-8').read()
    n = t.count(old)
    if n != 1:
        print("%-3s ANCHOR COUNT %d — not applied" % (cid, n)); rows.append((cid, "SKIP", n, "", "")); continue
    open(path, 'w', encoding='utf-8').write(t.replace(old, new, 1))
    rc, fails, npass = run(d)
    verdict = "ESCAPE" if rc == 0 else "detected"
    print("%-3s exit=%d PASS=%-3d %-9s first FAIL: %-60s | %s"
          % (cid, rc, npass, verdict, (fails[0] if fails else "(none)")[:60], desc))
    rows.append((cid, verdict, rc, fails[0] if fails else "", desc))

# F1: display-equation corruption, then the suite's documented fingerprint regeneration
d = os.path.join(BASE, 'F1'); clone(d)
p = os.path.join(d, 'chapters/ch04.tex'); t = open(p, encoding='utf-8').read()
old = BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8} ."
new = BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{12} ."
print("\nF1 anchor count:", t.count(old))
open(p, 'w', encoding='utf-8').write(t.replace(old, new, 1))
rc1, f1, n1 = run(d)
print("F1  step 1 (edit eq:wmax 1/8 -> 1/12): exit=%d PASS=%d FAIL=%d first FAIL: %s"
      % (rc1, n1, len(f1), (f1[0] if f1 else "(none)")[:70]))
subprocess.run([sys.executable, 'audit_stage15/regression.py', '--update-fingerprints'],
               cwd=d, capture_output=True, text=True)
rc2, f2, n2 = run(d)
print("F1  step 2 (after --update-fingerprints): exit=%d PASS=%d FAIL=%d  -> %s"
      % (rc2, n2, len(f2), "STILL ACCEPTED (escape)" if rc2 == 0 else "rejected"))
print("\nsummary: escapes %d / %d cases; F1 accepted-after-regen=%s"
      % (sum(1 for r in rows if r[1] == "ESCAPE"), len(rows), rc2 == 0))
