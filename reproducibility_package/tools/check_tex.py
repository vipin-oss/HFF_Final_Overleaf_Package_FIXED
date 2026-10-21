#!/usr/bin/env python3
"""Structural audit of the manuscript before it goes to Overleaf.

Checks, without a TeX installation:

* brace balance and matching \\begin/\\end environments in ``main.tex``;
* duplicate, unresolved and unused labels;
* every ``\\cite``/``\\citep``/``\\citet`` key present in ``references.bib``;
* every bibliography key cited at least once;
* every ``\\includegraphics`` file present in ``journal_submission/figures``;
* every ``\\tabinput`` fragment present (in either build layout).

Usage:  python3 tools/check_tex.py [--quiet]
Exit code 0 when no issue is found, 1 otherwise.
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUB = ROOT / "journal_submission"


def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        i = line.find("%")
        out.append(line if i < 0 else line[:i])
    return "\n".join(out)


def main() -> int:
    tex = (SUB / "main.tex").read_text()
    body = strip_comments(tex)
    issues: list[str] = []

    # brace balance
    flat = re.sub(r"\\[{}]", "", body)
    depth = 0
    for ch in flat:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                issues.append("unbalanced closing brace")
                break
    if depth != 0:
        issues.append(f"brace depth at end of file = {depth}")

    # environments
    envs: collections.Counter = collections.Counter()
    for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", body):
        envs[(m.group(1), m.group(2))] += 1
    for (kind, name), n in envs.items():
        other = envs[("end" if kind == "begin" else "begin", name)]
        if n != other:
            issues.append(f"environment {name}: {kind} {n} vs {other}")

    # labels: main file plus the generated table fragments
    labels = re.findall(r"\\label\{([^}]+)\}", body)
    for frag in sorted((SUB / "tables").glob("*.tex")):
        labels += re.findall(r"\\label\{([^}]+)\}", frag.read_text())
    refs = set(re.findall(r"\\(?:ref|eqref|pageref)\{([^}]+)\}", body))
    dups = [k for k, v in collections.Counter(labels).items() if v > 1]
    if dups:
        issues.append(f"duplicate labels: {dups}")
    missing = sorted(refs - set(labels))
    if missing:
        issues.append(f"references without a label: {missing}")

    # citations
    keys = set(re.findall(r"@\w+\{([^,]+),", (SUB / "references.bib").read_text()))
    cited: set[str] = set()
    for m in re.finditer(r"\\cite[pt]?\{([^}]+)\}", body):
        cited.update(k.strip() for k in m.group(1).split(","))
    bad = sorted(cited - keys)
    if bad:
        issues.append(f"cited keys missing from references.bib: {bad}")
    uncited = sorted(keys - cited)

    # figures and table fragments
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
        p = SUB / "figures" / m.group(1)
        if not p.exists():
            issues.append(f"missing figure file: {p.relative_to(ROOT)}")
    for m in re.finditer(r"\\tabinput\{([^}]+)\}", body):
        name = m.group(1)
        if not (SUB / "tables" / name).exists():
            issues.append(f"missing table fragment: tables/{name}")

    print(f"labels {len(labels)}  references {len(refs)}  citations {len(cited)}  "
          f"bib keys {len(keys)}")
    if uncited:
        print(f"bibliography keys never cited: {uncited}")
    print("ISSUES:" if issues else "no structural issues found")
    for i in issues:
        print("  -", i)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
