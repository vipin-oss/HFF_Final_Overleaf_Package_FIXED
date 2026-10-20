#!/usr/bin/env python3
"""Auditor part 4: remaining printed scalars that no suite check recomputes."""
import math
E,nu,alpha,ks=3.6e9,0.4,5e-5,0.25
rho,muf,cp,kf=1000.0,1e-3,4180.0,0.6
H0,d,L,U,q,L_o=5e-4,3e-3,3e-2,5e-2,5e3,2e-2
Nu=5.385; h=Nu*kf/(2*H0)
dTt=q*d/ks; dTb=q*L/(rho*U*H0*cp)
thbar=dTt/2+q/h+dTb/2
Ds=E*d**3/(12*(1-nu**2)); kth=(1+nu)*alpha*dTt/d
N0=E*d*alpha*thbar/(1-nu); Ncr=math.pi**2*Ds/L**2
print("dTt=%.3f K  q''/h=%.4f K  dTb=%.4f K  thbar=%.4f K  h=%.4f W/m2K" % (dTt,q/h,dTb,thbar,h))
Tcr=math.pi**2*d**2/(12*alpha*(1+nu)*L**2)
print("Tbar_cr = pi^2 d^2/(12 alpha (1+nu) L^2) = %.3f K (printed 117 in ch07:38, 117.5 in the M_b quotient)" % Tcr)
print("  sweep d=1,1.5,2,2.5,3 mm ->", ["%.1f" % (math.pi**2*(dd*1e-3)**2/(12*alpha*(1+nu)*L**2)) for dd in (1,1.5,2,2.5,3)],
      "(printed 13,29,52,82,117)")
print("M_b = Tcr/thbar = %.4f (printed 3.64) ; 117.5/32.3 = %.4f" % (Tcr/thbar, 117.5/32.3))
print("Ncr = %.1f N/m (printed 1.06e5)" % Ncr)
print("sigma_memb = -E alpha thbar/(1-nu) = %.4f MPa (printed -9.6)" % (-E*alpha*thbar/(1-nu)/1e6))
print("sigma_max = memb+bend = %.4f MPa ; ratio to sigma_y=90 MPa = %.4f (printed 0.15)" % (13.9165, 13.9165/90))
print("0.2 sigma_y cap = %.1f MPa ; frozen 13.9 < cap: %s" % (0.2*90, 13.9165 < 0.2*90))
pbar=(12*muf*U*(L+L_o)/H0**2 + 12*muf*U*L_o/H0**2)/2
lin = 48*kth*Ds/(5*pbar*L**2)
print("linear-limit Gamma_p = 48 kth Ds/(5 pbar L^2) = %.1f (printed 1.7e3)" % lin)
print("w_max^lin = kth L^2/8 = %.4e m ; wmax/lin = 1.3896 ; 1/(1-N0/Ncr) = %.4f" % (kth*L**2/8, 1/(1-N0/Ncr)))
print("kappa_th = (1+nu) alpha q''/k_s = %.4f 1/m (printed 1.4)" % kth)
print("kappa_geo d/2 = %.4e ; (kgeo-kth)d/2 = %.4e (printed 9.9e-4)" % (2.05907*d/2, (2.05907-kth)*d/2))
print("mid-span passage height 1 + wmax/H0 = %.6f (register 1.437740946)" % (1+2.188579e-4/H0))
print("Gr = g beta dT* H0^3/nu^2 with beta=2.1e-4, nu=1e-6: %.3f (printed 1.07)" %
      (9.81*2.1e-4*(q*H0/kf)*H0**3/1e-12))
print("Ri = Gr/Re_H0^2, Re=U H0/nu=25 -> %.3e" % ((9.81*2.1e-4*(q*H0/kf)*H0**3/1e-12)/(25**2)))
