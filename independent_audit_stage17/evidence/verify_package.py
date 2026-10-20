#!/usr/bin/env python3
"""Auditor: verify the shipped ZIP against package_manifest.txt and itself."""
import hashlib, zipfile, os, re, sys
Z = 'HFF_Final_Overleaf_Package.zip'
h = hashlib.sha256(open(Z, 'rb').read()).hexdigest()
z = zipfile.ZipFile(Z)
names = z.namelist()
print("zip sha256 = %s" % h)
print("size = %d bytes ; members = %d" % (os.path.getsize(Z), len(names)))
print("zip comment / CRS:", z.comment, "|", sorted({i.compress_type for i in z.infolist()}))
mani = open('audit_stage15/package_manifest.txt', encoding='utf-8').read()
rows = re.findall(r'^([0-9a-f]{64})[ \t]+(\S+)[ \t]*$', mani, re.M)
print("manifest rows = %d" % len(rows))
bad = []
for dig, name in rows:
    cand = name.split('/')[-1] if name not in names else name
    if cand not in names:
        bad.append((name, 'MISSING')); continue
    got = hashlib.sha256(z.read(cand)).hexdigest()
    if got != dig: bad.append((name, got))
print("member-digest mismatches:", bad if bad else "none")
print("members not in manifest:", [n for n in names if n not in {r[1] for r in rows}
                                    and n.split('/')[-1] not in {r[1].split('/')[-1] for r in rows}])
# CRC integrity
print("testzip (CRC):", z.testzip() or "ok")
# determinism: member order and timestamps
print("first 3 members:", names[:3])
print("timestamps:", sorted({i.date_time for i in z.infolist()}))
