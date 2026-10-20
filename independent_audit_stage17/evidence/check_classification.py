#!/usr/bin/env python3
"""Auditor: classify every assertion emitted by audit_stage15/regression.py by what it
actually asserts (AST, not regex), then join with the mutation campaign's biting check."""
import ast, re
from collections import Counter

src = open('audit_stage15/regression.py', encoding='utf-8').read()
tree = ast.parse(src)

# section boundaries: the print(...) calls that announce a section
secs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'print' and node.args:
        a = node.args[0]
        if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.startswith('SECTION'):
            secs.append((node.lineno, a.value))
secs.sort()

def section(lineno):
    lab = ('pre', '')
    for ln, t in secs:
        if ln <= lineno:
            m = re.match(r'SECTION ([0-9b]+)\s+(.*)', t)
            lab = (m.group(1), m.group(2).strip()) if m else lab
        else:
            break
    return lab

rows = []
for node in ast.walk(tree):
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ('check', 'cmp') and node.args):
        continue
    a0 = node.args[0]
    name = a0.value if isinstance(a0, ast.Constant) and isinstance(a0.value, str) else '?'
    seg = ast.get_source_segment(src, node) or ''
    rows.append((node.lineno, node.func.id, name, seg, section(node.lineno)))

def classify(kind, name, seg, where):
    if where[0] == '2b': return 'fingerprint'
    if where[0] == '6': return 'provenance/package'
    if where[0] == '7': return 'build freshness (reported)'
    if where[0] == '1': return 'structural'
    if kind == 'cmp': return 'numeric recompute'
    numeric = ('abs(' in seg) or ('isfinite(' in seg) or ('thp' in seg and 'thbar' in seg)
    call_read = ('val(' in seg) or ('/thbar' in seg) or ('wmax' in seg and 'abs' in seg)
    stringish = bool(re.search(r'\bnot in\b|\bin (C\d|ALL|BODY|APP|SRC|[a-z]\d)\b', seg)) \
                or 'P("' in seg or "P('" in seg
    if (numeric or call_read) and not stringish: return 'numeric recompute'
    if (numeric or call_read) and stringish: return 'numeric + string'
    if stringish: return 'claim string / presence'
    if 'os.path.exists' in seg or 'missing' in seg: return 'provenance/package'
    return 'other'

rows.sort()
c = Counter(r[4] for r in rows) if False else Counter(classify(r[1], r[2], r[3], r[4]) for r in rows)
print("assertions: check()=%d cmp()=%d total=%d" % (sum(r[1]=='check' for r in rows),
      sum(r[1]=='cmp' for r in rows), len(rows)))
for k, v in sorted(c.items(), key=lambda kv: -kv[1]): print("  %-30s %2d" % (k, v))
print("\n%-5s %-26s %-6s %s" % ("line", "class", "call", "name"))
for ln, kind, name, seg, where in rows:
    print("%-5d %-26s %-6s %s" % (ln, classify(kind, name, seg, where), kind, name))

print("\nCAMPAIGN biting check -> class")
try:
    for line in open('independent_audit_stage17/evidence/mutation_campaign_rerun.txt'):
        m = re.match(r'(\w+)\s+(detected|SURVIVED|SKIP)\s+(\S+)\s+(.*?)\s*\|', line)
        if not m: continue
        mid, res, kind, cname = m.groups()
        cand = [r for r in rows if r[2][:26] == cname.strip()[:26]]
        print("  %-3s %-9s %-12s %-44s -> %s" % (mid, res, kind, cname.strip()[:44],
              classify(cand[0][1], cand[0][2], cand[0][3], cand[0][4]) if cand else '?'))
except FileNotFoundError:
    pass
