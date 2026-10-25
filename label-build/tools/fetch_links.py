#!/usr/bin/env python3
"""Holt Streaming-Links über die UPC aus dem Register und schreibt sie in data/release-extras.json (links.apple / links.spotify).
Bereits von Hand eingetragene Links werden nie überschrieben. Titel werden gegengeprüft und Abweichungen gemeldet.

  Apple Music:  braucht keinen Zugang (öffentliche iTunes-Lookup-API).
  Spotify:      SPOTIFY_CLIENT_ID und SPOTIFY_CLIENT_SECRET als Umgebungsvariablen setzen
                (kostenlose App auf developer.spotify.com/dashboard anlegen), dann:
                SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET=... python3 tools/fetch_links.py spotify
Aufruf:  python3 tools/fetch_links.py apple|spotify|all"""
import base64, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "data/4spur-release-register.json"); EXT = os.path.join(ROOT, "data/release-extras.json")
reg = json.load(open(REG)); ext = json.load(open(EXT)); ext.setdefault("releases", {})
mode = sys.argv[1] if len(sys.argv) > 1 else "all"
norm = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())
def get(url, headers=None, data=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
def apple(upc):
    j = get("https://itunes.apple.com/lookup?" + urllib.parse.urlencode({"upc": upc, "entity": "album", "country": "de"}))
    a = next((x for x in j.get("results", []) if x.get("collectionViewUrl")), None)
    return (a["collectionViewUrl"].split("?")[0], a.get("collectionName", "")) if a else (None, "")
token = None
def spotify(upc):
    global token
    if not token:
        cid, sec = (os.environ.get("SPOTIFY_CLIENT_ID") or "").strip(), (os.environ.get("SPOTIFY_CLIENT_SECRET") or "").strip()
        if not (cid and sec): sys.exit("SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET fehlen")
        b = base64.b64encode(f"{cid}:{sec}".encode()).decode()
        try:
            token = get("https://accounts.spotify.com/api/token", {"Authorization": "Basic " + b, "Content-Type": "application/x-www-form-urlencoded"}, b"grant_type=client_credentials")["access_token"]
        except urllib.error.HTTPError as e:
            sys.exit(f"Anmeldung bei Spotify fehlgeschlagen (HTTP {e.code}): {e.read().decode()[:300]}\n-> Client ID/Secret prüfen (Secret in den App-Einstellungen unter 'View client secret', ohne Leerzeichen).")
    for _ in range(5):                      # bei Rate-Limit (429) kurz warten und erneut versuchen
        try:
            j = get("https://api.spotify.com/v1/search?" + urllib.parse.urlencode({"q": f"upc:{upc}", "type": "album", "limit": 1, "market": "DE"}), {"Authorization": "Bearer " + token})
            break
        except urllib.error.HTTPError as e:
            if e.code != 429: sys.exit(f"Spotify-Suche fehlgeschlagen (HTTP {e.code}) bei UPC {upc}: {e.read().decode()[:300]}")
            time.sleep(int(e.headers.get("Retry-After", "3")) + 1)
    else: return (None, "")
    it = j.get("albums", {}).get("items", [])
    return (it[0]["external_urls"]["spotify"], it[0]["name"]) if it else (None, "")
found = miss = warn = 0
for r in reg["releases"]:
    if r["label"] != "4Spur Records" or not r.get("upc"): continue
    links = ext["releases"].setdefault(r["product_id"], {}).setdefault("links", {})
    for key, fn in (("apple", apple), ("spotify", spotify)):
        if mode not in ("all", key) or links.get(key): continue
        try: url, name = fn(r["upc"])
        except Exception as e: print(f"FEHLER {key} {r['title']}: {e}"); continue
        if not url: miss += 1; print(f"kein Treffer {key:8} {r['title']}"); continue
        ok = norm(r["title"]) in norm(name) or norm(name) in norm(r["title"])
        links[key] = url; found += 1
        if not ok: warn += 1; print(f"PRÜFEN {key:8} Register: {r['title']!r}  Store: {name!r}")
        time.sleep(0.4)
    if not links: ext["releases"][r["product_id"]].pop("links")
json.dump(ext, open(EXT, "w"), ensure_ascii=False, indent=1)
print(f"{found} Links eingetragen, {miss} ohne Treffer, {warn} zu prüfen")
