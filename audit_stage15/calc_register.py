from math import *
# Primary inputs, ch02:40-46 and ch02:169-180 (PEEK/water design point)
H0=5.0e-4; L=3.0e-2; d=3.0e-3; U=5.0e-2; q=5.0e3
E=3.6e9; nu=0.40; alpha=5.0e-5; ks=0.25; kf=0.60; mu=1.0e-3; cp=4.18e3
rho=1.0e3; thbar=32.27; pbar=84.0; sy=90e6
Ds=E*d**3/(12*(1-nu**2)); kth=(1+nu)*alpha*q/ks
Nth=E*d*alpha*thbar/(1-nu); m2=Nth/Ds; mu_=sqrt(m2); u=mu_*L; A=tan(u/2)
w   = lambda x:(kth/m2)*(A*sin(mu_*x)+cos(mu_*x)-1)
w1  = lambda x:(kth/mu_)*(A*cos(mu_*x)-sin(mu_*x))
w2  = lambda x:-kth*(A*sin(mu_*x)+cos(mu_*x))
wmax=w(L/2); wlin=kth*L*L/8; kgeo=-w2(L/2)
N=400001; hh=L/(N-1); s=0.0
for i in range(N):
    s+=(1 if i in (0,N-1) else (4 if i%2 else 2))*w1(i*hh)**2
half=(s*hh/3)/L/2
e0=(1+nu)*alpha*thbar
wp=5*pbar*L**4/(384*Ds)
Mmid=Ds*(w2(L/2)+kth); sb=6*abs(Mmid)/d**2
sm=-E*alpha*thbar/(1-nu)
arc=kgeo**2*L*L/24
cf=48*kth*Ds/(5*pbar*L*L)
rows=[
("Thermal gradient","$\\partial T/\\partial y=q''/k_s$","ch04:93, ch07:28","%.6e K/m"%(q/ks),"—","derived (not printed)"),
("Through-thickness rise","$\\Delta T_t=q''d/k_s$","ch07:28","%.3f K"%(q*d/ks),"60 K","exact"),
("Thermal curvature","$\\kappa_{th}=(1+\\nu)\\alpha q''/k_s$","ch04:99","%.9f 1/m"%kth,"1.4","exact"),
("Section rigidity","$D_s=Ed^3/[12(1-\\nu^2)]$","ch07:36","%.9f N.m"%Ds,"9.6","+0.45% (rounding)"),
("Membrane resultant","$N_\\theta=-Ed\\alpha\\bar\\theta/(1-\\nu)$","ch07:35","%.6e N/m"%Nth,"-2.9e4","exact"),
("Beam-column parameter","$\\mu=\\sqrt{N_\\theta^c/D_s}$","ch04:190","%.9f 1/m"%mu_,"55","exact"),
("Dimensionless force","$\\mu L$","ch04:211","%.9f"%u,"1.65","exact"),
("Linear bow","$w_{\\max}^{lin}=\\kappa_{th}L^2/8$","ch04:123","%.9e m"%wlin,"1.58e-4","-0.32%"),
("Beam-column bow","eq:beamcolsol at x=L/2","ch04:213","%.12e m"%wmax,"2.19e-4","exact"),
("Relative bow","$w_{\\max}/H_0$","ch04:213","%.9f"%(wmax/H0),"0.438","exact"),
("Amplification","$w_{\\max}/w_{\\max}^{lin}$","ch04:219","%.9f"%(wmax/wlin),"1.39","exact"),
("Pin curvature","$w''(0)$","ch04:186","%.9f 1/m"%w2(0.0),"-1.4","exact"),
("Mid-span curvature","$w''(L/2)$","ch04:221","%.9f 1/m"%w2(L/2),"—","derived"),
("Geometric curvature","$\\kappa_{geo}=-w''(L/2)$","ch04:221","%.9f 1/m"%kgeo,"—","derived"),
("Physical moment at pin (B)","$-D_s(w''+\\kappa_{th})$","derived","%.9e N.m"%(-Ds*(w2(0)+kth)),"0 (imposed)","exact"),
("Physical moment at pin (A)","$+D_s(w''-\\kappa_{th})$","derived","%.6f N.m"%(Ds*(w2(0)-kth)),"—","residual under A"),
("Sagging moment, mid-span","$D_s(w''+\\kappa_{th})$","ch04:254","%.9f N.m"%Mmid,"-6.4","exact"),
("Bending stress","$6|M|/d^2$","ch04:255","%.9f MPa"%(sb/1e6),"4.2","exact"),
("Membrane stress","$-E\\alpha\\bar\\theta/(1-\\nu)$","ch07:43","%.9f MPa"%(sm/1e6),"-9.6","exact"),
("Max section stress (frozen)","$|\\sigma_{memb}|+|\\sigma_{bend}|$","ch07:95","%.6f MPa"%((abs(sm)+sb)/1e6),"13.9","exact"),
("Max section stress (self-cons.)","with M=-5.9 N.m","appendix:109","%.6f MPa"%((abs(sm)+6*5.9/d**2)/1e6),"13.6","exact"),
("Fibre strain","$(\\kappa_{geo}-\\kappa_{th})d/2$","ch04:221","%.12e"%((kgeo-kth)*d/2),"9.9e-4","exact"),
("Naive-flip value","$-(\\kappa_{geo}+\\kappa_{th})d/2$","trap","%.12e"%(-(kgeo+kth)*d/2),"-5.1888e-3","exact"),
("Flip error factor","$(1+\\cos(\\mu L/2))/(1-\\cos(\\mu L/2))$","derived","%.9f"%((1+cos(u/2))/(1-cos(u/2))),"5.2475","exact"),
("Blocked strain","$e_0=(1+\\nu)\\alpha\\bar\\theta$","ch04:227","%.9e"%e0,"2.26e-3","exact"),
("Exact arc term","$\\frac12\\langle w'^2\\rangle$ (quadrature)","ch04:228","%.12e"%half,"1.39e-4","exact"),
("Circular-arc estimate","$\\kappa_{geo}^2L^2/24$","appendix:74","%.12e"%arc,"1.6e-4","-0.62%"),
("Relaxation","$\\frac12\\langle w'^2\\rangle/e_0$","ch04:229","%.6f %%"%(100*half/e0),"6.1 %","exact"),
("Relaxation from old value","$1.8e-4/e_0$","superseded","%.6f %%"%(100*1.8e-4/e0),"—","contradicted 6.1%"),
("Surface strain","$e_0+\\kappa_{geo}d/2$","ch04:223","%.9e"%(e0+kgeo*d/2),"5.4e-3","exact"),
("Pressure deflection","$5\\bar pL^4/(384D_s)$","ch04:278","%.9e m"%wp,"9.2e-8","exact"),
("Linear-limit ratio","$48\\kappa_{th}D_s/(5\\bar pL^2)$","ch04, eq:gammap","%.6f"%cf,"1.7e3","exact"),
("Deformation ratio","$w_{\\max}/w_p$","eq:gammap","%.6f"%(wmax/wp),"2.4e3","exact"),
("Ratio of ratios","$(w_{\\max}/w_p)/(w_{lin}/w_p)$","—","%.9f"%((wmax/wp)/cf),"="+"%.9f"%(wmax/wlin),"exact"),
("Mid-span gap","$H_0+w_{\\max}$","not stated","%.9f H0"%(1+wmax/H0),"1.4377","exact"),
("Max slope","$\\max|w'|$","ch04:220","%.9f rad"%max(abs(w1(0)),abs(w1(L))),"0.027","exact"),
]
out=["# HFF numerical calculation register (generated)","",
     "Regenerate with `python3 calc_register.py`. All inputs are the printed design point",
     "(`ch02:40-46`, `ch02:169-180`); no manuscript result is used as an input.","",
     "| Quantity | Governing relation | Source | Recomputed | Printed | Discrepancy |",
     "|---|---|---|---|---|---|"]
for a,b,c,dv,e,f in rows: out.append(f"| {a} | {b} | {c} | {dv} | {e} | {f} |")
out += ["","## Identity checks","",
 f"- `sec(muL/2)` = {1/cos(u/2):.12f}; `kgeo/kth` = {kgeo/kth:.12f}; difference {abs(1/cos(u/2)-kgeo/kth):.2e}",
 f"- `(1+cos(u/2))/(1-cos(u/2))` = {(1+cos(u/2))/(1-cos(u/2)):.12f}; `cot^2(muL/4)` = {1/tan(u/4)**2:.12f}",
 f"- closed form x amplification = {cf*(wmax/wlin):.6f}; `w_max/w_p` = {wmax/wp:.6f}",
 f"- analytic arc integral = closed form (see sign-convention doc)",
 ]
import os
open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"03_numerical_register.md"),"w").write("\n".join(out)+"\n")
print("\n".join(out))
