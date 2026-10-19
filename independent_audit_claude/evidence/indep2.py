import mpmath as mp, sympy as sp, numpy as np
from scipy.integrate import solve_bvp
mp.mp.dps=30
E,nu,al,ks,q=mp.mpf('3.6e9'),mp.mpf('.4'),mp.mpf('5e-5'),mp.mpf('.25'),mp.mpf('5e3')
L,d=mp.mpf('3e-2'),mp.mpf('3e-3'); Ds=E*d**3/(12*(1-nu**2)); kth=(1+nu)*al*q/ks
# (1) the two sympy 'False' flags: confirm they are unsimplified-trig artefacts, by numeric substitution at 3 parameter sets
x,mu,k,Ls=sp.symbols('x mu k L',positive=True); A=sp.tan(mu*Ls/2)
w=k/mu**2*(A*sp.sin(mu*x)+sp.cos(mu*x)-1)
for (m_,k_,L_) in ((55.0,1.4,0.03),(30.0,0.7,0.05),(80.0,2.0,0.02)):
    s={mu:m_,k:k_,Ls:L_}
    print("params mu=%g k=%g L=%g : w(L)=%.2e  w''(L)+k=%.2e  w''(0)+k=%.2e"%(m_,k_,L_,
          float(w.subs(x,Ls).subs(s)),float((sp.diff(w,x,2)+k).subs(x,Ls).subs(s)),float((sp.diff(w,x,2)+k).subs(x,0).subs(s))))
# (2) self-consistent moment with printed thbar values 32.27 and 32.3 and with source-derived 32.265
def sc(th):
    Nc0=E*d*al*th/(1-nu)
    def closed(m):
        Aa=mp.tan(m*L/2)
        return (lambda y: -kth*(Aa*mp.sin(m*y)+mp.cos(m*y))), (lambda y: kth/m*(Aa*mp.cos(m*y)-mp.sin(m*y)))
    F=lambda Nc: Nc-(Nc0-E*d/(2*(1-nu**2))*mp.quad(lambda y: closed(mp.sqrt(Nc/Ds))[1](y)**2,[0,L/2,L])/L)
    Nsc=mp.findroot(F,Nc0*.95); w2,_=closed(mp.sqrt(Nsc/Ds)); Msc=Ds*(w2(L/2)+kth)
    w2f,_=closed(mp.sqrt(Nc0/Ds)); Mf=Ds*(w2f(L/2)+kth)
    return Mf,Msc,Nc0,Nsc
for th in ('32.265','32.27','32.3'):
    Mf,Msc,N0,Ns=sc(mp.mpf(th)); print("thbar=%s: M_frozen=%s  M_selfcons=%s N m ; sigma_sc(consistent N)=%s MPa"%(th,mp.nstr(Mf,6),mp.nstr(Msc,6),mp.nstr((Ns/d+6*abs(Msc)/d**2)/1e6,6)))
# (3) like-for-like Gamma_p: pressure deflection of the SAME pre-stressed pinned strip under uniform pbar
Dsf,Nf,Lf,ktf=float(Ds),float(E*d*al*mp.mpf('32.265')/(1-nu)),float(L),float(kth); pb=84.0
def bvp(N,load,kap):
    # D w'' + N w = -load*x(L-x)/2 - D*? ; for thermal: D w''+N w = -kap*D  (w''=-kap*(...)) -> use rhs
    def rhs(x,Y): return np.vstack([Y[1],(-N*Y[0]-load*x*(Lf-x)/2 - Dsf*kap)/Dsf])
    xs=np.linspace(0,Lf,801); s=solve_bvp(rhs,lambda a,b:np.array([a[0],b[0]]),xs,np.zeros((2,xs.size)),tol=1e-12,max_nodes=100000)
    return s.sol(Lf/2)[0]
wp0=bvp(0.0,pb,0.0); wpN=bvp(Nf,pb,0.0); wt0=bvp(0.0,0.0,ktf); wtN=bvp(Nf,0.0,ktf)
print("w_p(N=0)=%.6e  w_p(N)=%.6e  amplification of pressure deflection=%.5f"%(wp0,wpN,wpN/wp0))
print("w_th(N=0)=%.6e  w_th(N)=%.6e  amplification of thermal deflection=%.5f"%(wt0,wtN,wtN/wt0))
print("Gamma_p printed definition  w_th(N)/w_p(N=0) = %.1f"%(wtN/wp0))
print("Gamma_p like-for-like       w_th(N)/w_p(N)   = %.1f"%(wtN/wpN))
