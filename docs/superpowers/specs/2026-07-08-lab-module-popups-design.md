# Lab-Modul-Popups — Design

## Ziel

Auf `lab.html` bekommt jede der 9 Modul-Karten (`.lab-module`) einen Button, der vertiefende Informationen zum Format in einem Popup öffnet. Inhalt stammt aus den bestehenden Flyer-Texten im Obsidian-Vault (`02_Projekte/Website/Collective Sound Lab/`). Keine Bilder in v1. Deutsch only in v1 (siehe Scope).

## Scope

- Alle 9 Module werden umgesetzt (Content liegt für alle vollständig vor, Mehraufwand pro Modul ist minimal sobald das Grundmuster steht).
- Popups sind vorerst nur auf Deutsch. Die Seite ist sonst komplett zweisprachig (`data-en`-Attribute), aber die Vault-Texte existieren nur auf Deutsch. Im EN-Modus wird vorerst der deutsche Text angezeigt. Übersetzung ist ein separater, späterer Task.
- Keine Bilder in den Popups.

## Karten-Änderung

`.lab-module` wird zu `display: flex; flex-direction: column;`. Am Ende jeder Karte, nach dem Beschreibungstext, kommt eine neue Zeile:

```html
<div class="lab-module-more">
  <button class="lab-more-btn" data-dialog="dlg-klangkoffer" type="button">Mehr erfahren →</button>
</div>
```

`.lab-module-more` bekommt `margin-top: auto`, damit der Button unabhängig von der Textlänge der Nachbarkarten in derselben Grid-Zeile immer unten sitzt (linksbündig, eigene Zeile — wie vom Nutzer gefordert).

Button-Stil: neue, schlanke Klasse `.lab-more-btn` (Mono, klein, Akzentfarbe, Pfeil-Suffix, kein Hintergrund/Rahmen) — bewusst *nicht* `.btn`/`.btn-ghost` (44px hoch, zu wuchtig in einem 9er-Grid).

## Dialog-Struktur

Alle 9 `<dialog class="lab-dialog" id="dlg-*">`-Elemente liegen als Geschwister direkt nach `.lab-modules`, vor `.modules-cta`.

Grundgerüst (Beispiel Klangkoffer mobil, einfaches Modul ohne Tabs):

```html
<dialog class="lab-dialog" id="dlg-klangkoffer">
  <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen">×</button></form>
  <p class="lab-dialog-tag">Mobil &amp; niedrigschwellig</p>
  <h4>Klangkoffer mobil</h4>
  <p class="lab-dialog-lede">Alles kann ein Instrument sein.</p>

  <p>{Idee-Text}</p>
  <h5>Arbeitsweise</h5>
  <ul>{5 Punkte}</ul>
  <h5>Modul-Optionen</h5>
  <table>{3 Zeilen}</table>
  <h5>Fokus &amp; Nutzen</h5>
  <ul>{5 Punkte}</ul>
  <p class="lab-dialog-note">{Individuell anpassbar}</p>

  <div class="lab-dialog-cta">
    <a class="btn" href="kontakt.html">Projekt anfragen</a>
  </div>
</dialog>
```

Bei den 3 Dual-Modulen (Stadt hören, Podcast-Studio-Tag, Stimmen der Stadt) kommt zwischen Lede und Idee-Text ein Tab-Umschalter, der zwei komplette Content-Blöcke zeigt/versteckt:

```html
<div class="lab-dialog-tabs" role="tablist">
  <button class="lab-tab is-active" data-panel="schulen" type="button">Schulen</button>
  <button class="lab-tab" data-panel="traeger" type="button">Träger</button>
</div>
<div class="lab-dialog-panel" data-panel="schulen">{voller Block wie oben, Schulen-Text}</div>
<div class="lab-dialog-panel" data-panel="traeger" hidden>{voller Block, Träger-Text}</div>
```

Die CTA-Zeile liegt außerhalb der Panels (einmal pro Dialog, unabhängig vom aktiven Tab).

## Content-Mapping

| Karte (lab.html) | Quelle(n) im Vault |
|---|---|
| Klangkoffer mobil | `01_Schulen/S5 Klangkoffer Mobil.md` (nur Schulen) |
| Stadt hören | **Tabs:** `01_Schulen/S1 Soundwalk Lab.md` / `02_Träger/T2 Soundwalk Lab.md` |
| Hörspielwerkstatt | `01_Schulen/S2 Hörspiel Werkstatt.md` (nur Schulen) |
| Podcast-Studio-Tag | **Tabs:** `01_Schulen/S3 Podcast Studio Day.md` / `02_Träger/T3 Podcast Studio Day.md` |
| Text & Beat Studio | `01_Schulen/S4 Beat and Bars Lab.md` (nur Schulen) |
| Stimmen der Stadt | **Tabs:** `01_Schulen/S6 Voices of the City.md` / `02_Träger/T1 Voices of the City.md` |
| Erinnerungsarchiv | `02_Träger/T4 Memory Archive.md` (nur Träger) |
| Team-Audio-Session | `02_Träger/T5 Team Frequency.md` (nur Träger) |
| Klang für Raum und Ausstellung | `02_Träger/T6 Exhibition Sound Layer.md` (nur Träger) |

Feld-Mapping pro Quelle:

- „DIE IDEE" / „DAS FORMAT" → Idee-Absatz
- „ARBEITSWEISE" → Bullet-Liste
- „MODULOPTIONEN" / „BUCHUNGSOPTIONEN" → Tabelle (3 Zeilen, unverändert übernommen)
- „PÄDAGOGISCHER FOKUS" / „WIRKUNG UND ZIELE" → Bullet-Liste unter der einheitlichen Popup-Überschrift „Fokus & Nutzen" (Rubrik-Name vereinheitlicht, Inhalt unverändert aus der jeweiligen Quelldatei — bei Dual-Modulen hat jeder Tab seine eigenen 5 Punkte, keine Vermischung zwischen Schulen/Träger)
- „INDIVIDUELL ANPASSBAR" / „INDIVIDUELL KONZIPIERT" → Notiz-Absatz am Ende
- „TITEL" / „SUBLINE" aus den Flyern werden **nicht** als Dialog-Überschrift verwendet — die Dialog-Überschrift ist der bestehende Kartenname (z. B. „Klangkoffer mobil"). Die Flyer-Subline (z. B. „Alles kann ein Instrument sein.") wird als kursive Lede direkt unter dem Titel übernommen.

**Umlaut-Konvention:** `h4` läuft sitehweit über die AHDN-Schriftart, die keine Umlaute unterstützt (bereits sichtbar bei „Klang fuer Raum und Ausstellung"). Dialog-Titel folgen dieser Konvention (z. B. „Stadt hoeren"). Fließtext/Listen nutzen normale Umlaute (Barlow-Font unterstützt sie).

**Farben:** Die modul-individuellen Pastellfarben aus `00_Index.md` sind für Print-Flyer gedacht, nicht für die Website. Die Popups nutzen den bestehenden Lab-Seitenakzent (Orange), keine 9 verschiedenen Farbschemata.

## Styling

- Dialog-Fläche: `var(--bg)` (Crème, deckend), `max-width: 560px`, `max-height: 85vh`, `overflow-y: auto`, `border-radius: 0` (konsistent mit dem kantenscharfen Rest der Seite)
- `::backdrop`: `rgba(28,25,16,0.55)` abgetönt + leichter Blur
- Einblenden: kurze fadeUp-Animation (6px translateY + opacity), gleiche Easing-Kurve wie bestehende Hero-Reveals
- Typografie: `.lab-dialog-tag` wie `.lab-module-tag` (Mono/uppercase/klein), `h4` in AHDN, Lede kursiv wie `.lede`, Fließtext/Listen in Barlow
- Tabs: zwei kleine Mono-Buttons nebeneinander, aktiver Tab in Akzentfarbe mit Unterstrich, inaktiver in `--muted`
- Schließen: „×" oben rechts über natives `<form method="dialog">`, kein JS nötig

## JavaScript (main.js)

Neuer Block, nur aktiv wenn `document.body.classList.contains('page-lab')`:

- **Öffnen:** Click auf `.lab-more-btn` → `document.getElementById(btn.dataset.dialog).showModal()`
- **Schließen per Backdrop-Klick:** Click-Listener auf jedem `<dialog>`; wenn `event.target === dialog` (Klick außerhalb der Inhaltsbox), `.close()`. ESC und ×-Button funktionieren nativ.
- **Tabs:** Click auf `.lab-tab` togglet `is-active` unter Geschwister-Buttons und `hidden` auf dem passenden `.lab-dialog-panel`. Kein Reset des Tab-Zustands beim erneuten Öffnen (bleibt beim zuletzt gewählten Tab).

Kein zusätzliches Framework/Dependency.

## Testplan

Manueller Browser-Test (statischer Server, kein Build-Schritt):

- Alle 9 Buttons öffnen den richtigen Dialog mit korrektem Inhalt
- Tab-Umschalten bei den 3 Dual-Modulen zeigt jeweils den richtigen Text
- Schließen über ×-Button, ESC und Backdrop-Klick funktioniert
- CTA-Button verlinkt korrekt auf `kontakt.html`
- Karten-Grid bleibt bei 3/2/1 Spalten (Desktop/Tablet/Mobile) intakt, Button sitzt zeilenweise auf gleicher Höhe
- Bestehender Hover-/Tap-Highlight-Effekt der Karten wird nicht gestört
- Kurzer Mobile-/Touch-Check

## Bewusst nicht in v1

- Keine Bilder in den Popups
- Keine englische Übersetzung der Popup-Inhalte
- Keine Query-Param-Vorbefüllung des Kontaktformulars mit dem Modulnamen
