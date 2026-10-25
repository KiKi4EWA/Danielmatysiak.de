#!/usr/bin/env python3
"""Erzeugt site/label.html aus der Release-Liste und patcht Nav/Footer/JS/CSS/Sitemap/llms.txt.
Idempotent: auf frischer Kopie des Repos ausführen. Release-Daten: Orchard-Export (57 Audio-Produkte)."""
import re, html, pathlib, collections

SITE = pathlib.Path(__file__).parent / "site"
from releases_data import R
LINKS = {}  # Orchard-ID -> URL (Spotify/Smartlink), sobald bekannt

FMT = {"Single": "Single", "EP": "EP", "Album": "Album"}
def tile(pid, t, artist, feat, date, fmt):
    y = date[:4]
    code = f"4SR-{y}-{pid}"
    meta = f'<span class="release-code">{code} · {fmt}</span>'
    art = html.escape(artist) + (f' <span class="release-feat">feat. {html.escape(feat)}</span>' if feat else "")
    inner = f'{meta}<span class="release-title">{html.escape(t)}</span><span class="release-artist">{art}</span>'
    url = LINKS.get(pid)
    if url:
        return f'<li><a class="release-tile" href="{url}" target="_blank" rel="noopener">{inner}</a></li>'
    return f'<li><div class="release-tile">{inner}</div></li>'

by_year = collections.defaultdict(list)
for r in R: by_year[int(r[4][:4])].append(r)
blocks = []
for y in sorted(by_year, reverse=True):
    items = "\n          ".join(tile(*r) for r in sorted(by_year[y], key=lambda r: r[4], reverse=True))
    blocks.append(f'''      <div class="release-year">
        <p class="section-label">{y}</p>
        <ul class="release-grid">
          {items}
        </ul>
      </div>''')

nav_tpl = (SITE / "about.html").read_text()
head_nav = re.search(r'  <nav class="site-nav">.*?</nav>\n', nav_tpl, re.S).group(0)
head_nav = head_nav.replace(' class="active"', '').replace('<li><a href="lab.html">Lab</a></li>',
    '<li><a href="lab.html">Lab</a></li>\n        <li><a href="label.html" class="active">Label</a></li>')
foot = re.search(r'  <footer>.*?</footer>\n', nav_tpl, re.S).group(0)
foot = foot.replace('<a href="lab.html">Lab</a>', '<a href="lab.html">Lab</a>\n          <a href="label.html">Label</a>')

DESC = "4Spur Records: unabhängiges Berliner Label seit 2006. Dub, Grime, Hip-Hop, Elektronik. 57 Releases von Kingali 030, Ete & Ali, The Afterhour, TrapHole und mehr."
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
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"Organization","name":"4Spur Records","description":"Unabhängiges Musiklabel aus Berlin.","url":"https://danielmatysiak.de/label.html","founder":{{"@type":"Person","name":"Daniel Matysiak","url":"https://danielmatysiak.de"}}}}</script>
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

    <section class="hero">
      <p class="hero-kicker" data-en="03 — Label">03 — Label</p>
      <h1 data-en="4Spur<br>Records.">4Spur<br>Records.</h1>
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="lede" data-en="Independent label from Berlin. Dub, grime, hip-hop and electronic music, released since 2006. Recorded, mixed and mastered in the studio, no corporate detour.">Unabhängiges Label aus Berlin. Dub, Grime, Hip-Hop und Elektronik, veröffentlicht seit 2006. Im Studio aufgenommen, gemischt und gemastert, ohne Konzernumweg.</p>
        </div>
      </div>
    </section>

    <section class="section">
      <p class="eyebrow" data-en="Catalog">Katalog</p>
      <p class="section-intro" data-en="57 releases, sorted by original release year. Distribution via The Orchard."><span class="release-count">57</span> Releases, nach ursprünglichem Erscheinungsjahr sortiert. Vertrieb über The Orchard.</p>
{chr(10).join(blocks)}
    </section>

    <section class="section">
      <p class="section-label" data-en="Demos">Demos</p>
      <p class="section-intro" data-en="Making music that fits? Send a short message with a link to your tracks. No attachments, no mass mailings.">Du machst Musik, die passt? Schick eine kurze Nachricht mit Link zu deinen Tracks. Keine Anhänge, keine Massenmails.</p>
      <div class="cta-row">
        <a class="btn" href="kontakt.html"><span data-en="Send a demo">Demo schicken</span></a>
        <a class="btn-ghost" href="leistungen.html"><span data-en="Studio services">Studio-Leistungen</span></a>
      </div>
    </section>

  </main>

{foot}
  <script src="main.js"></script>

</body>
</html>
'''
(SITE / "label.html").write_text(page)

# ---- Nav/Footer in bestehenden Seiten
for f in ["index","leistungen","lab","about","faq","kontakt"]:
    p = SITE / f"{f}.html"; s = p.read_text()
    if 'label.html' in s: continue
    s = s.replace('<li><a href="lab.html">Lab</a></li>', '<li><a href="lab.html">Lab</a></li>\n        <li><a href="label.html">Label</a></li>')
    s = s.replace('<li><a href="lab.html" class="active">Lab</a></li>', '<li><a href="lab.html" class="active">Lab</a></li>\n        <li><a href="label.html">Label</a></li>')
    s = s.replace('          <a href="lab.html">Lab</a>\n', '          <a href="lab.html">Lab</a>\n          <a href="label.html">Label</a>\n')
    p.write_text(s)
# Kicker neu nummerieren
def sub(f, a, b):
    p = SITE / f; s = p.read_text(); assert a in s, (f, a); p.write_text(s.replace(a, b))
sub("about.html", "03 — About", "04 — About")
sub("faq.html", "04 — FAQ", "05 — FAQ")
sub("kontakt.html", 'data-en="05 — Contact">05 — Kontakt', 'data-en="06 — Contact">06 — Kontakt')

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
s = s.replace(chap, label + new)
(SITE / "index.html").write_text(s)

# ---- main.js
s = (SITE / "main.js").read_text()
s = s.replace("'lab.html', 'about.html'", "'lab.html', 'label.html', 'about.html'")
s = s.replace("    'page-lab':     'lab.html',\n", "    'page-lab':     'lab.html',\n    'page-label':   'label.html',\n")
(SITE / "main.js").write_text(s)

# ---- CSS
s = (SITE / "styles.css").read_text()
s = s.replace("body.page-about {", "body.page-label {\n  --accent:    #a8402e;\n  --accent-h:  #bd5440;\n}\n\nbody.page-about {", 1)
s = s.replace(".chapter-item:nth-child(5) { animation-delay: 140ms; }",
              ".chapter-item:nth-child(5) { animation-delay: 140ms; }\n.chapter-item:nth-child(6) { animation-delay: 170ms; }")
old = re.search(r"  \.chapter-item:nth-child\(3\):hover,.*?#7a4b90; \}\n", s, re.S).group(0)
newhov = '''  .chapter-item:nth-child(3):hover,
  .chapter-item:nth-child(3):hover .chapter-title { color: #a8402e; }
  .chapter-item:nth-child(4):hover,
  .chapter-item:nth-child(4):hover .chapter-title { color: #7a9672; }
  .chapter-item:nth-child(5):hover,
  .chapter-item:nth-child(5):hover .chapter-title { color: #9898cc; }
  .chapter-item:nth-child(6):hover,
  .chapter-item:nth-child(6):hover .chapter-title { color: #7a4b90; }
'''
s = s.replace(old, newhov)
s += '''
/* ─── LABEL: RELEASE GRID ─────────────────────────── */
.release-year { margin-top: 2.5rem; }

.release-grid {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1px;
  margin-top: 1rem;
  background: var(--line);
  border: 1px solid var(--line);
  padding: 0;
}

.release-grid li { margin: 0; display: flex; }

.release-tile {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  width: 100%;
  min-height: 9rem;
  padding: 1rem 1.1rem;
  background: var(--bg);
  color: var(--text);
  text-decoration: none;
  transition: background 160ms var(--ease-out), color 160ms var(--ease-out);
}

a.release-tile:active { background: var(--bg-2); color: var(--accent); }

@media (hover: hover) and (pointer: fine) {
  a.release-tile:hover { background: var(--bg-2); color: var(--accent); }
}

.release-code {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--muted);
}

.release-title {
  font-family: var(--display);
  font-size: clamp(20px, 2.2vw, 26px);
  line-height: 1.1;
}

.release-artist {
  margin-top: auto;
  font-family: var(--mono);
  font-size: 10.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.release-count { color: var(--accent); font-weight: 500; }
.release-feat { text-transform: none; letter-spacing: 0.02em; }

@media (max-width: 600px) {
  .release-grid { grid-template-columns: 1fr 1fr; }
  .release-tile { min-height: 7.5rem; padding: 0.8rem; }
  .release-title { font-size: 19px; overflow-wrap: anywhere; }
}
'''
(SITE / "styles.css").write_text(s)

# ---- Sitemap / llms.txt
s = (SITE / "sitemap.xml").read_text()
s = s.replace('  <url><loc>https://danielmatysiak.de/about.html', '  <url><loc>https://danielmatysiak.de/label.html</loc><priority>0.7</priority></url>\n  <url><loc>https://danielmatysiak.de/about.html')
(SITE / "sitemap.xml").write_text(s)
s = (SITE / "llms.txt").read_text()
add = "\n## Label: 4Spur Records\n\nUnabhängiges Label aus Berlin, Releases seit 2006 (Dub, Grime, Hip-Hop, Elektronik). 57 Veröffentlichungen, Vertrieb über The Orchard. Katalog: https://danielmatysiak.de/label.html\n"
if "4Spur" not in s:
    s = s.replace("\n## FAQ (Kurzfassung)", add + "\n## FAQ (Kurzfassung)", 1)
(SITE / "llms.txt").write_text(s)
print("ok", len(R), "releases")
