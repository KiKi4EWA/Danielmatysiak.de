#!/usr/bin/env python3
"""Erzeugt Bestandsliste-Cover.md und .csv aus data/ (Register, release-extras.json, cover-assignments.json).
Aufruf im Ordner label-build:  python3 tools/make_bestandsliste.py"""
import json, re, os, csv, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reg = [r for r in json.load(open(f"{ROOT}/data/4spur-release-register.json"))["releases"] if r["label"] == "4Spur Records"]
ex = json.load(open(f"{ROOT}/data/release-extras.json"))["releases"]
asg = json.load(open(f"{ROOT}/data/cover-assignments.json"))["covers"]
reg.sort(key=lambda r: (r["release_date"], r["product_id"]), reverse=True)
NOTES = {"2582371": "k12.jpg war bei Crystal Ship zugeordnet, ist jetzt frei (Zuordnung offen)", "5806400": "Cover als Bild geliefert (1500 x 1500 px), Künstlerin angenommen", "4882157": "Cover als Bild geliefert (1500 x 1500 px)", "2582797": "Cover als Bild geliefert (1500 x 1500 px), Künstlerin angenommen", "2545750": "Cover als Bild geliefert (1125 x 1125 px), Künstlerin angenommen",
         "4185847": "k47.jpg war 1876x1866, mittig auf 1866x1866 beschnitten", "2515398": "Artist auf der Seite ohne KingAli 030 (Orchard noch ändern)", "4220638": "C-Line 2023 angenommen"}
rows = []
for r in reg:
    pid = r["product_id"]; x = ex.get(pid, {}); by = x.get("cover_by"); note = []
    if pid in asg:
        status = "echtes Cover"; stem = os.path.splitext(asg[pid])[0]; file = asg[pid]
        credit = f"Cover Art {by}" if by else ("#oban_" + stem if re.fullmatch(r"[A-Za-z0-9_]+", stem) else "kein Titel (Name mit Leerzeichen/Sonderzeichen)")
    else:
        status = "Platzhalter"; file = ""; credit = ""; note.append("noch kein Original")
    if pid in NOTES: note.append(NOTES[pid])
    rows.append(dict(datum=r["release_date"], release=r["title"], artist=x.get("artist") or r["artist"], format=r["format"], pid=pid,
                     sichtbar="nein (ausgeblendet)" if x.get("hidden") else "ja", cover=status, datei=file, titel=credit, anmerkung="; ".join(note)))
with open(f"{ROOT}/Bestandsliste-Cover.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";"); w.writeheader(); w.writerows(rows)
vis = [x for x in rows if x["sichtbar"] == "ja"]; real = [x for x in vis if x["cover"] == "echtes Cover"]; ph = [x for x in vis if x["cover"] != "echtes Cover"]
md = ["# Bestandsliste Cover, 4Spur Records", "", f"Stand {datetime.date.today():%d.%m.%Y}. {len(rows)} Releases im Register, davon {len(vis)} auf der Seite sichtbar und {len(rows)-len(vis)} ausgeblendet.",
      f"Sichtbar: {len(real)} mit echtem Cover, {len(ph)} mit Platzhalter.", "",
      "| Datum | Release | Artist | Produkt-ID | Sichtbar | Cover | Originaldatei | Bildtitel / Credit | Anmerkung |", "|---|---|---|---|---|---|---|---|---|"]
for x in rows: md.append(f"| {x['datum']} | {x['release']} | {x['artist']} | {x['pid']} | {x['sichtbar']} | {x['cover']} | {('`'+x['datei']+'`') if x['datei'] else ''} | {x['titel']} | {x['anmerkung']} |")
md += ["", "## Noch Platzhalter (sichtbar)", ""] + [f"- {x['release']} ({x['pid']}): {x['anmerkung']}" for x in ph]
open(f"{ROOT}/Bestandsliste-Cover.md", "w").write("\n".join(md) + "\n")
print(len(rows), "Releases,", len(vis), "sichtbar,", len(real), "echt,", len(ph), "Platzhalter")
