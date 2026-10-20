#!/usr/bin/env python3
"""Auditor part 3 (corrected signs): self-consistent fixed point of eq:nupdate,
stress-producing strain, and the circular-arc estimate."""
import math
E,nu,alpha,ks=3.6e9,0.4,5e-5,0.25
rho,muf,cp,kf=1000.0,1e-3,4180.0,0.6
H0,d,L,U,q,L_o=5e-4,3e-3,3e-2,5e-2,5e3,2e-2
Nu=5.385; h=Nu*kf/(2*H0)
thbar=q*d/ks/2+q/h+q*L/(rho*U*H0*cp)/2
Ds=E*d**3/(12*(1-nu**2)); kth=(1+nu)*alpha*(q*d/ks)/d
N0=E*d*alpha*thbar/(1-nu); Karc=E*d/(2*(1-nu**2))
def state(N):
    mu=math.sqrt(N/Ds); u=mu*L; A=math.tan(u/2)
    wp=lambda x:(kth/mu)*(A*math.cos(mu*x)-math.sin(mu*x))
    Ns=200001; hh=L/(Ns-1); s=0.0
    for i in range(Ns):
        x=i*hh; c=1 if i in (0,Ns-1) else (4 if i%2 else 2); v=wp(x); s+=c*v*v
    arc=(s*hh/3)/L/2
    return dict(N=N,mu=mu,uL=u,wmax=(kth/mu**2)*(A*math.sin(mu*L/2)+math.cos(mu*L/2)-1),
                arc=arc,kgeo=kth/math.cos(u/2),M=-Ds*(kth/math.cos(u/2)-kth))
f=state(N0)
print("frozen:       N=%.1f  N/Ncr=%.4f  wmax=%.6e (%.4f H0)  arc=%.6e  DeltaN=%.1f (%.2f%%)"
      % (f['N'],f['N']/(math.pi**2*Ds/L**2),f['wmax'],f['wmax']/H0,f['arc'],Karc*2*f['arc'],100*Karc*2*f['arc']/N0))
print("              sigma_memb=%.4f MPa sigma_bend=%.4f MPa total=%.4f MPa"
      % (-E*alpha*thbar/(1-nu)/1e6, 6*abs(f['M'])/d**2/1e6,
         (-E*alpha*thbar/(1-nu)+6*abs(f['M'])/d**2*(-1)*(-1))/1e6))
print("              eps_mech=(1-nu^2)*sigma/E = %.5e  printed 3.25e-3"
      % ((1-nu**2)*(-E*alpha*thbar/(1-nu)+6*abs(f['M'])/d**2)/E))
print("              eps_mech = e0+(kgeo-kth)d/2 = %.5e"
      % ((1+nu)*alpha*thbar+(f['kgeo']-kth)*d/2))
print("              circular arc: kth*L^2/8=%.4e  kgeo^2 L^2/24=%.5e  printed 1.6e-4"
      % (kth*L**2/8, f['kgeo']**2*L**2/24))
N=N0
for it in range(200):
    a=2*state(N)['arc']; Nn=N0-Karc*a
    if abs(Nn-N)<1e-10: N=Nn; break
    N=Nn
s=state(N)
print("fixed point:  N*=%.1f N/m (printed 2.733e4)  relaxation %.3f%% (printed 5.9%%)"
      % (N, 100*(N0-N)/N0))
print("              wmax=%.6e m (%.4f H0) [printed 2.14e-4, 0.428]  arc=%.6e" % (s['wmax'],s['wmax']/H0,s['arc']))
print("              sigma_bend=%.4f MPa (printed 3.9)  M*=%.4f (printed -6.2?)  shift %.2f%%"
      % (6*abs(s['M'])/d**2/1e6, s['M'], 100*(abs(s['M'])/abs(f['M'])-1)))
print("              sigma_total*=%.4f MPa ; D-28 quotes 13.0 MPa ; frozen %.4f"
      % ((E*alpha*thbar/(1-nu)+6*abs(s['M'])/d**2)/1e6, 13.9165))
print("              sigma_memb* (relaxed) = %.4f MPa ; D-28 quotes 9.11 MPa (frozen 9.68)"
      % ((N/d)/1e6))
print("              5.9%% relaxation implies N=%.4e ; D-28 quotes N 2.733e4" % (N0*(1-0.059)))
