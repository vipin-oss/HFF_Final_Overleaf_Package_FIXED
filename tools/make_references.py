#!/usr/bin/env python3
"""Generate an Emerald (HFF) style reference list from ``references.bib``.

The manuscript is typeset to look like a paper in the *International Journal of
Numerical Methods for Heat & Fluid Flow*, whose reference list follows the
Emerald Harvard conventions::

    Surname, I.N., Surname, I.N. and Surname, I.N. (Year), "Title of the
    article", Journal Name, Vol. 12 No. 3, pp. 45-67, doi: 10.xxxx/yyyy.

    Surname, I.N. (Year), Title of the book, Publisher, Place.

``references.bib`` stays the single source of truth (it carries the Crossref-verified
metadata).  This script turns it into ``journal_submission/references.tex``, a
``thebibliography`` block whose ``\\bibitem`` labels are natbib author-year labels, so
that ``\\citep``/``\\citet`` keep working without running BibTeX.

Usage::

    python3 tools/make_references.py            # write references.tex
    python3 tools/make_references.py --check    # verify it is up to date

The script uses only the standard library.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIB = ROOT / "journal_submission" / "references.bib"
OUT = ROOT / "journal_submission" / "references.tex"

FIELDS = ("author", "title", "journal", "booktitle", "publisher", "address",
          "volume", "number", "pages", "year", "doi", "edition", "series")


def parse_bib(text: str) -> list[dict]:
    entries = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):
        kind, key, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        rec: dict = {"_type": kind, "_key": key}
        for field in FIELDS:
            mm = re.search(r"\b" + field + r"\s*=\s*\{(.*?)\}\s*(,|\n|$)", body, re.S)
            if mm:
                rec[field] = " ".join(mm.group(1).split())
        entries.append(rec)
    return entries


def split_authors(field: str) -> list[tuple[str, str]]:
    """Return (family, given) pairs from a BibTeX author field."""
    out = []
    for chunk in re.split(r"\s+and\s+", field):
        chunk = chunk.strip().rstrip(",")
        if not chunk:
            continue
        if "," in chunk:
            family, given = chunk.split(",", 1)
        else:                       # "Given Family"
            parts = chunk.split()
            family, given = parts[-1], " ".join(parts[:-1])
        out.append((family.strip(), given.strip()))
    return out


def initials(given: str) -> str:
    out = []
    for token in re.split(r"[\s]+", given):
        token = token.strip(".")
        if not token:
            continue
        if "-" in token:
            out.append("-".join(p[0].upper() + "." for p in token.split("-") if p))
        else:
            out.append(token[0].upper() + ".")
    return " ".join(out)


def author_list(authors: list[tuple[str, str]]) -> str:
    parts = [f"{fam}, {initials(giv)}" if giv else fam for fam, giv in authors]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def short_label(authors: list[tuple[str, str]]) -> str:
    fams = [a[0] for a in authors]
    if len(fams) == 1:
        return fams[0]
    if len(fams) == 2:
        return f"{fams[0]} and {fams[1]}"
    return f"{fams[0]} et al."


def tidy(text: str) -> str:
    """Protect characters that are special in LaTeX, keep existing markup."""
    text = re.sub(r"(?<!\\)&", lambda m: chr(92) + "&", text)
    text = re.sub(r"(?<!\\)%", lambda m: chr(92) + "%", text)
    text = re.sub(r"(?<!\\)_", lambda m: chr(92) + "_", text)
    return text


def pages_text(pages: str) -> str:
    """Emerald prints page ranges; article numbers get ``Art. no.``."""
    pages = pages.strip()
    if re.match(r"^[A-Za-z]", pages):
        return f"Art. no. {pages}"
    return f"pp. {pages.replace('--', '--')}"


def format_entry(rec: dict, suffix: str = "") -> tuple[str, str]:
    """Return (natbib label, formatted reference text).

    ``suffix`` disambiguates two entries by the same authors in the same year
    (``2019a``, ``2019b``); natbib needs the letter inside ``\\natexlab``.
    """
    authors = split_authors(rec.get("author", ""))
    year = rec.get("year", "n.d.")
    shown = f"{year}{suffix}"
    label = f"{short_label(authors)}({year}"
    label += f"{{\\natexlab{{{suffix}}}}})" if suffix else ")"
    names = tidy(author_list(authors))
    title = tidy(rec.get("title", ""))
    doi = rec.get("doi", "")
    tail = f", doi: {doi}" if doi else ""

    if rec["_type"] == "article":
        journal = tidy(rec.get("journal", ""))
        bits = [f"{names} ({shown})", f'"{title}"', f"\\textit{{{journal}}}"]
        if rec.get("volume"):
            vol = f"Vol. {rec['volume']}"
            if rec.get("number"):
                vol += f" No. {rec['number']}"
            bits.append(vol)
        if rec.get("pages"):
            bits.append(pages_text(rec["pages"]))
        body = ", ".join(bits) + tail + "."
    elif rec["_type"] == "book":
        bits = [f"{names} ({shown})", f"\\textit{{{title}}}"]
        if rec.get("edition"):
            bits[1] += f", {rec['edition']}rd ed." if rec["edition"] == "3" else \
                       f", {rec['edition']}"
        if rec.get("publisher"):
            bits.append(tidy(rec["publisher"]))
        if rec.get("address"):
            bits.append(tidy(rec["address"]))
        body = ", ".join(bits) + tail + "."
    else:                            # incollection / inproceedings
        bits = [f"{names} ({shown})", f'"{title}"']
        if rec.get("booktitle"):
            bits.append(f"in \\textit{{{tidy(rec['booktitle'])}}}")
        if rec.get("publisher"):
            bits.append(tidy(rec["publisher"]))
        if rec.get("address"):
            bits.append(tidy(rec["address"]))
        if rec.get("pages"):
            bits.append(pages_text(rec["pages"]))
        body = ", ".join(bits) + tail + "."
    return label, body


def sort_key(rec: dict):
    authors = split_authors(rec.get("author", ""))
    return (authors[0][0].lower() if authors else rec["_key"], rec.get("year", ""),
            rec.get("title", "").lower())


def build() -> str:
    entries = parse_bib(BIB.read_text())
    entries.sort(key=sort_key)
    lines = [
        "% ---------------------------------------------------------------------------",
        "%  references.tex -- generated by tools/make_references.py from references.bib",
        "%  Emerald (HFF) Harvard style.  Do not edit by hand: edit references.bib and",
        "%  re-run  python3 tools/make_references.py",
        f"%  {len(entries)} entries, alphabetically ordered by first author.",
        "% ---------------------------------------------------------------------------",
        r"\begingroup",
        r"\renewcommand{\section}[2]{}%",  # not used: heading is typeset in main.tex
        r"\begin{thebibliography}{99}",
        r"\setlength{\itemsep}{1pt}",
        "",
    ]
    # disambiguate identical author-year labels (2019a/2019b) before emitting
    base_labels = [format_entry(rec)[0] for rec in entries]
    counts = {lab: base_labels.count(lab) for lab in base_labels}
    seen: dict[str, int] = {}
    letters = "abcdefghij"
    for rec, base in zip(entries, base_labels):
        suffix = ""
        if counts[base] > 1:
            k = seen.get(base, 0)
            suffix = letters[k]
            seen[base] = k + 1
        label, body = format_entry(rec, suffix)
        lines.append(f"\\bibitem[{label}]{{{rec['_key']}}}")
        lines.append(body)
        lines.append("")
    lines += [r"\end{thebibliography}", r"\endgroup", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if references.tex differs from a fresh build")
    args = ap.parse_args()
    text = build()
    if args.check:
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            print("references.tex is out of date; re-run without --check", file=sys.stderr)
            return 1
        print(f"references.tex up to date ({text.count(chr(92) + 'bibitem')} entries)")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT} ({text.count(chr(92) + 'bibitem')} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
