#!/usr/bin/env python3
"""Erzeugt site/label.html + label.js und patcht Nav/Footer/JS/CSS/Sitemap/llms.txt.
Läuft auf einer frischen Kopie des Repos (nicht idempotent):
    rm -rf site && mkdir site && cp -R <repo>/. site/ && rm -rf site/.git && python3 build_label.py
Daten: data/4spur-release-register.json (Orchard-Register) + data/release-extras.json (optionale Redaktionsdaten je product_id).
Cover: site/img/covers/<product_id>-{320,640,960,1440}.webp (siehe tools/make_covers.py); fehlt die Datei, erscheint ein Platzhalter."""
import os, re, html, json, pathlib, collections

ROOT = pathlib.Path(__file__).parent
import sys
SITE = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "site"
reg = json.loads((ROOT / "data/4spur-release-register.json").read_text())
extras = json.loads((ROOT / "data/release-extras.json").read_text()).get("releases", {})
_cl = ROOT / "data/c-lines.json"
CLINE = json.loads(_cl.read_text()).get("years", {}) if _cl.exists() else {}
_ca = ROOT / "data/cover-assignments.json"
ASSIGN = json.loads(_ca.read_text()).get("covers", {}) if _ca.exists() else {}
def art_title(pid):
    """Dateiname 1203122.jpg -> #oban_1203122, k37.jpg -> #oban_k37 (Name unverändert; Leerzeichen und Sonderzeichen gelten als Abweichler: kein Titel)"""
    stem = os.path.splitext(ASSIGN.get(pid, ""))[0]
    return "#oban_" + stem if re.fullmatch(r"[A-Za-z0-9_]+", stem) else None

# Artist-Korrekturen aus den Extras (z. B. bis der Orchard-Eintrag angepasst ist)
for _r in reg["releases"]:
    if extras.get(_r["product_id"], {}).get("artist"): _r["artist"] = extras[_r["product_id"]]["artist"]
REL = sorted((r for r in reg["releases"] if r["label"] == "4Spur Records" and not extras.get(r["product_id"], {}).get("hidden")),
             key=lambda r: (r["release_date"], r["product_id"]), reverse=True)
# Redaktionelle Reihenfolge: DUB du PHONK und AUGENLIED tauschen die Plätze (DUB du PHONK nach vorn, damit sein Cover groß erscheint)
_i, _j = (next(k for k, r in enumerate(REL) if r["product_id"] == p) for p in ("7018769", "6564352"))
REL[_i], REL[_j] = REL[_j], REL[_i]
SIZES = (320, 640, 960, 1440)

# ---- Artists (Menü + Filter): Hauptkünstler aller sichtbaren Releases; Featuring zählt zur Zuordnung, erzeugt aber keinen Eintrag
def aslug(n): return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")
_NAME_FIX = {"kingali-030": "KingAli 030", "debbie-parker-inc": "Debbie Parker INC."}
_AD = ROOT / "data/artists.json"
ARTIST_INFO = json.loads(_AD.read_text()) if _AD.exists() else {}
ARTISTS = {}
for _r in REL:
    for _n in (n.strip() for n in _r["artist"].split(",") if n.strip()):
        ARTISTS.setdefault(aslug(_n), _NAME_FIX.get(aslug(_n), _n))
def tile_artists(r):
    names = [n.strip() for n in (r["artist"] + "," + (r.get("featuring") or "")).split(",") if n.strip()]
    return " ".join(dict.fromkeys(a for a in (aslug(n) for n in names) if a in ARTISTS))
def make_photo(slug, fname):
    """assets/<fname> -> img/artists/<slug>-photo-<breite>.webp (900 und 1600, nie größer als das Original); liefert Pfade und Maße oder None"""
    src = ROOT / "assets" / fname
    if not src.exists(): return None
    import subprocess, tempfile
    o = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(src)], capture_output=True, text=True).stdout.split()
    W, H = int(o[-3]), int(o[-1])
    widths = sorted({min(w, W) for w in (900, 1600)})
    out = SITE / "img/artists"; out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        png = pathlib.Path(td) / "p.png"
        subprocess.run(["sips", "-s", "format", "png", str(src), "--out", str(png)], check=True, capture_output=True)
        for w in widths:
            t = out / f"{slug}-photo-{w}.webp"
            if t.exists(): continue
            tmp = pathlib.Path(td) / f"r{w}.png"
            subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", str(w), str(png), "--out", str(tmp)], check=True, capture_output=True)
            subprocess.run(["cwebp", "-q", "82", "-m", "6", str(tmp), "-o", str(t)], check=True, capture_output=True)
    return {"s": f"img/artists/{slug}-photo-{widths[0]}.webp", "l": f"img/artists/{slug}-photo-{widths[-1]}.webp", "sw": widths[0], "lw": widths[-1], "w": W, "h": H}
ARTIST_LIST = []
for _slug, _name in sorted(ARTISTS.items(), key=lambda kv: kv[1].lower()):
    _info = ARTIST_INFO.get(_slug, {})
    ARTIST_LIST.append({k: v for k, v in {"slug": _slug, "name": _name, "bio": _info.get("bio"), "bioEn": _info.get("bioEn"), "spotify": _info.get("spotify"),
                                          "photo": make_photo(_slug, _info["photo"]) if _info.get("photo") else None, "photoAlt": _info.get("photoAlt"), "photoAltEn": _info.get("photoAltEn"),
                                          "count": sum(1 for r in REL if _slug in tile_artists(r).split())}.items() if v})
artist_json = json.dumps(ARTIST_LIST, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
ARTIST_LIST.sort(key=lambda a: (-a["count"], a["name"].lower()))   # nach Release-Anzahl, bei Gleichstand alphabetisch
menu_items = "\n".join(f'          <li><button type="button" data-artist="{a["slug"]}">{html.escape(a["name"])}<span class="menu-count">{a["count"]}</span></button></li>' for a in ARTIST_LIST)

# Große Kacheln: je Jahr das jüngste Release, abwechselnd links/rechts gesetzt.
# Redaktionelle Übersteuerung: "highlight": true/false in data/release-extras.json.
HL = set()
_seen_y = set()
_count = collections.Counter(r["release_date"][:4] for r in REL)
for _r in REL:                                   # REL ist absteigend nach Datum sortiert
    _y = _r["release_date"][:4]
    # nur Jahre mit mindestens 4 Releases bekommen eine große Kachel (sonst stehen große Kacheln direkt nebeneinander)
    if _y not in _seen_y and _count[_y] >= 4: _seen_y.add(_y); HL.add(_r["product_id"])
for _pid, _x in extras.items():
    if "highlight" in _x: (HL.add if _x["highlight"] else HL.discard)(_pid)
SIDE = {}
for _i, _r in enumerate(r for r in REL if r["product_id"] in HL):
    SIDE[_r["product_id"]] = "hl-left" if _i % 2 == 0 else "hl-right"
def is_hl(pid): return pid in HL

def cover_sizes(pid):
    have = [s for s in SIZES if (SITE / f"img/covers/{pid}-{s}.webp").exists()]
    return have if 640 in have else []

def de_date(iso):
    y, m, d = iso.split("-"); return f"{d}.{m}.{y}"

def cover_html(r):
    pid = r["product_id"]; have = cover_sizes(pid)
    veil = f'<span class="cover-info" aria-hidden="true"><span class="cover-artist">{html.escape(r["artist"]).replace("&amp;", "y").replace("808", '<span class="n808">808</span>')}</span></span>'
    if not have:
        return f'<span class="cover cover-ph" aria-hidden="true">{veil}</span>'
    srcset = ", ".join(f"img/covers/{pid}-{s}.webp {s}w" for s in have if s <= 960)   # 1440 nur für Detailfenster und Großansicht
    sizes = "(max-width: 600px) 50vw, (max-width: 1100px) 25vw, 17vw"
    if is_hl(pid):
        sizes = "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 34vw"
    return (f'<span class="cover"><img src="img/covers/{pid}-640.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="640" height="640" alt="" loading="lazy" decoding="async">{veil}</span>')

SEEN = set()
def tile(r):
    pid = r["product_id"]; x = extras.get(pid, {})
    y = r["release_date"][:4]
    anchor = ""
    if y not in SEEN:
        SEEN.add(y); anchor = f' id="y{y}"'
    artist = html.escape(r["artist"]) + (f' <span class="release-feat">feat. {html.escape(r["featuring"])}</span>' if r.get("featuring") else "")
    cls = f"release is-highlight {SIDE[pid]}" if is_hl(pid) else "release"
    return (f'<li class="{cls}" data-year="{y}" data-artists="{tile_artists(r)}"{anchor}><button type="button" class="release-open" data-id="{pid}" aria-haspopup="dialog">'
            f'{cover_html(r)}'
            f'<span class="meta"><span class="release-artist">{artist}</span>'
            f'<span class="release-title">{html.escape(r["title"])}</span>'
            f'<time class="release-date" datetime="{r["release_date"]}">{de_date(r["release_date"])}</time></span>'
            f'</button></li>')

by_year = collections.OrderedDict()
for r in REL: by_year.setdefault(r["release_date"][:4], []).append(r)

# ---- Künstlerkachel: Selbstporträt von Obruni Antwi (kein Release, zählt nicht mit)
import subprocess, tempfile
ART_ID = "obruni-antwi"
ART_YEAR = "2020"      # Die Kachel steht im Jahr 2020 (Lücke nach den ausgeblendeten Releases)
ARTIST_TILE = {
    "name": "Obruni Antwi",
    "role": "Cover-Künstlerin", "roleEn": "Cover artist",
    "bio": ["Obruni Antwi ist freie Künstlerin aus Berlin, geboren in Schwerin und Mitglied im VbK Berlin. Ihre Laufbahn begann in der DDR als Textildesignerin, außerdem war sie Leiterin einer Werkstatt. Aus der DDR kam sie nach West-Berlin und arbeitet seither als freie Künstlerin. Sie malt und arbeitet in vielen Techniken.",
            "Alle Cover auf dieser Seite stammen von ihr. Sie entstanden zwischen 2011 und 2014 mit Microsoft Paint, in ihrer digitalen Phase. 4Spur Records bedankt sich bei der Künstlerin, dass sie ihre Arbeiten als Cover zur Verfügung gestellt hat."],
    "bioEn": ["Obruni Antwi is a freelance artist from Berlin, born in Schwerin and a member of VbK Berlin. Her career began in the GDR as a textile designer, and she also ran a workshop. She came from the GDR to West Berlin and has worked as a freelance artist ever since. She paints and works in many techniques.",
              "All covers on this page are by her. They were made between 2011 and 2014 with Microsoft Paint, during her digital phase. 4Spur Records thanks the artist for making her works available as covers."],
    "links": [["X", "https://x.com/ObruniAntwi"], ["oncyber", "https://oncyber.io/rubadubsundays"]],
}
def ensure_artist_images():
    src = ROOT / "assets/obruni-antwi-selbstportrait.jpg"
    out = SITE / "img/artists"; out.mkdir(parents=True, exist_ok=True)
    if not src.exists(): return False
    def dims(p):
        o = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)], capture_output=True, text=True).stdout.split()
        return int(o[-3]), int(o[-1])
    W, H = dims(src)
    with tempfile.TemporaryDirectory() as td:
        full = pathlib.Path(td) / "full.png"
        subprocess.run(["sips", "-s", "format", "png", str(src), "--out", str(full)], check=True, capture_output=True)
        jobs = [(full, f"{ART_ID}-full-{w}.webp", w) for w in (480, 960)]
        for srcp, name, w in jobs:
            if (out / name).exists(): continue
            tmp = pathlib.Path(td) / ("r_" + name + ".png")
            subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", str(w), str(srcp), "--out", str(tmp)], check=True, capture_output=True)
            subprocess.run(["cwebp", "-q", "88", "-m", "6", str(tmp), "-o", str(out / name)], check=True, capture_output=True)
    return True
HAS_ARTIST = ensure_artist_images()

def artist_tile():
    a = ARTIST_TILE
    veil = f'<span class="cover-info" aria-hidden="true"><span class="cover-artist">{html.escape(a["name"])}</span></span>'
    img = (f'<span class="cover"><img src="img/artists/{ART_ID}-full-480.webp" srcset="img/artists/{ART_ID}-full-480.webp 480w, img/artists/{ART_ID}-full-960.webp 960w" '
           f'sizes="(max-width: 600px) 50vw, (max-width: 1100px) 25vw, 17vw" width="480" height="739" alt="Selbstporträt von Obruni Antwi" loading="lazy" decoding="async">{veil}</span>')
    return (f'<li class="release artist-tile" id="y{ART_YEAR}" data-year="{ART_YEAR}"><button type="button" class="release-open" data-id="{ART_ID}" aria-haspopup="dialog">{img}'
            f'<span class="meta"><span class="release-artist" data-en="{a["roleEn"]}">{html.escape(a["role"])}</span>'
            f'<span class="release-title">{html.escape(a["name"])}</span></span></button></li>')

_tiles = [tile(r) for r in REL]
if HAS_ARTIST:
    _pos = next((i for i, r in enumerate(REL) if r["release_date"][:4] < ART_YEAR), len(_tiles))
    _tiles.insert(_pos, artist_tile())
grid = "\n          ".join(_tiles)
wall = f'''      <ul class="release-grid" role="list">
          {grid}
      </ul>'''

RAIL_YEARS = sorted(set(by_year) | ({ART_YEAR} if HAS_ARTIST else set()), reverse=True)
year_nav = "\n".join(f'      <li><a href="#y{y}">{y}</a></li>' for y in RAIL_YEARS)

# Daten für das Detailpanel (ohne interne Felder: keine UPC, Source-URL, Projekt, Katalogcode)
data = {}
if HAS_ARTIST:
    data[ART_ID] = {"id": ART_ID, "kind": "artist", "name": ARTIST_TILE["name"], "role": ARTIST_TILE["role"], "roleEn": ARTIST_TILE["roleEn"],
                    "bio": ARTIST_TILE["bio"], "bioEn": ARTIST_TILE["bioEn"], "links": ARTIST_TILE["links"],
                    "image": f"img/artists/{ART_ID}-full-960.webp", "imageSmall": f"img/artists/{ART_ID}-full-480.webp"}
for r in REL:
    pid = r["product_id"]; x = extras.get(pid, {})
    data[pid] = {k: v for k, v in {
        "id": pid, "title": r["title"], "artist": r["artist"], "feat": r.get("featuring"),
        "date": r["release_date"], "format": r["format"], "cover": cover_sizes(pid) or None,
        "links": x.get("links"), "tracks": x.get("tracks"), "duration": x.get("duration"),
        "art": (None if x.get("cover_by") else art_title(pid)), "artBy": (x.get("cover_by") if (pid in ASSIGN and cover_sizes(pid)) else None), "cline": (f'{CLINE[pid]} 4Spur Records' if pid in CLINE else f'{r["release_date"][:4]} 4Spur Records'), "description": x.get("description"), "descriptionEn": x.get("description_en"), "credits": x.get("credits"), "videos": x.get("videos"),
    }.items() if v}
data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---- Strukturierte Daten (SEO/GEO): Label + Release-Liste
GENRES = ["Dub", "Reggae", "Hip-Hop", "Electronic", "Ambient", "House"]
LABEL_ID = "https://danielmatysiak.de/label.html#label"
RELTYPE = {"Single": "SingleRelease", "EP": "EPRelease", "Album": "AlbumRelease"}
def _artists(a): return [{"@type": "MusicGroup", "name": n.strip()} for n in a.split(",") if n.strip()]
_items = []
for _i, _r in enumerate(REL, 1):
    _l = extras.get(_r["product_id"], {}).get("links", {})
    _same = [u for u in (_l.get("spotify"), _l.get("apple")) if u]
    _it = {"@type": "MusicAlbum", "name": _r["title"], "byArtist": _artists(_r["artist"]), "datePublished": _r["release_date"],
           "albumReleaseType": "https://schema.org/" + RELTYPE.get(_r["format"], "AlbumRelease"), "publisher": {"@id": LABEL_ID}}
    if _same: _it["sameAs"] = _same
    _d = extras.get(_r["product_id"], {}).get("description")
    if _d: _it["description"] = _d
    _items.append({"@type": "ListItem", "position": _i, "item": _it})
LD = json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "@id": LABEL_ID, "name": "4Spur Records", "url": "https://danielmatysiak.de/label.html",
     "description": "Unabhängiges Label für Dub, Reggae, Hip-Hop, Electronic, Ambient und House Music aus Berlin.",
     "knowsAbout": GENRES, "address": {"@type": "PostalAddress", "addressLocality": "Berlin", "addressCountry": "DE"},
     "founder": {"@type": "Person", "name": "Daniel Matysiak", "url": "https://danielmatysiak.de"}},
    *([{"@type": "Person", "name": "Obruni Antwi", "jobTitle": "Künstlerin", "sameAs": [u for _, u in ARTIST_TILE["links"]],
        "image": f"https://danielmatysiak.de/img/artists/{ART_ID}-full-960.webp"}] if HAS_ARTIST else []),
    {"@type": "ItemList", "name": "4Spur Records Releases", "numberOfItems": len(_items), "itemListOrder": "https://schema.org/ItemListOrderDescending", "itemListElement": _items},
]}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

nav_tpl = (SITE / "about.html").read_text()
head_nav = re.search(r'  <nav class="site-nav">.*?</nav>\n', nav_tpl, re.S).group(0)
head_nav = head_nav.replace(' class="active"', '').replace('<li><a href="lab.html">Lab</a></li>',
    '<li><a href="lab.html">Lab</a></li>\n        <li><a href="label.html" class="active">Label</a></li>')
foot = re.search(r'  <footer>.*?</footer>\n', nav_tpl, re.S).group(0)
foot = foot.replace('<a href="lab.html">Lab</a>', '<a href="lab.html">Lab</a>\n          <a href="label.html">Label</a>')

N = len(REL)
CREDIT = '<a href="#r-obruni-antwi">Obruni Antwi</a>' if HAS_ARTIST else "Obruni Antwi"
DESC = f"4Spur Records: unabhängiges Label aus Berlin für Dub, Reggae, Hip-Hop, Electronic, Ambient und House. {N} Releases seit 2006, mit Covern von Obruni Antwi."
page = f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>4Spur Records – Label aus Berlin · Daniel Matysiak</title>
  <meta name="description" content="{DESC}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://danielmatysiak.de/label.html">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Daniel Matysiak">
  <meta property="og:title" content="4Spur Records – Label aus Berlin">
  <meta property="og:description" content="{DESC}">
  <meta property="og:url" content="https://danielmatysiak.de/label.html">
  <meta property="og:image" content="https://danielmatysiak.de/img/og_studio.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="de_DE">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://danielmatysiak.de/img/og_studio.jpg">
  <meta name="twitter:title" content="4Spur Records – Label aus Berlin">
  <meta name="twitter:description" content="{DESC}">
  <script type="application/ld+json">{LD}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Boogaloo&family=Barlow:wght@400;500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="favicon_studio_32.png">
  <link rel="icon" type="image/png" sizes="512x512" href="favicon_studio_512.png">
  <link rel="apple-touch-icon" href="favicon_studio_512.png">
  <link rel="stylesheet" href="styles.css">
</head>
<body class="page-label">

{head_nav}
  <main class="page">

    <section class="hero hero-deco">
      <p class="hero-kicker" data-en="03 — Label">03 — Label</p>
      <h1 data-en="4Spur<br>Records.">4Spur<br>Records.</h1>
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="lede" data-en="Independent label for dub, reggae, hip-hop, electronic, ambient and house music. Here you will find every release at a glance.">Unabhängiges Label für Dub, Reggae, Hip-Hop, Electronic, Ambient und House Music. Hier findest du alle Releases im Überblick.</p>
          <div class="cta-row">
            <button type="button" class="btn btn-menu" id="artist-btn" popovertarget="artist-menu" aria-haspopup="true" aria-expanded="false"><span data-en="Label artists">Label-Künstler</span><span class="caret" aria-hidden="true"></span></button>
            <a class="btn-ghost" href="kontakt.html"><span data-en="Contact">Kontakt</span></a>
          </div>
        </div>
        <aside class="hero-panel">
          <p class="hero-panel-label"><span>4Spur Records</span></p>
          <ul>
            <li><span data-en="Releases">Releases</span> <span>{N}+</span></li>
            <li><span data-en="Since">Seit</span> <span>2006</span></li>
            <li><span data-en="Distribution">Vertrieb</span> <span>The Orchard</span></li>
            <li><span data-en="Location">Standort</span> <span>Berlin / Worldwide</span></li>
          </ul>
        </aside>
      </div>
      <img class="hero-deco-img hero-deco-full" src="img/audio_neve.webp" alt="" aria-hidden="true">
    </section>

    <div id="artist-menu" popover class="artist-menu">
      <ul>
        <li><button type="button" data-artist="" data-en="All artists">Alle Künstler</button></li>
{menu_items}
      </ul>
    </div>

    <section class="artist-intro" id="artist-intro" aria-live="polite" hidden>
      <p class="eyebrow">Artist</p>
      <h2 class="artist-intro-name"></h2>
      <div class="artist-intro-body">
        <p class="artist-intro-text"></p>
        <button type="button" class="artist-intro-photo" aria-haspopup="dialog" hidden><img alt="" loading="lazy" decoding="async" width="900" height="675"></button>
      </div>
      <p class="artist-intro-meta"><span class="artist-intro-count"></span><a class="artist-intro-link" target="_blank" rel="noopener" hidden>Spotify ↗</a><button type="button" class="artist-intro-reset"></button></p>
    </section>

    <section class="section release-wall" id="archiv">
      <p class="eyebrow" data-en="Archive">Archiv</p>
      <p class="section-intro" data-en="{N}+ releases, newest first. Click a cover for details."><span class="release-count">{N}+</span> Releases, neueste zuerst. Klick auf ein Cover öffnet die Details.</p>
{wall}
      <p class="cover-credit"><span data-en="Cover Art by">Cover Art by</span> {CREDIT}</p>
    </section>

  </main>

  <nav class="year-nav" id="year-nav" aria-label="Jahre" data-no-swipe>
    <ul>
{year_nav}
    </ul>
  </nav>

  <dialog class="release-panel" id="release-panel" aria-labelledby="panel-title" data-no-swipe>
    <div class="panel-inner">
      <button type="button" class="panel-close" id="panel-close"><span aria-hidden="true">×</span><span class="visually-hidden" id="panel-close-label">Schließen</span></button>
      <div class="panel-body" id="panel-body"></div>
    </div>
  </dialog>

  <dialog class="lightbox" id="lightbox" aria-label="Cover groß" data-no-swipe>
    <button type="button" class="lightbox-close" id="lightbox-close" aria-label="Schließen"><span aria-hidden="true">×</span></button>
    <figure class="lightbox-fig">
      <span class="lightbox-art">
        <img id="lightbox-img" alt="" width="1440" height="1440">
      </span>
      <figcaption id="lightbox-cap"></figcaption>
    </figure>
  </dialog>

  <script type="application/json" id="release-data">{data_json}</script>
  <script type="application/json" id="artist-data">{artist_json}</script>

{foot}
  <script src="main.js"></script>
  <script src="label.js" defer></script>

</body>
</html>
'''
(SITE / "label.html").write_text(page)
(SITE / "label.js").write_text((ROOT / "label.js").read_text())

# ---- Nav/Footer in bestehenden Seiten
for f in ["index","leistungen","lab","about","faq","kontakt"]:
    p = SITE / f"{f}.html"; s = p.read_text()
    if 'label.html' in s: continue
    s = s.replace('<li><a href="lab.html">Lab</a></li>', '<li><a href="lab.html">Lab</a></li>\n        <li><a href="label.html">Label</a></li>')
    s = s.replace('<li><a href="lab.html" class="active">Lab</a></li>', '<li><a href="lab.html" class="active">Lab</a></li>\n        <li><a href="label.html">Label</a></li>')
    s = s.replace('          <a href="lab.html">Lab</a>\n', '          <a href="lab.html">Lab</a>\n          <a href="label.html">Label</a>\n')
    p.write_text(s)
def sub(f, a, b):
    p = SITE / f; s = p.read_text(); assert a in s, (f, a); p.write_text(s.replace(a, b))
sub("about.html", "03 — About", "04 — About")
# Rechtliches (Kontakt-Seite: Impressum + Datenschutz) an die Label-Seite anpassen
sub("kontakt.html", "Angaben gemäß § 5 TMG", "Angaben gemäß § 5 DDG")
sub("kontakt.html", """          <h3>Haftung für Inhalte</h3>""", """          <h3>Label</h3>
          <p>4Spur Records ist das Label von Daniel Matysiak (Anschrift wie oben). Der Vertrieb der Releases erfolgt über The Orchard.</p>
          <h3>Haftung für Inhalte</h3>""")
sub("kontakt.html", """          <p>Für Inhalte verlinkter externer Seiten bin ich nicht verantwortlich. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstöße erkennbar.</p>""", """          <p>Für Inhalte verlinkter externer Seiten bin ich nicht verantwortlich. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstöße erkennbar.</p>
          <h3>Urheberrecht und Bildnachweis</h3>
          <p>Die Cover der Releases auf der Label-Seite stammen von Obruni Antwi oder von Daniel Matysiak (Angabe jeweils beim Cover). Die Rechte an den Fotos der Artists liegen bei Daniel Matysiak; die Abgebildeten sind mit der Veröffentlichung einverstanden. Die Rechte an Musik und Covern liegen bei den jeweiligen Urheberinnen und Urhebern. Eine Nutzung über die Wiedergabe auf dieser Seite hinaus bedarf der Zustimmung.</p>""")
sub("kontakt.html", """Diese Website verwendet keine Cookies, kein Tracking und keine Analyse-Dienste. Es werden keine personenbezogenen Daten gespeichert, außer wenn du das Kontaktformular nutzt.</p>""", """Diese Website setzt selbst keine Cookies und verwendet kein Tracking und keine Analyse-Dienste. Es werden keine personenbezogenen Daten gespeichert, außer wenn du das Kontaktformular nutzt. Eine Ausnahme ist der optionale Spotify-Player auf der Label-Seite (siehe unten).</p>
          <h3>Hosting</h3>
          <p>Diese Website wird über GitHub Pages (GitHub Inc., USA) bereitgestellt. Beim Aufruf verarbeitet der Hosting-Anbieter technisch notwendige Verbindungsdaten, insbesondere deine IP-Adresse. Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO (sicherer und stabiler Betrieb der Website).</p>
          <h3>Lokale Speicherung im Browser</h3>
          <p>Die Seite speichert in deinem Browser (localStorage bzw. sessionStorage) ausschließlich technisch notwendige Einstellungen: deine Sprachwahl (Deutsch/Englisch) und die Richtung der Seitenübergänge. Diese Werte verlassen dein Gerät nicht. Rechtsgrundlage: § 25 Abs. 2 Nr. 2 TDDDG. Zusätzlich merkt sich die Label-Seite deine Zustimmung zum Spotify-Player (siehe unten).</p>
          <h3>Spotify-Player (Label-Seite)</h3>
          <p>Auf der Label-Seite kannst du in den Details eines Releases einen Player von Spotify (Spotify AB, Regeringsgatan 19, 111 53 Stockholm, Schweden) einblenden. Der Player wird erst geladen, wenn du auf „Anhören“ klickst. Erst dann wird eine Verbindung zu Spotify hergestellt, dabei werden unter anderem deine IP-Adresse und Geräteinformationen übertragen, und Spotify kann Cookies oder ähnliche Technologien auf deinem Gerät einsetzen. Auf die weitere Verarbeitung durch Spotify habe ich keinen Einfluss; es gilt die Datenschutzerklärung von Spotify. Rechtsgrundlage ist deine Einwilligung (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG), die du mit dem Klick erteilst. Damit du nicht jedes Mal neu zustimmen musst, wird die Zustimmung in deinem Browser gespeichert (Eintrag „4spur-spotify-player“ im localStorage); bei weiteren Releases erscheint der Player dann direkt. Du kannst die Einwilligung jederzeit widerrufen: im Detailfenster des Releases über „Spotify-Einwilligung widerrufen“ oder indem du die Website-Daten dieser Seite in deinem Browser löschst. Wer den Player nicht nutzen möchte, kann die Releases über die Links zu Spotify und Apple Music anhören.</p>
          <h3>Links zu Streaming-Plattformen und sozialen Netzwerken</h3>
          <p>Die Seite enthält Links zu Spotify, Apple Music, The Orchard (Promo-Seiten zum Hören ohne Anmeldung), SoundCloud, LinkedIn, X und weiteren Seiten. Beim bloßen Anzeigen der Links werden keine Daten an diese Anbieter übertragen. Erst wenn du einen Link anklickst, gelten die Datenschutzbestimmungen des jeweiligen Anbieters.</p>""")
sub("kontakt.html", """Du hast das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung. Kontakt: hallo@danielmatysiak.de</p>""", """Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch sowie das Recht, erteilte Einwilligungen mit Wirkung für die Zukunft zu widerrufen. Kontakt: hallo@danielmatysiak.de. Außerdem kannst du dich bei einer Datenschutz-Aufsichtsbehörde beschweren, zum Beispiel bei der Berliner Beauftragten für Datenschutz und Informationsfreiheit.</p>""")
# Über-mich-Seite: Labelarbeit erwähnen + Verweis aufs Label unten
sub("about.html", '            <p data-en="My tool is sound.',
    '            <p data-en="I have been making music for over 20 years and release it on my own label, 4Spur Records.">Seit über 20 Jahren mache ich Musik und veröffentliche sie auf meinem Label 4Spur Records.</p>\n            <p data-en="My tool is sound.')
sub("about.html", '<a class="btn-ghost" href="leistungen.html"><span data-en="Services & Pricing">Leistungen &amp; Preise</span></a>',
    '<a class="btn-ghost" href="leistungen.html"><span data-en="Services & Pricing">Leistungen &amp; Preise</span></a>\n        <a class="btn-ghost" href="label.html"><span data-en="To the label 4Spur Records">Zum Label 4Spur Records</span></a>')
sub("faq.html", "04 — FAQ", "05 — FAQ")
sub("kontakt.html", 'data-en="05 — Contact">05 — Kontakt', 'data-en="06 — Contact">06 — Kontakt')

# ---- Audio-Seite: Streaming-Widgets (Spotify, Audius, SoundCloud) entfernen, stattdessen Verweis aufs Label
_p = SITE / "leistungen.html"; _s = _p.read_text()
if 'class="releases-block"' in _s:
    _i = _s.index('<div class="releases-block">'); _j = _s.index("</section>", _i)
    _s = _s[:_i] + '''<p class="section-intro" data-en="Releases and studio productions are published on 4Spur Records, the independent label from Berlin. The full catalog is on the label page.">Veröffentlichungen und Studio-Produktionen erscheinen auf 4Spur Records, dem unabhängigen Label aus Berlin. Den ganzen Katalog findest du auf der Label-Seite.</p>
      <div class="cta-row">
        <a class="btn" href="label.html"><span data-en="To the label">Zum Label</span></a>
      </div>
    ''' + _s[_j:]
    _p.write_text(_s)

# ---- Startseite: Kapitelliste 01–06
s = (SITE / "index.html").read_text()
chap = re.search(r'(        <a class="chapter-item" href="about\.html">.*?)(?=      </nav>)', s, re.S).group(1)
new = chap
for old, n in (("05","06"),("04","05"),("03","04")):
    new = new.replace(f'<span class="chapter-num">{old}</span>', f'<span class="chapter-num">{n}</span>')
label = '''        <a class="chapter-item" href="label.html">
          <span class="chapter-num">03</span>
          <span class="chapter-title">Label</span>
          <span class="chapter-desc" data-en="4Spur Records · Releases">4Spur Records · Releases</span>
        </a>
'''
(SITE / "index.html").write_text(s.replace(chap, label + new))

# ---- main.js
s = (SITE / "main.js").read_text()
s = s.replace("'lab.html', 'about.html'", "'lab.html', 'label.html', 'about.html'")
_m = re.search(r"    'page-audio':   \[[^\n]*\],\n", s)
s = s.replace(_m.group(0), _m.group(0) + _m.group(0).replace("'page-audio':  ", "'page-label':  "), 1)
s = s.replace("if (key === 'page-audio') {", "if (key === 'page-audio' || key === 'page-label') {", 1)
s = s.replace("const parallaxPages = ['page-home', 'page-audio', 'page-lab'];", "const parallaxPages = ['page-home', 'page-audio', 'page-label', 'page-lab'];", 1)
s = s.replace("    'page-lab':     'lab.html',\n", "    'page-lab':     'lab.html',\n    'page-label':   'label.html',\n")
(SITE / "main.js").write_text(s)

# ---- CSS
s = (SITE / "styles.css").read_text()
s = s.replace("body.page-about {", "body.page-label {\n  --accent:    #4878b0;\n  --accent-h:  #5a8cc8;\n}\n\nbody.page-about {", 1)
s = s.replace(".chapter-item:nth-child(5) { animation-delay: 140ms; }",
              ".chapter-item:nth-child(5) { animation-delay: 140ms; }\n.chapter-item:nth-child(6) { animation-delay: 170ms; }")
old = re.search(r"  \.chapter-item:nth-child\(3\):hover,.*?#7a4b90; \}\n", s, re.S).group(0)
newhov = '''  .chapter-item:nth-child(3):hover,
  .chapter-item:nth-child(3):hover .chapter-title { color: #4878b0; }
  .chapter-item:nth-child(4):hover,
  .chapter-item:nth-child(4):hover .chapter-title { color: #7a9672; }
  .chapter-item:nth-child(5):hover,
  .chapter-item:nth-child(5):hover .chapter-title { color: #9898cc; }
  .chapter-item:nth-child(6):hover,
  .chapter-item:nth-child(6):hover .chapter-title { color: #7a4b90; }
'''
s = s.replace(old, newhov)
s += "\n" + (ROOT / "label.css").read_text()
(SITE / "styles.css").write_text(s)

# ---- Sitemap / llms.txt
s = (SITE / "sitemap.xml").read_text()
s = s.replace('  <url><loc>https://danielmatysiak.de/about.html', '  <url><loc>https://danielmatysiak.de/label.html</loc><priority>0.7</priority></url>\n  <url><loc>https://danielmatysiak.de/about.html')
(SITE / "sitemap.xml").write_text(s)
s = (SITE / "llms.txt").read_text()
_names = collections.Counter()
for _r in REL:
    for _n in _r["artist"].split(","): _names[_n.strip()] += 1
_seen = {}; 
for _n, _c in _names.most_common():
    _seen.setdefault(re.sub(r"[^a-z0-9]", "", _n.lower()), _n)
ARTISTS = ", ".join(sorted(_seen.values(), key=str.lower))
add = (f"\n## Label: 4Spur Records\n\n"
       f"4Spur Records ist ein unabhängiges Label für Dub, Reggae, Hip-Hop, Electronic, Ambient und House Music. Standort: Berlin / Worldwide. Vertrieb: The Orchard. "
       f"Der Katalog umfasst {N}+ Releases seit 2006 (Singles, EPs, Alben), chronologisch sortiert, mit Spotify-Player und Links zu Spotify und Apple Music.\n\n"
       f"Künstler im Katalog: {ARTISTS}.\n\n"
       f"Die Cover stammen von Obruni Antwi, freier Künstlerin aus Berlin (geboren in Schwerin, Mitglied im VbK Berlin, Laufbahn als Textildesignerin in der DDR). Die Bilder entstanden 2011 bis 2014 mit Microsoft Paint.\n\n"
       f"Katalog: https://danielmatysiak.de/label.html\n")
if "4Spur" not in s:
    s = s.replace("\n## FAQ (Kurzfassung)", add + "\n## FAQ (Kurzfassung)", 1)
s = s.replace("- [About](https://danielmatysiak.de/about.html)", "- [Label: 4Spur Records](https://danielmatysiak.de/label.html)\n- [About](https://danielmatysiak.de/about.html)", 1)
(SITE / "llms.txt").write_text(s)
# ---- Reihenfolge: Audio, Label, About, Lab, FAQ, Kontakt (Menü, Footer, Startseite, Wischreihenfolge, Kapitelnummern)
_NAV = re.compile(r'(?P<lab><li><a href="lab\.html"(?: class="active")?>Lab</a></li>)\s*(?P<label><li><a href="label\.html"(?: class="active")?>Label</a></li>)\s*(?P<about><li><a href="about\.html"(?: class="active")?>About</a></li>)')
_FOOT = re.compile(r'(?P<lab><a href="lab\.html">Lab</a>)(?P<w1>\s*)(?P<label><a href="label\.html">Label</a>)(?P<w2>\s*)(?P<about><a href="about\.html">About</a>)')
for _p in SITE.glob("*.html"):
    _t = _p.read_text()
    _t = _NAV.sub(lambda m: m["label"] + "\n        " + m["about"] + "\n        " + m["lab"], _t)
    _t = _FOOT.sub(lambda m: m["label"] + m["w1"] + m["about"] + m["w2"] + m["lab"], _t)
    _p.write_text(_t)
sub("label.html", '<p class="hero-kicker" data-en="03 — Label">03 — Label</p>', '<p class="hero-kicker" data-en="02 — Label">02 — Label</p>')
sub("about.html", "04 — About", "03 — About")
sub("lab.html", "02 — Collective Sound Lab", "04 — Collective Sound Lab")
_i = (SITE / "index.html").read_text()
_blocks = re.findall(r'        <a class="chapter-item" href="[a-z]+\.html">.*?</a>\n', _i, re.S)
_by = {re.search(r'href="([a-z]+)\.html"', b).group(1): b for b in _blocks}
_order = ["leistungen", "label", "about", "lab", "faq", "kontakt"]
assert set(_order) == set(_by), _by.keys()
_new = "".join(re.sub(r'(<span class="chapter-num">)\d\d', lambda m, n=n: m[1] + f"{n:02d}", _by[k]) for n, k in enumerate(_order, 1))
_i = _i.replace("".join(_blocks), _new)
(SITE / "index.html").write_text(_i)
_m = (SITE / "main.js").read_text()
_m = _m.replace("'leistungen.html', 'lab.html', 'label.html', 'about.html', 'faq.html'", "'leistungen.html', 'label.html', 'about.html', 'lab.html', 'faq.html'", 1)
(SITE / "main.js").write_text(_m)

print("ok", N, "releases,", len(by_year), "Jahre")
