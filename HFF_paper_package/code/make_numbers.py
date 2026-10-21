#!/usr/bin/env python3
"""Write numbers.tex: LaTeX macros for every computed number quoted in the manuscript.

The manuscript never types a computed value by hand.  It uses the macros defined here, which are
regenerated from results/baseline.json (hff_model.py) and results/q8_study.json (q8_strip.py).
"""
from __future__ import annotations

import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
OUT = HERE.parent / "numbers.tex"


def sci(x: float, digits: int = 2) -> str:
    """LaTeX scientific notation  a\\times10^{b}  (math mode content)."""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10**e
    m_txt = f"{m:.{digits}f}"
    if float(m_txt) >= 10:
        m_txt = f"{m / 10:.{digits}f}"
        e += 1
    return f"{m_txt}\\times10^{{{e}}}"


def richardson(f_c, f_m, f_f, r=2.0):
    """Observed order, extrapolated value and GCI (Roache, Fs = 1.25) from three levels."""
    e1, e2 = f_m - f_c, f_f - f_m
    if e1 * e2 <= 0 or e2 == 0:
        return None
    p = math.log(abs(e1 / e2)) / math.log(r)
    f_inf = f_f + e2 / (r**p - 1)
    gci = 1.25 * abs(e2 / f_f) / (r**p - 1)
    return p, f_inf, gci


def main() -> None:
    B = json.loads((RES / "baseline.json").read_text())
    r, fb, ce, ss = B["baseline"], B["feedback"], B["ceilings"], B["stainless"]
    Q = json.loads((RES / "q8_study.json").read_text())
    runs = {(x["nx"], x["ny"]): x for x in Q["runs"]}

    m: dict[str, str] = {}
    hm_H0 = 5.0e-4
    NcrBeam = r['N_cr']

    def put(name, text):
        m[name] = text

    # ---- baseline (Section 4, Tables) ----
    put("NumRe", f"{r['Re']:.0f}")
    put("NumPr", f"{r['Pr']:.2f}")
    put("NumPe", f"{r['Pe']:.0f}")
    put("NumDp", f"{r['dp']:.0f}")
    put("NumTauW", f"{r['tau_w']:.1f}")
    put("NumRi", sci(r["Ri"], 1))
    put("NumBr", sci(r["Br"], 1))
    put("NumDTstar", f"{r['dT_scale']:.2f}")
    put("NumDTt", f"{r['dT_t']:.0f}")
    put("NumDTb", f"{r['dT_b']:.2f}")
    put("NumQoverH", f"{r['q_over_h']:.2f}")
    put("NumHrigid", f"{r['h_rigid']:.0f}")
    put("NumThetaBar", f"{r['theta_bar']:.1f}")
    put("NumKappa", f"{r['kappa_th']:.1f}")
    put("NumDs", f"{r['D_s']:.2f}")
    put("NumNtheta", f"{abs(r['N_theta']) / 1e4:.2f}\\times10^{{4}}")
    put("NumNcr", f"{r['N_cr'] / 1e5:.2f}\\times10^{{5}}")
    put("NumNratio", f"{r['Nc_over_Ncr']:.3f}")
    put("NumTcr", f"{r['T_cr']:.0f}")
    put("NumMb", f"{r['M_b']:.2f}")
    put("NumMuL", f"{r['mu_L_frozen']:.2f}")
    put("NumWlin", sci(r["w_lin"], 2))
    put("NumWlinH", f"{r['w_lin_over_H0']:.3f}")
    put("NumWfrozen", sci(r["w_frozen"], 2))
    put("NumWfrozenH", f"{r['w_frozen_over_H0']:.3f}")
    put("NumWsc", sci(r["w_sc"], 2))
    put("NumWscH", f"{r['w_sc_over_H0']:.3f}")
    put("NumAmpFrozen", f"{r['amplification_frozen']:.2f}")
    put("NumAmpSc", f"{r['w_sc'] / r['w_lin']:.2f}")
    put("NumAmpEuler", f"{r['amplification_euler']:.2f}")
    put("NumRelax", f"{100 * r['relaxation_sc']:.1f}")
    put("NumExcessFrozen", f"{100 * r['frozen_over_sc_excess']:.1f}")
    put("NumHmidFrozen", f"{r['H_mid_frozen_over_H0']:.4f}")
    put("NumHmidSc", f"{r['H_mid_sc_over_H0']:.3f}")
    put("NumHmidMm", f"{1e3 * r['H_mid_frozen']:.3f}")
    put("NumWfrozenMm", f"{1e3 * r['w_frozen']:.3f}")
    put("NumSlope", f"{r['slope_max']:.3f}")
    put("NumArcStrain", sci(r["arc_strain_frozen"], 2))
    put("NumFibreStrain", sci(r["fibre_strain"], 2))
    put("NumSigBend", f"{r['sigma_bend'] / 1e6:.1f}")
    put("NumSigMemb", f"{r['sigma_memb'] / 1e6:.1f}")
    put("NumSigMax", f"{r['sigma_max'] / 1e6:.1f}")
    put("NumSigFrac", f"{r['stress_fraction']:.2f}")
    put("NumMmid", f"{abs(r['M_mid']):.1f}")
    put("NumPbar", f"{r['p_bar']:.0f}")
    put("NumPentry", f"{r['p_strip_entry']:.0f}")
    put("NumPexit", f"{r['p_strip_exit']:.0f}")
    put("NumWp", sci(r["w_p_lin"], 2))
    put("NumWpBC", sci(r["w_p_bc"], 2))
    put("NumGammaLin", f"{r['Gamma_p_lin']:.1f}")
    put("NumGammaLinRound", f"{r['Gamma_p_lin']:.0f}")
    put("NumGammaBC", f"{r['Gamma_p_bc']:.1f}")
    put("NumGammaBCRound", f"{r['Gamma_p_bc']:.0f}")
    put("NumGammaMixed", f"{r['Gamma_p_mixed']:.1f}")
    put("NumDpLub", f"{r['dp_lub_deformed']:.0f}")
    put("NumDpLubRatio", f"{r['dp_ratio_lub']:.2f}")
    put("NumDpLubDrop", f"{100 * (1 - r['dp_ratio_lub']):.0f}")
    put("NumHydFeedbackPct", f"{100 * r['w_p_bc'] / r['w_frozen']:.2f}")
    put("NumExcessRatio", f"{r['q_over_h_ratio']:.2f}")
    put("NumExcessDeformed", f"{r['q_over_h_mean_deformed']:.2f}")
    put("NumReHL", f"{r['Re_Hover_L']:.2f}")
    put("NumLoverLT", f"{r['L_over_LT']:.1f}")
    put("NumLT", f"{1e3 * r['L_T_est']:.1f}")
    put("NumFeedbackExtraK", f"{fb['extra_interface_excess_K']:.2f}")
    put("NumFeedbackPct", f"{100 * fb['relative_change_in_w']:.1f}")
    put("NumQw", f"{ce['q_w_guard'] / 1e3:.1f}")
    put("NumQs", f"{ce['q_stress_guard'] / 1e3:.1f}")
    put("NumQb", f"{ce['q_buckling_guard'] / 1e3:.1f}")
    put("NumExcessW", f"{100 * ce['excess_w_guard']:.1f}")
    put("NumExcessS", f"{100 * ce['excess_stress_guard']:.1f}")
    put("NumExcessB", f"{100 * ce['excess_buckling_guard']:.0f}")
    put("NumRatioW", f"{ce['ratio_w_guard']:.2f}")
    put("NumRatioS", f"{ce['ratio_stress_guard']:.2f}")
    put("NumWHs", f"{ce['wH0_stress_guard']:.2f}")
    put("NumWHb", f"{ce['wH0_buckling_guard']:.2f}")
    put("NumStainlessKappa", sci(ss["kappa_th"], 1))
    put("NumStainlessWH", sci(ss["w_lin_over_H0"], 1))
    put("NumPolymerOverStainless", f"{r['w_lin_over_H0'] / ss['w_lin_over_H0']:.0f}")

    # ---- Q8 mesh study (Section 5) ----
    mid = lambda nx, ny, mode: runs[(nx, ny)][mode]["d/2"]
    put("QPointMin", f"{min(mid(nx, ny, 'POINT') for nx, ny in runs):.5f}")
    put("QPointMax", f"{max(mid(nx, ny, 'POINT') for nx, ny in runs):.5f}")
    put("QPatchMax", f"{max(x['patch'] for x in runs.values()):.0e}".replace("e-", "\\times10^{-") + "}")
    put("QPinCoarse", f"{mid(6, 2, 'PIN'):.4f}")
    put("QPinTwo", f"{mid(192, 2, 'PIN'):.5f}")
    put("QPinFour", f"{mid(192, 4, 'PIN'):.5f}")
    put("QPinEight", f"{mid(192, 8, 'PIN'):.5f}")
    put("QPinDefect", f"{100 * (1 - mid(192, 8, 'PIN')):.2f}")
    # axial change of the PIN ratio over the last two refinements, NY = 8
    put("QPinAxialLast", f"{abs(mid(192, 8, 'PIN') - mid(96, 8, 'PIN')):.0e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}")
    put("QPinThickLast", f"{abs(mid(192, 8, 'PIN') - mid(192, 4, 'PIN')):.0e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}")
    put("QPinThickFirst", f"{abs(mid(192, 4, 'PIN') - mid(192, 2, 'PIN')):.1e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}")
    # clamp
    for ny in (2, 4, 8):
        seq = [mid(nx, ny, "CLAMP") for nx in (6, 12, 24, 48, 96, 192)]
        ric = richardson(seq[-3], seq[-2], seq[-1])
        tag = {2: "Two", 4: "Four", 8: "Eight"}[ny]
        put(f"QClampLast{tag}", f"{seq[-1]:+.4f}".replace("-", "-"))
        if ric:
            p, finf, gci = ric
            put(f"QClampOrder{tag}", f"{p:.1f}")
            put(f"QClampInf{tag}", f"{finf:+.4f}")
            put(f"QClampGCI{tag}", f"{100 * gci:.1f}")
    put("QClampCoarse", f"{mid(6, 2, 'CLAMP'):+.3f}")
    put("QClampTwelveTwo", f"{mid(12, 2, 'CLAMP'):+.3f}")
    put("QElemMax", f"{max(x['elements'] for x in runs.values())}")


    # ---- restrained, geometrically nonlinear Q8 (Section 5) ----
    NL = json.loads((RES / "q8_nl.json").read_text())
    nruns = {(x["nx"], x["ny"]): x for x in NL["runs"]}
    fine = nruns[(192, 8)]
    wl_beam, wf, wsc = NL["w_lin_beam"], NL["w_frozen_beam"], NL["w_sc_beam"]
    ncf, ncs = NL["Nc_frozen_beam"], NL["Nc_sc_beam"]
    wl_fe, wn_fe = fine["linear"]["w_mid"], fine["nonlinear"]["w_mid"]
    put("NLwFE", sci(wn_fe, 3))
    put("NLwFEH", f"{wn_fe / hm_H0:.3f}")
    put("NLlinRatio", f"{wl_fe / wl_beam:.4f}")
    put("NLampFE", f"{wn_fe / wl_fe:.3f}")
    put("NLoverSc", f"{wn_fe / wsc:.3f}")
    put("NLoverScPct", f"{100 * (wn_fe / wsc - 1):.1f}")
    put("NLoverFrozenPct", f"{100 * (wn_fe / wf - 1):.1f}")
    put("NLNmidLin", f"{fine['linear']['Nc_mid'] / 1e3:.2f}")
    put("NLNmidNL", f"{fine['nonlinear']['Nc_mid'] / 1e3:.2f}")
    put("NLNmidLinPct", f"{100 * (fine['linear']['Nc_mid'] / ncf - 1):.1f}")
    put("NLNmidNLPct", f"{100 * (fine['nonlinear']['Nc_mid'] / ncs - 1):.1f}")
    put("NLrelaxFE", f"{100 * (1 - fine['nonlinear']['Nc_mid'] / fine['linear']['Nc_mid']):.1f}")
    put("NLconvAxial", f"{100 * abs(nruns[(192, 8)]['nonlinear']['w_mid'] / nruns[(96, 8)]['nonlinear']['w_mid'] - 1):.3f}")
    put("NLconvThick", f"{100 * abs(nruns[(96, 4)]['nonlinear']['w_mid'] / nruns[(96, 8)]['nonlinear']['w_mid'] - 1):.2f}")
    put("NLtangentMax", f"{max(x['tangent_check'] for x in NL['runs']):.0e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}")
    put("NLnewtonMax", f"{max(it for x in NL['runs'] for (_, it, _) in x['newton'])}")
    put("NLresMax", f"{max(r for x in NL['runs'] for (_, _, r) in x['newton']):.0e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}")
    put("NLthetaBar", f"{NL['theta_bar']:.1f}")
    put("NLNmidAmpEuler", f"{1 / (1 - fine['nonlinear']['Nc_mid'] / NcrBeam):.3f}")


    # ---- independent P2-triangle code and thin-strip study (Section 5) ----
    IND = json.loads((RES / "fe_independent.json").read_text())
    iruns = {(x["nx"], x["ny"]): x for x in IND["runs"]}
    ifine = iruns[(192, 8)]
    put("IndElements", f"{ifine['elements']}")
    put("IndW", sci(ifine["w_nl"], 3))
    put("IndDiffPct", f"{100 * abs(ifine['w_nl'] / wn_fe - 1):.3f}")
    put("IndLinDiffPct", f"{100 * abs(ifine['w_lin'] / wl_fe - 1):.4f}")
    put("IndNDiffPct", f"{100 * abs(ifine['Nc_nl'] / fine['nonlinear']['Nc_mid'] - 1):.2f}")
    put("IndConv", f"{100 * abs(iruns[(192, 8)]['w_nl'] / iruns[(96, 8)]['w_nl'] - 1):.2f}")
    SL = json.loads((RES / "slenderness.json").read_text())
    rows = []
    for rw in SL["rows"]:
        b = rw["beam"]
        rows.append(f"{rw['d_over_L']:.3f} & {1e3 * rw['d']:.2f} & {rw['fe_w_lin'] / b['w_lin']:.4f} & "
                    f"{rw['fe_w_nl'] / b['w_sc']:.4f} & {rw['fe_w_nl'] / b['w_frozen']:.4f} & "
                    f"{rw['fe_Nc_nl'] / b['N_sc']:.4f} \\\\")
    (HERE.parent / "tab_slender.tex").write_text("% AUTO-GENERATED by make_numbers.py\n"
        "\\begin{tabular}{@{}cccccc@{}}\n\\toprule\n"
        "$d/L$ & $d$ (mm) & $w^{\\rm lin}_{\\rm FE}/w^{\\rm lin}_{\\rm beam}$ & $w^{\\rm NL}_{\\rm FE}/w_{\\rm sc}$ & "
        "$w^{\\rm NL}_{\\rm FE}/w_{\\rm ff}$ & $N_{c,\\rm FE}/N_c^{\\rm sc}$ \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    first, last = SL["rows"][0], SL["rows"][-1]
    put("SlForceRatio", f"{SL['force_ratio']:.3f}")
    put("SlFirstPct", f"{100 * (first['fe_w_nl'] / first['beam']['w_sc'] - 1):.1f}")
    put("SlLastPct", f"{100 * (last['fe_w_nl'] / last['beam']['w_sc'] - 1):+.1f}".replace("-", "-"))
    put("SlLastDL", f"{last['d_over_L']:.3f}")
    put("SlLastFrozenPct", f"{100 * (1 - last['fe_w_nl'] / last['beam']['w_frozen']):.0f}")
    mid_row = SL["rows"][2]
    put("SlMidPct", f"{100 * (mid_row['fe_w_nl'] / mid_row['beam']['w_sc'] - 1):.1f}")
    mc = SL["mesh_check"]
    put("SlMeshPct", f"{100 * abs(mc['ratio_384x16'] - mc['ratio_192x8']):.2f}")
    put("SlMidDL", f"{mid_row['d_over_L']:.3f}")

    # ---- generated tables ----
    tabs = []
    rows = []
    for ny in (2, 4, 8):
        seq = [mid(nx, ny, "CLAMP") for nx in (6, 12, 24, 48, 96, 192)]
        ric = richardson(seq[-3], seq[-2], seq[-1])
        p_txt = f"{ric[0]:.1f}" if ric else "--"
        inf_txt = f"{ric[1]:+.4f}" if ric else "--"
        gci_txt = f"{100 * ric[2]:.1f}" if ric else "--"
        rows.append(f"{ny} & {192 * ny} & {mid(192, ny, 'POINT'):.5f} & {mid(192, ny, 'PIN'):.5f} & "
                    f"{seq[2]:+.4f} & {seq[-1]:+.4f} & {p_txt} & {inf_txt} & {gci_txt} \\\\")
    tabs.append("\\begin{tabular}{@{}rrcccccrr@{}}\n\\toprule\n"
                "$N_y$ & elements & point pin & full-edge pin & clamp & clamp & $p$ & clamp, extrap. & GCI (\\%) \\\\\n"
                " & ($N_x=192$) & ($N_x=192$) & ($N_x=192$) & ($N_x=24$) & ($N_x=192$) & & & \\\\\n\\midrule\n"
                + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (HERE.parent / "tab_q8_mesh.tex").write_text("% AUTO-GENERATED by make_numbers.py\n" + tabs[0].replace("-0.", "$-$0."))
    rows = []
    for (nx, ny), x in sorted(nruns.items(), key=lambda kv: kv[1]["elements"]):
        rows.append(f"${nx}\\times{ny}$ & {x['elements']} & {x['linear']['w_mid'] / wl_beam:.4f} & "
                    f"{1e6 * x['nonlinear']['w_mid']:.2f} & {x['nonlinear']['w_mid'] / hm_H0:.4f} & "
                    f"{x['nonlinear']['Nc_mid'] / 1e3:.2f} \\\\")
    (HERE.parent / "tab_q8_nl.tex").write_text("% AUTO-GENERATED by make_numbers.py\n"
        "\\begin{tabular}{@{}lrcccc@{}}\n\\toprule\n"
        "mesh $N_x\\times N_y$ & elements & $w^{\\rm lin}/(\\kth L^2/8)$ & $w_{\\max}^{\\rm NL}$ (\\si{\\micro\\metre}) & $w_{\\max}^{\\rm NL}/H_0$ & $N_c$ at mid-span (kN\\,m$^{-1}$) \\\\\n"
        "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

    lines = ["% AUTO-GENERATED by code/make_numbers.py -- do not edit by hand.", ""]
    for k, v in m.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} with {len(m)} macros")


if __name__ == "__main__":
    main()
