#!/usr/bin/env python3
"""Cover-Masterdateien (z. B. 3000x3000) -> kleine WebP-Größen für die Website.
Aufruf:  python3 tools/make_covers.py <ordner_mit_masters> [zielordner=site/img/covers]
Dateinamen der Masters: <product_id>.jpg|png|tif  (z. B. 7018769.jpg)
Erzeugt <product_id>-320.webp, -640, -960, -1440. Nicht-quadratische Masters werden abgelehnt (keine Beschneidung)."""
import sys, pathlib, subprocess, tempfile, shutil
src = pathlib.Path(sys.argv[1]); dst = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "site/img/covers")
dst.mkdir(parents=True, exist_ok=True)
SIZES = (320, 640, 960, 1440)
def dims(p):
    o = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)], capture_output=True, text=True).stdout
    v = {l.split(":")[0].strip(): int(l.split(":")[1]) for l in o.splitlines() if ":" in l and "pixel" in l}
    return v["pixelWidth"], v["pixelHeight"]
for f in sorted(src.iterdir()):
    if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".tif", ".tiff"): continue
    w, h = dims(f)
    if w != h: print(f"SKIP {f.name}: nicht quadratisch ({w}x{h})"); continue
    for s in SIZES:
        if s > w: continue
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td) / "r.png"
            subprocess.run(["sips", "-s", "format", "png", "-z", str(s), str(s), str(f), "--out", str(tmp)], check=True, capture_output=True)
            subprocess.run(["cwebp", "-q", "82", "-m", "6", str(tmp), "-o", str(dst / f"{f.stem}-{s}.webp")], check=True, capture_output=True)
    print("ok", f.name)
