# label-build: Generator der Label-Seite (label.html)

`label.html`, `label.js` und die Label-Teile in `styles.css`, `main.js`, `sitemap.xml`, `llms.txt` und den Menüs
werden aus diesen Dateien erzeugt. Nicht von Hand bearbeiten, sondern hier ändern und neu bauen.

## Daten
- `data/4spur-release-register.json`: Release-Register aus dem Orchard-Export (Titel, Artist, Datum, Format, UPC).
- `data/release-extras.json`: Redaktionelles je `product_id`: `links` (spotify, apple, ...), `description` / `description_en`,
  `highlight` (true/false), `hidden` (true blendet ein Release aus), `tracks`, `credits`.
- `assets/`: Quelle für die Künstlerkachel (Obruni Antwi).

## Neu bauen
Der Generator ist nicht wiederholbar: er braucht eine frische Kopie von `main` (ohne Label-Änderungen).

```bash
mkdir /tmp/site && git archive main | tar -x -C /tmp/site
python3 label-build/build_label.py /tmp/site
```

Ergebnis in `/tmp/site`, von dort die geänderten Dateien in den Branch kopieren.

## Cover
`python3 label-build/tools/make_covers.py <ordner_mit_masters> /tmp/site/img/covers`
Dateinamen der Masters: `<product_id>.jpg` (quadratisch). Ohne Cover erscheinen neutrale Platzhalter.

## Spotify-Links
`SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET="$(pbpaste)" python3 label-build/tools/fetch_links.py spotify`
Apple-Music-Links: `python3 label-build/tools/fetch_links.py apple` (ohne Zugangsdaten). Bereits eingetragene Links bleiben unberührt.
