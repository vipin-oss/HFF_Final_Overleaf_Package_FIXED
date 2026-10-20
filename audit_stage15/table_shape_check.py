#!/usr/bin/env python3
"""Static table-shape check: every row of every tabular/longtable must have the number of cells
its column specification declares.

This is a build-integrity check that a LaTeX engine is not needed to perform.  It exists because a
row with MORE `&` than the declared columns is a hard LaTeX error ("Extra alignment tab has been
changed to \\cr"), and the shipped package contained three such rows (register D-33, D-34, D-35)
that no previous stage could detect: there is no TeX engine in this environment, and nothing
counted cells.  A row with FEWER cells is legal but leaves trailing cells empty, which is reported
as a warning (register D-32 was in that state).

Usage:  python3 audit_stage15/table_shape_check.py [--strict]
Exit 0 if no row overflows its column specification and (with --strict) no row is short.
"""
import glob
import os
import re
import sys


def spec_columns(spec):
    """number of columns declared by a tabular/longtable column specification"""
    s = spec.strip()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]                               # the outer braces of the argument
    s = re.sub(r'@\{[^{}]*\}', '', s)            # inter-column material: no column
    s = re.sub(r'!\{[^{}]*\}', '', s)
    s = re.sub(r'>\{[^{}]*\}', '', s)             # column modifiers
    s = re.sub(r'<\{[^{}]*\}', '', s)
    s = re.sub(r'\{[^{}]*\}', '', s)              # p{3cm}, S[..] arg groups
    s = re.sub(r'\[[^\[\]]*\]', '', s)            # S[table-format=..]
    s = re.sub(r'[|*]', '', s)
    return len(re.findall(r'[lcrXSpmb]', s))


def rows_of(body):
    """logical rows: split on the \\\\ terminator, brace-aware"""
    out, depth, cur = [], 0, []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth == 0 and body.startswith('\\\\', i):
            out.append(''.join(cur))
            cur = []
            i += 2
            continue
        cur.append(ch)
        i += 1
    if ''.join(cur).strip():
        out.append(''.join(cur))
    return out


def cells(row):
    """number of cells contributed by a row, honouring \\multicolumn"""
    depth, n, i = 0, 1, 0
    while i < len(row):
        ch = row[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '&' and depth == 0:
            n += 1
        elif depth == 0 and row.startswith('\\multicolumn', i):
            m = re.match(r'\\multicolumn\{(\d+)\}', row[i:])
            if m:
                n += int(m.group(1)) - 1
                i += m.end()
                continue
        i += 1
    return n


SKIP_ROW = re.compile(r'^\s*(?:\\toprule|\\midrule|\\bottomrule|\\endhead|\\endfirsthead|'
                      r'\\endfoot|\\endlastfoot|\\caption|\\label|$)')


def scan(root='.'):
    """returns (n_files, n_rows_checked, over_full_rows, short_rows) for the manuscript"""
    files = [os.path.join(root, f) for f in ['main.tex']] + \
            sorted(glob.glob(os.path.join(root, 'chapters/*.tex'))) + \
            sorted(glob.glob(os.path.join(root, 'figures/*.tex')))
    bad, short, checked = [], [], 0
    for f in files:
        src = re.sub(r'(?<!\\)%.*', '', open(f, encoding='utf-8').read())
        for m in re.finditer(r'\\begin\{(tabular|longtable)\}(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
                             r'(.*?)\\end\{\1\}', src, re.S):
            ncol = spec_columns(m.group(2))
            for r in rows_of(m.group(3)):
                if SKIP_ROW.match(r):
                    continue
                if not r.strip() or '&' not in r and '\\multicolumn' not in r:
                    continue
                c = cells(r)
                checked += 1
                line = src[:m.start(3)].count('\n') + 1
                if c > ncol:
                    bad.append((f, line, ncol, c, r.strip()[:70]))
                elif c < ncol:
                    short.append((f, line, ncol, c, r.strip()[:70]))
    return len(files), checked, bad, short


def main():
    nfiles, checked, bad, short = scan()
    print('tables: %d files scanned, %d rows checked' % (nfiles, checked))
    print('rows with MORE cells than the column spec (LaTeX error): %d' % len(bad))
    for f, ln, nc, c, txt in bad:
        print('  ERROR %-28s line %-4d spec=%d cells=%d  %s' % (f, ln, nc, c, txt))
    print('rows with FEWER cells (legal, empty trailing cells): %d' % len(short))
    for f, ln, nc, c, txt in short:
        print('  SHORT %-28s line %-4d spec=%d cells=%d  %s' % (f, ln, nc, c, txt))
    strict = '--strict' in sys.argv
    ok = not bad and (not short or not strict)
    print('RESULT:', 'OK' if ok else 'PROBLEMS FOUND')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
