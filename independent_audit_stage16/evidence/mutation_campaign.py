#!/usr/bin/env python3
"""Independent adversarial mutations for the Stage 16 audit.

Each mutation changes MATHEMATICS while leaving the superficial assertions of
audit_stage15/regression.py untouched. Every mutant is applied to an isolated copy.
A survivor is reported as a gap in the suite (not necessarily an error in the document).
"""
import os, shutil, subprocess, sys
BS = chr(92)
ROOT = '/home/user/HFF_Final_Overleaf_Package_FIXED'
BASE = '/tmp/audit16/m'

M = [
 # id, file, old, new, what the mutation breaks
 ("A1","chapters/ch04.tex",
   "w^{''}(0)=w^{''}(L)=-"+BS+"kappa_{"+BS+"mathrm{th}},",
   "w^{''}(0)=w^{''}(L)=-"+BS+"frac{"+BS+"kappa_{"+BS+"mathrm{th}}}{2},",
   "moment BC: half the thermal curvature at the pins"),
 ("A2","chapters/ch04.tex",
   BS+"frac{1-"+BS+"cos"+BS+"mu L}{"+BS+"sin"+BS+"mu L}",
   BS+"frac{1-"+BS+"cos"+BS+"mu L}{2"+BS+"sin"+BS+"mu L}",
   "closed-form solution: particular integral halved"),
 ("A3","chapters/ch04.tex",
   BS+"frac{Ed}{2(1-"+BS+"nu^2)}"+BS+",",
   BS+"frac{Ed}{(1-"+BS+"nu^2)}"+BS+",",
   "compatibility update: factor 2 lost"),
 ("A4","chapters/ch04.tex",
   BS+"frac{"+BS+"kappa_{"+BS+"mathrm{th}}L^2}{8} .",
   BS+"frac{"+BS+"kappa_{"+BS+"mathrm{th}}L^2}{12} .",
   "linear bow formula: 1/8 -> 1/12"),
 ("A5","chapters/appendix.tex",
   "$"+BS+"bar"+BS+"theta=32.3$ K",
   "$"+BS+"bar"+BS+"theta=34.3$ K",
   "printed mean temperature"),
 ("A6","chapters/ch02.tex",
   "$1.0"+BS+"times10^{-3}$ & "+BS+"si{"+BS+"pascal"+BS+"second}",
   "$2.0"+BS+"times10^{-3}$ & "+BS+"si{"+BS+"pascal"+BS+"second}",
   "water viscosity (feeds the whole pressure chain)"),
 ("A7","chapters/ch02.tex",
   BS+"SI{5.0e3}{"+BS+"watt"+BS+"per"+BS+"square"+BS+"metre}",
   BS+"SI{6.0e3}{"+BS+"watt"+BS+"per"+BS+"square"+BS+"metre}",
   "imposed heat flux (feeds every thermal result)"),
 ("A8","chapters/ch08.tex",
   "inject a spurious outlet mass source (register D-25).",
   "inject a spurious outlet mass source; the level is fixed by imposing "
   "$"+BS+"int_{"+BS+"Ga_"+BS+"mathrm{out}}p"+BS+","+BS+"mathrm dx=0$ (register D-25).",
   "reintroduces a gauge constraint in different notation"),
 ("A9","chapters/ch08.tex",
   BS+"int_{"+BS+"Ga_{"+BS+"mathrm{end}}}"+BS+"varphi_1"+BS+","+BS+"mathrm dY=0",
   BS+"int_{"+BS+"Ga_"+BS+"mathrm{end}}"+BS+"varphi_1"+BS+","+BS+"mathrm dY=1",
   "function space: non-homogeneous integral condition (not a subspace)"),
 ("A10","chapters/ch08.tex",
   "+"+BS+"sum_{K}"+BS+"int_{K}"+BS+"tau_K",
   "-"+BS+"sum_{K}"+BS+"int_{K}"+BS+"tau_K",
   "SUPG term sign"),
 ("A11","chapters/audit_appendix.tex",
   "The ``total mechanical surface strain $5.4"+BS+"times10^{-3}$'' was undefined and did not correspond to any strain in the model",
   "The ``total mechanical surface strain $5.4"+BS+"times10^{-3}$'' is the stress-producing surface strain",
   "register D-31 reverts to the withdrawn false claim"),
 ("A12","chapters/ch07.tex",
   "$2.19"+BS+"times10^{-4}/9.2"+BS+"times10^{-8}=2.4"+BS+"times10^{3}$",
   "$2.19"+BS+"times10^{-4}/9.2"+BS+"times10^{-8}=2.9"+BS+"times10^{3}$",
   "table value of Gamma_p"),
 ("A13","chapters/appendix.tex",
   "$"+BS+"sigma_{"+BS+"mathrm{bend}}=6|M|/d^2=4.2$ MPa",
   "$"+BS+"sigma_{"+BS+"mathrm{bend}}=6|M|/d^2=5.2$ MPa",
   "frozen bending stress in their own arithmetic appendix"),
 ("A14","chapters/appendix.tex",
   "circular-arc estimate $1.6"+BS+"times10^{-4}$",
   "circular-arc estimate $1.9"+BS+"times10^{-4}$",
   "circular-arc estimate (14.6 % high, so 1.9e-4 is inside the 'tolerance' band)"),
 ("A15","chapters/ch11.tex",
   "carries an $O(d/L)$ stiffening relative to ideal point pins --- a few per cent at the baseline",
   "carries an $O(d/L)$ stiffening relative to ideal point pins --- of order one at the baseline",
   "claim reversed in the wrong direction"),
 ("A16","chapters/ch08.tex",
   "written as a "+BS+"emph{stress} $N_"+BS+"theta^c/d$",
   "written as a "+BS+"emph{stress} $N_"+BS+"theta^c/(2d)$",
   "explanatory 1/d becomes 1/(2d) while eq:weaks is untouched"),
 ("A17","chapters/ch08.tex",
   "which is\ntaken as $T_"+BS+"Gamma^{(k+1)}$ and closes the thermal loop",
   "which is\ndiscarded, the loop instead being closed on the extracted flux",
   "loop closure removed while both Dirichlet/Neumann keywords survive"),
 ("A18","chapters/ch04.tex",
   "D_s"+BS+",w^{''''}(x)+N_"+BS+"theta^c"+BS+",w^{''}(x)=0,",
   "D_s"+BS+",w^{''''}(x)-N_"+BS+"theta^c"+BS+",w^{''}(x)=0,",
   "beam-column ODE sign (buckling term becomes stiffening)"),
 ("A19","chapters/ch07.tex",
   "the frozen-force value $13.9$~MPa",
   "the frozen-force value $14.9$~MPa",
   "the conservative stress value in the design chapter"),
 ("A20","chapters/appendix.tex",
   "$M_{"+BS+"mathrm{mid}}=-6.4$ N"+BS+",m per unit depth",
   "$M_{"+BS+"mathrm{mid}}=-8.4$ N"+BS+",m per unit depth",
   "mid-span moment in the arithmetic appendix"),
 ("A21","chapters/ch02.tex",
   "the conditions are therefore $d_2=0$, $"+BS+"langle d_1"+BS+"rangle=0$ taken as the",
   "the conditions are therefore $d_2=0$, $d_1=0$ taken as the",
   "pin reverted to a clamp in Assumption A9 only (B7 untouched)"),
 ("A22","chapters/ch08.tex",
   "b("+BS+"mathbf v,p)+c("+BS+"bu;"+BS+"bu,"+BS+"mathbf v)",
   "b("+BS+"mathbf v,p)-c("+BS+"bu;"+BS+"bu,"+BS+"mathbf v)",
   "convective term sign in the momentum weak form"),
 ("A23","chapters/ch04.tex",
   "N_{"+BS+"mathrm{cr}}="+BS+"pi^2D_s/L^2",
   "N_{"+BS+"mathrm{cr}}=4"+BS+"pi^2D_s/L^2",
   "critical load: clamped eigenvalue substituted for the pinned one"),
 ("A24","chapters/appendix.tex",
   "$"+BS+"mu=55$ "+BS+"si{"+BS+"per"+BS+"metre}, $"+BS+"mu L=1.65$",
   "$"+BS+"mu=55$ "+BS+"si{"+BS+"per"+BS+"metre}, $"+BS+"mu L=2.65$",
   "printed beam-column parameter"),
 ("A25","chapters/ch09.tex",
   "amplification\n$1.39$",
   "amplification\n$1.29$",
   "benchmark acceptance value (expected to be caught)"),
]

def clone(dst):
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git','project_archive'))

def run(dst):
    p = subprocess.run([sys.executable,'audit_stage15/regression.py'], cwd=dst,
                       capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return p.returncode, fails, p.stderr

survivors = []
print("%-4s %-8s %s" % ("id","result","first failing check / note"))
for mid, f, old, new, desc in M:
    dst = os.path.join(BASE, mid)
    clone(dst)
    path = os.path.join(dst, f)
    t = open(path, encoding='utf-8').read()
    if t.count(old) != 1:
        print("%-4s %-8s ANCHOR COUNT %d -- mutation not applied (%s)" % (mid, "SKIP", t.count(old), desc))
        survivors.append((mid, desc, "anchor"))
        continue
    open(path,'w',encoding='utf-8').write(t.replace(old,new,1))
    rc, fails, err = run(dst)
    if rc == 0:
        print("%-4s %-8s SURVIVED -- %s" % (mid, "caught" if False else "ESCAPED", desc))
        survivors.append((mid, desc, "survived"))
    else:
        print("%-4s %-8s %-58s | %s" % (mid, "caught", fails[0][:58] if fails else "?", desc))
print()
print("SURVIVORS: %d of %d" % (len(survivors), len(M)))
for s in survivors: print("  ", s)
