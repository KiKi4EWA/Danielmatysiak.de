# Lab-Modul-Popups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Jede der 9 Modul-Karten auf `lab.html` bekommt einen Button, der ein natives `<dialog>`-Popup mit vertiefenden Infos aus dem Obsidian-Vault öffnet.

**Architecture:** Reines HTML/CSS/JS ohne Framework, passend zur bestehenden statischen Seite. Ein `<dialog>` pro Modul, alle als Geschwister nach `.lab-modules` im DOM. Ein Button pro Karte öffnet per `showModal()`. Die 3 Module mit Schulen/Träger-Varianten bekommen zusätzlich einen JS-Tab-Umschalter innerhalb ihres Dialogs.

**Tech Stack:** Vanilla HTML/CSS/JS, natives `<dialog>`-Element, kein Build-Schritt (statische Seite, deployed via GitHub Pages).

## Global Constraints

- Keine Bilder in den Popups (v1).
- Popups nur auf Deutsch, auch im EN-Toggle-Modus (v1) — siehe Design-Spec.
- `h4`-Titel ohne Umlaute (AHDN-Font-Limitierung), Fließtext/Listen mit normalen Umlauten.
- Popup-Akzentfarbe = bestehender Lab-Seitenakzent (`var(--accent)`, Orange), keine modul-individuellen Farben.
- Kein zusätzliches Framework/Dependency.
- Design-Referenz: `docs/superpowers/specs/2026-07-08-lab-module-popups-design.md`

---

### Task 1: CSS-Fundament + JS-Mechanik + erstes Modul (Klangkoffer mobil)

**Files:**
- Modify: `styles.css:1084-1089` (`.lab-module`-Regel), Einfügung nach `styles.css:1158` (nach `.lab-cta p`)
- Modify: `styles.css:406-408` (Accent-Tint-Selektorliste)
- Modify: `main.js` (Anhang nach Zeile 253)
- Modify: `lab.html:114-118` (erste Karte „Klangkoffer mobil"), Einfügung nach `lab.html:159` (nach `</div>` von `.lab-modules`, vor `.modules-cta`)

**Interfaces:**
- Produziert: CSS-Klassen `.lab-module-more`, `.lab-more-btn`, `.lab-dialog`, `.lab-dialog-tag`, `.lab-dialog-lede`, `.lab-dialog-close`, `.lab-dialog-cta`, `.lab-dialog-table`, `.lab-dialog h5`
- Produziert: JS-Verhalten — Click auf `.lab-more-btn[data-dialog]` öffnet `#<data-dialog-wert>` per `showModal()`; Click auf `<dialog>`-Fläche außerhalb der Inhaltsbox schließt den Dialog
- Konsumiert (Task 3): dieselben Klassen/Mechanik, erweitert um Tabs

- [ ] **Step 1: `.lab-module` zu Flex-Column machen**

In `styles.css` die bestehende Regel ersetzen:

```css
.lab-module {
  border-top: 1px solid var(--line);
  padding: 1.25rem 1.5rem 1.25rem 0;
  background: none;
  transition: border-color 180ms ease, background 180ms ease;
  display: flex;
  flex-direction: column;
}
```

- [ ] **Step 2: Neue CSS-Klassen einfügen**

In `styles.css` direkt nach dem Block `.lab-cta p { font-size: 15px; color: var(--muted); }` (vor dem Kommentar `/* ─── EDITORIAL LIST ──────────────────────────────── */`) einfügen:

```css
/* ─── LAB MODULE POPUPS ───────────────────────────── */
.lab-module-more {
  margin-top: auto;
  padding-top: 0.75rem;
}

.lab-more-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  padding: 0;
}

@media (hover: hover) and (pointer: fine) {
  .lab-more-btn:hover { text-decoration: underline; }
}

.lab-dialog {
  max-width: 560px;
  width: calc(100% - 2.5rem);
  max-height: 85vh;
  overflow-y: auto;
  padding: clamp(1.5rem, 4vw, 2.25rem);
  border: none;
  border-radius: 0;
  background: var(--bg);
  color: var(--text);
  opacity: 0;
  transform: translateY(6px);
}

.lab-dialog[open] {
  animation: fadeUp 280ms var(--ease-out) forwards;
}

.lab-dialog::backdrop {
  background: rgba(28, 25, 16, 0.55);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.lab-dialog-close {
  display: flex;
  justify-content: flex-end;
  margin: 0 0 0.5rem;
}

.lab-dialog-close button {
  background: none;
  border: none;
  font-size: 22px;
  line-height: 1;
  color: var(--muted);
  cursor: pointer;
  padding: 0.25rem;
}

@media (hover: hover) and (pointer: fine) {
  .lab-dialog-close button:hover { color: var(--accent); }
}

.lab-dialog-tag {
  font-family: var(--mono);
  font-size: 11.5px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.4rem;
}

.lab-dialog h4 {
  font-size: clamp(20px, 3vw, 26px);
  margin-bottom: 0.5rem;
}

.lab-dialog-lede {
  font-style: italic;
  color: var(--muted);
  font-size: 15px;
  margin: 0 0 1.25rem;
}

.lab-dialog h5 {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 1.25rem 0 0.5rem;
}

.lab-dialog p {
  font-size: 14.5px;
  color: var(--muted);
  line-height: 1.6;
}

.lab-dialog ul {
  margin: 0 0 1rem;
  padding-left: 1.1rem;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.6;
}

.lab-dialog ul li { margin-bottom: 0.35rem; }

.lab-dialog-note {
  font-style: italic;
  font-size: 13.5px;
}

.lab-dialog-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0 1.25rem;
}

.lab-dialog-table tr { border-top: 1px solid var(--line); }
.lab-dialog-table tr:first-child { border-top: none; }

.lab-dialog-table th,
.lab-dialog-table td {
  text-align: left;
  padding: 0.6rem 0;
  font-size: 14px;
  vertical-align: top;
  font-weight: 400;
}

.lab-dialog-table th {
  font-family: var(--mono);
  font-weight: 500;
  white-space: nowrap;
  padding-right: 1rem;
  color: var(--text);
}

.lab-dialog-table td { color: var(--muted); }

.lab-dialog-cta { margin-top: 1.5rem; }

.lab-dialog-tabs {
  display: flex;
  gap: 1.25rem;
  margin: 0.25rem 0 1.25rem;
  border-bottom: 1px solid var(--line);
}

.lab-tab {
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--mono);
  font-size: 11.5px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 0 0 0.6rem;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.lab-tab.is-active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
```

- [ ] **Step 3: Dialog-CTA in die Accent-Tint-Selektorliste aufnehmen**

In `styles.css` die bestehende Regel:

```css
.section .btn,
.section .btn-ghost,
form .btn {
  background: color-mix(in srgb, var(--accent) 12%, transparent);
}
```

ersetzen durch:

```css
.section .btn,
.section .btn-ghost,
form .btn,
.lab-dialog .btn {
  background: color-mix(in srgb, var(--accent) 12%, transparent);
}
```

Und die zugehörige Hover-Regel:

```css
@media (hover: hover) and (pointer: fine) {
  .section .btn:hover,
  form .btn:hover { background: color-mix(in srgb, var(--accent) 22%, transparent); }
  .section .btn-ghost:hover { background: color-mix(in srgb, var(--accent) 16%, transparent); }
}
```

ersetzen durch:

```css
@media (hover: hover) and (pointer: fine) {
  .section .btn:hover,
  form .btn:hover,
  .lab-dialog .btn:hover { background: color-mix(in srgb, var(--accent) 22%, transparent); }
  .section .btn-ghost:hover { background: color-mix(in srgb, var(--accent) 16%, transparent); }
}
```

- [ ] **Step 4: JS-Mechanik in `main.js` anhängen**

Am Ende von `main.js` (nach der bestehenden Mobile-Tap-Highlight-Logik, Zeile 253) anfügen:

```javascript

// Lab-Modul-Popups: Öffnen per Button, Schließen per Backdrop-Klick, Tabs umschalten
if (document.body.classList.contains('page-lab')) {
  document.querySelectorAll('.lab-more-btn').forEach(btn => {
    const dialog = document.getElementById(btn.dataset.dialog);
    if (!dialog) return;
    btn.addEventListener('click', () => dialog.showModal());
  });

  document.querySelectorAll('.lab-dialog').forEach(dialog => {
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) dialog.close();
    });

    dialog.querySelectorAll('.lab-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const target = tab.dataset.panel;
        dialog.querySelectorAll('.lab-tab').forEach(t => t.classList.toggle('is-active', t === tab));
        dialog.querySelectorAll('.lab-dialog-panel').forEach(p => {
          p.hidden = p.dataset.panel !== target;
        });
      });
    });
  });
}
```

- [ ] **Step 5: Button auf der Karte „Klangkoffer mobil" ergänzen**

In `lab.html` die bestehende erste Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Mobile & accessible">Mobil &amp; niedrigschwellig</p>
          <h4 data-en="Mobile Sound Kit">Klangkoffer mobil</h4>
          <p data-en="<strong>A ready-to-use audio format for primary school, all-day care, and open groups.</strong> A playful introduction to listening, recording, and creating together."><strong>Ein sofort einsetzbares Audio-Format für Grundschule, Ganztag und offene Gruppen.</strong> Ein spielerischer Einstieg in Hören, Aufnehmen und gemeinsames Gestalten.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Mobile & accessible">Mobil &amp; niedrigschwellig</p>
          <h4 data-en="Mobile Sound Kit">Klangkoffer mobil</h4>
          <p data-en="<strong>A ready-to-use audio format for primary school, all-day care, and open groups.</strong> A playful introduction to listening, recording, and creating together."><strong>Ein sofort einsetzbares Audio-Format für Grundschule, Ganztag und offene Gruppen.</strong> Ein spielerischer Einstieg in Hören, Aufnehmen und gemeinsames Gestalten.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-klangkoffer" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 6: Dialog für „Klangkoffer mobil" einfügen**

In `lab.html` direkt nach dem schließenden `</div>` von `.lab-modules` (Zeile 159, vor `<div class="modules-cta">`) einfügen:

```html
      <dialog class="lab-dialog" id="dlg-klangkoffer">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Mobil &amp; niedrigschwellig</p>
        <h4>Klangkoffer mobil</h4>
        <p class="lab-dialog-lede">Alles kann ein Instrument sein.</p>

        <p>Ein mobiles Setup aus Mikrofonen, kleinen Instrumenten und Geräuschobjekten kommt direkt in die Klasse. Gemeinsam erzeugen wir Klänge, sortieren sie, spielen mit Rhythmus und Stille – und bauen am Ende ein kleines gemeinsames Hörstück. Keine Vorkenntnisse. Nur Neugier.</p>

        <h5>Arbeitsweise</h5>
        <ul>
          <li>Mobiles Setup wird vollständig mitgebracht</li>
          <li>Klangerkundung in kleinen Gruppen</li>
          <li>Spiel mit Geräuschen, Rhythmus und Stille</li>
          <li>Einfaches Editing gemeinsam</li>
          <li>Ergebnis: Mini-Album oder kurzes Hörstück</li>
        </ul>

        <h5>Modul-Optionen</h5>
        <table class="lab-dialog-table">
          <tr><th>1 Projekttag</th><td>Entdecken → Aufnehmen → gemeinsames Hörstück</td></tr>
          <tr><th>2 Projekttage</th><td>Eigene Klangobjekte → Komposition → Präsentation</td></tr>
          <tr><th>Mehrteilig</th><td>Regelmäßige Klang-AG → wachsendes Archiv</td></tr>
        </table>

        <h5>Fokus &amp; Nutzen</h5>
        <ul>
          <li>Entdeckendes Lernen und Neugier fördern</li>
          <li>Konzentration und Zuhören stärken</li>
          <li>Rhythmusgefühl und Motorik</li>
          <li>Kreativität und Spielfreude</li>
          <li>Gemeinsames Produzieren als Erlebnis</li>
        </ul>

        <p class="lab-dialog-note">Geeignet für Grundschule, Kita und Familienzentren. Alter, Gruppengröße und Dauer werden abgestimmt. Auch als festes AG-Format oder Ferienprojekt buchbar.</p>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>
```

- [ ] **Step 7: Strukturprüfung per grep**

Run:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
comm -3 <(grep -o 'data-dialog="[^"]*"' lab.html | sed 's/data-dialog="//;s/"//' | sort -u) <(grep -o 'id="dlg-[^"]*"' lab.html | sed 's/id="//;s/"//' | sort -u)
```

Expected: keine Ausgabe (jeder Button hat genau einen passenden Dialog und umgekehrt).

- [ ] **Step 8: Manueller Browser-Test**

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de" && python3 -m http.server 8000
```

Im Browser `http://localhost:8000/lab.html` öffnen. Prüfen:
- Button „Mehr erfahren →" erscheint unten links auf der Karte „Klangkoffer mobil"
- Klick öffnet den Dialog mit dem vollständigen Inhalt
- Klick auf den abgedunkelten Hintergrund schließt den Dialog
- ESC schließt den Dialog
- Klick auf „×" schließt den Dialog
- „Projekt anfragen" verlinkt auf `kontakt.html`

Server danach mit `Ctrl+C` beenden.

- [ ] **Step 9: Commit**

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
git add styles.css main.js lab.html
git commit -m "Add lab module popup mechanism + first dialog (Klangkoffer mobil)"
```

---

### Task 2: Restliche 5 Einzel-Module (ohne Tabs)

**Files:**
- Modify: `lab.html` (5 Karten + 5 Dialoge)

**Interfaces:**
- Konsumiert: `.lab-more-btn`, `.lab-dialog`, `.lab-dialog-*`-Klassen und JS-Mechanik aus Task 1 (unverändert, keine neuen Selektoren)

- [ ] **Step 1: Button bei „Hörspielwerkstatt" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Language & Audio">Sprache &amp; Audio</p>
          <h4 data-en="Audio Drama Workshop">Hoerspielwerkstatt</h4>
          <p data-en="<strong>Write, speak, perform.</strong> From texts, roles, and sounds, a shared radio play or short audio scene is created."><strong>Schreiben, sprechen, inszenieren.</strong> Aus Texten, Rollen und Geräuschen entsteht ein gemeinsames Hörspiel oder eine kurze Audio-Szene.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Language & Audio">Sprache &amp; Audio</p>
          <h4 data-en="Audio Drama Workshop">Hoerspielwerkstatt</h4>
          <p data-en="<strong>Write, speak, perform.</strong> From texts, roles, and sounds, a shared radio play or short audio scene is created."><strong>Schreiben, sprechen, inszenieren.</strong> Aus Texten, Rollen und Geräuschen entsteht ein gemeinsames Hörspiel oder eine kurze Audio-Szene.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-hoerspiel" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 2: Button bei „Text & Beat Studio" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Text & Rhythm">Text &amp; Rhythmus</p>
          <h4 data-en="Text &amp; Beat Studio">Text &amp; Beat Studio</h4>
          <p data-en="<strong>Language meets rhythm.</strong> Texts, spoken word, rap, or short performances are recorded, shaped, and realised as a compact production."><strong>Sprache trifft Rhythmus.</strong> Texte, Spoken Word, Rap oder kurze Performances werden aufgenommen, geformt und als kompakte Produktion umgesetzt.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Text & Rhythm">Text &amp; Rhythmus</p>
          <h4 data-en="Text &amp; Beat Studio">Text &amp; Beat Studio</h4>
          <p data-en="<strong>Language meets rhythm.</strong> Texts, spoken word, rap, or short performances are recorded, shaped, and realised as a compact production."><strong>Sprache trifft Rhythmus.</strong> Texte, Spoken Word, Rap oder kurze Performances werden aufgenommen, geformt und als kompakte Produktion umgesetzt.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-beatbars" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 3: Button bei „Erinnerungsarchiv" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Memory">Erinnerung</p>
          <h4 data-en="Memory Archive">Erinnerungsarchiv</h4>
          <p data-en="<strong>Preserving conversations, making biographical traces audible.</strong> For intergenerational projects, local history, and documentary formats with a clear perspective."><strong>Gespräche festhalten, biografische Spuren hörbar machen.</strong> Für Generationenprojekte, lokale Geschichte und dokumentarische Formate mit Haltung.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Memory">Erinnerung</p>
          <h4 data-en="Memory Archive">Erinnerungsarchiv</h4>
          <p data-en="<strong>Preserving conversations, making biographical traces audible.</strong> For intergenerational projects, local history, and documentary formats with a clear perspective."><strong>Gespräche festhalten, biografische Spuren hörbar machen.</strong> Für Generationenprojekte, lokale Geschichte und dokumentarische Formate mit Haltung.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-memory" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 4: Button bei „Team-Audio-Session" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Team & Collaboration">Team &amp; Zusammenarbeit</p>
          <h4 data-en="Team Audio Session">Team-Audio-Session</h4>
          <p data-en="<strong>A shared audio format for groups, staff, or teams.</strong> Exchange, role clarification, and collaboration are translated into a concrete outcome."><strong>Ein gemeinsames Audio-Format für Gruppen, Kollegien oder Teams.</strong> Austausch, Rollenklärung und Zusammenarbeit werden in ein konkretes Ergebnis übersetzt.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Team & Collaboration">Team &amp; Zusammenarbeit</p>
          <h4 data-en="Team Audio Session">Team-Audio-Session</h4>
          <p data-en="<strong>A shared audio format for groups, staff, or teams.</strong> Exchange, role clarification, and collaboration are translated into a concrete outcome."><strong>Ein gemeinsames Audio-Format für Gruppen, Kollegien oder Teams.</strong> Austausch, Rollenklärung und Zusammenarbeit werden in ein konkretes Ergebnis übersetzt.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-team" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 5: Button bei „Klang für Raum und Ausstellung" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Exhibition & Space">Ausstellung &amp; Raum</p>
          <h4 data-en="Sound for Space and Exhibition">Klang fuer Raum und Ausstellung</h4>
          <p data-en="<strong>Audio for exhibitions, installations, or locations.</strong> Voices, textures, field recordings, or compositions are developed so that sound carries both spatially and conceptually."><strong>Audio für Ausstellung, Installation oder Ort.</strong> Stimmen, Flächen, Field Recordings oder Kompositionen werden so entwickelt, dass Klang räumlich und inhaltlich trägt.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Exhibition & Space">Ausstellung &amp; Raum</p>
          <h4 data-en="Sound for Space and Exhibition">Klang fuer Raum und Ausstellung</h4>
          <p data-en="<strong>Audio for exhibitions, installations, or locations.</strong> Voices, textures, field recordings, or compositions are developed so that sound carries both spatially and conceptually."><strong>Audio für Ausstellung, Installation oder Ort.</strong> Stimmen, Flächen, Field Recordings oder Kompositionen werden so entwickelt, dass Klang räumlich und inhaltlich trägt.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-exhibition" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 6: 5 Dialoge einfügen**

In `lab.html` nach dem Dialog `#dlg-klangkoffer` (aus Task 1), noch vor `<div class="modules-cta">`, einfügen:

```html
      <dialog class="lab-dialog" id="dlg-hoerspiel">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Sprache &amp; Audio</p>
        <h4>Hoerspielwerkstatt</h4>
        <p class="lab-dialog-lede">Aus Sprache wird eine Welt.</p>

        <p>Die Gruppe schreibt eigene Szenen, spricht Rollen, baut Geräuschkulissen und komponiert Musik. Aus einem leeren Blatt entsteht ein fertiges Hörspiel – mit Dramaturgie, Spannung, Stimme und Klang. Das Ergebnis gehört der Gruppe.</p>

        <h5>Arbeitsweise</h5>
        <ul>
          <li>Gruppen bis 6 Personen mit klar verteilten Rollen</li>
          <li>Textarbeit, Sprechproben und Recording im Wechsel</li>
          <li>Professionelle Aufnahmetechnik wird vollständig gestellt</li>
          <li>Schnitt, Mix und Abmischung inklusive</li>
          <li>Abschluss: fertiges Hörspiel zum Anhören und Zeigen</li>
        </ul>

        <h5>Modul-Optionen</h5>
        <table class="lab-dialog-table">
          <tr><th>1 Projekttag</th><td>Einführung → Szenenarbeit → Aufnahme → Demo</td></tr>
          <tr><th>2 Projekttage</th><td>Vollständiges Skript → Recording → Postproduktion</td></tr>
          <tr><th>3–5 Projekttage</th><td>Mehrteiliges Hörspiel → Aufführung oder Veröffentlichung</td></tr>
        </table>

        <h5>Fokus &amp; Nutzen</h5>
        <ul>
          <li>Sprache als Ausdrucksmittel bewusst einsetzen</li>
          <li>Kreatives Schreiben und Dramaturgie</li>
          <li>Stimme, Körper und Performance</li>
          <li>Teamarbeit und Rollenverantwortung</li>
          <li>Konzentration und Zuhören</li>
        </ul>

        <p class="lab-dialog-note">Das Thema kommt aus der Gruppe. Ob Fiktion, Geschichte oder Biografie – der Inhalt gehört der Klasse. Auch als MSA-Projekt oder fächerübergreifendes Format buchbar.</p>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>

      <dialog class="lab-dialog" id="dlg-beatbars">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Text &amp; Rhythmus</p>
        <h4>Text &amp; Beat Studio</h4>
        <p class="lab-dialog-lede">Rap ist Sprache. Und Sprache ist Macht.</p>

        <p>Jugendliche produzieren eigene Beats, schreiben Texte über ihr Leben und nehmen sie auf. Keine Vorkenntnisse nötig. Nur die Bereitschaft, etwas zu sagen. Am Ende steht ein echter Track – geschrieben, gesprochen und produziert von der Gruppe selbst.</p>

        <h5>Arbeitsweise</h5>
        <ul>
          <li>Beat-Produktion in der Gruppe</li>
          <li>Textarbeit zu persönlichen oder vorgegebenen Themen</li>
          <li>Recording und Performance-Coaching</li>
          <li>Jede Person findet ihre Rolle – Schreiben, Sprechen, Produzieren</li>
          <li>Abschluss: fertiger Track als Gruppenprodukt</li>
        </ul>

        <h5>Modul-Optionen</h5>
        <table class="lab-dialog-table">
          <tr><th>1 Projekttag</th><td>Einstieg Beat &amp; Text → Aufnahme → Demo-Track</td></tr>
          <tr><th>2–4 Termine</th><td>Vertiefung Textarbeit → Recording → fertiger Track</td></tr>
          <tr><th>5–8 Termine</th><td>Intensivprojekt → mehrere Tracks oder EP → Listening Session</td></tr>
        </table>

        <h5>Fokus &amp; Nutzen</h5>
        <ul>
          <li>Selbstwirksamkeit und Ausdrucksstärke entwickeln</li>
          <li>Sprache als Werkzeug bewusst einsetzen</li>
          <li>Rhythmusgefühl und Körperbewusstsein fördern</li>
          <li>Gruppenidentität und gegenseitigen Respekt stärken</li>
          <li>Audio als eigenes Medium erleben</li>
        </ul>

        <p class="lab-dialog-note">Das Format passt sich Alter und Gruppe an. Ob offene Themen oder konkrete Aufgaben – der Rahmen wird gemeinsam festgelegt. Auch als mehrteilige Reihe oder Abschluss-Event buchbar.</p>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>

      <dialog class="lab-dialog" id="dlg-memory">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Erinnerung</p>
        <h4>Erinnerungsarchiv</h4>
        <p class="lab-dialog-lede">Was nicht gesagt wird, geht verloren.</p>

        <p>Biografien, Erinnerungen und Zeitzeugenschaft werden aufgenommen, dokumentiert und archiviert. Strukturiert, würdevoll, mit klarer Einwilligung. Das Ergebnis ist ein Archiv – intern nutzbar, ausstellungsfähig oder als kuratierte Kurzfassung öffentlich einsetzbar.</p>

        <h5>Arbeitsweise</h5>
        <ul>
          <li>Freigaben und Einwilligungen werden vorab schriftlich geklärt</li>
          <li>Sensible Themen mit klarer Moderation</li>
          <li>Aufnahme in sicherer, ruhiger Umgebung</li>
          <li>Postproduktion: Schnitt, Mix, Archivformat</li>
          <li>Ergebnis: Archiv-Dateien + optional kuratierte Kurzfassung</li>
        </ul>

        <h5>Buchungsoptionen</h5>
        <table class="lab-dialog-table">
          <tr><th>1–2 Termine</th><td>Einführung → Aufnahmen → Archiv-Übergabe</td></tr>
          <tr><th>Mehrteilige Reihe</th><td>Mehrere Gespräche → kuratiertes Archiv</td></tr>
          <tr><th>Ausstellungsmodul</th><td>Klang-Stationen aus dem Archiv → raumfähige Ausgabe</td></tr>
        </table>

        <h5>Fokus &amp; Nutzen</h5>
        <ul>
          <li>Biografien und Geschichte dokumentieren</li>
          <li>Würde und Stimme der Beteiligten stärken</li>
          <li>Internes oder öffentliches Archiv aufbauen</li>
          <li>Dokumentierte, datenschutzkonforme Produktion</li>
          <li>Nutzbar für Ausstellung, Bericht oder Kommunikation</li>
        </ul>

        <p class="lab-dialog-note">Geeignet für Kultureinrichtungen, Ämter, Jugendhilfe und Träger. Auf Wunsch anonymisierte Fassungen möglich. Zielgruppe, Sensibilität und Nutzung werden vorab im Briefing geklärt.</p>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>

      <dialog class="lab-dialog" id="dlg-team">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Team &amp; Zusammenarbeit</p>
        <h4>Team-Audio-Session</h4>
        <p class="lab-dialog-lede">Kultur wird hörbar.</p>

        <p>Ein Audio-Format als Teamergebnis. Onboarding-Story, Team-Manifest, Werte in O-Ton, interne Mini-Serie. Die Gruppe produziert gemeinsam – mit klarer Rollenverteilung, professioneller Technik und einem Ergebnis, das intern oder öffentlich einsetzbar ist.</p>

        <h5>Arbeitsweise</h5>
        <ul>
          <li>Format-Entwicklung gemeinsam mit dem Team</li>
          <li>Klare Rollen: Sprechen, Aufnahme, Regie, Inhalt</li>
          <li>Professionelles Setup wird vollständig mitgebracht</li>
          <li>Postproduktion: Schnitt, Mix, Ausgabe</li>
          <li>Ergebnis: 1–3 Episoden oder ein fertiger Track</li>
        </ul>

        <h5>Buchungsoptionen</h5>
        <table class="lab-dialog-table">
          <tr><th>Workshop (4h)</th><td>Einführung → Format → Aufnahme → Demo</td></tr>
          <tr><th>Tagesprojekt (6h)</th><td>Vollständige Episode → abgemischt → übergeben</td></tr>
          <tr><th>Mehrteilige Reihe</th><td>Redaktion aufbauen → regelmäßiges internes Format</td></tr>
        </table>

        <h5>Fokus &amp; Nutzen</h5>
        <ul>
          <li>Teamzusammenhalt durch gemeinsames Produzieren stärken</li>
          <li>Unternehmenskultur hörbar und kommunizierbar machen</li>
          <li>Onboarding und interne Kommunikation verbessern</li>
          <li>Employer Branding mit echten Stimmen</li>
          <li>Professionelles, direkt nutzbares Ergebnis</li>
        </ul>

        <p class="lab-dialog-note">Das Format wird auf Ihre Organisation abgestimmt. Thema, Tonalität und Nutzung werden vorab vereinbart. Auch für CSR-Projekte oder externe Kommunikation geeignet.</p>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>

      <dialog class="lab-dialog" id="dlg-exhibition">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Ausstellung &amp; Raum</p>
        <h4>Klang fuer Raum und Ausstellung</h4>
        <p class="lab-dialog-lede">Was man hört, versteht man anders.</p>

        <p>Klang-Ebenen für Ausstellungsräume, Stationen oder Objekte. Field Recording, Voice Layer, Musik – alles klar abgemischt und raumfähig ausgegeben. Das Ergebnis orientiert, schafft Stimmung und macht Inhalte zugänglich. Für Ausstellungen, Installationen, Stadtteilprojekte oder Events.</p>

        <h5>Arbeitsweise</h5>
        <ul>
          <li>Briefing: Raum, Ziel, Stimmung, Zielgruppe</li>
          <li>Field Recording, Sprachaufnahmen oder Musik je nach Format</li>
          <li>Postproduktion: Mix, Mastering, Mehrkanal oder Stereo</li>
          <li>Ausgabe in passenden Formaten für Ihre Technik</li>
          <li>Optional: Vor-Ort-Installation und Einweisung</li>
        </ul>

        <h5>Buchungsoptionen</h5>
        <table class="lab-dialog-table">
          <tr><th>Einzelmodul</th><td>1 Klang-Station → Konzept → Produktion → Übergabe</td></tr>
          <tr><th>Mehrteilig</th><td>Mehrere Stationen → abgestimmte Klangwelt</td></tr>
          <tr><th>Event-Modul</th><td>Live-Aufnahme + Beschallung + Listening Session</td></tr>
        </table>

        <h5>Fokus &amp; Nutzen</h5>
        <ul>
          <li>Raumorientierung und Atmosphäre schaffen</li>
          <li>Inhalte akustisch zugänglich machen</li>
          <li>Audio-Barrierefreiheit ermöglichen</li>
          <li>Professionelle Klangqualität für Ausstellung oder Raum</li>
          <li>Nutzbar für Kultur, Quartier, Beteiligung und Prävention</li>
        </ul>

        <p class="lab-dialog-note">Jede Raumsituation ist anders. Format, Technik und Ausgabe werden vorab geklärt. Mehrkanal für komplexe Räume oder Stereo – je nach Bedarf und Budget.</p>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>
```

- [ ] **Step 7: Strukturprüfung per grep**

Run:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
comm -3 <(grep -o 'data-dialog="[^"]*"' lab.html | sed 's/data-dialog="//;s/"//' | sort -u) <(grep -o 'id="dlg-[^"]*"' lab.html | sed 's/id="//;s/"//' | sort -u)
```

Expected: keine Ausgabe.

- [ ] **Step 8: Manueller Browser-Test**

Wie Task 1 Step 8, für alle 5 neuen Module: Button erscheint, Dialog öffnet mit korrektem Inhalt, alle Schließen-Wege funktionieren.

- [ ] **Step 9: Commit**

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
git add lab.html
git commit -m "Add remaining 5 single-audience lab module popups"
```

---

### Task 3: Tab-Mechanik + erstes Dual-Modul (Stadt hören)

**Files:**
- Modify: `lab.html:119-123` (Karte „Stadt hören"), Einfügung eines neuen Dialogs

**Interfaces:**
- Konsumiert: JS-Tab-Handler aus Task 1 Step 4 (bereits generisch für `.lab-tab`/`.lab-dialog-panel`, keine Änderung nötig)
- Produziert: `.lab-dialog-panel[data-panel]`-Markup-Muster für Task 4

- [ ] **Step 1: Button bei „Stadt hören" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Perception">Wahrnehmung</p>
          <h4 data-en="Listen to the City">Stadt hoeren</h4>
          <p data-en="<strong>Sound walk, field recording, listening map.</strong> A group explores a location through sounds, voices, and atmospheres and develops their own audio piece from it."><strong>Soundwalk, Feldaufnahme, Hörkarte.</strong> Eine Gruppe erkundet einen Ort über Geräusche, Stimmen und Atmosphären und entwickelt daraus ein eigenes Hörstück.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="Perception">Wahrnehmung</p>
          <h4 data-en="Listen to the City">Stadt hoeren</h4>
          <p data-en="<strong>Sound walk, field recording, listening map.</strong> A group explores a location through sounds, voices, and atmospheres and develops their own audio piece from it."><strong>Soundwalk, Feldaufnahme, Hörkarte.</strong> Eine Gruppe erkundet einen Ort über Geräusche, Stimmen und Atmosphären und entwickelt daraus ein eigenes Hörstück.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-soundwalk" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 2: Dialog mit Tabs einfügen**

In `lab.html` nach dem Dialog `#dlg-exhibition` einfügen:

```html
      <dialog class="lab-dialog" id="dlg-soundwalk">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Wahrnehmung</p>
        <h4>Stadt hoeren</h4>
        <p class="lab-dialog-lede">Die Umgebung ist das Instrument.</p>

        <div class="lab-dialog-tabs" role="tablist">
          <button class="lab-tab is-active" data-panel="schulen" type="button">Schulen</button>
          <button class="lab-tab" data-panel="traeger" type="button">Träger</button>
        </div>

        <div class="lab-dialog-panel" data-panel="schulen">
          <p>Schülerinnen und Schüler verlassen das Klassenzimmer und nehmen ihre Umgebung mit anderen Ohren wahr. Geräusche aus Park, Schulhof, Stadtteil oder Wald werden gesammelt, verglichen und zu einer Komposition zusammengefügt. Das Ergebnis ist ein gemeinsames Hörstück – entstanden aus dem, was immer schon da war.</p>

          <h5>Arbeitsweise</h5>
          <ul>
            <li>Geführter Soundwalk mit konkreten Aufnahmeaufgaben</li>
            <li>Gruppen bis 6 Personen mit klaren Rollen</li>
            <li>Professionelles mobiles Recording-Setup wird vollständig gestellt</li>
            <li>Editing und Komposition im Anschluss gemeinsam</li>
            <li>Abschluss: fertiges Klangstück als Gruppenprodukt</li>
          </ul>

          <h5>Modul-Optionen</h5>
          <table class="lab-dialog-table">
            <tr><th>1 Projekttag</th><td>Einführung → Soundwalk → Editing → Präsentation</td></tr>
            <tr><th>2 Projekttage</th><td>Vertiefung → Konzeptentwicklung → Komposition → Feinschliff</td></tr>
            <tr><th>3–5 Projekttage</th><td>Intensivmodul → mehrere Walks → Dramaturgie → schulinterne Präsentation</td></tr>
          </table>

          <h5>Fokus &amp; Nutzen</h5>
          <ul>
            <li>Bewusstes Zuhören und Wahrnehmungsschulung</li>
            <li>Achtsamkeit und Konzentration</li>
            <li>Medienkompetenz durch eigenes Produzieren</li>
            <li>Teamarbeit und Rollenverantwortung</li>
            <li>Kreativer Ausdruck über Klang</li>
          </ul>

          <p class="lab-dialog-note">Ort, Thema und Dauer werden gemeinsam abgestimmt. Fächerübergreifende Ansätze mit Sachunterricht, Musik oder Kunst sind ausdrücklich möglich.</p>
        </div>

        <div class="lab-dialog-panel" data-panel="traeger" hidden>
          <p>Teilnehmende erkunden ihren Ort mit anderen Sinnen. Ein geführter Soundwalk mit konkreten Aufnahmeaufgaben – danach Editing und Komposition zu einer Soundscape. Das Ergebnis ist ausstellungsfähig, dokumentierbar oder als Beteiligungsformat intern verwendbar.</p>

          <h5>Arbeitsweise</h5>
          <ul>
            <li>Geführter Soundwalk mit klaren Aufgaben</li>
            <li>Gruppen bis 10 Personen</li>
            <li>Professionelles Recording-Setup wird vollständig gestellt</li>
            <li>Postproduktion: Editing, Mix, Ausgabe im gewünschten Format</li>
            <li>Ergebnis: Soundscape Library + fertiges Klangstück</li>
          </ul>

          <h5>Buchungsoptionen</h5>
          <table class="lab-dialog-table">
            <tr><th>1 Termin</th><td>Soundwalk → Aufnahmen → einfache Montage → Übergabe</td></tr>
            <tr><th>2–3 Termine</th><td>Komposition → Dramaturgie → Feinschliff</td></tr>
            <tr><th>Projektreihe</th><td>Mehrere Orte → wachsendes Klangarchiv</td></tr>
          </table>

          <h5>Fokus &amp; Nutzen</h5>
          <ul>
            <li>Achtsamkeit und Wahrnehmung fördern</li>
            <li>Raum und Umfeld dokumentieren</li>
            <li>Kreatives Ergebnis für Öffentlichkeitsarbeit</li>
            <li>Gruppenarbeit und Kollaboration stärken</li>
            <li>Ausstellungsfähiges Audioprodukt</li>
          </ul>

          <p class="lab-dialog-note">Geeignet für Jugendhilfe, Quartiersprojekte, Kultureinrichtungen und Ämter. Ort, Thema und Nutzung werden im Briefing abgestimmt.</p>
        </div>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>
```

- [ ] **Step 3: Strukturprüfung per grep**

Run:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
comm -3 <(grep -o 'data-dialog="[^"]*"' lab.html | sed 's/data-dialog="//;s/"//' | sort -u) <(grep -o 'id="dlg-[^"]*"' lab.html | sed 's/id="//;s/"//' | sort -u)
```

Expected: keine Ausgabe.

- [ ] **Step 4: Manueller Browser-Test inkl. Tabs**

Wie Task 1 Step 8, zusätzlich prüfen:
- Dialog öffnet standardmäßig auf Tab „Schulen"
- Klick auf „Träger" blendet den Träger-Inhalt ein und den Schulen-Inhalt aus, Tab-Unterstrich wechselt auf „Träger"
- Erneuter Klick auf „Schulen" schaltet zurück

- [ ] **Step 5: Commit**

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
git add lab.html
git commit -m "Add tab mechanism + Stadt hoeren dual-audience popup"
```

---

### Task 4: Verbleibende 2 Dual-Module (Podcast-Studio-Tag, Stimmen der Stadt)

**Files:**
- Modify: `lab.html:129-132` (Karte „Podcast-Studio-Tag"), `lab.html:139-143` (Karte „Stimmen der Stadt")

**Interfaces:**
- Konsumiert: identisches Tab-Muster aus Task 3, keine neuen Selektoren

- [ ] **Step 1: Button bei „Podcast-Studio-Tag" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag">Podcast</p>
          <h4 data-en="Podcast Studio Day">Podcast-Studio-Tag</h4>
          <p data-en="<strong>One topic, one episode, one clear output.</strong> Research, conversation, presenting, and editing lead to a finished episode in a short time."><strong>Ein Thema, eine Folge, ein klarer Output.</strong> Recherche, Gespräch, Moderation und Schnitt führen in kurzer Zeit zu einer fertigen Episode.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag">Podcast</p>
          <h4 data-en="Podcast Studio Day">Podcast-Studio-Tag</h4>
          <p data-en="<strong>One topic, one episode, one clear output.</strong> Research, conversation, presenting, and editing lead to a finished episode in a short time."><strong>Ein Thema, eine Folge, ein klarer Output.</strong> Recherche, Gespräch, Moderation und Schnitt führen in kurzer Zeit zu einer fertigen Episode.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-podcast" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 2: Button bei „Stimmen der Stadt" ergänzen**

In `lab.html` die Karte:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="City & Participation">Stadt &amp; Beteiligung</p>
          <h4 data-en="Voices of the City">Stimmen der Stadt</h4>
          <p data-en="<strong>Interviews, on-location audio, and perspectives from a community.</strong> The module collects voices and condenses them into a shared portrait of a city or neighbourhood."><strong>Interviews, O-Töne und Perspektiven aus einem Umfeld.</strong> Das Modul sammelt Stimmen und verdichtet sie zu einem gemeinsamen Stadt- oder Nachbarschaftsporträt.</p>
        </div>
```

ersetzen durch:

```html
        <div class="lab-module">
          <p class="lab-module-tag" data-en="City & Participation">Stadt &amp; Beteiligung</p>
          <h4 data-en="Voices of the City">Stimmen der Stadt</h4>
          <p data-en="<strong>Interviews, on-location audio, and perspectives from a community.</strong> The module collects voices and condenses them into a shared portrait of a city or neighbourhood."><strong>Interviews, O-Töne und Perspektiven aus einem Umfeld.</strong> Das Modul sammelt Stimmen und verdichtet sie zu einem gemeinsamen Stadt- oder Nachbarschaftsporträt.</p>
          <div class="lab-module-more">
            <button class="lab-more-btn" data-dialog="dlg-voices" type="button">Mehr erfahren →</button>
          </div>
        </div>
```

- [ ] **Step 3: 2 Dialoge mit Tabs einfügen**

In `lab.html` nach dem Dialog `#dlg-soundwalk` einfügen:

```html
      <dialog class="lab-dialog" id="dlg-podcast">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Podcast</p>
        <h4>Podcast-Studio-Tag</h4>
        <p class="lab-dialog-lede">Was die Klasse zu sagen hat, wird hörbar.</p>

        <div class="lab-dialog-tabs" role="tablist">
          <button class="lab-tab is-active" data-panel="schulen" type="button">Schulen</button>
          <button class="lab-tab" data-panel="traeger" type="button">Träger</button>
        </div>

        <div class="lab-dialog-panel" data-panel="schulen">
          <p>In einem Projekttag produzieren Schülerinnen und Schüler eine vollständige Podcast-Episode. Thema definieren, Interview führen, aufnehmen – und am Ende eine fertige, abgemischte Produktion in der Hand halten. Keine Vorkenntnisse nötig. Nur etwas zu sagen haben.</p>

          <h5>Arbeitsweise</h5>
          <ul>
            <li>Themenentwicklung und Redaktionsrunde zu Beginn</li>
            <li>Interview- und Sprechtraining</li>
            <li>Aufnahme mit professionellem Setup</li>
            <li>Schnitt, Mix und Lautheitskorrektur inklusive</li>
            <li>Finale Episode als Audiodatei – bereit zum Anhören und Teilen</li>
          </ul>

          <h5>Modul-Optionen</h5>
          <table class="lab-dialog-table">
            <tr><th>1 Projekttag</th><td>Einführung → Aufnahme → abgemischte Episode</td></tr>
            <tr><th>2 Projekttage</th><td>Recherche → Interview → Schnitt → Feinschliff</td></tr>
            <tr><th>3–5 Projekttage</th><td>Mini-Podcastserie → mehrere Episoden → eigenes Format</td></tr>
          </table>

          <h5>Fokus &amp; Nutzen</h5>
          <ul>
            <li>Medienkompetenz durch eigenes Produzieren</li>
            <li>Strukturiertes Argumentieren und Sprechen</li>
            <li>Recherche und Interviewführung</li>
            <li>Teamarbeit in Redaktionsstruktur</li>
            <li>Technisches Grundverständnis für Audio</li>
          </ul>

          <p class="lab-dialog-note">Das Thema kommt aus der Klasse oder dem Lehrplan. Ob aktuelles Thema, Schulprojekt oder Abschluss einer Unterrichtsreihe – jedes Format ist möglich.</p>
        </div>

        <div class="lab-dialog-panel" data-panel="traeger" hidden>
          <p>In einem Produktionstag entsteht eine vollständige Podcast-Episode. Thema definieren, Interview führen, aufnehmen – und am Ende eine abgemischte, veröffentlichungsfertige Produktion übergeben. Für Öffentlichkeitsarbeit, interne Kommunikation oder Beteiligungsformate.</p>

          <h5>Arbeitsweise</h5>
          <ul>
            <li>Themen- und Formatentwicklung zu Beginn</li>
            <li>Interview-Coaching und Sprechvorbereitung</li>
            <li>Aufnahme mit professionellem Setup</li>
            <li>Schnitt, Mix, Lautheit, Export inklusive</li>
            <li>Finale Episode bereit für Plattformen oder internen Einsatz</li>
          </ul>

          <h5>Buchungsoptionen</h5>
          <table class="lab-dialog-table">
            <tr><th>1 Termin (6h)</th><td>Einführung → Aufnahme → abgemischte Episode</td></tr>
            <tr><th>2–3 Termine</th><td>Recherche → Interview → Schnitt → Feinschliff</td></tr>
            <tr><th>Podcast-Reihe</th><td>Redaktion aufbauen → regelmäßiges Format</td></tr>
          </table>

          <h5>Fokus &amp; Nutzen</h5>
          <ul>
            <li>Öffentlichkeitsarbeit durch eigenes Format stärken</li>
            <li>Zielgruppen aktiv einbinden und zu Wort kommen lassen</li>
            <li>Interne Kommunikation hörbar machen</li>
            <li>Professionelles, direkt nutzbares Ergebnis</li>
            <li>Datenschutzkonforme Produktion</li>
          </ul>

          <p class="lab-dialog-note">Format und Thema werden im Briefing gemeinsam entwickelt. Ob Einzel-Episode, Interview-Reihe oder interne Produktion – das Konzept kommt aus Ihrer Einrichtung.</p>
        </div>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>

      <dialog class="lab-dialog" id="dlg-voices">
        <form method="dialog" class="lab-dialog-close"><button aria-label="Schliessen" type="submit">×</button></form>
        <p class="lab-dialog-tag">Stadt &amp; Beteiligung</p>
        <h4>Stimmen der Stadt</h4>
        <p class="lab-dialog-lede">Was klingt in deinem Kiez?</p>

        <div class="lab-dialog-tabs" role="tablist">
          <button class="lab-tab is-active" data-panel="schulen" type="button">Schulen</button>
          <button class="lab-tab" data-panel="traeger" type="button">Träger</button>
        </div>

        <div class="lab-dialog-panel" data-panel="schulen">
          <p>Die Gruppe geht raus und sammelt Stimmen, Geräusche und Statements aus dem eigenen Umfeld. Nachbarn, Orte, Momente. Daraus entsteht ein gemeinsames Hörstück – eine Klangdokumentation des eigenen Kiezes. Subjektiv, präzise, hörbar.</p>

          <h5>Arbeitsweise</h5>
          <ul>
            <li>Recherche und Vorbereitung in der Gruppe</li>
            <li>Feldaufnahmen im eigenen Umfeld</li>
            <li>Rollen: Aufnahme, Interview, Regie</li>
            <li>Editing und Montage im Anschluss</li>
            <li>Ergebnis: Hörstück oder Podcast-Episode, 6–15 Minuten</li>
          </ul>

          <h5>Modul-Optionen</h5>
          <table class="lab-dialog-table">
            <tr><th>1 Projekttag</th><td>Einführung → Aufnahmen → erste Montage → Demo</td></tr>
            <tr><th>2–3 Projekttage</th><td>Interviews → vollständiges Stück → Feinschliff</td></tr>
            <tr><th>Projektwoche</th><td>Dokumentarprojekt → Präsentation oder Veröffentlichung</td></tr>
          </table>

          <h5>Fokus &amp; Nutzen</h5>
          <ul>
            <li>Perspektivwechsel und Empathie</li>
            <li>Recherche und Interviewführung</li>
            <li>Identität und Zugehörigkeit reflektieren</li>
            <li>Medienkompetenz durch Dokumentararbeit</li>
            <li>Verantwortung beim öffentlichen Erzählen</li>
          </ul>

          <p class="lab-dialog-note">Ob Schulumgebung, Quartiersprojekt oder biografisches Thema – der Ausgangspunkt kommt aus der Gruppe. Auch als fächerübergreifendes oder sozialkundliches Projekt buchbar.</p>
        </div>

        <div class="lab-dialog-panel" data-panel="traeger" hidden>
          <p>Gruppen sammeln Stimmen, Statements und Geräusche aus ihrem Umfeld. Bewohner, Teilnehmende, Nachbarn. Daraus entsteht ein Hörstück oder eine Podcast-Folge – dokumentarisch, präzise, mit echten Stimmen. Das Ergebnis ist intern nutzbar oder öffentlich einsetzbar.</p>

          <h5>Arbeitsweise</h5>
          <ul>
            <li>Klare Rollenverteilung: Aufnahme, Interview, Regie</li>
            <li>Gruppen bis 10 Personen, moderiert und strukturiert</li>
            <li>Freigaben und Datenschutz werden vorab geklärt</li>
            <li>Postproduktion: Schnitt, Mix, Ausgabe</li>
            <li>Ergebnis: Hörstück oder Podcast-Episode, 6–15 Minuten</li>
          </ul>

          <h5>Buchungsoptionen</h5>
          <table class="lab-dialog-table">
            <tr><th>1 Termin (6h)</th><td>Einführung → Aufnahmen → Montage → Übergabe</td></tr>
            <tr><th>2–3 Termine</th><td>Vertiefung → vollständige Produktion → Freigabe</td></tr>
            <tr><th>Projektreihe</th><td>Mehrere Folgen → Archiv oder laufendes Format</td></tr>
          </table>

          <h5>Fokus &amp; Nutzen</h5>
          <ul>
            <li>Beteiligung als hörbares Produkt dokumentieren</li>
            <li>Stimmen der Zielgruppe sichtbar machen</li>
            <li>Öffentlichkeitsarbeit mit echten Inhalten stärken</li>
            <li>Selbstwirksamkeit der Teilnehmenden fördern</li>
            <li>Professionelles, nutzbares Ergebnis</li>
          </ul>

          <p class="lab-dialog-note">Thema, Zielgruppe und Nutzung werden im Briefing gemeinsam geklärt. Ob internes Archiv, Öffentlichkeitsarbeit oder Quartiersprojekt – das Format wird passend entwickelt.</p>
        </div>

        <div class="lab-dialog-cta">
          <a class="btn" href="kontakt.html">Projekt anfragen</a>
        </div>
      </dialog>
```

- [ ] **Step 4: Strukturprüfung per grep — alle 9 Module**

Run:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
echo "Buttons: $(grep -c 'lab-more-btn' lab.html)"
echo "Dialoge: $(grep -c '<dialog class="lab-dialog"' lab.html)"
comm -3 <(grep -o 'data-dialog="[^"]*"' lab.html | sed 's/data-dialog="//;s/"//' | sort -u) <(grep -o 'id="dlg-[^"]*"' lab.html | sed 's/id="//;s/"//' | sort -u)
```

Expected: `Buttons: 9`, `Dialoge: 9`, keine Ausgabe bei der `comm`-Zeile.

- [ ] **Step 5: Manueller Browser-Test aller 9 Module**

Server starten wie in Task 1 Step 8. Für jedes der 9 Module: Button sichtbar, Dialog öffnet mit korrektem Text, bei den 3 Dual-Modulen (Stadt hören, Podcast-Studio-Tag, Stimmen der Stadt) Tab-Umschalten testen. Zusätzlich:

- Grid-Ansicht bei 3 Browserbreiten prüfen: Desktop (>900px, 3 Spalten), Tablet (600–900px, 2 Spalten), Mobile (<600px, 1 Spalte) — Button bleibt in jeder Kartenreihe unten links, auch bei unterschiedlich langen Beschreibungstexten
- Bestehender Hover-Effekt der Karte (Rahmenfarbe/Hintergrund wechselt zu Akzent) funktioniert weiterhin, auch wenn der Mauszeiger über dem neuen Button steht

- [ ] **Step 6: Commit**

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
git add lab.html
git commit -m "Add remaining dual-audience lab module popups (Podcast, Stimmen der Stadt)"
```

---

### Task 5: Abschluss-Verifikation

**Files:**
- Keine Änderungen — nur Verifikation über den gesamten Feature-Umfang

**Interfaces:**
- Konsumiert: alle Artefakte aus Task 1–4

- [ ] **Step 1: Vollständigkeitsprüfung gegen die Content-Mapping-Tabelle**

Run:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
for id in dlg-klangkoffer dlg-soundwalk dlg-hoerspiel dlg-podcast dlg-beatbars dlg-voices dlg-memory dlg-team dlg-exhibition; do
  grep -q "id=\"$id\"" lab.html && echo "OK  $id" || echo "FEHLT $id"
done
```

Expected: alle 9 Zeilen `OK`.

- [ ] **Step 2: HTML-Grundvalidität prüfen (ausgewogene Tags)**

Run:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
python3 -c "
import xml.etree.ElementTree as ET
import re
html = open('lab.html', encoding='utf-8').read()
# grobe Prüfung: <dialog...>/<\/dialog> Anzahl gleich
opens = len(re.findall(r'<dialog class=\"lab-dialog\"', html))
closes = len(re.findall(r'</dialog>', html))
print(f'dialog open={opens} close={closes}')
assert opens == closes == 9
print('OK')
"
```

Expected: `dialog open=9 close=9` gefolgt von `OK`.

- [ ] **Step 3: Vollständiger manueller Regressionstest im Browser**

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de" && python3 -m http.server 8000
```

Auf `http://localhost:8000/lab.html`:
- Jedes der 9 Popups einmal öffnen und wieder schließen (×, ESC, Backdrop-Klick)
- Bei den 3 Dual-Modulen beide Tabs durchklicken
- Restliche Seite (Hero, Ablauf-Phasen, „Für wen"-Pillars, Buchungs-CTA) sieht unverändert aus — keine Regressions durch die CSS-Änderungen an `.lab-module`
- `leistungen.html`, `about.html`, `faq.html`, `kontakt.html` kurz gegenchecken, da `styles.css` global eingebunden ist (Accent-Tint-Selektorliste wurde erweitert) — Buttons dort sehen unverändert aus

Server danach mit `Ctrl+C` beenden.

- [ ] **Step 4: Abschluss-Commit (falls in Schritt 3 noch Korrekturen nötig waren)**

Falls beim Regressionstest Anpassungen nötig waren, diese committen:

```bash
cd "/Users/kiki4ewa/Documents/Claude/Projects/DanielMatysiak.de"
git add -A
git commit -m "Fix regressions found in final lab popup verification pass"
```

Falls keine Korrekturen nötig waren, diesen Schritt überspringen.

---

## Deploy

Dieser Plan deployed nicht automatisch. Nach Abschluss aller Tasks das `deploy`-Skill nutzen, um den fertigen Stand auf GitHub Pages zu veröffentlichen (git push + Live-Verifikation), wie beim vorherigen `llms.txt`-Update.
