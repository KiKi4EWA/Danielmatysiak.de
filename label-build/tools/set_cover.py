#!/usr/bin/env python3
"""Setzt ein neues Cover für ein Release (Bild liegt als Datei vor, hat aber keinen Originalnamen mit Schema).
Aufruf (im Ordner label-build):  python3 tools/set_cover.py <product_id> <bilddatei> <asset-name.jpg> [Cover-Künstler]
- kopiert das Bild nach assets/<asset-name>, erzeugt die Web-Größen in site/img/covers (alte Größen werden entfernt)
- trägt die Zuordnung in data/cover-assignments.json ein und den Künstler als cover_by in data/release-extras.json"""
import sys, os, json, glob, shutil, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pid, img, asset = sys.argv[1], sys.argv[2], sys.argv[3]
by = sys.argv[4] if len(sys.argv) > 4 else "Obruni Antwi"
dst = os.path.join(ROOT, "assets", asset); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(img, dst)
out = os.path.join(ROOT, "site/img/covers"); os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, f"{pid}-*.webp")): os.remove(f)
with tempfile.TemporaryDirectory() as td:
    os.symlink(dst, os.path.join(td, f"{pid}.jpg"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/make_covers.py"), td, out], check=True)
a = json.load(open(f"{ROOT}/data/cover-assignments.json")); a["covers"][pid] = asset; json.dump(a, open(f"{ROOT}/data/cover-assignments.json", "w"), ensure_ascii=False, indent=1)
d = json.load(open(f"{ROOT}/data/release-extras.json")); d["releases"].setdefault(pid, {})["cover_by"] = by; json.dump(d, open(f"{ROOT}/data/release-extras.json", "w"), ensure_ascii=False, indent=1)
print("ok", pid, asset, by)
