#!/usr/bin/env bash
# Mutation test of audit_stage15/regression.py. Usage: mutation_test_regression.sh <repo-or-worktree at 7c9749f>
# Works on a scratch COPY; the repository is never modified.
set -u
SRC=${1:?path to repository checkout}; W=$(mktemp -d); git -C "$SRC" archive HEAD | tar -x -C "$W"; cd "$W"
reset(){ git -C "$SRC" show HEAD:"$1" > "$1"; }
run(){ python3 audit_stage15/regression.py 2>&1 | grep -E '^FAIL|ALL CHECKS PASSED|CHECK\(S\) FAILED' | head -3 | sed 's/^/      /'; }
t(){ echo "[$1] $2"; }
t C1 "CONTROL  ch03: pressure term +p -> -p (expected: caught)";            sed -i "s/w^{''''}(x)= +\\\\,p(x)/w^{''''}(x)= -\\\\,p(x)/" chapters/ch03.tex; run; reset chapters/ch03.tex
t C2 "CONTROL  ch02 caption: 'away from the channel' -> 'positive into the channel' (expected: caught)"; sed -i '0,/away from the channel (Figure/s//positive into the channel (Figure/' chapters/ch02.tex; run; reset chapters/ch02.tex
t M1 "ch04: printed w_max 2.19e-4 -> 7.77e-4";                              sed -i 's/w_{\\max}=2.19\\times10^{-4}\\,\\mathrm{m}=0.438/w_{\\max}=7.77\\times10^{-4}\\,\\mathrm{m}=0.438/' chapters/ch04.tex; run; reset chapters/ch04.tex
t M2 "ch08: flip sign of geometric-stiffness term (- to +)";                sed -i 's/^-\\int_{\\Om_s^0}N_\\theta^c/+\\int_{\\Om_s^0}N_\\theta^c/' chapters/ch08.tex; run; reset chapters/ch08.tex
t M3 "ch01: 'bows away from the interior' -> 'bows toward the interior'";   sed -i 's/bows away from the interior/bows toward the interior/' chapters/ch01.tex; run; reset chapters/ch01.tex
t M4 "ch02 Table: PEEK Poisson ratio 0.40 -> 0.30 (a primary input)";       sed -i 's/PEEK Poisson ratio \& \$\\nu\$ \& \$0.40\$/PEEK Poisson ratio \& $\\nu$ \& $0.30$/' chapters/ch02.tex; grep -c 'nu\$ & \$0.30' chapters/ch02.tex | sed 's/^/      mutation applied: /'; run; reset chapters/ch02.tex
t M5 "ch08: pressure-gauge constraint changed to a different integral";     sed -i 's/int_{\\Ga_{\\mathrm{out}}}p\\,\\mathrm ds=0/int_{\\Ga_{\\mathrm{out}}}p^2\\,\\mathrm ds=7/' chapters/ch08.tex; run; reset chapters/ch08.tex
echo "[V1] vacuous arc-estimate assertion, evaluated exactly as written in regression.py with a deliberately wrong curvature:"
python3 - <<'PY'
L=3e-2
for kgeo in (0.0, 1.0, 2.059):
    print("      kgeo=%.3f -> assertion `abs(-w2)**2*L*L/24/1e-4 - 1.59 < 0.005` is %s" % (kgeo, abs(-(-kgeo))**2*L*L/24/1e-4 - 1.59 < 0.005))
PY
rm -rf "$W"
