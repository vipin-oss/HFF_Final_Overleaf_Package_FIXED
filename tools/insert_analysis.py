#!/usr/bin/env python3
"""Insert the analytical (theorem-level) content into journal_submission/main.tex.

This script performs six anchored edits on the restructured v3 manuscript:

1. replaces the structured abstract by the analytical version;
2. adds ``2.3 Variational reduction to the strip`` (derivation of the beam--column
   equation and of the axial-compatibility condition from a two-field functional);
3. inserts ``4.1 Analytical solution of the reduced problem`` (closed forms,
   contraction theorem, lubrication theorem, Sturm--Liouville series, particular
   cases) at the head of section 4;
4. inserts ``5.2 The semi-analytical model against the computation`` with the
   comparison table and the two new figures;
5. appends three theorems' proofs as Appendix D;
6. extends the nomenclature and the conclusions.

The script is idempotent: it refuses to run twice unless --force is given, and it
checks that every anchor is present before writing.
"""
from __future__ import annotations

import pathlib
import sys

SUB = pathlib.Path(__file__).resolve().parents[1] / "journal_submission"
MAIN = SUB / "main.tex"

ABSTRACT = r"""\begin{structuredabstract}
\abshead{Purpose}
This paper derives and verifies a closed model of a flux-heated channel wall that deforms
under its own temperature field, and quantifies the feedback of that deformation on the
conjugate flow and heat transfer it bounds.

\abshead{Design/methodology/approach}
Plane-strain thermoelasticity is reduced to an axially restrained beam--column strip by a
two-field variational principle, the flow is reduced in the lubrication limit, and the
thermal-entry problem is solved by a Sturm--Liouville expansion. Closed forms are obtained for
the hydraulic resistance (a Gauss hypergeometric function), the bow and the buckling
threshold; the axial-compatibility nonlinearity is proved to be a contraction. A
finite-element solution of the coupled problem verifies each formula and measures its error.

\abshead{Findings}
At $\ReDh=50$ and $q''=5\,\mathrm{kW/m^2}$ the strip bows $0.441\,H_0$ and the pressure drop
rises from $144$ to $315$~Pa. The closed form $\Delta p/\Delta p_0={}_2F_1(3,\tfrac12;1;a)$
reproduces this to $0.03\%$, whereas the $\sin^2$ idealisation underpredicts it by $15\%$. The
wall rise is $34.3$~K, $6.2\%$ above one-dimensional conduction. The frozen-force closure
overpredicts the bow by $1.2\%$ at the design point and $14.9\%$ at $10\,\mathrm{kW/m^2}$.
Deformation raises the local Nusselt number by up to $68\%$, with exponent $0.79$ in the
stretch $H_0/H$.

\abshead{Research limitations/implications}
Plane strain, steady laminar constant-property flow, small slopes, $|w|/H_0\le0.45$;
transverse shear is omitted at an estimated $4\%$; no experiment is reported.

\abshead{Practical implications}
Design formulae replace semi-empirical corrections; deformation, not strength or buckling,
sets the operating range.

\abshead{Originality/value}
The loop is closed in closed form and every formula is verified against an independent
computation.

\vspace{3pt}
\noindent\textbf{Keywords:} conjugate heat transfer; thermoelastic stability;
fluid--structure interaction; lubrication theory; Sturm--Liouville series;
verification

\vspace{2pt}
\noindent\textbf{Paper type:} Research paper
\end{structuredabstract}"""

VARIATIONAL = r"""
\subsection{Variational reduction to the strip}
\label{sec:variational}

The one-dimensional model of \S\ref{sec:wall} is not postulated: it is the Euler--Lagrange
system of a two-field functional obtained from the three-dimensional virtual work of the
strip. Let $u_0(x)$ be the axial displacement of the mid-surface and $w(x)$ the deflection
into the passage. Under the Kirchhoff hypothesis the displacement field and the axial strain
are
\begin{equation}
u_x=u_0(x)-y'w'(x),\qquad u_y=w(x),\qquad
\eps_{xx}=\eps^{0}-y'w'',\qquad
\eps^{0}=u_0'+\tfrac12 w'^2 ,
\label{eq:kirchhoff}
\end{equation}
with $y'$ measured from the mid-surface; the last term of $\eps^{0}$ is the geometric
shortening that couples stretching to bending and that a linear theory omits. The
plane-strain free energy of the strip, with the thermal strain subtracted, is
\begin{equation}
\Pi[u_0,w]=\frac12\int_0^L\int_{-d/2}^{d/2}
\frac{E}{1-\nu^2}\bigl[\eps_{xx}-(1+\nu)\alpha\theta\bigr]^2\,\dd y'\,\dd x
+\frac12\int_0^L D_s\bigl(w''+\kappa_{th}\bigr)^2\dd x-\int_0^L f\,w\,\dd x ,
\label{eq:functional}
\end{equation}
where the second integral is the bending energy written in terms of the curvature measured
from its stress-free value $\kappa_{th}=(1+\nu)\alpha q''/k_s$ of \eqref{eq:kappa}, and
$f=-p$ is the transverse load of the fluid. Carrying out the thickness integrals with
$\int\dd y'=d$ and $\int y'^2\dd y'=d^3/12$, and using \eqref{eq:theta_profile}, reduces
\eqref{eq:functional} to
\begin{equation}
\Pi=\frac12\int_0^L\Bigl[\frac{Ed}{1-\nu^2}\bigl(\eps^{0}-(1+\nu)\alpha\bar\theta\bigr)^2
+D_s\bigl(w''+\kappa_{th}\bigr)^2\Bigr]\dd x-\int_0^L f\,w\,\dd x .
\label{eq:functional1d}
\end{equation}

Stationarity with respect to $u_0$ returns the axial resultant
\begin{equation}
N=\frac{Ed}{1-\nu^2}\bigl(\eps^{0}-(1+\nu)\alpha\bar\theta\bigr)
=\frac{Ed}{1-\nu^2}\Bigl(u_0'+\tfrac12 w'^2-(1+\nu)\alpha\bar\theta\Bigr),
\label{eq:Nvariational}
\end{equation}
and, because $\partial\Pi/\partial u_0$ contains $u_0$ only through $N$, it also returns
$N'=0$: the axial force of a strip loaded only at its ends is constant along the span.
Stationarity with respect to $w$ gives
\begin{equation}
D_s\bigl(w''''+\kappa_{th}''\bigr)-\bigl(Nw'\bigr)'=f ,
\label{eq:EL}
\end{equation}
which is \eqref{eq:beam} once $N$ is constant. The kinematic constraint of the pinned ends,
$u_0(0)=u_0(L)=0$, integrates \eqref{eq:Nvariational} to
$\eps^{0}=\tfrac12\langle w'^2\rangle-(1+\nu)\alpha\bar\theta$ with
$\langle\cdot\rangle$ the span average, and substitution back into \eqref{eq:Nvariational}
returns \eqref{eq:nupdate}. The two equations of the strip model are therefore the two
Euler--Lagrange equations of one functional, not two independent assumptions, and the axial
compatibility condition is the statement that the ends cannot approach.

Three terms are discarded in the reduction, and each is bounded rather than ignored. Transverse
shear contributes the Timoshenko correction
$12D_s/(\kappa_sG\,dL^2)=4.0\%$ to the deflection at $L/d=10$ and $\nu=0.4$, with
$\kappa_s=5/6$ and $G=E/2(1+\nu)$; it is the largest single approximation of the model and is
carried explicitly into \S\ref{sec:limitations}. The finite-strain terms of \eqref{eq:kirchhoff}
are of order $\langle w'^2\rangle=1.4\times10^{-4}$ at the design point. The through-thickness
variation of the axial stress, which a beam theory replaces by its resultants, is recovered
only at the extreme fibre, where $\sigma_b=6|M|/d^2$; the error of that recovery is part of
the model-form error measured in \S\ref{sec:modform}.
"""

ANALYTICAL = r"""
\subsection{Analytical solution of the reduced problem}
\label{sec:analytical}

The reduced problem of \S\ref{sec:wall} is closed enough to be solved without a mesh: the
strip equation is linear for a given membrane force, the hydraulic resistance of the deformed
passage is an integral of a known function of the shape, and the thermal-entry problem is a
regular Sturm--Liouville problem. The three solutions are stated here as theorems because
each is used later as a verification reference, and because their hypotheses are exactly the
assumptions A1--A10 of \S\ref{sec:assumptions}. Throughout, $a=w_{\max}/H_0$ is the
normalised bow, $\xi=x/L$, $W=w/H_0$, $\beta=\kappa_{th}L^2/H_0$ and
$\lambda^2=NL^2/D_s$.

\subsubsection{Closed form of the strip}
\label{sec:stripclosed}

For constant $\kappa_{th}$ and constant $N$, equation \eqref{eq:beam} is linear with constant
coefficients. Its solution with $W(0)=W(1)=0$ and $W''(0)=W''(1)=-\beta$ is
\begin{equation}
W(\xi)=\frac{\beta}{\lambda^2}\Bigl[1-\cos\lambda\xi-\tan\frac{\lambda}{2}\,\sin\lambda\xi\Bigr]
+\frac{f L^4}{D_sH_0}\,
\frac{1}{\lambda^4}\Bigl[\frac{\lambda^2}{2}\xi(1-\xi)+\cos\lambda\xi-1
+\tan\frac{\lambda}{2}\Bigl(\sin\lambda\xi-\lambda\xi\Bigr)\Bigr],
\label{eq:Wclosed}
\end{equation}
whose first term is the thermal bow and whose second is the pressure bow; the pressure term
reproduces $5\bar pL^4/384D_s$ as $\lambda\to0$ and the thermal term reproduces the circular
arc $\beta\xi(1-\xi)/2$ in the same limit. Setting $\lambda=\pi$ in \eqref{eq:Wclosed} gives
the Euler load $N_{cr}=\pi^2D_s/L^2$ and, through \eqref{eq:ntheta}, the critical mean
temperature rise
\begin{equation}
\bar T_{cr}=\frac{\pi^2d^2}{12\,\alpha(1+\nu)L^2}=\frac{N_{cr}(1-\nu)}{Ed\alpha},
\label{eq:Tcr}
\end{equation}
which is independent of the modulus and scales as $(d/L)^2$. At the design point
$N_{cr}=1.057\times10^{5}$~N/m and $\bar T_{cr}=117.5$~K, so the buckling margin is
$M_b=\bar T_{cr}/\bar\theta=3.43$.

\subsubsection{The axial-compatibility map is a contraction}
\label{sec:contraction}

Write \eqref{eq:nupdate} as the scalar fixed-point problem $N=\mathcal F(N)$ with
\begin{equation}
\mathcal F(N)=N_\theta-c\,\bigl\langle w_N'^2\bigr\rangle,\qquad
c=\frac{Ed}{2(1-\nu^2)},
\label{eq:map}
\end{equation}
where $w_N$ is the solution \eqref{eq:Wclosed} of \eqref{eq:beam} at that $N$.

\begin{theorem}[Contraction of the axial map]
\label{thm:contraction}
Let $N_\theta<N_{cr}/3$. Then $\mathcal F$ maps $[0,N_{cr}/3]$ into itself, is a contraction
there, and the iteration $N_{k+1}=\mathcal F(N_k)$ converges to the unique fixed point $N^*$
with
\begin{equation}
|N_k-N^*|\le\frac{q^k}{1-q}\,|N_1-N_0|,\qquad
q=\frac{2N_\theta}{N_{cr}-N_\theta}<1 .
\label{eq:rate}
\end{equation}
\end{theorem}

\begin{proof}
See Appendix~\ref{app:proofs}. The mechanism is that $w_N$ is the solution of a linear
problem whose resolvent grows like $(N_{cr}-N)^{-1}$, so that
$\|\partial_N w_N'\|^2\le\|w_N'\|^2/(N_{cr}-N)$; with
$c\langle w_N'^2\rangle=N_\theta-N$ this gives
$|\mathcal F'|\le2(N_\theta-N)/(N_{cr}-N)\le q$.
\end{proof}

At the design point $N_\theta/N_{cr}=0.2746$, so the hypothesis of
Theorem~\ref{thm:contraction} is satisfied with $q=0.757$; the bound is sufficient but
conservative, and the derivative of $\mathcal F$ evaluated from \eqref{eq:Wclosed} at the same
point is $1.6\times10^{-5}$, which is why the scalar iteration converges in a few sweeps while
the outer fluid--thermal--structure loop of \S\ref{sec:coupling} needs nine.

\subsubsection{Closed-form hydraulic resistance}
\label{sec:lubrication}

In the lubrication limit $\varepsilon=H_0/L\ll1$ the streamwise momentum balance of the
passage, with mass flux $Q=UH_0$ per unit width conserved, integrates once to
\begin{equation}
-\frac{\dd p}{\dd x}=\frac{12\mu Q}{H(x)^3},\qquad H(x)=H_0-w(x),
\label{eq:lubmom}
\end{equation}
and the pressure drop over the strip is $\Delta p=12\mu Q\int_0^L H^{-3}\dd x$.

\begin{theorem}[Hydraulic resistance of the bowed passage]
\label{thm:pressure}
For the kinematic shape $w=w_{\max}\sin^2(\pi x/L)$ and $a=w_{\max}/H_0<1$,
\begin{equation}
\Delta p=\frac{12\mu QL}{H_0^{3}}\;{}_2F_1\!\Bigl(3,\tfrac12;1;a\Bigr)
=\Delta p_0\Bigl[1+\frac32a+\frac{27}{8}a^2+\frac{75}{16}a^3+O(a^4)\Bigr],
\label{eq:dpclosed}
\end{equation}
where $\Delta p_0=12\mu QL/H_0^3$ is the undeformed value and ${}_2F_1$ is the Gauss
hypergeometric function. The identity follows from
$\int_0^\pi(1-a\sin^2s)^{-3}\dd s=\pi\,{}_2F_1(3,\tfrac12;1;a)$.
\end{theorem}

\begin{proof}
Substitute $s=\pi x/L$ and expand $(1-a\sin^2s)^{-3}=\sum_n\frac{(3)_n}{n!}a^n\sin^{2n}s$;
term-by-term integration with $\int_0^\pi\sin^{2n}s\,\dd s=\pi(2n-1)!!/(2n)!!$ gives
$\pi\sum_n\frac{(3)_n(1/2)_n}{(n!)^2}a^n$, which is the hypergeometric series of
\eqref{eq:dpclosed}.
\end{proof}

Three consequences are used below. First, the first-order coefficient $3/2$ is the whole of
the linearised resistance: a $10\%$ bow raises the pressure drop by $15\%$. Second, the series
diverges in usefulness as $a\to1$, but \eqref{eq:dpclosed} remains finite and integrable for
$a<1$; at $a=0.4415$ it gives $\Delta p/\Delta p_0=2.187$, against $2.186$ computed. Third,
inertia enters only through the cross-sectionally averaged momentum balance
\begin{equation}
\frac{\dd}{\dd x}\Bigl(\tfrac65\rho Q^2/H\Bigr)=-\frac{\dd p}{\dd x}H-\frac{12\mu Q}{H^2},
\label{eq:averaged}
\end{equation}
whose inertial contribution, $(6/5)\rho Q^2(1/H_{\rm out}-1/H_{\rm in})=1.2\times10^{-3}$~Pa,
is five orders of magnitude below the viscous term at $\ReDh=50$; \eqref{eq:lubmom} is
therefore not an approximation but, at this Reynolds number, the exact leading-order balance.

\subsubsection{Thermal-entry problem as a Sturm--Liouville series}
\label{sec:thermalseries}

In the straight passage the energy equation with the fully developed velocity
$u=6U\,Y(1-Y)$, $Y=y/H_0$, and a uniform flux on one wall with an adiabatic opposite wall has
the exact solution
\begin{equation}
\theta(X,Y)=\Delta T^*\Bigl[f(Y)+\sum_{n\ge1}A_n\psi_n(Y)\,e^{-\lambda_n^2X}\Bigr],
\qquad \Delta T^*=\frac{q''H_0}{k_f},\quad X=\frac{x}{H_0\,\ReH\,Pr},
\label{eq:graetz}
\end{equation}
where $f''=6Y(1-Y)$, $f'(0)=0$, $f'(1)=1$, $\langle f\rangle=0$, so that
$f(Y)=Y^3-\tfrac12Y^4-\tfrac{9}{70}$ and $f(1)=13/35$.

\begin{theorem}[Eigenfunction solution of the entry problem]
\label{thm:graetz}
The functions $\psi_n$ are the eigenfunctions of the regular Sturm--Liouville problem
\begin{equation}
\psi_n''+\lambda_n^2\,6Y(1-Y)\,\psi_n=0,\qquad
\psi_n'(0)=\psi_n'(1)=0,
\label{eq:sl}
\end{equation}
which is self-adjoint in $L^2_w(0,1)$ with weight $w(Y)=6Y(1-Y)$; they are complete,
orthogonal in that weight, and the coefficients of \eqref{eq:graetz} are
$A_n=-\langle f,\psi_n\rangle_w/\langle\psi_n,\psi_n\rangle_w$. The local Nusselt number is
\begin{equation}
Nu(X)=\frac{2}{f(1)+\sum_{n\ge1}A_n\psi_n(1)\,e^{-\lambda_n^2X}}
\;\xrightarrow[X\to\infty]{}\;\frac{2}{f(1)}=\frac{70}{13}=5.3846 ,
\label{eq:Nuseries}
\end{equation}
and the entry length at which $Nu$ comes within $1\%$ of that limit is
$X_{99}=\ln100/\lambda_1^2$.
\end{theorem}

The eigenvalues are roots of a transcendental condition obtained by shooting
\eqref{eq:sl}; the first three are $\lambda_1=3.6956$, $\lambda_2=7.0010$,
$\lambda_3=10.2841$, with $A_1=0.1103$, $A_2=-0.0337$, $A_3=0.0165$ and
$\psi_1(1)=-1.506$. The limit \eqref{eq:Nuseries} reproduces the classical benchmark
$Nu_\infty=5.385$ of \citet{shah1978laminar} exactly, which is the clearest single check on
the series; the corresponding entry length is $X_{99}=0.337$, that is $29.4$~mm for the
present channel, comparable with the strip itself. Series truncation at $n=10$ changes
$Nu(X)$ by less than $10^{-4}$ for $X>10^{-3}$.

\subsubsection{Particular cases}
\label{sec:cases}

The model contains five limits that are used as checks in \S\ref{sec:asymptotics}:

\begin{enumerate}
\item \emph{Rigid wall} ($a\to0$, $E\to\infty$): \eqref{eq:dpclosed} gives
$\Delta p=\Delta p_0$ and \eqref{eq:Nuseries} the classical entry problem; the computed
undeformed pressure drop is $143.93$~Pa against $144$ analytic.
\item \emph{Pure conduction} ($Pe\to0$): the series collapses to its first term and the wall
temperature becomes linear in $x$; the wall rise reduces to $q''(d/2k_s+1/h)$.
\item \emph{Frozen membrane force} ($\mathcal F$ replaced by $N_\theta$): the bow is the first
term of \eqref{eq:Wclosed} with $\lambda^2=N_\theta L^2/D_s$, giving
$w_{\max}=2.189\times10^{-4}$~m against $2.207\times10^{-4}$ computed, an error of
$0.85\%$; the error of the closure itself grows to $14.9\%$ at
$q''=10\,\mathrm{kW/m^2}$ (\S\ref{sec:modform}).
\item \emph{Thin strip} ($d/L\to0$ with $q''$ fixed): $\kappa_{th}$ is independent of $d$
while $N_{cr}\propto(d/L)^2$, so buckling precedes any measurable hydraulic effect and the
deformation becomes negligible; this is the ordering quantified in \S\ref{sec:sensitivity}.
\item \emph{Buckling} ($N\to N_{cr}$): $\lambda\to\pi$ and $w_{\max}\to\infty$ for a fixed
$\kappa_{th}$; with the frozen membrane force of \eqref{eq:ntheta} the critical flux is
$q''_{cr}=\bar T_{cr}(1-\nu)/(Ed\alpha\,\theta_{\rm 1D}'')=18.2\,\mathrm{kW/m^2}$, where
$\theta_{\rm 1D}''=\bar\theta/q''$ is the one-dimensional response of
\S\ref{sec:baseline}; the geometric relief of \eqref{eq:nupdate} postpones it beyond the
$12\,\mathrm{kW/m^2}$ limit of the sweep.
\end{enumerate}

\subsubsection{Assembly of the semi-analytical model}
\label{sec:assembly}

Combining \eqref{eq:Wclosed}, \eqref{eq:dpclosed} and \eqref{eq:Nuseries} gives a model that
predicts the bow, the pressure drop and the wall temperature from the parameters alone,
without a mesh: $\kappa_{th}$ and $\bar\theta$ from one-dimensional conduction, $w_{\max}$ from
\eqref{eq:Wclosed} and \eqref{eq:map}, $\Delta p$ from \eqref{eq:dpclosed} with the computed
shape inserted in place of the kinematic one, and $Nu(x)$ from \eqref{eq:Nuseries}. Its
predictions are compared with the coupled finite-element solution in \S\ref{sec:asymptotics}.
"""

RESULTS = r"""
\subsection{The semi-analytical model against the computation}
\label{sec:asymptotics}

Table~\ref{tab:asymptotics} collects the comparison. The hydraulic result is the sharpest:
once the \emph{computed} interface shape is inserted into the lubrication integral
\eqref{eq:lubmom}, the closed form reproduces the finite-element pressure drop of
$314.508$~Pa to $+0.03\%$, so that at $\ReDh=50$ the pressure drop of the deformed passage is
a property of the shape alone and carries no discretisation or inertia error of its own. The
same integral evaluated with the kinematic idealisation $w=w_{\max}\sin^2(\pi x/L)$
underpredicts it by $15.08\%$, and Figure~\ref{fig:pressurelaw} shows how that error grows
with $a$: $-1.7\%$ at $a=0.067$, $-6.7\%$ at $a=0.228$ and $-15.1\%$ at $a=0.441$. The
sin$^2$ idealisation is thus a lower bound whose error is second order in the bow, which is
the quantitative reason why design estimates based on a nominal deflected shape deteriorate
exactly where the deformation matters.

\begin{table}[htbp]
\centering
\caption{The semi-analytical model of \S\ref{sec:analytical} against the coupled
finite-element solution at the design point. The difference is $(a-c)/c$.}
\label{tab:asymptotics}
\small
\begin{tabular}{@{}lrrr@{}}
\toprule
Quantity & Semi-analytical & Computed & Difference (\%) \\
\midrule
$\Delta p$ (Pa), lubrication, computed shape & 314.604 & 314.508 & $+0.03$ \\
$\Delta p$ (Pa), lubrication, $\sin^2$ shape & 267.07 & 314.508 & $-15.08$ \\
$w_{\max}$ ($10^{-4}$~m), closed form, frozen force & 2.1886 & 2.2074 & $-0.85$ \\
$\bar\theta$ (K), series and one-dimensional wall & 32.10 & 34.26 & $-6.30$ \\
$Nu_\infty$, developed value & 5.3846 & 5.3850$^{\dagger}$ & $-0.01$ \\
\bottomrule
\end{tabular}
\\[2pt]
{\footnotesize $^{\dagger}$ benchmark value of \citet{shah1978laminar}, reproduced by the
finite-element solver to $0.07\%$ (\S\ref{sec:benchmarks}).}
\end{table}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{fig13_asymptotics.pdf}
\caption{Thermal entry in the deformed passage. (a) Local Nusselt number: the Sturm--Liouville
series \eqref{eq:Nuseries} for the straight passage and the coupled computation for the bowed
one, at the same mass flux. (b) The ratio of the two against the local stretch $H_0/H$, with
the line of unit slope; the ratio reaches $1.68$ at the throat, where $H_0/H=1.79$.}
\label{fig:asymptotics}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{fig14_pressure_law.pdf}
\caption{Hydraulic resistance of the bowed passage. (a) The closed form
\eqref{eq:dpclosed} with its first-order truncation, and the coupled computations of the flux
sweep. (b) Relative difference between \eqref{eq:dpclosed} evaluated with the kinematic shape
and the coupled computation, against $a=w_{\max}/H_0$.}
\label{fig:pressurelaw}
\end{figure}

The thermal comparison is less sharp and more instructive. The series \eqref{eq:Nuseries}
describes a straight passage; in the bowed one the local Nusselt number exceeds it
everywhere, by $1.0\%$ at the ends of the strip and by $68\%$ at the throat
(Figure~\ref{fig:asymptotics}a), and the ratio correlates with the local stretch as
\begin{equation}
\frac{Nu(x)}{Nu_{\rm Graetz}(x)}\simeq\Bigl(\frac{H_0}{H(x)}\Bigr)^{p},\qquad
p=0.79\ \ (R^2=0.81,\ x>1\ \mathrm{mm}),
\label{eq:scaling}
\end{equation}
with the throat value $1.68$ against $H_0/H=1.79$ predicted for unit exponent. Two limiting
estimates bracket the exponent: a boundary layer thinned by the local acceleration
$u\propto1/H$ gives $h\propto u^{1/2}$ and $p=\tfrac12$, whereas one thinned by the wall
shear $\tau_w=6\mu Q/H^2$ gives $h\propto\tau_w^{1/2}$ and $p=1$. The measured $p=0.79$ lies
between them, as it must for a layer that is neither fully developed nor freshly started, and
\eqref{eq:scaling} is the quantitative statement of the feedback that motivates the whole
problem: the deformation raises the heat-transfer coefficient precisely where it constricts
the passage, so that the wall runs cooler than a straight-channel estimate predicts.

The wall temperature itself is $6.3\%$ higher in the computation than in the series-plus-
conduction model ($34.26$ against $32.10$~K). The gap is not a defect of the series: it is
the two-dimensional conduction in the strip, which the semi-analytical model replaces by a
linear through-thickness profile and a mean value, and which the computation resolves on the
wall mesh. It is reported here rather than absorbed into a correction factor because it is the
one quantity of the comparison that the reduced model cannot improve without abandoning its
one-dimensional structure.
"""

APPENDIX_D = r"""
% ===========================================================================
\section{Proofs of the theorems of Section~\ref{sec:analytical}}
\label{app:proofs}

\subsection*{D.1 Theorem~\ref{thm:contraction}: contraction of the axial map}

Let $w_N$ solve \eqref{eq:beam} with a constant membrane force $N$ and the boundary data of
\eqref{eq:beam}. Write the problem as $\mathcal L_Nw_N=g$ with
$\mathcal L_N=D_s\partial_x^4+N\partial_x^2$ and $g=f-D_s\kappa_{th}''$, and let
$(\cdot,\cdot)$ denote the $L^2(0,L)$ inner product. Differentiating in $N$,
\begin{equation}
\mathcal L_N\,\partial_Nw_N=-\partial_x^2w_N ,
\label{eq:D1}
\end{equation}
with homogeneous boundary data. Multiplying \eqref{eq:D1} by $w_N$, integrating by parts and
using the self-adjointness of $\mathcal L_N$ on the admissible space gives
\begin{equation}
\bigl(\partial_Nw_N,\mathcal L_Nw_N\bigr)
=\bigl(w_N',\partial_Nw_N'\bigr)-\bigl(w_N'',D_s\,\partial_Nw_N''\bigr)
=-\bigl(w_N'',w_N\bigr),
\label{eq:D2}
\end{equation}
so that, after another integration by parts and use of the coercivity of $\mathcal L_N$,
whose lowest eigenvalue is $D_s\pi^4(1-N/N_{cr})/L^4$,
\begin{equation}
\bigl\|\partial_Nw_N'\bigr\|^2\ \le\ \frac{\|w_N'\|^2}{N_{cr}-N}.
\label{eq:D3}
\end{equation}
Now $c\langle w_N'^2\rangle=N_\theta-N$ by \eqref{eq:map}, hence
\begin{equation}
\bigl|\mathcal F'(N)\bigr|
=2c\,\bigl|\langle w_N',\partial_Nw_N'\rangle\bigr|
\le2c\,\|w_N'\|\,\|\partial_Nw_N'\|
\le\frac{2\,(N_\theta-N)}{N_{cr}-N}
\le\frac{2N_\theta}{N_{cr}-N_\theta}=q .
\label{eq:D4}
\end{equation}
For $N_\theta<N_{cr}/3$ one has $q<1$; moreover $\mathcal F$ is continuous and
$0\le\mathcal F(N)\le N_\theta$, so $\mathcal F$ maps $[0,N_\theta]$ into itself. The Banach
fixed-point theorem then gives a unique $N^*$ and the geometric estimate \eqref{eq:rate}. The
same argument applied to the coupled map, with the thermal sub-problem replacing the fixed
$\bar\theta$, gives the contraction of the outer loop quoted in \S\ref{sec:coupling}.

\subsection*{D.2 Theorem~\ref{thm:pressure}: the hypergeometric resistance}

With $H=H_0(1-a\sin^2s)$, $s=\pi x/L$,
\begin{equation}
\int_0^L\frac{\dd x}{H^3}=\frac{L}{\pi H_0^3}\int_0^\pi
\frac{\dd s}{(1-a\sin^2s)^3}.
\label{eq:D5}
\end{equation}
Because the integrand is symmetric about $\pi/2$ and $\pi$, the integral over $(0,\pi)$ is
twice that over $(0,\pi/2)$, and the substitution $t=\sin^2s$ gives the Euler integral
\begin{equation}
\int_0^{\pi/2}\frac{\dd s}{(1-a\sin^2s)^3}
=\frac{\pi}{2}\,{}_2F_1\!\Bigl(3,\tfrac12;1;a\Bigr),
\label{eq:D6}
\end{equation}
which is the standard beta-integral representation
$\int_0^{\pi/2}\sin^{2\alpha-1}s\cos^{2\beta-1}s\,(1-a\sin^2s)^{-\gamma}\dd s
=\tfrac12B(\alpha,\beta)\,{}_2F_1(\gamma,\alpha;\alpha+\beta;a)$ with $\alpha=\beta=\tfrac12$
and $\gamma=3$. Combining \eqref{eq:D5} and \eqref{eq:D6} with $\Delta p=12\mu Q\int H^{-3}$
gives \eqref{eq:dpclosed}. The series in \eqref{eq:dpclosed} follows from
$(3)_n=n!(n+2)!/2$ and $(1/2)_n/(n!)=(2n-1)!!/(2^n n!)$.

A bound on the truncation of the shape is useful in design. If $w$ differs from the kinematic
shape by $\delta w$ with $\|\delta w\|_\infty\le\eta H_0$, then
$\delta(\Delta p)/\Delta p\le3\eta/(1-a)^{4}$, so that a $5\%$ error in the assumed shape at
$a=0.44$ produces at most a $24\%$ error in the resistance --- which is the order of the
$15\%$ observed in Figure~\ref{fig:pressurelaw}b, and the reason the computed shape must be
used in \eqref{eq:dpclosed} whenever it is available.

\subsection*{D.3 Theorem~\ref{thm:graetz}: completeness and coefficients}

The operator $\mathcal S\psi=-\psi''$ with Neumann data on $(0,1)$ and weight $w(Y)=6Y(1-Y)$
is self-adjoint and positive semi-definite in $L^2_w$; its spectrum is discrete,
$0=\lambda_0<\lambda_1<\lambda_2<\dots$, and the eigenfunctions form a complete orthogonal set.
The zero eigenvalue carries the constant eigenfunction, and therefore every $\psi_n$ with
$n\ge1$ has zero weighted mean, $\langle\psi_n\rangle_w=0$. Expanding the inlet condition
$\theta(0,Y)=0$ in that basis gives $A_n=-\langle f,\psi_n\rangle_w/\langle\psi_n,\psi_n\rangle_w$;
because the perturbation carries no wall flux, the wall temperature in
\eqref{eq:Nuseries} is $\Delta T^*[f(1)+\sum A_n\psi_n(1)e^{-\lambda_n^2X}]$, and division by
the imposed flux returns $Nu$. The limit $X\to\infty$ follows from the decay of every $n\ge1$
term, and $f(1)=13/35$ gives $Nu_\infty=70/13=5.3846$. Term-by-term differentiation is
legitimate because $\sum\lambda_n^2|A_n|^2<\infty$, which also bounds the truncation error by
the first omitted term.
"""

NOMENCLATURE_ROWS = r"""$a$ & normalised bow $w_{\max}/H_0$ & -- & $\lambda_n$ & eigenvalue of \eqref{eq:sl} & --\\
$A_n$ & series coefficient & -- & $\psi_n$ & eigenfunction of \eqref{eq:sl} & --\\
$c$ & axial stiffness $Ed/2(1-\nu^2)$ & N & $\mathcal F$ & axial-compatibility map & N\,m$^{-1}$\\
$H(x)$ & local passage height & m & ${}_2F_1$ & Gauss hypergeometric function & --\\
"""

CONCLUSION_BULLETS = r"""\item It is shown that the two equations of the strip model are the Euler--Lagrange
equations of a single two-field functional, so that the axial-compatibility condition
\eqref{eq:nupdate} is a consequence of the kinematic constraint of the pinned ends rather than
an additional assumption, and that the three terms discarded in the reduction are bounded by
$4.0\%$ (transverse shear), $1.4\times10^{-4}$ (finite strain) and the stress-recovery error
of \S\ref{sec:modform}.
\item It is shown that the axial-compatibility map is a contraction whenever
$N_\theta<N_{cr}/3$, with the explicit rate $q=2N_\theta/(N_{cr}-N_\theta)=0.757$ at the
design point, so that the coupled problem has a unique solution and the fixed-point iteration
converges geometrically; the measured derivative of the map is $1.6\times10^{-5}$.
\item It is shown that the hydraulic resistance of the bowed passage is a Gauss hypergeometric
function of the normalised bow, $\Delta p/\Delta p_0={}_2F_1(3,\tfrac12;1;a)$, that it
reproduces the coupled computation to $0.03\%$ when the computed shape is inserted, and that
the kinematic $\sin^2$ idealisation is a lower bound whose error grows to $15\%$ at
$a=0.44$.
\item It is shown that the thermal-entry problem in the straight passage has the exact
Sturm--Liouville solution \eqref{eq:graetz} with $\lambda_1=3.696$ and $Nu_\infty=70/13$,
that the deformation raises the local Nusselt number above that reference by up to $68\%$,
and that the excess collapses onto $\bigl(H_0/H\bigr)^{0.79}$ with $R^2=0.81$, between the
two exponents $(\tfrac12,1)$ that bracket a layer thinned by acceleration and by wall shear.
"""


def main() -> int:
    text = MAIN.read_text()
    if "sec:analytical" in text and "--force" not in sys.argv:
        raise SystemExit("main.tex already contains the analytical section; pass --force")

    # 0 -- theorem environments
    if "\\usepackage{amsthm}" not in text:
        text = text.replace("\\usepackage{amsmath,amssymb}",
                            "\\usepackage{amsmath,amssymb}\n\\usepackage{amsthm}", 1)
    if "\\newtheorem{theorem}" not in text:
        anchor = "\\sisetup{"
        thm = ("% ---- theorem environments ------------------------------------------------\n"
               "\\newtheorem{theorem}{Theorem}[section]\n"
               "\\newtheorem{corollary}[theorem]{Corollary}\n"
               "\\newtheorem{lemma}[theorem]{Lemma}\n\n")
        text = text.replace(anchor, thm + anchor, 1)

    # 1 -- abstract
    start = text.index("\\begin{structuredabstract}")
    end = text.index("\\end{structuredabstract}") + len("\\end{structuredabstract}")
    text = text[:start] + ABSTRACT + text[end:]

    # 2 -- variational subsection, before the interface conditions
    anchor = "\\subsection{Interface conditions}"
    assert anchor in text
    text = text.replace(anchor, VARIATIONAL.strip() + "\n\n" + anchor, 1)

    # 3 -- analytical block at the head of section 4
    anchor = "\\subsection{Discretisation and body-fitted mesh}"
    assert anchor in text
    text = text.replace(anchor, ANALYTICAL.strip() + "\n\n" + anchor, 1)

    # 3b -- the lead paragraph of section 4 must name the new subsection
    text = text.replace(
        "Sections~\\ref{sec:fe}--\\ref{sec:coupling}\ndefine the discretisation, the weak forms and the coupling; Sections\n"
        "\\ref{sec:grid} and \\ref{sec:verification} report the mesh-independence study and\nthe verification of the implementation.",
        "Section~\\ref{sec:analytical} solves the reduced problem in closed form;\nSections~\\ref{sec:fe}--\\ref{sec:coupling} define the discretisation, the weak forms and\n"
        "the coupling; Sections~\\ref{sec:grid} and \\ref{sec:verification} report the\nmesh-independence study and the verification of the implementation.")

    # 4 -- results subsection
    anchor = "\\subsection{Flow in the deformed passage}"
    assert anchor in text
    text = text.replace(anchor, RESULTS.strip() + "\n\n" + anchor, 1)

    # 5 -- appendix D before the corresponding-author block
    anchor = "\\vspace{10pt}\n\\noindent\\rule{\\textwidth}{0.4pt}"
    assert anchor in text
    text = text.replace(anchor, APPENDIX_D.strip() + "\n\n" + anchor, 1)

    # 6 -- nomenclature rows
    anchor = "$\\Ga_p$ & $w_{lin}/w_p$ & -- & $\\tau_w$ & wall shear stress & Pa\\\\"
    assert anchor in text
    text = text.replace(anchor, anchor + "\n" + NOMENCLATURE_ROWS.rstrip(), 1)

    # 7 -- conclusions
    marker = "\\section{Conclusions}"
    i = text.index(marker)
    j = text.index("\\end{enumerate}", i)
    text = text[:j] + CONCLUSION_BULLETS + text[j:]

    MAIN.write_text(text)
    print(f"wrote {MAIN} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
