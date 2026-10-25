#!/usr/bin/env python3
"""Entfernt den Spotify-Link aus dem Footer (footer-socials) in allen HTML-Seiten eines Ordners. Idempotent.
Aufruf: python3 tools/strip_footer_spotify.py <ordner>"""
import re, sys, pathlib
n = 0
for p in pathlib.Path(sys.argv[1]).glob("*.html"):
    s = p.read_text()
    t = re.sub(r'(<div class="footer-socials">.*?)\n[ \t]*<a href="https://open\.spotify\.com/[^"]*"[^>]*>Spotify</a>', r'\1', s, flags=re.S)
    if t != s: p.write_text(t); n += 1
print("Spotify-Link im Footer entfernt in", n, "Seiten")
