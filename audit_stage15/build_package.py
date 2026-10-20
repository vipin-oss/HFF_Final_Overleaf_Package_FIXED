#!/usr/bin/env python3
"""Build HFF_Final_Overleaf_Package.zip from exactly the tracked sources.

Deterministic: fixed member order, fixed timestamps, sorted names, deflate level 9.
Records the SHA-256 of the ZIP and of every member in audit_stage15/package_manifest.txt.
"""
import os, hashlib, zipfile, sys

ZIP_NAME = 'HFF_Final_Overleaf_Package.zip'
STAMP = (2026, 10, 19, 0, 0, 0)

FIXED = ['main.tex', 'references.bib', 'main.pdf', 'README.md']

SKIP_DIRS = {'__pycache__'}
SKIP_EXT = ('.pyc', '.pyo')

def walk_top(d):
    """every file under d, sorted; byte-code caches are never shipped"""
    out = []
    for root, dirs, files in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith(SKIP_EXT):
                continue
            out.append(os.path.join(root, f).replace(os.sep, '/'))
    return sorted(out)

MEMBERS = FIXED + walk_top('chapters') + walk_top('figures') + walk_top('audit_stage15') + [
    'HFF_final_pre_coding_checklist.md',
    'HFF_final_reference_status.csv',
    'HFF_final_reference_status_notes.txt',
    'HFF_source_pdf_consistency_report.md',
    'HFF_revision_summary.md',
    'HFF_final_packaging_report.md',
] + walk_top('project_archive')

SELF = 'audit_stage15/package_manifest.txt'
MEMBERS = [m for m in MEMBERS if m != SELF]   # the manifest cannot hash itself

missing = [m for m in MEMBERS if not os.path.isfile(m)]
if missing:
    print("MISSING (not zipped):", missing); sys.exit(1)

def add(zf, name):
    zi = zipfile.ZipInfo(name, date_time=STAMP)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.external_attr = 0o644 << 16
    with open(name, 'rb') as fh:
        zf.writestr(zi, fh.read(), compresslevel=9)

if os.path.exists(ZIP_NAME): os.remove(ZIP_NAME)
with zipfile.ZipFile(ZIP_NAME, 'w') as zf:
    for m in MEMBERS: add(zf, m)

with open(ZIP_NAME, 'rb') as fh:
    digest = hashlib.sha256(fh.read()).hexdigest()

lines = ["HFF_Final_Overleaf_Package.zip",
         "sha256 %s" % digest,
         "size   %d bytes" % os.path.getsize(ZIP_NAME),
         "members %d" % len(MEMBERS), ""]
for m in MEMBERS:
    lines.append("%s  %s" % (hashlib.sha256(open(m, 'rb').read()).hexdigest(), m))
open('audit_stage15/package_manifest.txt', 'w', encoding='utf-8').write("\n".join(lines) + "\n")
print(digest, os.path.getsize(ZIP_NAME), len(MEMBERS))
