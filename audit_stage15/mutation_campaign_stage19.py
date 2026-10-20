#!/usr/bin/env python3
"""Stage 19 mutation campaign: the five classes that survived suite v4, three Stage 18
regression cases re-asserted under suite v5, and three positive controls.

The five required classes (each escaped suite v4 at commit 5741d36; see
`independent_audit_stage18/HFF_Stage18_Final_Acceptance_Audit.md` §7.2):

  M3c  a pointwise pressure datum, $p(\\mathbf 0)=0$, beside the explanation that a normalisation
       would over-determine the system;
  M6b  an adopting statement phrased "we choose ... rather than ...", i.e. an adopting verb that is
       outside any fixed vocabulary, in a sentence that also carries a rejecting token;
  M7   a double thermal datum in the Condition column of a `tab:bcs` row whose Boundary cell does
       not name Gamma_if;
  M8   a double thermal datum in prose written without the "on <surface>" pattern;
  M10  a stale end-condition magnitude written "2 pct" instead of "2 per cent" or "2 %".

Further cases re-assert the Stage 18 protection under the hardened suite: G5 (a mean over Om_f with
adopting wording, in another chapter), T3 (theta-bar total corrupted with its components intact),
T4 (T_cr changed with its own numerator/quotient made internally consistent), W2 (eq:wmax corrupted
with the fingerprint deliberately regenerated) and W3 (eq:wmax given a form the parser cannot read,
which must fail rather than skip).

Three POSITIVE CONTROLS must pass: a legitimately reworded rejection of the normalisation, a
legitimate sentence that states the interface Dirichlet datum and the heated-face flux together, and
a legitimately added display equation (a fingerprint addition is reported, never failed).

Every case is applied to a FRESH ISOLATED COPY of the repository; the repository is never modified
and the clean baseline is run first. A case counts as DETECTED only when

  (i)   the mutated copy runs the suite to completion (no traceback, no syntax error, no missing file),
  (ii)  the suite exits non-zero, and
  (iii) the declared INTENDED assertion is among the failing checks.

Anything else is reported as ESCAPED, INVALID (wrong failure) or ANCHOR (mutation not applicable).
A detection supported only by the fingerprint layer is counted separately and never as substantive.

Run from the repository root:
    python3 audit_stage15/mutation_campaign_stage19.py
    python3 audit_stage15/mutation_campaign_stage19.py --results /tmp/before.txt   (keep the record)
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
if '--results' in sys.argv:                      # never clobber a committed record by accident
    RESULTS = sys.argv[sys.argv.index('--results') + 1]
FINGERPRINT_CHECKS = {"no display equation has changed", "no register row has changed",
                      "no equation or register row removed"}

# --------------------------------------------------------------------------------------------
# the five required classes
# --------------------------------------------------------------------------------------------
GAUGE_SENTENCE = ("inject a spurious outlet mass source (register D-25, corrected in D-30).")

M19 = [
    ("M3c", "required",
     "chapters/ch08.tex",
     GAUGE_SENTENCE,
     "inject a spurious outlet mass source; the level is nevertheless pinned by "
     "$p(" + BS + "mathbf 0)=0$ at an interior point (register D-25, corrected in D-30).",
     "pointwise pressure datum in another notation, in the same sentence as its own explanation",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual", "default"),

    ("M6b", "required",
     "chapters/ch08.tex",
     GAUGE_SENTENCE,
     GAUGE_SENTENCE + " There is no such freedom in this problem; we choose the extra equation "
     "$" + BS + "int_{" + BS + "Om_f}p" + BS + ",dx=0$ for the level rather than rely on the "
     "outflow condition.",
     "adopting statement phrased 'we choose ... rather than ...' (verb outside any vocabulary)",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual", "default"),

    ("M7", "required",
     "chapters/ch05.tex",
     "B9 & variant of B6 & $T_s=T_h$ on $" + BS + "Ga_h^0$ & regime D; matched heat-input rule (A10)",
     "B9 & variant of B6 & $T_s=T_h$ on $" + BS + "Ga_h^0$, $"
     + BS + "partial_nT_s=q^{''}/k_s$ & regime D; matched heat-input rule (A10)",
     "double thermal datum in a Condition column whose Boundary cell omits Gamma_if",
     "no tab:bcs row gives any surface a solid Dirichlet AND a solid Neumann thermal datum",
     "default"),

    ("M8", "required",
     "chapters/ch08.tex",
     "Prescribing the interface " + BS + "emph{temperature} to the solid",
     "In addition, the solid also receives the measured flux $"
     + BS + "partial_nT_s=q^{''}/k_s$ together with its interface temperature "
     "$T_s=T_" + BS + "Gamma^{(k)}$. Prescribing the interface " + BS + "emph{temperature} to the solid",
     "prose double datum written without the 'on <surface>' pattern",
     "no prose datum gives the solid a temperature AND a non-heated-face heat flux in one sentence",
     "default"),

    ("M10", "required",
     "chapters/ch04.tex",
     "gives $1.0000$ of $" + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ for point pins",
     "gives, to within about two pct, $1.0000$ of $"
     + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ for point pins",
     "stale end-effect magnitude spelled 'pct'",
     "no stale end-effect percentage survives", "default"),

    # ---- Stage 18 protections re-asserted under the hardened suite ----
    ("G5", "additional",
     "chapters/ch05.tex",
     "Because no gauge freedom exists, nothing is imposed to fix it;",
     "Because no gauge freedom exists, nothing is imposed to fix it, and the level is normalised "
     "through $" + BS + "overline{p}_{" + BS + "Om_f}=0$;",
     "mean over Om_f with adopting wording, in another chapter",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual", "default"),

    ("T3", "additional",
     "chapters/ch07.tex",
     "$30.0+1.55+0.72" + BS + "approx32.3$ K",
     "$30.0+1.55+0.72" + BS + "approx34.3$ K",
     "theta-bar cell: components right, quoted total wrong",
     "the theta-bar cell total is the recomputed theta-bar", "default"),

    ("T4", "additional",
     "chapters/appendix.tex",
     "$M_b=117.5/32.3=3.64$.",
     "$M_b=100.0/32.3=3.10$.",
     "T_cr changed with numerator and quotient made internally consistent",
     "the M_b numerator is the recomputed T_cr", "default"),

    ("W2", "additional",
     "chapters/ch04.tex",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8}",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{7}",
     "plausible but wrong eq:wmax denominator, fingerprint REGENERATED",
     "the eq:wmax denominator reproduces the printed linear w_max (appendix A3)", "regen"),

    ("W3", "additional",
     "chapters/ch04.tex",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8}",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{2(1-"
     + BS + "nu)}",
     "eq:wmax replaced by a form the constants parser cannot read (must fail, not skip)",
     "eq:wmax states a parabola and a w_max with explicit constants", "regen"),
]

# --------------------------------------------------------------------------------------------
# positive controls: the hardened checks must NOT reject these
# --------------------------------------------------------------------------------------------
CONTROLS = [
    ("P1",
     "chapters/ch08.tex",
     "inject a spurious outlet mass source (register D-25, corrected in D-30).",
     "inject a spurious outlet mass source (register D-25, corrected in D-30). No normalisation is "
     "imposed: constraining $" + BS + "int_{" + BS + "Ga_{" + BS + "mathrm{out}}}p" + BS + ","
     + BS + "mathrm ds=0$ would over-determine the system.",
     "legitimate reworded rejection of the normalisation: the constraint is named and rejected in the "
     "same clause by 'would over-determine', with no adopting verb",
     "default"),

    ("P2",
     "chapters/ch08.tex",
     "Prescribing the interface " + BS + "emph{temperature} to the solid",
     "Equivalently, one statement prescribes $T_s=T_" + BS + "Gamma^{(k)}$ on $"
     + BS + "Ga_{" + BS + "mathrm{if}}$ and $+k_s" + BS + "nabla T_s" + BS + "cdot"
     + BS + "bn_{" + BS + "mathrm{out}}=q^{''}$ on $" + BS + "Ga_h^0$, so no second thermal datum "
     "is introduced. Prescribing the interface " + BS + "emph{temperature} to the solid",
     "legitimate sentence carrying an interface Dirichlet datum AND a heated-face flux, explicitly "
     "on Gamma_h^0: the double-datum test must not fire",
     "default"),

    ("P3",
     "chapters/ch10.tex",
     "or even conjectured quantitatively before the computations exist.",
     "or even conjectured quantitatively before the computations exist.\n"
     + BS + "begin{equation}" + BS + "label{eq:stage19probe}\n"
     "a^2+b^2=c^2\n" + BS + "end{equation}",
     "legitimately added display equation: an addition is reported by the fingerprint layer, never "
     "failed, and the suite must still exit 0",
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


def apply_and_run(case, tag):
    mid, kind, rel, old, new, desc, expect, mode = case
    dst = os.path.join(BASE, mid)
    clone(dst)
    path = os.path.join(dst, rel)
    src = open(path, encoding='utf-8').read()
    n = src.count(old)
    detail = ["### %s  [%s]  %s" % (mid, kind, desc), "    file     %s" % rel]
    if n != 1:
        detail.append("    RESULT   not applied (anchor count %d)" % n)
        return 'ANCHOR', detail, None
    open(path, 'w', encoding='utf-8').write(src.replace(old, new, 1))
    cmd, rc, fails, stdout, err = run(dst, mode)
    crash = ('Traceback' in err) or (rc != 0 and not fails)
    hit = [f for f in fails if expect in f]
    if rc == 0:
        res = "ESCAPED"
    elif crash:
        res = "INVALID"
    elif hit:
        res = "detected"
    else:
        res = "INVALID"
    substantive = [f for f in fails if f not in FINGERPRINT_CHECKS]
    if res == 'detected':
        kindstr = "substantive" if substantive else "fingerprint-only"
    else:
        kindstr = "not a valid detection"
    detail += ["    command  %s" % " ".join(cmd),
               "    exit     %d" % rc,
               "    intended %s" % expect,
               "    fails    %s" % (fails if fails else "none"),
               "    stderr   %s" % (err.strip().splitlines()[-1] if err.strip() else "empty"),
               "    RESULT   %s (%s)" % (res, kindstr), ""]
    return res, detail, (kindstr, hits := (hit[0] if hit else (fails[0] if fails else '-')))


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
    say("%-5s %-9s %-9s %s" % ("id", "result", "layer", "intended assertion / first failing check"))
    say("%-5s %-9s %-9s %s" % ("base", "PASS" if rc == 0 else "FAIL", "",
                                "%d checks, exit %d" % (passes, rc)))
    if rc != 0:
        say("BASELINE FAILS: campaign aborted")
        open(RESULTS, 'w').write("\n".join(out) + "\n")
        return 1

    tally = {"detected": 0, "ESCAPED": 0, "INVALID": 0, "ANCHOR": 0}
    layer = {"substantive": 0, "fingerprint-only": 0}
    seen = {}
    for case in M19:
        res, det, info = apply_and_run(case, case[1])
        detail += det
        seen[case[0]] = res
        tally[res] = tally.get(res, 0) + 1
        if info:
            layer[info[0]] = layer.get(info[0], 0) + 1
        say("%-5s %-9s %-9s %s | %s" % (case[0], res, (info[0] if info else ''),
                                         (info[1] if info else '-'), case[5]))

    say("")
    req = [c[0] for c in M19 if c[1] == 'required']
    req_ok = sum(1 for k in req if seen.get(k) == 'detected')
    say("REQUIRED CLASSES %d (%s): detected %d of %d"
        % (len(req), ' '.join(req), req_ok, len(req)))
    say("ALL MUTANTS %d: detected %d, escaped %d, invalid %d, anchor not applied %d"
        % (len(M19), tally['detected'], tally['ESCAPED'], tally['INVALID'], tally['ANCHOR']))
    say("  of the detections: %d substantive, %d fingerprint-only"
        % (layer['substantive'], layer['fingerprint-only']))

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
            say("%-5s %-9s not applied (anchor %d) | %s" % (mid, "ANCHOR", n, desc))
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
                   "    RESULT   %s" % ("PASS, as intended" if good else "REJECTED, control violated"),
                   ""]
        say("%-5s %-9s %-9s | %s" % (mid, "PASS" if good else "REJECTED", "", desc))

    say("")
    say("CONTROLS %d: %d passed as intended" % (len(CONTROLS), ok_ctrl))
    with open(RESULTS, 'w') as fh:
        fh.write("Stage 19 mutation campaign -- raw results\n")
        fh.write("repository: %s\n" % ROOT)
        fh.write("suite: audit_stage15/regression.py (version 5, Stage 19)\n")
        fh.write("baseline: exit 0, %d checks passed in a fresh isolated copy\n\n" % passes)
        fh.write("summary\n-------\n")
        fh.write("\n".join(out) + "\n\n")
        fh.write("per-case evidence\n-----------------\n")
        fh.write("\n".join(detail) + "\n")
    say("raw evidence written to " + RESULTS)
    good = (tally['ESCAPED'] == 0 and tally['INVALID'] == 0 and tally['ANCHOR'] == 0
            and req_ok == len(req) and ok_ctrl == len(CONTROLS))
    return 0 if good else 1


if __name__ == '__main__':
    sys.exit(main())
