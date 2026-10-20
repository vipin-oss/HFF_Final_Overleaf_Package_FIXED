#!/usr/bin/env python3
"""Auditor part 2: independent beam-column fixed point, derived kinematic quantities,
and ODE/BC residual verification (signs re-derived, not copied)."""
import math
E,nu,alpha,ks = 3.6e9,0.4,5e-5,0.25
rho,muf,cp,kf = 1000.0,1.0e-3,4180.0,0.6
H0,d,L,U,q,L_o = 5e-4,3e-3,3e-2,5e-2,5e3,2e-2
Nu = 5.385
Dh=2*H0; h=Nu*kf/Dh
dTt=q*d/ks; dTb=q*L/(rho*U*H0*cp)
thbar=dTt/2+q/h+dTb/2
Ds=E*d**3/(12*(1-nu**2)); kth=(1+nu)*alpha*dTt/d
N0=E*d*alpha*thbar/(1-nu)
Karc=E*d/(2*(1-nu**2))

def state(N):
    mu=math.sqrt(abs(N)/Ds); u=mu*L; A=math.tan(u/2)
    w=lambda x:(kth/mu**2)*(A*math.sin(mu*x)+math.cos(mu*x)-1)
    wp=lambda x:(kth/mu)*(A*math.cos(mu*x)-math.sin(mu*x))
    Ns=200001; hh=L/(Ns-1); s=0.0
    for i in range(Ns):
        x=i*hh; c=1 if i in (0,Ns-1) else (4 if i%2 else 2); v=wp(x); s+=c*v*v
    arc=(s*hh/3)/L/2
    return dict(mu=mu,uL=u,wmax=w(L/2),kgeo=kth/math.cos(u/2),
                Mmid=-Ds*(kth/math.cos(u/2)-kth),arc=arc,
                slope=max(abs(wp(i*L/40000)) for i in range(40001)))

print("components of theta-bar: dTt/2=%.4f  q''/h=%.4f (h=%.4g)  dTb/2=%.4f  sum=%.4f"
      % (dTt/2, q/h, h, dTb/2, thbar))
print("printed component line in ch07: '30 + 1.6 + 0.7';  q''/h to 1 dp = %.1f  -> printed 1.6 %s"
      % (round(q/h,1), "MISMATCH" if abs(round(q/h,1)-1.6)>0.05 else "ok"))
print()
f=state(N0)
print("frozen force N0=%.1f N/m ; N0/Ncr=%.5f" % (N0, N0/(math.pi**2*Ds/L**2)))
print("  mu=%.4f muL=%.5f wmax=%.6e (%.4f H0) kgeo=%.5f Mmid=%.5f arc=%.6e slope=%.5f"
      % (f['mu'],f['uL'],f['wmax'],f['wmax']/H0,f['kgeo'],f['Mmid'],f['arc'],f['slope']))
print("  amplification wmax/(kth L^2/8) = %.4f ; 1/(1-N0/Ncr)=%.4f"
      % (f['wmax']/(kth*L**2/8), 1/(1-N0/(math.pi**2*Ds/L**2))))
print("  fibre strain (kgeo-kth)d/2 = %.6e ; kgeo d/2 = %.6e ; e0 = %.6e ; e0+kgeo d/2 = %.6e"
      % ((f['kgeo']-kth)*d/2, f['kgeo']*d/2, (1+nu)*alpha*thbar, (1+nu)*alpha*thbar+f['kgeo']*d/2))
eps_mech = abs(kth*d/2) + abs((1+nu)*alpha*thbar)  # mechanical surface strain, see ch04
print("  |eps_mech| candidate = %.6e ; printed 3.25e-3" % eps_mech)
print("  arc/(e0) = %.4f%%  -> first-iterate force relaxation %.2f%%"
      % (100*f['arc']/((1+nu)*alpha*thbar), 100*Karc*f['arc']/N0))
N=N0
for it in range(60):
    a=state(N)['arc']; Nn=N0+Karc*a
    if abs(Nn-N)<1e-9: N=Nn; break
    N=Nn
s=state(N)
print()
print("fixed point of eq:nupdate: N*=%.1f N/m  relaxation %.3f%%  wmax=%.6e (%.4f H0)  arc=%.6e"
      % (N, 100*(N0-N)/N0, s['wmax'], s['wmax']/H0, s['arc']))
print("  printed: N 2.733e4 ('2.904e4 -> 2.733e4'), relaxation 5.9%, w 2.14e-4, 0.428 H0")
print("  Mmid*=%.4f  sigma_bend*=%.4f MPa  vs frozen %.4f / %.4f MPa  shift %.2f%%"
      % (s['Mmid'], 6*abs(s['Mmid'])/d**2/1e6, f['Mmid'], 6*abs(f['Mmid'])/d**2/1e6,
         100*(6*abs(s['Mmid'])/d**2/(6*abs(f['Mmid'])/d**2)-1)))
print("  sigma_memb*=-E alpha thbar/(1-nu)=%.4f MPa ; frozen %.4f MPa"
      % (-E*alpha*thbar/(1-nu)/1e6, -E*alpha*thbar/(1-nu)/1e6))
print("  total |sigma|* = %.4f MPa ; frozen %.4f MPa" % ((-E*alpha*thbar/(1-nu)+N0/d)/1e6, 13.9165))
print()
print("ODE + BC residuals (w = (kth/mu^2)(A sin mu x + cos mu x - 1), A=tan(muL/2)):")
mu=f['mu']; A=math.tan(mu*L/2)
for x in (0.3*L,0.5*L,0.77*L):
    wpp=-kth*(A*math.sin(mu*x)+math.cos(mu*x))
    w4=kth*mu**2*(A*math.sin(mu*x)+math.cos(mu*x))
    print("   x/L=%.2f  Ds w'''' + N w'' = %.3e" % (x/L, Ds*w4+N0*wpp))
w=lambda x:(kth/mu**2)*(A*math.sin(mu*x)+math.cos(mu*x)-1)
wpp=lambda x:-kth*(A*math.sin(mu*x)+math.cos(mu*x))
print("   w(0)=%.2e w(L)=%.2e w''(0)+kth=%.2e w''(L)+kth=%.2e"
      % (w(0),w(L),wpp(0)+kth,wpp(L)+kth))
print()
print("pressure/deflection checks:")
dp=12*muf*U*(L+L_o)/H0**2; pL=dp*L_o/(L+L_o); pbar=(dp+pL)/2
print("  dp=%.1f Pa pL=%.1f pbar=%.1f | printed 72 Pa? (table says 72 for 12 mu U L/H0^2 with L=3cm) -> %.1f"
      % (dp,pL,pbar,12*muf*U*L/H0**2))
wp=5*pbar*L**4/(384*Ds)
print("  wp=%.4e m (printed 9.2e-8) ; Gamma mixed=%.2f (printed 2.4e3)"
      % (wp, f['wmax']/wp))
# circular-arc estimate of 0.5<w'^2>
wc = 4*f['wmax']/L  # parabola-ish mean slope
print("  circular-arc check: 0.5<w'^2> approx from w''=const: %.3e ; printed 1.6e-4"
      % (0.5*(4*f['wmax']/L)**2/3))
