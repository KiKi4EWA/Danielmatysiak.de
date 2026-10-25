#!/usr/bin/env python3
"""Baut produktionen.html (Plattenwand für Arbeiten für andere Künstler) aus der Label-Seite des Repos.
Aufruf: python3 tools/build_produktionen.py <repo-ordner>
Daten: data/produktionen.json (Spotify-Album-ID, Titel, Künstler, Datum, Format); Cover: assets/produktionen/<id>.jpg -> img/covers/<id>-{320,640}.webp"""
import re, sys, json, html, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = pathlib.Path(sys.argv[1]).resolve()
D = json.loads((ROOT / "data/produktionen.json").read_text())["releases"]
D.sort(key=lambda r: (r["date"], r["id"]), reverse=True)

# Cover -> WebP
out = REPO / "img/covers"; out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    for r in D:
        src = ROOT / "assets/produktionen" / f'{r["id"]}.jpg'
        for w in (320, 640):
            t = out / f'{r["id"]}-{w}.webp'
            if t.exists(): continue
            png = pathlib.Path(td) / f'{r["id"]}-{w}.png'
            subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", str(w), str(src), "--out", str(png)], check=True, capture_output=True)
            subprocess.run(["cwebp", "-q", "86", "-m", "6", str(png), "-o", str(t)], check=True, capture_output=True)

s = (REPO / "label.html").read_text()
def cut(start, end, repl, flags=re.S):
    global s
    m = re.search(start + r".*?" + end, s, flags); assert m, start
    s = s.replace(m.group(0), repl, 1)

de_date = lambda iso: ".".join(reversed(iso.split("-")))
SEEN = set()
def tile(r):
    y = r["date"][:4]; anchor = ""
    if y not in SEEN: SEEN.add(y); anchor = f' id="y{y}"'
    srcset = ", ".join(f'img/covers/{r["id"]}-{w}.webp {w}w' for w in (320, 640))
    a = html.escape(r["artist"])
    t = html.escape(r["title"])
    return (f'<li class="release" data-year="{y}" data-artists=""{anchor}><button type="button" class="release-open" data-id="{r["id"]}" aria-haspopup="dialog">'
            f'<span class="cover"><img src="img/covers/{r["id"]}-640.webp" srcset="{srcset}" sizes="(max-width: 600px) 50vw, (max-width: 1100px) 25vw, 17vw" width="640" height="640" alt="" loading="lazy" decoding="async">'
            f'<span class="cover-info" aria-hidden="true"><span class="cover-artist">{a}</span></span></span>'
            f'<span class="meta"><span class="release-artist">{a}</span><span class="release-title">{t}</span>'
            f'<time class="release-date" datetime="{r["date"]}">{de_date(r["date"])}</time></span></button></li>')
grid = "\n          ".join(tile(r) for r in D)
N = len(D)

# Kopf
s = re.sub(r"<title>.*?</title>", "<title>Produktionen für andere Künstler – Daniel Matysiak</title>", s, 1)
DESC = "Ausgewählte Arbeiten für andere Künstler: Releases, an denen Daniel Matysiak beteiligt war, darunter Nicolas Sosa, ANNA T, Tiita und Wolfgang Tillmans."
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, 1)
s = s.replace('content="index, follow"', 'content="noindex, follow"', 1)
s = s.replace("https://danielmatysiak.de/label.html", "https://danielmatysiak.de/produktionen.html")
s = re.sub(r'(<meta property="og:title" content=")[^"]*"', r'\1Produktionen für andere Künstler – Daniel Matysiak"', s, 1)
s = re.sub(r'(<meta name="twitter:title" content=")[^"]*"', r'\1Produktionen für andere Künstler – Daniel Matysiak"', s, 1)
s = re.sub(r'(<meta property="og:description" content=")[^"]*"', rf'\1{DESC}"', s, 1)
s = re.sub(r'(<meta name="twitter:description" content=")[^"]*"', rf'\1{DESC}"', s, 1)
s = re.sub(r'  <script type="application/ld\+json">.*?</script>\n', "", s, 1, flags=re.S)
# Menü: Audio aktiv statt Label
s = s.replace('<li><a href="label.html" class="active">Label</a></li>', '<li><a href="label.html">Label</a></li>', 1)
s = s.replace('<li><a href="leistungen.html">Audio</a></li>', '<li><a href="leistungen.html" class="active">Audio</a></li>', 1)

# Hero
cut(r'<section class="hero hero-deco">', r'</section>', '''<section class="hero hero-deco">
      <p class="hero-kicker" data-en="Audio · Productions">Audio · Produktionen</p>
      <h1 data-en="Productions.">Produktionen.</h1>
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="lede" data-en="Selected works for other artists: releases I have produced, mixed or mastered outside of my own label 4Spur Records.">Ausgewählte Arbeiten für andere Künstler: Releases, die ich außerhalb meines eigenen Labels 4Spur Records produziert, gemischt oder gemastert habe.</p>
          <div class="cta-row">
            <a class="btn" href="kontakt.html"><span data-en="Start a project">Projekt anfragen</span></a>
            <a class="btn-ghost" href="leistungen.html"><span data-en="Back to Audio">Zurück zu Audio</span></a>
          </div>
        </div>
      </div>
      <img class="hero-deco-img hero-deco-full" src="img/audio_neve.webp" alt="" aria-hidden="true">
    </section>''')
# Artist-Menü und Textblock entfallen
cut(r'<div id="artist-menu" popover', r'</div>\n\s*\n', "")
cut(r'<section class="artist-intro"', r'</section>\n\s*\n', "")
# Wand
cut(r'<section class="section release-wall" id="archiv">', r'</section>', f'''<section class="section release-wall" id="archiv">
      <p class="eyebrow" data-en="Selected works">Ausgewählte Arbeiten</p>
      <p class="section-intro" data-en="{N} selected works for other artists, newest first. Click a cover for details."><span class="release-count">{N}</span> ausgewählte Arbeiten für andere Künstler, neueste zuerst. Klick auf ein Cover öffnet die Details.</p>
      <ul class="release-grid" role="list">
          {grid}
      </ul>
      <div class="cta-row">
        <a class="btn" href="https://open.spotify.com/playlist/0XUePz5P5GzsRHbm8iVkRv" target="_blank" rel="noopener"><span data-en="Playlist on Spotify ↗">Playlist auf Spotify ↗</span></a>
        <a class="btn-ghost" href="label.html"><span data-en="To the label">Zum Label</span></a>
      </div>
    </section>''')
# Jahresleiste
years = sorted({r["date"][:4] for r in D}, reverse=True)
cut(r'(?<=<nav class="year-nav" id="year-nav" aria-label="Jahre" data-no-swipe>\n)\s*<ul>', r'</ul>', "    <ul>\n" + "\n".join(f'      <li><a href="#y{y}">{y}</a></li>' for y in years) + "\n    </ul>")
# Daten
data = {r["id"]: {"id": r["id"], "title": r["title"], "artist": r["artist"], "date": r["date"], "format": r["format"], "cover": [320, 640],
                  "links": {"spotify": f'https://open.spotify.com/album/{r["id"]}'}, "cline": r["date"][:4],
                  "credits": r.get("credits"), "description": r.get("description"), "descriptionEn": r.get("description_en")} for r in D}
data = {k: {a: b for a, b in v.items() if b} for k, v in data.items()}
dj = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
cut(r'<script type="application/json" id="release-data">', r'</script>', f'<script type="application/json" id="release-data">{dj}</script>')
s = re.sub(r'\s*<script type="application/json" id="artist-data">.*?</script>', "", s, 1, flags=re.S)
(REPO / "produktionen.html").write_text(s)
print("produktionen.html:", N, "Releases,", len(years), "Jahre")
