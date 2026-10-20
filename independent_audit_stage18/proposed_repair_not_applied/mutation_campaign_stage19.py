#!/usr/bin/env python3
"""Stage 19 mutation campaign: the four assertions that escaped at commit 5741d36, plus two
positive controls.

The Stage 18 audit of 5741d36 ran 44 campaign cases and 30 independent mutations.  Four
independent mutations survived suite v4:

  M3c  a POINTWISE pressure datum, $p(\\mathbf 0)=0$, introduced beside the explanation that a
       normalisation would over-determine the system;
  M7   a double thermal datum in the *Condition* column of tab:bcs, in a row whose Boundary cell
       does not name Gamma_if (so the old check never looked at it);
  M8   a double thermal datum in prose, written without the "on <surface>" pattern;
  M10  a stale end-effect magnitude written "2 pct" instead of "2 per cent".

This campaign makes each of those a permanent case, each applied to a FRESH ISOLATED COPY of the
repository (the repository itself is never modified) after a clean baseline run.  A case counts as
DETECTED only if the suite exits non-zero AND the declared intended check is among the failures.
Two controls must NOT fail: a legitimately reworded rejection of the normalisation (P1) and a
legitimately added display equation (F2; fingerprints report an addition, they never fail it).

Run from the repository root:  python3 audit_stage15/mutation_campaign_stage19.py
Raw per-case evidence: audit_stage15/stage19_mutation_results.txt
"""
import os
import re
import shutil
import subprocess
import sys

BS = chr(92)
ROOT = os.path.abspath('.')
BASE = '/tmp/hff_mut19'
RESULTS = os.path.join('audit_stage15', 'stage19_mutation_results.txt')
FINGERPRINT_CHECKS = {"no display equation has changed", "no register row has changed",
                      "no equation or register row removed"}

M19 = [
    ("M3c", "chapters/ch08.tex",
     "inject a spurious outlet mass source (register D-25, corrected in D-30).",
     "inject a spurious outlet mass source; the level is nevertheless pinned by "
     "$p(" + BS + "mathbf 0)=0$ at an interior point (register D-25, corrected in D-30).",
     "pointwise pressure datum in another notation, beside the explanation",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual"),
    ("M7", "chapters/ch05.tex",
     "B9 & variant of B6 & $T_s=T_h$ on $" + BS + "Ga_h^0$ & regime D; matched heat-input rule (A10)",
     "B9 & variant of B6 & $T_s=T_h$ on $" + BS + "Ga_h^0$, $"
     + BS + "partial_nT_s=q^{''}/k_s$ & regime D; matched heat-input rule (A10)",
     "double thermal datum in a Condition column whose Boundary cell omits Gamma_if",
     "no tab:bcs row gives any surface a solid Dirichlet AND a solid Neumann thermal datum"),
    ("M8", "chapters/ch08.tex",
     "Prescribing the interface " + BS + "emph{temperature} to the solid",
     "In addition, the solid also receives the measured flux $"
     + BS + "partial_nT_s=q^{''}/k_s$ together with its interface temperature "
     "$T_s=T_" + BS + "Gamma^{(k)}$. Prescribing the interface " + BS + "emph{temperature} to the solid",
     "prose double datum written without the 'on <surface>' pattern",
     "no sentence gives the solid a Dirichlet interface temperature AND an interface heat flux"),
    ("M10", "chapters/ch04.tex",
     "gives $1.0000$ of $" + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ for point pins",
     "gives, to within about two pct, $1.0000$ of $"
     + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ for point pins",
     "stale end-effect magnitude spelled 'pct'",
     "no stale end-effect percentage survives"),
    ("G5", "chapters/ch05.tex",
     "Because no gauge freedom exists, nothing is imposed to fix it;",
     "Because no gauge freedom exists, nothing is imposed to fix it, and the level is normalised "
     "through $" + BS + "overline{p}_{" + BS + "Om_f}=0$;",
     "equivalent normalisation, different notation, different chapter, adopting wording",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual"),
    ("T3", "chapters/ch07.tex",
     "$30.0+1.55+0.72" + BS + "approx32.3$ K",
     "$30.0+1.55+0.72" + BS + "approx34.3$ K",
     "theta-bar cell: components right, quoted total wrong",
     "the theta-bar cell total is the recomputed theta-bar"),
    ("T4", "chapters/appendix.tex",
     "$M_b=117.5/32.3=3.64$.",
     "$M_b=100.0/32.3=3.10$.",
     "T_cr changed with the related text updated consistently (numerator and quotient agree)",
     "the M_b numerator is the recomputed T_cr"),
    ("W2", "chapters/ch04.tex",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8}",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{7}",
     "plausible but wrong eq:wmax denominator, fingerprint REGENERATED",
     "the eq:wmax denominator reproduces the printed linear w_max (appendix A3)", "regen"),
]

CONTROLS = [
    ("P1", "chapters/ch08.tex",
     "would over-determine the system and, with a Lagrange multiplier,\n"
     "inject a spurious outlet mass source (register D-25, corrected in D-30).",
     "would over-determine the system, so it is not imposed; with a Lagrange multiplier it would\n"
     "also inject a spurious outlet mass source (register D-25, corrected in D-30).",
     "legitimate reworded rejection must still PASS (the check is not a keyword ban)", "default"),
    ("F2", "chapters/ch10.tex",
     "or even conjectured quantitatively before the computations exist.",
     "or even conjectured quantitatively before the computations exist.\n"
     + BS + "begin{equation}" + BS + "label{eq:auditprobe}\n"
     "a^2+b^2=c^2\n" + BS + "end{equation}",
     "legitimately added display equation must still PASS (a new fingerprint is reported, not failed)",
     "default"),
]


def clone(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', 'project_archive'))


def run(dst, mode):
    cmd = [sys.executable, 'audit_stage15/regression.py']
    if mode == 'regen':
        cmd.append('--update-fingerprints')
    p = subprocess.run(cmd, cwd=dst, capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return cmd, p.returncode, fails, p.stdout, p.stderr


def main():
    os.makedirs(BASE, exist_ok=True)
    out, detail = [], []

    def say(s=""):
        print(s)
        out.append(s)

    base = os.path.join(BASE, 'baseline')
    clone(base)
    cmd, rc, fails, stdout, err = run(base, 'default')
    m = re.search(r'ALL (\d+) CHECKS PASSED', stdout)
    passes = int(m.group(1)) if m else 0
    say("%-5s %-10s %s" % ("id", "result", "intended assertion / first failing check"))
    say("%-5s %-10s %s" % ("base", "PASS" if rc == 0 else "FAIL", "%d checks" % passes))
    if rc != 0:
        say("BASELINE FAILS: campaign aborted")
        open(RESULTS, 'w').write("\n".join(out) + "\n")
        return 1

    tally = {"detected": 0, "escaped": 0, "invalid": 0, "anchor": 0}
    substantive = fponly = 0
    for case in M19:
        mid, rel, old, new, desc, expect = case[:6]
        mode = case[6] if len(case) > 6 else "default"
        dst = os.path.join(BASE, mid)
        clone(dst)
        path = os.path.join(dst, rel)
        src = open(path, encoding='utf-8').read()
        n = src.count(old)
        detail.append("### %s  %s" % (mid, desc))
        detail.append("    file     %s" % rel)
        if n != 1:
            say("%-5s %-10s ANCHOR COUNT %d (%s)" % (mid, "not applied", n, desc))
            detail.append("    RESULT   not applied (anchor count %d)" % n)
            tally["anchor"] += 1
            continue
        open(path, 'w', encoding='utf-8').write(src.replace(old, new, 1))
        cmd, rc, fails, stdout, err = run(dst, mode)
        hit = [f for f in fails if expect in f]
        crash = ('Traceback' in err) or (rc != 0 and not fails)
        if rc == 0:
            res = "ESCAPED"
        elif crash:
            res = "INVALID"
        elif hit:
            res = "detected"
        else:
            res = "INVALID"
        tally[res if res != "INVALID" else "invalid"] += 1
        if res == "detected":
            if [f for f in fails if f not in FINGERPRINT_CHECKS]:
                substantive += 1
                kind = "substantive"
            else:
                fponly += 1
                kind = "fingerprint-only"
        else:
            kind = "not a valid detection"
        detail += ["    command  %s" % " ".join(cmd),
                   "    exit     %d" % rc,
                   "    intended %s" % expect,
                   "    fails    %s" % (fails if fails else "none"),
                   "    stderr   %s" % (err.strip().splitlines()[-1] if err.strip() else "empty"),
                   "    RESULT   %s (%s)" % (res, kind), ""]
        say("%-5s %-10s %-46s | %s" % (mid, res, (hit[0] if hit else (fails[0] if fails else "-")), desc))

    say("")
    say("MUTANTS %d: detected %d, escaped %d, invalid %d, anchor not applied %d"
        % (len(M19), tally["detected"], tally["escaped"], tally["invalid"], tally["anchor"]))
    say("  of the detections, %d are substantive and %d fingerprint-only" % (substantive, fponly))
    ok_ctrl = 0
    for mid, rel, old, new, desc, mode in CONTROLS:
        dst = os.path.join(BASE, mid)
        clone(dst)
        path = os.path.join(dst, rel)
        src = open(path, encoding='utf-8').read()
        n = src.count(old)
        detail.append("### control %s  %s" % (mid, desc))
        detail.append("    file     %s" % rel)
        if n != 1:
            say("%-5s %-10s ANCHOR COUNT %d (%s)" % (mid, "not applied", n, desc))
            detail.append("    RESULT   not applied (anchor count %d)" % n)
            continue
        open(path, 'w', encoding='utf-8').write(src.replace(old, new, 1))
        cmd, rc, fails, stdout, err = run(dst, mode)
        good = (rc == 0)
        ok_ctrl += 1 if good else 0
        added = re.search(r'new fingerprint keys[^\n]*', stdout)
        detail += ["    command  %s" % " ".join(cmd),
                   "    exit     %d" % rc,
                   "    fails    %s" % (fails if fails else "none"),
                   "    added    %s" % (added.group(0) if added else "none"),
                   "    RESULT   %s" % ("PASS, as intended" if good else "FAILED, control violated"), ""]
        say("%-5s %-10s | %s" % (mid, ("PASS" if good else "CONTROL-FAIL"), desc))

    say("")
    say("CONTROLS %d: %d behaved as intended" % (len(CONTROLS), ok_ctrl))
    with open(RESULTS, 'w') as fh:
        fh.write("Stage 19 mutation campaign -- raw results\n")
        fh.write("repository: %s\n" % ROOT)
        fh.write("suite: audit_stage15/regression.py (Stage 19 additions to version 4)\n")
        fh.write("baseline: exit 0, %d checks passed in a fresh isolated copy\n\n" % passes)
        fh.write("summary\n-------\n")
        fh.write("\n".join(out) + "\n\n")
        fh.write("per-case evidence\n-----------------\n")
        fh.write("\n".join(detail) + "\n")
    say("raw evidence written to " + RESULTS)
    good = (tally["escaped"] == 0 and tally["invalid"] == 0 and tally["anchor"] == 0
            and ok_ctrl == len(CONTROLS))
    return 0 if good else 1


if __name__ == '__main__':
    sys.exit(main())
