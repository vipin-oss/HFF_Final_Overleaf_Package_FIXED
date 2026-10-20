#!/usr/bin/env python3
"""HFF regression suite, version 6 (Stage 20).

Version 3 answers the Stage 16 audit finding that the suite was blind to equation-level
faults.  It has three independent layers:

  A. structural / claim checks on the source strings;
  B. FINGERPRINTS: every display equation and every register row is canonicalised, hashed and
     compared with audit_stage15/equation_fingerprints.json.  Editing an equation therefore
     fails the suite unless the fingerprint file is deliberately regenerated with
     `python3 audit_stage15/regression.py --update-fingerprints`.
     A fingerprint is CHANGE DETECTION, NEVER A CORRECTNESS PROOF: it records that an expression
     is unchanged, not that it is right.  Regeneration therefore no longer short-circuits the
     run (Stage 18 fix, F1): it writes the file, prints a warning and then executes every
     substantive check below, exiting non-zero if any of them fails.  Corrupting an equation and
     regenerating its fingerprint cannot turn a wrong expression into a passing suite;
  C. numeric checks that parse BOTH the printed inputs and the printed results out of the
     manuscript and recompute.

Stage 19 makes three existing semantic tests structural, because the Stage 18 audit showed each
could be satisfied by the same statement in another notation: the pressure gauge is judged by the
CLAUSE carrying the constraint (contrastive connectives are clause boundaries) and recognises a
datum at a single point, p(\mathbf 0)=0; tab:bcs is tested row by row for any surface, so the
Boundary cell no longer decides whether a row is looked at; and the prose datum test is a shape test
(a solid Dirichlet datum together with a non-zero solid flux datum that is not placed on the heated
face) rather than a search for "on <surface>".  Stale end-effect magnitudes written "pct" or
"percentage points" are included in the scan.  An expression the parser cannot read now fails the
run instead of skipping the numeric checks that depend on it.

Run from the repository root:  python3 audit_stage15/regression.py
"""
import re, glob, sys, os, json, hashlib, time, importlib.util

from math import *


def P(x):
    """plain TeX text: @ stands for one backslash."""
    return x.replace("@", "\\")


def R(x):
    """regex literal for TeX: @ stands for one escaped backslash."""
    return x.replace("@", "\\\\")

BS = chr(92)
FAIL, N_PASS, WARN = [], 0, []
def check(name, ok, detail=""):
    global N_PASS
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + str(detail)) if detail else ""))
    if ok: N_PASS += 1
    else: FAIL.append(name)

def read(p): return open(p, encoding='utf-8').read()

FILES = ['main.tex'] + sorted(glob.glob('chapters/*.tex')) + sorted(glob.glob('figures/*.tex'))
REQUIRED = (['main.tex', 'references.bib', 'README.md'] +
            ['chapters/ch%02d.tex' % i for i in range(1, 12)] +
            ['chapters/appendix.tex', 'chapters/audit_appendix.tex'])
_MISSING = [p for p in REQUIRED if not os.path.isfile(p)]
if _MISSING:
    print("FAIL  required source files missing: %s" % ", ".join(_MISSING))
    print("FAIL  the suite cannot run; NO check below this line was executed")
    sys.exit(1)
SRC = {f: read(f) for f in FILES}
ALL = ''.join(SRC.values())
BODY = ''.join(SRC[f] for f in FILES if f != 'chapters/audit_appendix.tex')
C2, C3, C4, C5, C7, C8, C9 = (SRC['chapters/ch0%d.tex' % i] for i in (2,3,4,5,7,8,9))
C6, C11 = SRC['chapters/ch06.tex'], SRC['chapters/ch11.tex']
APP = SRC['chapters/appendix.tex']

# ----------------------------------------------------------------------------------
print("=" * 78); print("SECTION 1  Structural integrity"); print("=" * 78)
def stripped(t): return re.sub(r'(?<!\\)%.*', '', re.sub(r'\\[{}%]', '', t))
badb = [f for f in FILES if stripped(SRC[f]).count('{') != stripped(SRC[f]).count('}')]
bade = [f for f in FILES if len(re.findall(r'\\begin\{', re.sub(r'(?<!\\)%.*','',SRC[f])))
        != len(re.findall(r'\\end\{', re.sub(r'(?<!\\)%.*','',SRC[f])))]
check("braces balanced in all %d files" % len(FILES), not badb, badb)
check("environments balanced", not bade, bade)

labels = re.findall(r'\\label\{([^}]+)\}', ALL)
refs = set(re.findall(r'\\(?:eq)?ref\{([^}]+)\}', ALL))
dups = sorted({k for k in labels if labels.count(k) > 1})
check("labels unique", not dups, "%d labels, dups=%s" % (len(labels), dups or "none"))
check("no dangling references", not (refs - set(labels)), sorted(refs - set(labels)))

bibkeys = set(re.findall(r'@\w+\{([^,]+),', read('references.bib')))
cited = set()
for grp in re.findall(r'\\cite[a-z]*\{([^}]*)\}', re.sub(r'(?<!\\)%.*','',ALL)):
    for k in grp.replace('\n','').split(','):
        if k.strip(): cited.add(k.strip())
check("all cited keys resolve", not (cited - bibkeys), sorted(cited - bibkeys))
check("no uncited bib entries", not (bibkeys - cited), sorted(bibkeys - cited))
defined = set(re.findall(r'\\(?:newcommand|renewcommand|DeclareMathOperator|def)\*?\{?\\([A-Za-z]+)',
                         SRC['main.tex']))
undefined = [m for m in ('ie','eg','cf','etal','wrt') if (BS+m) in ALL and m not in defined]
check("no undefined shorthand macros", not undefined, undefined)
REG_ROWS = [l for l in SRC['chapters/audit_appendix.tex'].split('\n') if re.match(r'^D-\d+ &', l)]
check("register rows present and counted", len(REG_ROWS) == 35, "%d rows" % len(REG_ROWS))

# ----------------------------------------------------------------------------------
print(); print("=" * 78); print("SECTION 2  Claims: sign, boundary conditions, units, model"); print("=" * 78)
check("deflection convention w = +d_2", ('w=+d_2' in BODY) or ('w = +d_2' in BODY))
check("pressure term is D_s w'''' = +p", (",w^{''''}(x)= +"+BS+",p(x)") in C3)
check("pressure term is not -p",       (",w^{''''}(x)= -"+BS+",p(x)") not in BODY)

check("geometric term present, negative, with N/d", ("-"+BS+"int_{"+BS+"Om_s^0}"+BS+"frac{N_"+BS+"theta^c}{d}") in C8)
check("old no-1/d geometric form removed", ("-"+BS+"int_{"+BS+"Om_s^0}N_"+BS+"theta^c"+BS+","+BS+"partial_X d_2") not in C8)
check("geometric term sign not flipped", ("+"+BS+"int_{"+BS+"Om_s^0}"+BS+"frac{N_"+BS+"theta^c}{d}") not in C8)
check("no halved 1/(2d) coefficient anywhere", (BS+"frac{N_"+BS+"theta^c}{2d}") not in ALL)

m7 = re.search(r'B7 & strip ends.*?' + BS*2 + r'\n', C5, re.S)
b7 = m7.group(0) if m7 else ''
check("B7 found", bool(m7))
check("B7 is not a full-edge clamp", 'd_1=d_2=0' not in b7, b7[:60])
check("B7 imposes d_2=0", 'd_2=0' in b7, b7[:60])
check("B7 blocks mean axial displacement", (BS+"langle d_1"+BS+"rangle=0") in b7, b7[:60])

i9 = C2.find(P("@item[@textbf{A9}]"))
j9 = C2.find(P("@item[@textbf{A10}]"), i9 + 1)
a9 = C2[i9:j9] if (i9 >= 0 and j9 > i9) else ''
check("A9 found", bool(a9))
check("A9 states the pin, not a clamp", ('d_2=0' in a9) and (BS+'langle d_1'+BS+'rangle=0' in a9))
check("A9 no longer says the ends have zero displacement", 'have zero displacement' not in a9)
check("A9 is not a clamp", (P("emph{not} $d_1=d_2=0$ pointwise") in a9) and (P("emph{clamp}") in a9))
check("A9 carries the measured 0.998", '0.998' in a9)

check("V_s defined with phi_2 = 0 on end edges", (BS+"varphi_2=0") in C8)
check("V_s is not a clamp", (BS+"boldsymbol"+BS+"varphi="+BS+"mathbf 0"+BS+" "+BS+"text{on the pinned ends}") not in C8)
check("V_s integral condition is homogeneous", (BS+"varphi_1"+BS+","+BS+"mathrm dY=0") in C8)

# --- thermal well-posedness (NEW-01 / D-32) ---
check("solid receives the interface temperature (Dirichlet)",
      ('solid thermal' in C8) and ('Dirichlet datum' in C8))
check("fluid receives the interface flux (Neumann)",
      (BS+'emph{Neumann datum}' in C8) and ('k_f'+BS+'nabla T_f'+BS+'cdot'+BS+'bn=q_'+BS+'Gamma^{(k)}' in C8))
check("the false 'temperature level is fixed' claim is gone", 'temperature level is fixed' not in C8)
check("the pure-Neumann argument is stated", 'pure-Neumann' in C8)
check("the level is traced into theta-bar and N_theta",
      (BS+'bar'+BS+'theta' in C8) and ('N_'+BS+'theta' in C8) and ('inherit the level' in C8))
check("ch05 and ch08 agree that a solid flux datum is inadmissible",
      ('pure-Neumann' in C5) and ('register D-32' in C5) and ('register D-32' in C8))
check("step 1 gives the solid T_s = T_Gamma^{(k)} on the interface",
      P("T_s=T_@Gamma^{(k)}$ on $@Ga_{@mathrm{if}}$") in C8, "Dirichlet datum in the iteration step")
check("the flux-datum alternative is marked as the rejected one",
      "Transferring the conjugate flux instead would give the solid flux data" in C8,
      "the paragraph must not read as a description of the adopted solid problem")
check("the kernel/compatibility argument is spelled out",
      ("has the constant" in C8) and ("in its kernel" in C8) and ("sum to zero" in C8)
      and ("doubly inadmissible" in C8) and ("no constant in its kernel" not in C8))
check("the loop closes on the extracted interface temperature",
      "which closes the thermal loop" in C8)

# --- pressure gauge (Stage 18 G1/G2, hardened in Stage 19) -----------------------------------
# A pressure normalisation may appear ONLY as an explicitly rejected counterfactual.  Two things
# decide the verdict, and neither is a character window:
#   (a) NOTATION: the constraint is recognised as an integral, a mean, a zero-mean claim, or a datum
#       at a single point (p(\mathbf 0)=0, p|_{x_0}=0).  A pointwise datum is the same gauge choice
#       in another notation, and it is what suite v4 missed;
#   (b) CLAUSE: the rejecting language must be in the clause that carries the constraint, and that
#       clause must not carry adopting language.  Contrastive connectives are clause boundaries, so
#       "we choose X for the level rather than rely on the outflow condition" is judged on
#       "we choose X for the level" and fails.  A sentence-level test let "rather than" excuse the
#       adoption elsewhere in the sentence, which is what suite v4 missed.
P_NORM = [
    re.compile(r'\\int[^$]{0,140}?(?<![A-Za-z\\\\])p(?![A-Za-z])[^$]{0,80}?=\s*0'),
    re.compile(r'\\langle\s*p\s*\\rangle[^$]{0,40}?=\s*0'),
    re.compile(r'\\overline\{\s*p\s*\}[^$]{0,40}?=\s*0'),
    re.compile(r'\\bar\{?\s*p\s*\}?[^$]{0,40}?=\s*0'),
    re.compile(r'(zero[- ]mean|mean[- ]zero)[^.$]{0,40}?(?:pressure|\bp\b)', re.I),
    # a datum at one point is a normalisation too (suite v4 blind spot M3c)
    re.compile(r'(?<![A-Za-z])p\s*\(\s*(?:\\mathbf\s*\{?\s*0\s*\}?|\\boldsymbol\s*\{?\s*0\s*\}?|'
               r'0|x_0|\\mathbf\{x\}_0)\s*\)\s*=\s*0'),
    re.compile(r'(?<![A-Za-z])p\s*(?:\\big|\\Big|\\left)?\s*\\?\|_\{[^{}]{1,24}\}\s*=\s*0'),
]
REJECT = re.compile(r'(over-determin|overdetermin|would be inadmissible|would inject|spurious|'
                    r'nothing is imposed|is not imposed|are not imposed|not imposed|must not be\b|'
                    r'no gauge|no such freedom|rather than|instead of|unnecessary|redundant|'
                    r'would be wrong|not required|no freedom|no normalis|no normaliz)', re.I)
ADOPT = re.compile(r'(we (?:impose|fix|set|enforce|adopt|normalise|normalize|require|pin|anchor|'
                   r'choose|use|take|add|append|supplement|close)|'
                   r'(?:is|are|was|were) (?:imposed|enforced|fixed|required|normalised|normalized|'
                   r'pinned|anchored|chosen|added)|'
                   r'imposes?\b|enforces?\b|adding the|adding a|add the|we take|is set to zero|'
                   r'is normalised|is normalized|we normalise|we normalize|we choose|'
                   r'pinn(?:ed|ing)\b|anchors? the|normalis(?:ed|ing)\s+(?:to|by)|'
                   r'normaliz(?:ed|ing)\s+(?:to|by)|closes? the system)', re.I)
# "nothing is imposed", "no normalisation is needed": the negation may reach the verb across a noun.
NEG_ADOPT = re.compile(r'(nothing|not|never|no)\b[^.;]{0,40}?\b(?:is|are|was|were|be)?\s*'
                       r'(?:imposed|enforced|required|fixed|added|normalised|normalized|needed)',
                       re.I)
# Clause boundaries: punctuation and the contrastive connectives that introduce an ALTERNATIVE.
# Splitting at "rather than" is the point: the rejected alternative is not the clause that carries
# the constraint, so its rejection cannot launder the adoption clause.
CLAUSE_SPLIT = re.compile(r'(?<=[;:])\s+|\s*(?:---|--)\s*|'
                          r'\s*,?\s*\b(?:rather than|instead of|although|though|whereas|but|'
                          r'while)\b\s*', re.I)


def _flat_sentences(txt):
    flat = re.sub(r'\s+', ' ', re.sub(r'(?<!\\)%.*', '', txt))
    spans, start = [], 0
    for m in re.finditer(r'(?<=[.!?])\s+(?=[A-Z\\$])', flat):
        spans.append((start, m.start())); start = m.end()
    spans.append((start, len(flat)))
    return flat, spans


def _sentence_at(spans, flat, i):
    for a, b in spans:
        if a <= i < b:
            return flat[a:b], a
    return flat[max(0, i-160):i+160], max(0, i-160)


def _clauses(sent):
    """(start, end) spans of the clauses of one sentence."""
    spans, start = [], 0
    for m in CLAUSE_SPLIT.finditer(sent):
        if m.start() > start:
            spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(sent)))
    return spans


def _clause_at(sent, i):
    for a, b in _clauses(sent):
        if a <= i < b:
            return sent[a:b]
    return sent


# The formulation must not impose a normalisation; the historical register (audit_appendix)
# *describes* the removed constraint, so there the whole register row must call it an error.
gauge_seen, gauge_bad = [], []
for f in FILES:
    if f == 'chapters/audit_appendix.tex':
        for line in SRC[f].split('\n'):
            for pat in P_NORM:
                for m in pat.finditer(line):
                    ok = bool(re.search(r'(over-determin|overdetermin|removed|no such freedom|'
                                        r'not imposed|must not)', line, re.I))
                    gauge_seen.append((f + ' (register row)', line[max(0, m.start()-40):m.start()+60], ok))
                    if not ok:
                        gauge_bad.append("%s: %s" % (f + ' (register row)', line[:120]))
        continue
    flat, spans = _flat_sentences(SRC[f])
    for pat in P_NORM:
        for m in pat.finditer(flat):
            sent, s0 = _sentence_at(spans, flat, m.start())
            clause = _clause_at(sent, m.start() - s0)
            adopt = ADOPT.search(NEG_ADOPT.sub(' ', clause))
            ok = bool(REJECT.search(clause)) and not adopt
            gauge_seen.append((f, flat[m.start():m.start()+60], ok))
            if not ok:
                gauge_bad.append("%s: %s" % (f, clause[:120]))
check("a pressure normalisation occurs only as an explicitly rejected counterfactual",
      not gauge_bad, gauge_bad[:2])
check("the rejected pressure normalisation is still identified explicitly", bool(gauge_seen),
      "normalisation occurrences=%d" % len(gauge_seen))
for _f, _s, _ok in gauge_seen:
    print("INFO  pressure normalisation in %s (%s): %s" % (_f, "rejected" if _ok else "ADOPTED", _s))
# Positive control: the legitimate datum is a boundary value on the outflow section, so the test
# above checks the absence of a normalisation, not the absence of any pressure datum.
check("the outflow pressure datum is a boundary value, not an interior point constraint",
      bool(re.search(r'p\\to\s*0', C5)) and ('traction-free' in C5),
      "B2: the level at the outflow is an output, not an imposed datum")
# --- Stage 20 (F-2): the explanation must be in the FORMULATION, not only in the register -------
# Before this check, deleting the whole "no pressure gauge is required ... would over-determine the
# system" argument from ch08 left the suite green, because `gauge_seen` was satisfied by the D-30
# register row in audit_appendix, which *describes* the removed constraint.
_f8_gauge = [s for (f, s, _ok) in gauge_seen if f == 'chapters/ch08.tex']
check("the formulation itself states why no pressure gauge is imposed",
      bool(_f8_gauge), "gauge occurrences in ch08 = %d (register-only would be 0)" % len(_f8_gauge))
check("the formulation states that no pressure gauge is required",
      'No pressure gauge is required' in re.sub(r'\s+', ' ', C8))
check("register pointer corrected to D-30", 'corrected in D-30' in C8)
check("SUPG stabilised weak form written", 'eq:supgwf' in C8)
check("SUPG P2 length scale addressed", ('h_K'+BS+'to h_K/p') in C8)

reversed_phrases = ["into the channel","into the flow","into the passage",
                    "toward the interior","towards the interior","bows toward"]
hits = [p for p in reversed_phrases if p in BODY]
check("no reversed-bow phrasing in body text", not hits, hits)

# --- NEW-05: no residual "a few per cent" stiffening claim (NEW-05 / D-33) ---
def stale_few(txt, name):
    out = []
    for m in re.finditer(r'a few per[\s\n]*cent', txt):
        ctx = txt[max(0, m.start()-200):m.start()+200]
        if ('superseded' not in ctx) and ('earlier' not in ctx):
            out.append(ctx[:70].replace('\n',' '))
    return out
check("ch04 has no stale few-per-cent stiffening claim", not stale_few(C4, 'ch04'), stale_few(C4,'ch04'))
check("ch11 has no stale few-per-cent stiffening claim", not stale_few(C11,'ch11'), stale_few(C11,'ch11'))
def measured_end(txt, name):
    """the end-effect magnitude must be the measured 0.2 %, with the Q8 evidence and the register"""
    return (P("$0.2@%$") in txt) and (P("$1.0000$") in txt) and ("$0.998$" in txt) and ("D-26" in txt)
check("ch04 states the measured 0.2 % with its Q8 evidence", measured_end(C4, 'ch04'))
check("ch11 states the measured 0.2 % with its Q8 evidence", measured_end(C11, 'ch11'))
check("no 'one-time numerical check' left in the pin context",
      'one-time numerical check' not in BODY)

# --- I-11: every Gamma_p presentation is labelled ---
check("A8 labels the mixed ratio", 'emph{mixed}' in APP)
check("A8 gives the like-for-like value", P("1.27@times10^{-7}") in APP and P("1.73@times10^3") in APP)
check("dictionary labels Gamma_p", 'mixed; like-for-like' in APP)
check("ch07 table labels Gamma_p mixed", P("Gamma_p$ & $w_{@max}/w_p$, @eqref{eq:gammap} (mixed)") in C7)
check("ch07 prose gives both ratios", ("mixed ratio" in C7) and (R("@times").join([]) or P("1.73@times10^{3}") in C7))
check("A-5 is defined on the like-for-like ratio", 'like-for-like' in C6 and 'D-29' in C6)

# --- I-15: stated as unverified, not as closed (Stage 18: this check was `... or True`) ---
FIGCLAIM = re.compile(r'(visually verified|visual(?:ly)? (?:check|inspection) (?:passed|confirms|confirmed)'
                      r'|rendered (?:correctly|as intended)|verified by eye|confirmed by eye'
                      r'|figure(?:s)? (?:were|was) inspected)', re.I)
fig_claims = []
for f in FILES:
    for m in FIGCLAIM.finditer(re.sub(r'(?<!\\)%.*', '', SRC[f])):
        fig_claims.append("%s: %s" % (f, SRC[f][max(0, m.start()-90):m.end()+60].replace('\n', ' ')[:110]))
check("no chapter claims a visual verification of a figure (I-15 remains open)",
      not fig_claims, fig_claims[:2])
LEDGER = read('audit_stage15/01_master_issue_ledger.md')
check("the ledger still records I-15 as OPEN",
      bool(re.search(r'\|\s*I-15\s*\|[^|]*\|\s*\*\*OPEN\*\*', LEDGER)), "I-15 row")

# --- Stage 19 corrections: reference-temperature convention and Q8 evidence scope -------------
# These are pins on the corrected statements, not semantic proofs: each asserts that the caveat is
# still present where the claim it qualifies is made.
def _flat(f):
    # '$' and '~' carry no meaning here: '$24$-element' must read as '24-element', so they are
    # removed BEFORE whitespace is collapsed (otherwise they would leave a space behind).
    s = re.sub(r'(?<!\\)%.*', '', SRC[f]).replace('$', '').replace('~', ' ')
    return re.sub(r'\s+', ' ', s)

_D26 = [l for l in SRC['chapters/audit_appendix.tex'].split('\n') if l.startswith('D-26 &')]
_F06, _F04, _F11 = _flat('chapters/ch06.tex'), _flat('chapters/ch04.tex'), _flat('chapters/ch11.tex')
check("ch06 states that T_in is the inflow datum, not a property input",
      ('is \\emph{not} a property input' in _F06) and ('inflow Dirichlet datum' in _F06))
check("ch06 states the T_ref = T_in convention behind the quoted theta-bar",
      (P("T_{@mathrm{ref}}=T_{@mathrm{in}}") in _F06) and ('measured from the inlet bulk' in _F06))
check("ch04 scopes the Q8 values to one finite mesh, not a converged strip solution",
      ('24-element' in _F04) and ('finite-mesh' in _F04) and ('not a converged strip solution' in _F04))
check("ch11 scopes the Q8 comparison to a finite mesh, not a converged strip solution",
      ('24-element' in _F11) and ('finite-mesh' in _F11) and ('not a' in _F11 and 'converged' in _F11))
_D26F = _D26[0].replace('$', '') if _D26 else ''
# --- Stage 20 (F-1): the Q8 ratios are sampled at a FIXED physical height ---------------------
# The Stage 19 statement that "the absolute ratios shift with the through-thickness
# discretisation" was an artefact of reading lat[(NX,1)]/lat[(NX,2)], whose physical heights move
# with NY (d/4 and d/2 at NY=2, d/8 and d/4 at NY=4).  The study `q8_height_study.py` samples at
# fixed heights; the pins below keep the manuscript on that footing.
_I4 = _F04.find('The full-edge pin idealization')
_J4 = _F04.find('no separate end-compliance correction')
_Q8P = _F04[_I4:_J4] if (_I4 >= 0 and _J4 > _I4) else ''
check("ch04 states that the Q8 ratios are sampled at the mid-surface (y = d/2)",
      ('mid-surface' in _Q8P) and ('y=d/2' in _Q8P), _Q8P[:90])
check("the withdrawn claim that the Q8 ratios shift with the through-thickness mesh is absent",
      'shift with the through-thickness' not in _F04)
check("ch11 states that the Q8 ratios are sampled at the mid-surface",
      ('mid-surface' in _F11) or ('mid-surface' in _D26F))
check("the ledger records the Stage 19 repairs", 'Stage 19' in LEDGER)

# ----------------------------------------------------------------------------------
print(); print("=" * 78); print("SECTION 2b Fingerprints of every display equation and register row"); print("=" * 78)
FING = 'audit_stage15/equation_fingerprints.json'

def canon(t):
    t = re.sub(r'(?<!\\)%.*', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def fingerprint():
    fp = {}
    for f in FILES:
        t = re.sub(r'(?<!\\)%.*', '', SRC[f])
        for i, m in enumerate(re.finditer(
                r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}', t, re.S)):
            body = m.group(2)
            lab = re.search(r'\\label\{([^}]+)\}', body)
            key = ('eq:' + lab.group(1)) if lab else ('eq:%s#%d' % (f, i))
            fp[key] = hashlib.sha256(canon(body).encode()).hexdigest()[:16]
    for row in REG_ROWS:
        rid = row.split('&')[0].strip()
        fp['reg:' + rid] = hashlib.sha256(canon(row).encode()).hexdigest()[:16]
    return fp

FP = fingerprint()
REGEN = '--update-fingerprints' in sys.argv
if REGEN:
    json.dump(FP, open(FING, 'w'), indent=1, sort_keys=True)
    print("WROTE  %s (%d entries)" % (FING, len(FP)))
    print("WARNING  fingerprints were REGENERATED in this run.  A fingerprint is change detection,")
    print("WARNING  never a correctness proof: it records that an expression is unchanged, not that")
    print("WARNING  it is right.  Regeneration therefore cannot make a wrong expression right.  Every")
    print("WARNING  substantive check below still runs, and this process still exits non-zero if any")
    print("WARNING  of them fails (Stage 18, finding F1).")
if not os.path.exists(FING):
    print("FAIL  fingerprint file missing -- run with --update-fingerprints once, deliberately")
    FAIL.append("fingerprints")
elif REGEN:
    print("INFO  fingerprint comparison SKIPPED: the file was regenerated in this same run.")
    print("INFO  %d fingerprints recomputed (44 expected equations + 32 register rows)." % len(FP))
else:
    OLD = json.load(open(FING))
    changed = sorted(k for k in FP if k in OLD and FP[k] != OLD[k])
    added = sorted(set(FP) - set(OLD))
    removed = sorted(set(OLD) - set(FP))
    eq_changed = [k for k in changed if not k.startswith('reg:')]
    reg_changed = [k for k in changed if k.startswith('reg:')]
    check("no display equation has changed", not eq_changed, eq_changed[:6])
    check("no register row has changed", not reg_changed, reg_changed[:6])
    check("no equation or register row removed", not removed, removed[:6])
    if added:
        WARN.append("new fingerprint keys (deliberate additions): %s" % added[:6])
    print("INFO  %d fingerprints checked (%d equations, %d register rows)"
          % (len(FP), len([k for k in FP if not k.startswith('reg:')]),
             len([k for k in FP if k.startswith('reg:')])))
    for w in WARN: print("INFO  " + w)

# ----------------------------------------------------------------------------------
print(); print("=" * 78); print("SECTION 3  Inputs parsed from the manuscript"); print("=" * 78)
def si(label):
    """first \\SI{...}{...} on the line that starts with `label`"""
    for line in C2.split('\n'):
        if line.startswith(label):
            m = re.search(r'\\SI\{([0-9.eE+-]+)\}', line)
            if m: return float(m.group(1))
    raise SystemExit("cannot parse SI value for %r" % label)
def table_value(label):
    m = re.search(re.escape(label) + r'[^&]*&[^&]*&\s*([^&]+?)&', C2)
    if not m: raise SystemExit("cannot find table row for %r" % label)
    return num(m.group(1))

def num(s):
    s = s.strip().strip('$').strip()
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*\\times\s*10\^\{?(-?\d+)\}?', s)
    if m: return float(m.group(1)) * 10.0 ** float(m.group(2))
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)', s)
    if m: return float(m.group(1))
    raise ValueError("cannot parse number from %r" % s)

E     = table_value("PEEK Young's modulus")
nu    = table_value("PEEK Poisson ratio")
alpha = table_value("PEEK expansion coefficient")
ks    = table_value("PEEK conductivity")
rho   = table_value("Water density")
muf   = table_value("Water dynamic viscosity")
cp    = table_value("Water specific heat")
kf    = table_value("Water conductivity")
H0    = si("Channel height")
L     = si("Heated, deformable length")
d     = si("Wall thickness")
U     = si("Mean inlet velocity")
q     = si("Imposed heat flux")
L_o   = float(re.search(r'Entrance / exit lengths.*?\\SI\{[0-9.eE+-]+\}\{[^}]*\}; \\SI\{([0-9.eE+-]+)\}', C2).group(1))
Nu_H1 = float(re.search(r'\\mathrm\{Nu\}_\{H1\}=([0-9.]+)', C9).group(1))
print("  geometry: L=%.4g d=%.4g H0=%.4g U=%.4g q=%.4g Lo=%.4g Nu=%.4g" % (L,d,H0,U,q,L_o,Nu_H1))
check("L/d = 10 at the baseline", abs(L/d - 10.0) < 1e-9, L/d)
check("nu in (0,0.5)", 0 < nu < 0.5, nu)
if not (0 < nu < 0.5):
    print("FATAL: nu outside (0,0.5)"); sys.exit(1)
check("all parsed inputs positive and finite",
      all(isfinite(v) and v > 0 for v in (E,nu,alpha,ks,rho,muf,cp,kf,H0,L,U,q,L_o)), "")

# ---- recompute everything from the parsed inputs ----
h     = Nu_H1*kf/(2*H0)
thbar = (q*d/ks)/2 + q/h + (q*L/(rho*U*H0*cp))/2
Ds    = E*d**3/(12*(1-nu**2)); kth = (1+nu)*alpha*q/ks
N0    = E*d*alpha*thbar/(1-nu); mu = sqrt(N0/Ds); uL = mu*L; A = tan(uL/2)
w     = lambda x: (kth/mu**2)*(A*sin(mu*x)+cos(mu*x)-1)
w1    = lambda x: (kth/mu)*(A*cos(mu*x)-sin(mu*x))
w2    = lambda x: -kth*(A*sin(mu*x)+cos(mu*x))
wmax, kgeo = w(L/2), -w2(L/2)
Ncr   = pi**2*Ds/L**2
Mmid  = Ds*(w2(L/2)+kth)
dp    = 12*muf*U*(L+L_o)/H0**2
p0    = dp; pL = dp*L_o/(L+L_o); pbar = (p0+pL)/2
wp    = 5*pbar*L**4/(384*Ds)
wp_bc = (-pbar*L**2/(8*N0) + (pbar*Ds/N0**2)*(1/cos(sqrt(N0/Ds)*L/2)-1))
print("  theta_bar=%.5f K  p0=%.2f pL=%.2f pbar=%.2f Pa  w_max=%.6e m" % (thbar,p0,pL,pbar,wmax))

Nq = 200001; hq = L/(Nq-1); sacc = 0.0
for i in range(Nq):
    c = 1 if i in (0, Nq-1) else (4 if i % 2 else 2)
    sacc += c*w1(i*hq)**2
arc = (sacc*hq/3)/L/2
e0  = (1+nu)*alpha*thbar
max_mech = max(abs(-e0 + (d/2)*(w2(L/2)+kth)), abs(-e0 - (d/2)*(w2(L/2)+kth)))
envelope = e0 + kgeo*d/2
smax_slope = max(abs(w1(i*L/20000)) for i in range(20001))

def fixed_point(th):
    Nn0 = E*d*alpha*th/(1-nu); Nc = Nn0
    for _ in range(60):
        m = sqrt(Nc/Ds); a = tan(m*L/2)
        f1 = lambda x: (kth/m)*(a*cos(m*x)-sin(m*x))
        NS = 40001; hL = L/(NS-1); ss = 0.0
        for i in range(NS):
            c = 1 if i in (0,NS-1) else (4 if i%2 else 2)
            ss += c*f1(i*hL)**2
        Nc = Nn0 - E*d/(2*(1-nu**2))*((ss*hL/3)/L)
    m = sqrt(Nc/Ds); a = tan(m*L/2)
    wsc = (kth/m**2)*(a*sin(m*L/2)+cos(m*L/2)-1)
    Msc = Ds*(-kth*(a*sin(m*L/2)+cos(m*L/2)) + kth)
    return Nc, wsc, Msc
Nc, wsc, Msc = fixed_point(thbar)
sig_fr = (N0/d + 6*abs(Mmid)/d**2)/1e6
sig_sc = (Nc/d + 6*abs(Msc)/d**2)/1e6

# ----------------------------------------------------------------------------------
print(); print("=" * 78); print("SECTION 4  Printed results vs recomputation"); print("=" * 78)
def val(txt, pre, post="", exp=0, span=None, ctx=220, num=r'(-?[0-9.]+)'):
    """locate the literal TeX context (pre + number + post) and return the number, scaled"""
    if span is not None:
        i = txt.find(P(span))
        if i < 0: return None
        txt = txt[i:i+ctx]
    pat = re.escape(P(pre)) + num + re.escape(P(post))
    m = re.search(pat, txt, re.S)
    return float(m.group(1)) * 10.0**exp if m else None
def cmp(name, printed_v, computed, tol):
    if printed_v is None:
        check(name, False, "printed value not found"); return
    rel = abs(computed-printed_v)/max(abs(printed_v),1e-300)
    check(name, rel <= tol, "printed=%.6g computed=%.6g rel=%.2e" % (printed_v, computed, rel))

# --- temperature level and pressure chain ---
thp = val(APP, "@bar@theta=", "$ K")
check("printed theta-bar equals the recomputed value to its 3-s.f. rounding",
      thp is not None and abs(thbar-thp) <= 0.05, "printed=%s computed=%.4f" % (thp, thbar))
cmp("appendix N_theta matches",  val(APP, " K: $", "@times10^4$ N/m", 4, span="N_@theta$ at $"), -N0, 0.01)
cmp("appendix N_cr matches",     val(APP, "9@times10^{-4}=", "@times10^5$ N/m", 5), Ncr, 0.005)
cmp("appendix M_b matches",      val(APP, "M_b=117.5/32.3="), 117.5/thbar, 0.01)
cmp("ch07 M_b matches",          val(C7, "$117.5/32.3=", "$ ("), 117.5/thbar, 0.01)
cmp("appendix mu*L matches",     val(APP, "@mu L=", "$"), uL, 0.01)

# --- deflection and stress ---
cmp("ch04 printed w_max matches recomputation", val(C4, "w_{@max}=", "@times10^{-4}@,", -4), wmax, 0.01)
cmp("ch04 printed w_max/H0 matches", val(C4, "@mathrm{m}=", "@,H_0"), wmax/H0, 0.01)
cmp("ch04 printed linear w/H0 matches", val(C4, "}{H_0}="), kth*L*L/8/H0, 0.01)
cmp("ch04 amplification matches", val(C4, "amplification by the factor $", "$"), wmax/(kth*L*L/8), 0.01)
cmp("ch04 fibre strain matches", val(C4, "d/2=", "@times10^{-4}", -4, span="kappa_{@mathrm{geo}}-"), (kgeo-kth)*d/2, 0.02)
cmp("ch04 arc term matches quadrature", val(C4, "rangle", "@times10^{-4}", -4, span="arc-stretching term", num=r"\s*=\s*(-?[0-9.]+)"), arc, 0.01)
cmp("ch04 relaxation matches arcterm/e0", val(C4, "relaxation of $", "@%$"), 100*arc/e0, 0.02)
_r = (kgeo**2*L*L/24)/arc
check("circular-arc estimate is an upper bound, 10-20% above exact", 1.10 < _r < 1.20, "ratio %.4f" % _r)
cmp("appendix circular-arc estimate matches", val(APP, "circular-arc estimate $", "@times10^{-4}$", -4), kgeo**2*L*L/24, 0.02)
cmp("appendix w'_max matches", val(APP, "w'_{@max}=", "$ rad"), smax_slope, 0.02)
cmp("appendix M_mid matches", val(APP, "M_{@mathrm{mid}}=-", "$ N"), abs(Mmid), 0.02)
cmp("appendix sigma_bend frozen matches", val(APP, "6|M|/d^2=", "$ MPa"), 6*abs(Mmid)/d**2/1e6, 0.02)
cmp("ch07 table sigma_bend matches", val(C7, "=", "@times10^{6}$ Pa", 6, span="sigma_{@mathrm{bend}}"), 6*abs(Mmid)/d**2, 0.02)
cmp("ch07 table w_max matches", val(C7, "& $", "@times10^{-4}$", -4, span="frozen force"), wmax, 0.01)
cmp("ch07 conservative stress 13.9 matches", val(C7, "@approx", "$ MPa"), sig_fr, 0.01)
cmp("ch09 V-C3 amplification matches", val(C9, "amplification", "$ at $@mu L", num=r"\s*\$\s*(-?[0-9.]+)"), wmax/(kth*L*L/8), 0.01)

# --- Gamma_p, both definitions ---
cmp("ch04 Gamma_p = w_max/w_p matches", val(C4, "=", "@times10^{3}@quad@text{at the baseline}", 3), wmax/wp, 0.01)
cmp("ch04 linear-limit closed form matches", val(C4, "5@bar pL^2)=", "@times10^{3}", 3), 48*kth*Ds/(5*pbar*L*L), 0.01)
cmp("ch04 like-for-like w_p matches beam-column pressure solution", val(C4, "w_p(N_@theta^c)=", "@times10^{-7}$", -7), wp_bc, 0.01)
cmp("ch04 like-for-like Gamma_p matches", val(C4, "w_{@max}/w_p(N_@theta^c)=", "@times10^{3}$", 3), wmax/wp_bc, 0.01)
cmp("appendix A8 w_p matches", val(APP, "384(9.6)]=", "@times10^{-8}$", -8), wp, 0.02)
cmp("appendix A8 Gamma_p matches", val(APP, "9.2@times10^{-8}=", "@times10^3$;", 3), wmax/wp, 0.02)
cmp("appendix A8 like-for-like Gamma_p matches", val(APP, "and $@Gamma_p=", "@times10^3$ (register D-29)", 3), wmax/wp_bc, 0.02)
cmp("ch07 table w_p matches", val(C7, "384@cdot9.6)=", "@times10^{-8}$", -8), wp, 0.02)
cmp("ch07 table Gamma_p matches", val(C7, "9.2@times10^{-8}=", "@times10^{3}$ ($@ge5$, A-5 met)", 3), wmax/wp, 0.02)

# --- strains and self-consistent state ---
cmp("appendix self-consistent w_max matches", val(APP, "w_{@max}=", "@times10^{-4}$ m", -4, span="Self-consistent comparison"), wsc, 0.01)
cmp("appendix self-consistent sigma_bend matches", val(APP, "sigma_{@mathrm{bend}}=", "$ MPa", span="Self-consistent comparison"), 6*abs(Msc)/d**2/1e6, 0.02)
check("frozen stress exceeds self-consistent (conservative)", sig_fr > sig_sc, "%.4f > %.4f" % (sig_fr, sig_sc))
check("frozen stress below 0.2 sigma_y cap", sig_fr < 0.2*90, sig_fr)
check("E/(1-nu^2)*max|eps_mech| reproduces frozen sigma_max",
      abs(E/(1-nu**2)*max_mech/1e6 - sig_fr) < 1e-3, "%.6f vs %.6f" % (E/(1-nu**2)*max_mech/1e6, sig_fr))
cmp("ch04 printed mechanical surface strain matches", val(C4, "@varepsilon_{@mathrm{mech}}|", "@times10^{-3}", -3, num=r"\s*=\s*(-?[0-9.]+)"), max_mech, 0.02)
cmp("appendix envelope matches", val(APP, "d/2=", "@times10^{-3}", -3, span="@kappa_{@mathrm{geo}}d/2"), envelope, 0.01)
cmp("appendix e0 matches", val(APP, "@bar@theta=", "@times10^{-3}", -3, span="e_0=(1+"), e0, 0.01)

# --- prose that quotes a derived quantity must quote the derived quantity ---
check("ch08 writes the geometric stress with 1/d (not 1/(2d))",
      P("@frac{N_@theta^c}{d}") in C8 and P("N_@theta^c/(2d)") not in C8,
      "prose factor must match eq:weaks")
check("ch04 critical load is the pinned eigenvalue pi^2 D_s/L^2",
      P("N_{@mathrm{cr}}=@pi^2D_s/L^2") in C4 and P("N_{@mathrm{cr}}=4@pi^2D_s/L^2") not in C4,
      "the assignment must stay pinned; 4pi^2 is only the rejected clamped alternative")
check("ch07 table quotes the pinned critical load",
      P("N_{@mathrm{cr}}$ & $@pi^2D_s/L^2$") in C7, "table row")
_allowed_stress = {round(sig_fr, 1), round(sig_sc, 1), 90.0, round(0.2*90, 1)}
_seen = sorted({float(m.group(1)) for m in re.finditer(r'\$([0-9]+\.[0-9]+)\$~MPa', C7)})
check("every stress quoted in ch07 prose is one of the recomputed values",
      bool(_seen) and set(_seen) <= _allowed_stress,
      "seen=%s allowed=%s" % (_seen, sorted(_allowed_stress)))

# --- T1: the theta-bar table cell, recomputed from its own formula and from the inputs ---
# The cell quotes three components and a total.  Each component is recomputed from the parsed
# inputs (q, d, k_s, Nu_H1, k_f, H0, rho, U, c_p, L) at the precision at which it is printed,
# and the total is compared with both the quoted value and the recomputed theta-bar.
_cell = re.search(r'\$\\bar\\theta\$ \(mean wall rise\) & \$\\Delta T_t/2\+q\^\{\'\'\}/h\+\\Delta T_b/2\$ & '
                  r'\$([0-9.]+)\+([0-9.]+)\+([0-9.]+)\\approx([0-9.]+)\$ K', C7)
check("the theta-bar cell quotes its three components and the total", bool(_cell))
if _cell:
    c1, c2, c3, ctot = (float(g) for g in _cell.groups())
    comps = (q*d/ks/2, q/h, q*L/(rho*U*H0*cp)/2)
    errs = [abs(a - b) for a, b in zip((c1, c2, c3), comps)]
    check("each component printed in the theta-bar cell is its recomputed value at 2 dp",
          max(errs) <= 0.0050001,
          "printed=(%.2f, %.2f, %.2f) recomputed=(%.4f, %.4f, %.4f) maxerr=%.4f"
          % (c1, c2, c3, comps[0], comps[1], comps[2], max(errs)))
    check("the theta-bar cell total is the recomputed theta-bar",
          abs(ctot - thbar) <= 0.05 and abs((c1 + c2 + c3) - thbar) <= 0.05,
          "quoted=%.2f sum=%.2f recomputed=%.4f" % (ctot, c1 + c2 + c3, thbar))

# --- T2: T_cr and the M_b margin, recomputed from eq:tcr and from theta-bar ---
_tcr = re.search(r'\\frac\{\\pi\^2d\^2\}\{([0-9]+)[^}]*\\alpha\(1\+\\nu\)L\^2\}', re.sub(r'\s+', ' ', C4))
check("eq:tcr carries an explicit analytic denominator coefficient", bool(_tcr))
check("the eq:tcr denominator coefficient is parseable (so T_cr can be checked at all)",
      bool(_tcr), "a form the parser cannot read must fail, not skip the T_cr checks")
if _tcr:
    Tcr = pi**2*d*d/(float(_tcr.group(1))*alpha*(1+nu)*L*L)
    print("INFO  eq:tcr coefficient %s -> T_cr=%.4f K" % (_tcr.group(1), Tcr))
    cmp("the denominator printed in A4 matches 12 alpha (1+nu) L^2",
        val(APP, "With denominator $12@alpha(1+@nu)L^2=", "@times10^{-7}$", -7), 12*alpha*(1+nu)*L*L, 0.01)
    cmp("ch07 table T_cr is the recomputed threshold", val(C7, "9@times10^{-4})]=", "$ K"), Tcr, 0.005)
    _sw = re.search(r'\$\\bar T_\{\\mathrm\{cr\}\}=\\\{([0-9.,]+)\\\}\$ K', APP)
    check("the T_cr versus thickness catalogue is present", bool(_sw))
    if _sw:
        pred = [Tcr*(mm/3.0)**2 for mm in (1.0, 1.5, 2.0, 2.5, 3.0)]
        got = [float(x) for x in _sw.group(1).split(',')]
        check("the T_cr versus thickness catalogue matches eq:tcr",
              len(got) == 5 and max(abs(a - b) for a, b in zip(pred, got)) <= 0.5,
              "printed=%s recomputed=%s" % (got, ["%.2f" % v for v in pred]))
    _mb = re.search(r'M_b=([0-9.]+)/([0-9.]+)=([0-9.]+)', APP)
    check("the M_b row carries numerator, denominator and quotient", bool(_mb))
    if _mb:
        n_, dn_, qq_ = (float(g) for g in _mb.groups())
        check("the M_b numerator is the recomputed T_cr", abs(n_ - Tcr) <= 0.05,
              "printed %.2f recomputed %.4f" % (n_, Tcr))
        check("the M_b denominator is the recomputed theta-bar", abs(dn_ - thbar) <= 0.05,
              "printed %.2f recomputed %.4f" % (dn_, thbar))
        check("the M_b quotient is T_cr/theta-bar", abs(qq_ - Tcr/thbar) <= 0.005,
              "printed %.2f recomputed %.4f" % (qq_, Tcr/thbar))
        check("bound A-2 (M_b >= 2) is met by the recomputed margin",
              Tcr/thbar >= 2.0 and qq_ >= 2.0,
              "computed M_b=%.4f, printed %.2f" % (Tcr/thbar, qq_))
        _ceil = val(C7, "restricting $@bar@theta@le", "$ K")
        # The displayed value must be the one-decimal rounding OF THE EXACT VALUE, not the rounding
        # of an already-rounded 117.5 (Stage 19 correction: 58.75 -> 58.8 was a double rounding).
        check("the M_b = 2 ceiling is the correctly rounded T_cr/2 (58.7 K)",
              _ceil is not None and abs(_ceil - round(Tcr/2.0, 1)) < 1e-12,
              "printed=%s exact=%.6f one-dp=%.1f" % (_ceil, Tcr/2.0, round(Tcr/2.0, 1)))
        cmp("the M_b = 2 ceiling reproduces the quoted 9.1e3 W/m2",
            val(C7, "$q^{''}@approx", "@times10^{3}$", 3, span="restricting $@bar@theta@le"),
            q*(Tcr/2.0)/thbar, 0.01)

# --- eq:wmax: validated against its governing relation, its own printed value and the
#     small-force limit of eq:beamcolsol -- not by searching for the number 8 ---
_w1 = re.search(r'w_\{\\max\}=\\frac\{\\kappa_\{\\mathrm\{th\}\}L\^2\}\{([0-9]+)\}', C4)
_wq = re.search(r'w\(x\)=\\frac\{\\kappa_\{\\mathrm\{th\}\}\}\{([0-9]+)\}\\,?x\(L-x\)', C4)
check("eq:wmax states a parabola and a w_max with explicit constants", bool(_w1 and _wq))
check("the eq:wmax constants are parseable (so the value can be checked at all)",
      bool(_w1 and _wq),
      "a form the parser cannot read must fail, not skip the numerator/denominator checks")
if _w1 and _wq:
    nden, nquad = float(_w1.group(1)), float(_wq.group(1))
    implied = kth*L*L/nden
    check("the parabola's mid-span value equals the w_max of the same equation",
          abs(kth*L*L/(4*nquad) - implied) <= 1e-30 + 1e-12*abs(implied),
          "1/(4*%g) vs 1/%g" % (nquad, nden))
    cmp("the eq:wmax denominator reproduces the printed linear w_max (appendix A3)",
        val(APP, ")/8=", "@times10^{-4}$ m", -4), implied, 0.005)
    cmp("the eq:wmax denominator reproduces the printed linear w_max (ch07 table)",
        val(C7, ")/8=", "@times10^{-4}$ m", -4), implied, 0.005)
    mu_s = 1e-4*pi/L
    a_s = tan(mu_s*L/2)
    w_eps = (kth/mu_s**2)*(a_s*sin(mu_s*L/2) + cos(mu_s*L/2) - 1)
    check("eq:wmax is the mu -> 0 limit of eq:beamcolsol",
          abs(w_eps/implied - 1) < 1e-6, "ratio-1=%.2e" % (w_eps/implied - 1.0))
    _wf = lambda x: kth/nquad*x*(L - x)
    _hh = 1e-5*L
    _res = max(abs((_wf(x + _hh) - 2*_wf(x) + _wf(x - _hh))/_hh**2 + kth)
               for x in (0.31*L, 0.5*L, 0.73*L))
    check("the eq:wmax parabola satisfies w'' = -kappa_th with w(0) = w(L) = 0",
          _res < 1e-6*kth and abs(_wf(0)) < 1e-30 and abs(_wf(L)) < 1e-30,
          "residual=%.2e" % _res)

if '--chain' in sys.argv:
    print(); print("=" * 78)
    print("DEPENDENCY CHAIN  inputs -> theta-bar -> N_theta -> geometry -> stress -> ratios")
    print("=" * 78)
    rows = [
        ("theta-bar", thbar, "K", "recomputed from E, nu, alpha, d, q'', k_s (ch02/ch09 inputs)"),
        ("N_theta", -N0, "N/m", "-E alpha theta-bar d/(1-nu)"),
        ("N_cr", Ncr, "N/m", "pi^2 D_s/L^2"),
        ("mu L", uL, "-", "L sqrt(-N_theta/D_s)"),
        ("kappa_geo", kgeo, "1/m", "2 w_max/L^2 (parabolic fit of the beam-column solution)"),
        ("w_max", wmax, "m", "frozen-force beam-column solution"),
        ("M_mid", Mmid, "N m/m", "D_s (kappa_geo - kappa_th)"),
        ("sigma_bend", 6*abs(Mmid)/d**2/1e6, "MPa", "6|M|/d^2"),
        ("Gamma_p mixed", wmax/wp, "-", "w_max / w_p"),
        ("Gamma_p like-for-like", wmax/wp_bc, "-", "w_max / w_p(N_theta^c)"),
        ("w_max self-consistent", wsc, "m", "fixed point of eq:nupdate"),
        ("end-effect penalty", 100*(1-0.998), "%", "measured Q8 value, register D-26"),
        ("D-32 consequence", thbar, "K", "level inherited from T_in through eq:iftemp; not free"),
    ]
    for name, v, unit, how in rows:
        print("  %-22s %14.6g %-6s %s" % (name, v, unit, how))
    print()

print(); print("=" * 78); print("SECTION 5  Exact identities"); print("=" * 78)
check("kappa_geo = kappa_th*sec(muL/2)", abs(kgeo/kth - 1/cos(uL/2)) < 1e-12)
ratio = (kgeo+kth)/(kgeo-kth)
check("(kgeo+kth)/(kgeo-kth) = cot^2(muL/4)", abs(ratio - 1/tan(uL/4)**2) < 1e-10, "%.9f" % ratio)
# --- eq:beamcol (Stage 20, F-4): the printed equation is PARSED and the closed-form solution is
#     tested against the printed coefficients.  Stage 19 tested the solution against literals in
#     this file, so replacing w''=-kappa_th by -kappa_th/2 in the text survived both the suite and
#     fingerprint regeneration.  The parsed quantities are the ones the derivation requires:
#     the reduced beam-column equation with equal D_s and N_theta^c weights, and a zero total end
#     moment w'' = -kappa_th, which is M = D_s(w''+kappa_th) = 0 at the pins.
_C4F = re.sub(r'\s+', ' ', C4)
_ode = re.search(r'([0-9]*\.?[0-9]*)\\?,?D_s\\,w\^\{\'\'\'\'\}\(x\)\s*([+-])\s*'
                 r'([0-9]*\.?[0-9]*)\\?,?N_\\theta\^c\\,w\^\{\'\'\}\(x\)\s*=\s*0', _C4F)
_cD = (float(_ode.group(1)) if _ode.group(1) else 1.0) if _ode else None
_cN = (float(_ode.group(3)) if _ode.group(3) else 1.0) if _ode else None
_sg = _ode.group(2) if _ode else None
check("eq:beamcol is the reduced beam-column equation D_s w'''' + N_theta^c w'' = 0",
      bool(_ode) and _cD == 1.0 and _cN == 1.0 and _sg == '+',
      "parsed %s D_s %s %s N_theta^c" % (_cD, _sg, _cN))
_bc_w = re.search(r'w\(0\)=w\(L\)=0', _C4F)
_bc_m = re.search(r"w\^\{\'\'\}\(0\)=w\^\{\'\'\}\(L\)=-\s*([0-9]*\.?[0-9]*)"
                  r"\\?,?\\?kappa_\{\\mathrm\{th\}\}", _C4F)
_cB = (float(_bc_m.group(1)) if _bc_m.group(1) else 1.0) if _bc_m else None
check("eq:beamcol states the zero total end moment, w'' = -kappa_th at both pins",
      bool(_bc_w) and _cB == 1.0, "printed end-curvature coefficient %s" % _cB)
res = max(abs((_cD or 1)*Ds*(kth*mu**2*(A*sin(mu*x)+cos(mu*x))) + (_cN or 1)*N0*w2(x))
          for x in (0.3*L,0.5*L,0.77*L))
check("eq:beamcolsol satisfies the printed ODE", res < 1e-8, "%.2e" % res)
check("eq:beamcolsol satisfies the printed BCs",
      max(abs(w(0)), abs(w(L)), abs(w2(0)+(_cB or 1)*kth), abs(w2(L)+(_cB or 1)*kth)) < 1e-12)

# ----------------------------------------------------------------------------------
print(); print("=" * 78)
print("SECTION 5b  Interface data set, Gamma_p nomenclature, stale-claim scan")
print("=" * 78)

# --- G3: the boundary-condition set must give each side exactly ONE thermal datum on Gamma_if.
# The table is parsed, not searched: a row whose boundary is Gamma_if may not carry a solid flux
# datum, and may not carry a solid Dirichlet and a solid Neumann datum at the same time.
def bc_rows(txt):
    rows = {}
    for line in txt.split('\n'):
        m = re.match(r'^\s*(B\d+)\s*&\s*(.*?)\s*\\\\\s*$', line)
        if m:
            rows[m.group(1)] = [x.strip() for x in m.group(2).split(' & ')]
    return rows

BC = bc_rows(C5)
check("tab:bcs is parsed row by row", len(BC) >= 9, sorted(BC))
IFACE = {k: v for k, v in BC.items() if v and 'Ga_{\mathrm{if}}' in v[0]}
check("tab:bcs has a boundary row for Gamma_if", bool(IFACE), sorted(IFACE))
DIR_S = re.compile(r'(?<![A-Za-z])T_s\s*=')
NEU_S = re.compile(r'(\\nabla\s*T_s\s*\\cdot|\\partial_n\s*T_s|\\partial_nT_s)')
# A NON-ZERO flux datum: an adiabatic condition ($\partial_nT_s=0$) is not a thermal load and is
# therefore not a second datum (rows B7 and B8 legitimately carry it).
FLUX_NZ = re.compile(r'(\\nabla\s*T_s\s*\\cdot\s*\\bn(?:_\{\\mathrm\{out\}\})?|\\partial_n\s*T_s)'
                     r'\s*=\s*(?!0(?![0-9.]))')
HEATED = re.compile(r'(\\Ga_h\^0|\\Gamma_h\^0|Ga_\{\\mathrm\{h\}\}|Ga_\{h\})')
# Row-level test, independent of the Boundary cell (suite v4 blind spot M7): any row whose Condition
# carries a solid Dirichlet datum AND a solid Neumann datum is a double datum, and a non-zero solid
# flux datum is admissible only on the heated outer face (B6, regime N).
double_rows, flux_rows = [], []
for k, v in sorted(BC.items()):
    cond = ' , '.join(v[1:])
    boundary = v[0] if v else ''
    if DIR_S.search(cond) and NEU_S.search(cond):
        double_rows.append("%s [boundary %s]: %s" % (k, boundary[:40], cond[:90]))
    if FLUX_NZ.search(cond) and not HEATED.search(boundary):
        flux_rows.append("%s [boundary %s]: %s" % (k, boundary[:40], cond[:90]))
check("no Gamma_if row gives the solid a Dirichlet AND a Neumann temperature datum",
      not [d for d in double_rows if d.split()[0] in IFACE], double_rows[:2])
check("no tab:bcs row gives any surface a solid Dirichlet AND a solid Neumann thermal datum",
      not double_rows, double_rows[:2])
check("no tab:bcs row puts a non-zero solid flux datum on a surface other than the heated face",
      not flux_rows, flux_rows[:2])
# The same condition in prose, judged sentence by sentence and by the SHAPE of the data rather than
# by one phrasing (suite v4 blind spot M8).  Tables are removed first: tab:bcs is tested row by row
# above, and a flattened table would put several surfaces into one "sentence".
#   * a solid Dirichlet datum is "T_s = ...";
#   * a solid flux datum is "grad T_s . n = ..." or "partial_n T_s = ...", and only a NON-ZERO
#     right-hand side is a datum (zero flux is an adiabatic condition);
#   * such a flux is admissible only where the sentence places it on the heated outer face.
# The test is shape-based, so "together with its interface temperature" is caught even though it
# never says "on Gamma_if".
IF_NAME = re.compile(r'Ga_\{\\mathrm\{if\}\}|Ga_\{if\}')
FLUX_D = re.compile(r'(\\nabla\s*T_s\s*\\cdot\s*\\bn(?:_\{\\mathrm\{out\}\})?|\\partial_n\s*T_s)'
                    r'\s*=\s*([^,;\s$]{0,24})')
# Where a flux datum is placed is decided by the CLAUSE that carries it, in either order, and
# either by naming the face or by naming it in words (Stage 20, finding F-3).  The Stage 19 form
# required the literal sequence "on $\Gamma_h^0$" immediately AFTER the flux, and so rejected three
# correct statements: "... on the outer face $\Gamma_h^0$", a fronted "On $\Gamma_h^0$ the solid
# carries ...", and "... is applied on the heated face".  A flux whose clause names no heated
# surface is still a datum in the wrong place, and a flux whose tail names $\Gamma_{if}$ is still a
# flux datum on the interface.
ON_HEATED = re.compile(r'(?:outer|heated)\s+(?:outer\s+|heated\s+)?(?:face|surface|wall|side)'
                       r'|(?:Ga|Gamma)_h\b|Ga_\{\\mathrm{h}\}')
DIR_IF = re.compile(r'T_s\s*=\s*T_\\?(?:\\Ga|\\Gamma)')

def _clause_of(sent, a, b):
    """the ;/: delimited clause of `sent` that contains the span [a, b)"""
    left = max(sent.rfind(';', 0, a), sent.rfind(':', 0, a)) + 1
    cuts = [p for p in (sent.find(';', b), sent.find(':', b)) if p != -1]
    return sent[left:(min(cuts) if cuts else len(sent))]
dir_if, flux_if, dbl_prose, flux_elsewhere = [], [], [], []
for f in FILES:
    if f == 'chapters/audit_appendix.tex':
        continue
    raw = re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}', ' ', SRC[f], flags=re.S)
    flatf = re.sub(r'\s+', ' ', re.sub(r'(?<!\\)%.*', '', raw))
    for sent in re.split(r'(?<=[.;])\s+', flatf):
        has_if = bool(IF_NAME.search(sent))
        dir_here = DIR_S.search(sent)
        if has_if and dir_here:
            dir_if.append("%s: %s" % (f, sent[:90]))
        here_if, here_other = [], []
        for m in FLUX_D.finditer(sent):
            rhs = m.group(2).strip()
            if rhs in ('0', '0.', ''):
                continue                       # adiabatic datum, not a thermal load
            tail = sent[m.end():m.end() + 90]
            seg = _clause_of(sent, m.start(), m.end())
            on_if = bool(IF_NAME.search(tail)) or bool(IF_NAME.search(rhs))
            on_heated = bool(ON_HEATED.search(seg)) or bool(ON_HEATED.search(rhs))
            if on_if:
                here_if.append(m.group(0)[:70])
            elif not on_heated:
                here_other.append(m.group(0)[:70])
        if here_if:
            flux_if.append("%s: %s" % (f, here_if[0]))
        if here_other:
            flux_elsewhere.append("%s: %s" % (f, here_other[0]))
        if dir_here and (here_if or here_other):
            dbl_prose.append("%s: %s" % (f, sent[:90]))
check("the solid interface temperature is imposed as a Dirichlet datum", bool(dir_if), dir_if[:2])
check("no solid flux datum is imposed on Gamma_if anywhere in the formulation",
      not flux_if, flux_if[:2])
check("no prose datum gives the solid a temperature AND a non-heated-face heat flux in one sentence",
      not dbl_prose, dbl_prose[:2])
check("no prose sentence puts a non-zero solid flux datum on a surface other than the heated face",
      not flux_elsewhere, flux_elsewhere[:2])
check("the solid problem keeps its flux datum on the outer face, not the interface",
      (r'\Ga_h^0' in C8) and (r'\Ga_h^0' in C5), "B6/step 1")
# --- N1: the Gamma_p nomenclature entry itself (not the dictionary, not a neighbouring row) ---
_nom = re.search(r'^\$\\Gamma_p\$ & (.*?) & (.*?) \\\\ *$', APP, re.M)
check("the Gamma_p nomenclature entry exists", bool(_nom))
if _nom:
    entry = _nom.group(1)
    check("the Gamma_p nomenclature entry defines the labelled ratio",
          r'w_{\max}/w_p' in entry and r'\eqref{eq:gammap}' in entry, entry[:100])
    check("the Gamma_p nomenclature entry distinguishes the mixed and like-for-like presentations",
          ('mixed' in entry) and ('like-for-like' in entry), entry[:100])
    check("the Gamma_p nomenclature entry is not a bare thermal-to-pressure description",
          'thermal-to-pressure' not in entry, entry[:100])

# --- S1: stale end-condition percentages, reworded or not, across every file that states them ---
SCAN = list(FILES) + [f for f in ('README.md', 'HFF_revision_summary.md',
                                  'HFF_source_pdf_consistency_report.md',
                                  'HFF_final_packaging_report.md',
                                  'HFF_final_pre_coding_checklist.md',
                                  'HFF_final_reference_status_notes.txt') if os.path.exists(f)]
END_CTX = re.compile(r'(end[- ]effect|end condition|end-compliance|pinned end|pin\b|pins\b|clamp|'
                     r'stiffen|aspect ratio|B7|A9|D-26|kappa_\{\\mathrm\{th\}\}L\^2/8)', re.I)
STALE = re.compile(r'(?:(?:about|approximately|roughly|some|around|nearly|close to|~|approx)\s*)?'
                   r'(?<![\d.])(?:one|two|three|few|couple|[123])(?:\.\d+)?\s*'
                   r'(?:of\s+)?(?:per[\s~-]*cent|pct\b|percentage\s*points?|\\?%)',
                   re.I)
SUPERSEDED = re.compile(r'(supersed|withdrawn|earlier|previously|no longer|replaced|obsolete)', re.I)
stale_hits, scanned = [], []
for f in SCAN:
    flatf = re.sub(r'\s+', ' ', re.sub(r'(?<!\\)%.*', '', read(f)))
    n_end = 0
    for sent in re.split(r'(?<=[.;:])\s+', flatf):
        if not END_CTX.search(sent):
            continue
        n_end += 1
        if STALE.search(sent) and not SUPERSEDED.search(sent):
            stale_hits.append("%s: %s" % (f, sent[:100]))
    scanned.append("%s(%d)" % (f, n_end))
check("no stale end-effect percentage survives in the %d scanned files" % len(SCAN),
      not stale_hits, stale_hits[:2])
print("INFO  files scanned for stale end-effect claims, with end-effect sentences counted:")
for _s in scanned:
    print("INFO    " + _s)
print("INFO  correct end-effect magnitude present in ch04 and ch11: %s"
      % (("$0.2\\%$" in C4) and ("$0.2\\%$" in C11)))

# ----------------------------------------------------------------------------------
print(); print("=" * 78); print("SECTION 6  Package provenance"); print("=" * 78)
# --- table shape (Stage 20, S20-E): a row with more `&` than the column specification is a hard
#     LaTeX error ("Extra alignment tab has been changed to \\cr"), and no TeX engine is available
#     here, so nothing else in the suite or in any campaign could catch it.  Three register rows
#     (D-33, D-34, D-35) and one short row (D-32) were in that state and are repaired.  This check
#     counts cells statically against the declared column specification of every tabular/longtable.
sys.dont_write_bytecode = True          # the scan must not leave a __pycache__ in the tree
_tsc_spec = importlib.util.spec_from_file_location('table_shape_check',
                                                   'audit_stage15/table_shape_check.py')
_tsc = importlib.util.module_from_spec(_tsc_spec)
_tsc_spec.loader.exec_module(_tsc)
_nf, _nr, _over, _short = _tsc.scan('.')
check("every table row has exactly its declared number of cells", not _over and not _short,
      "%d files, %d rows, %d over-full, %d short" % (_nf, _nr, len(_over), len(_short)))
check("tracked main.pdf exists", os.path.exists('main.pdf'),
      ("%d bytes" % os.path.getsize('main.pdf')) if os.path.exists('main.pdf') else "")
readme = read('README.md') if os.path.exists('README.md') else ''
named = re.findall(r'`([A-Za-z0-9_\-/.]+\.zip)`', readme)
missing = [z for z in named if not os.path.exists(z)]
check("every package filename in README.md exists", not missing, missing)

# ----------------------------------------------------------------------------------
print(); print("=" * 78); print("SECTION 7  Build freshness (REPORTED, NOT ASSERTED)"); print("=" * 78)
_src = list(FILES) + ['references.bib']
_pdf = os.path.getmtime('main.pdf')
_stale = sorted(f for f in _src if os.path.getmtime(f) > _pdf)
if _stale:
    print("WARNING  main.pdf predates %d source file(s); a LaTeX rebuild is REQUIRED." % len(_stale))
    print("WARNING  No TeX engine is available in this environment, so no rebuild is executed or")
    print("WARNING  claimed. The tracked main.pdf does NOT contain the Stage 18 corrections.")
else:
    print("INFO     main.pdf is newer than every source file")

print(); print("=" * 78)
if FAIL:
    print("%d of %d CHECKS FAILED:" % (len(FAIL), len(FAIL)+N_PASS))
    for f in FAIL: print("  - " + f)
    sys.exit(1)
print("ALL %d CHECKS PASSED" % N_PASS)
