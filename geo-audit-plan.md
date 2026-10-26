# GEO-Audit & KI-Sichtbarkeit – danielmatysiak.de

Stand: 19.06.2026

## Status quo

- robots.txt: offen für alle Crawler (`Allow: /`), kein Block für GPTBot, ClaudeBot, PerplexityBot oder Google-Extended.
- sitemap.xml: vorhanden, korrekt verlinkt, alle Hauptseiten erfasst.
- Content: statisches HTML, kein JS-Rendering nötig. main.js macht nur optische Effekte (Hero-Bilder, Parallax). KI-Crawler sehen den vollen Text ohne JS auszuführen.
- Structured Data (schema.org): schon vorhanden auf index.html, about.html, lab.html, leistungen.html, kontakt.html. Typen: Person, LocalBusiness, ProfessionalService, EducationalOrganization, PostalAddress, OpeningHoursSpecification.

Fazit: technische Basis ist gut. Kein Quatsch-Workaround nötig, nur zwei konkrete Lücken.

## Lücken

1. **Keine llms.txt.** Das Klartext-Infoblatt für LLMs fehlt komplett.
2. **faq.html ohne Schema-Markup.** Einzige Seite ohne structured data, dabei wäre FAQPage hier am wertvollsten.

## Maßnahmen

### 1. llms.txt erstellen
Inhalt: wer Daniel ist, Leistungen, Standort Berlin, Kontakt, Linkliste zu den Unterseiten (Leistungen, Lab, About, FAQ, Kontakt). Liegt im Root, analog zu robots.txt.

Aufwand: ca. 10 Minuten.

### 2. FAQPage Schema in faq.html
JSON-LD mit den bestehenden Frage/Antwort-Paaren aus dem FAQ-Content. Macht jede Antwort einzeln maschinenlesbar.

Aufwand: ca. 15–20 Minuten, Content ist schon da.

### 3. Social-Profile-Konsistenz (separat besprochen)
Bio-Links bei Insta, TikTok, SoundCloud auf denselben Link setzen. Bringt vor allem echten Traffic, nicht direkt Ranking (meist nofollow), hilft aber beim Auffinden und Crawlen der Seite.

Aufwand: ca. 5 Minuten pro Plattform.

## Bewusst nicht tun

- Eigene Review-Domain (z. B. "danielmatysiakreviews.com"). Kein echter Mehrwert, Risiko als Site-Reputation-Abuse eingestuft zu werden.
- Massenhaft Backlinks/Verzeichniseinträge. Risiko Linkschema-Penalty bei Google. Qualität und Relevanz schlagen Masse.

## Reihenfolge

1. llms.txt (sofort, quick win)
2. FAQPage Schema (sofort, quick win)
3. Social Bio-Links checken (sofort, quick win)

Alle drei Punkte sind unter 30 Minuten Gesamtaufwand und können sofort umgesetzt werden.
