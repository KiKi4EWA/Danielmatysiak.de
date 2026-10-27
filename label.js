// 4Spur Records: Detailpanel, Jahresnavigation, Datumsformat
(function () {
  const dataEl = document.getElementById('release-data');
  const panel = document.getElementById('release-panel');
  if (!dataEl || !panel) return;
  const DATA = JSON.parse(dataEl.textContent);
  const body = document.getElementById('panel-body');
  const closeBtn = document.getElementById('panel-close');
  const closeLbl = document.getElementById('panel-close-label');
  const root = document.documentElement;
  const T = {
    de: { close: 'Schließen', listen: 'Anhören', soon: 'Streaming-Link folgt.', hide: 'Player schließen', consent: n => `Player von ${n}. Beim Laden werden Daten an ${n} übertragen.`, open: 'Öffnen in', orchardTip: 'Alle Tracks ohne Anmeldung anhören', revoke: 'Spotify-Einwilligung widerrufen', tracks: 'Tracks', credits: 'Credits', video: 'Video', feat: 'feat.' },
    en: { close: 'Close', listen: 'Listen', soon: 'Streaming link coming soon.', hide: 'Close player', consent: n => `Player from ${n}. Loading it sends data to ${n}.`, open: 'Open in', orchardTip: 'Listen to all tracks without signing in', revoke: 'Withdraw Spotify consent', tracks: 'Tracks', credits: 'Credits', video: 'Video', feat: 'feat.' },
  };
  const PLATFORMS = [['orchard', 'The Orchard'], ['spotify', 'Spotify'], ['apple', 'Apple Music'], ['bandcamp', 'Bandcamp'], ['youtube', 'YouTube'], ['soundcloud', 'SoundCloud'], ['other', 'Web']];
  const lang = () => (root.lang === 'en' ? 'en' : 'de');
  const fmtDate = iso => {
    const [y, m, d] = iso.split('-').map(Number);
    return lang() === 'en'
      ? new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(Date.UTC(y, m - 1, d)))
      : `${String(d).padStart(2, '0')}.${String(m).padStart(2, '0')}.${y}`;
  };
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const safeUrl = u => { try { const x = new URL(u); return x.protocol === 'https:' ? x.href : null; } catch (e) { return null; } };
  const linkItem = (name, url) => { const li = el('li'); const a = el('a', null, name); a.href = url; a.target = '_blank'; a.rel = 'noopener'; li.appendChild(a); return li; };

  let opener = null, currentId = null, activeArtist = null;

  function coverEl(r) {
    if (!r.cover) return el('div', 'panel-cover cover-ph');
    const wrap = el('div', 'panel-cover');
    const img = document.createElement('img');
    img.src = `img/covers/${r.id}-${r.cover.includes(960) ? 960 : 640}.webp`;
    img.srcset = r.cover.map(s => `img/covers/${r.id}-${s}.webp ${s}w`).join(', ');
    img.sizes = '(max-width: 700px) 100vw, 480px';
    img.width = 640; img.height = 640; img.alt = '';
    wrap.appendChild(img);
    return wrap;
  }

  // Player-Einbettung: nur Spotify (Album-Link nötig). Alle anderen Plattformen bleiben normale Links.
  function embedOf(r) {
    // Einzelner Titel statt ganzem Album (z. B. bei Produktionen, an denen nur ein Titel beteiligt war)
    if (r.embedTrack && /^[A-Za-z0-9]+$/.test(r.embedTrack)) return { name: 'Spotify', src: `https://open.spotify.com/embed/track/${r.embedTrack}?utm_source=generator`, h: 152 };
    const u = safeUrl((r.links || {}).spotify), m = u && u.match(/open\.spotify\.com\/(?:intl-[a-z]+\/)?album\/([A-Za-z0-9]+)/);
    return m ? { name: 'Spotify', src: `https://open.spotify.com/embed/album/${m[1]}?utm_source=generator`, h: 152 } : null;
  }

  function renderArtist(r) {
    const t = T[lang()], en = lang() === 'en';
    body.replaceChildren();
    const wrap = el('button', 'panel-cover is-portrait'); wrap.type = 'button';
    wrap.setAttribute('aria-label', en ? 'View larger' : 'Großansicht');
    const img = document.createElement('img');
    img.src = r.imageSmall; img.srcset = `${r.imageSmall} 480w, ${r.image} 960w`; img.sizes = '(max-width: 700px) 70vw, 300px';
    img.alt = en ? 'Self-portrait of ' + r.name : 'Selbstporträt von ' + r.name; img.width = 480; img.height = 739;
    wrap.appendChild(img);
    wrap.addEventListener('click', () => openArtistLightbox(r, wrap));
    body.appendChild(wrap);
    const head = el('div', 'panel-head');
    head.appendChild(el('p', 'panel-artist', en ? r.roleEn : r.role));
    const title = el('h2', 'panel-title', r.name); title.id = 'panel-title';
    head.appendChild(title); body.appendChild(head);
    (en ? r.bioEn : r.bio).forEach(p => body.appendChild(el('p', 'panel-desc', p)));
    const p = el('p', 'panel-open', `${en ? 'More from her' : 'Mehr von ihr'} `);
    r.links.forEach(([n, u]) => { const l = el('a', null, `${n} ↗`); l.href = u; l.target = '_blank'; l.rel = 'noopener'; p.appendChild(l); });
    body.appendChild(p);
    closeBtn.setAttribute('aria-label', t.close); closeLbl.textContent = t.close;
  }

  function render(id) {
    const r = DATA[id]; if (!r) return;
    if (r.kind === 'artist') return renderArtist(r);
    const t = T[lang()];
    body.replaceChildren();
    body.appendChild(coverEl(r));

    const head = el('div', 'panel-head');
    const artist = el('p', 'panel-artist', r.artist);
    if (r.feat) artist.appendChild(el('span', 'release-feat', ` ${t.feat} ${r.feat}`));
    // Die Display-Schrift hat keine brauchbaren Klammern: Versionszusatz "(…)" in Textschrift setzen
    const tm = r.title.match(/^(.*?)\s*(\([^)]*\))\s*$/);
    const title = el('h2', 'panel-title'); title.id = 'panel-title';
    // Die Display-Schrift hat keinen Schrägstrich: „/“ in Textschrift setzen
    (tm ? tm[1] : r.title).split('/').forEach((part, i) => { if (i) title.appendChild(el('span', 'title-slash', '/')); title.appendChild(document.createTextNode(part)); });
    if (tm) title.appendChild(el('span', 'title-ver', tm[2]));
    const meta = el('p', 'panel-meta');
    const time = el('time', null, fmtDate(r.date)); time.dateTime = r.date;
    meta.append(time, document.createTextNode(` · ${r.format}`));
    if (r.duration) meta.append(document.createTextNode(` · ${r.duration}`));
    head.append(artist, title, meta);
    if ((r.art || r.artBy) && r.cover) {
      const art = el('p', 'panel-art'); art.appendChild(el('span', null, 'Cover Art'));
      const ab = el('button', 'art-open', r.art || r.artBy); ab.type = 'button'; ab.setAttribute('aria-haspopup', 'dialog');
      ab.dataset.tip = lang() === 'en' ? 'Show cover large' : 'Cover groß anzeigen';   // eigener Tooltip (Schrift der Seite), kein System-Tooltip
      ab.addEventListener('click', () => openLightbox(r, ab));
      art.append(' ', ab); head.appendChild(art);
    }
    body.appendChild(head);

    const desc = lang() === 'en' && r.descriptionEn ? r.descriptionEn : r.description;
    if (desc) body.appendChild(el('p', 'panel-desc', desc));

    // Titelliste vor dem Player
    if (r.tracks && r.tracks.length) {
      body.appendChild(el('h3', 'panel-h', t.tracks));
      const ol = el('ol', 'panel-tracks');
      r.tracks.forEach(x => { const li = el('li'); li.appendChild(el('span', null, x.title)); if (x.duration) li.appendChild(el('span', 'track-dur', x.duration)); ol.appendChild(li); });
      body.appendChild(ol);
    }
    // Credits (Rolle + Name) ebenfalls vor dem Player
    if (r.credits && r.credits.length) {
      body.appendChild(el('h3', 'panel-h', t.credits));
      const dl = el('dl', 'panel-credits');
      r.credits.forEach(c => dl.append(el('dt', null, c.role), el('dd', null, c.name)));
      body.appendChild(dl);
    }
    const links = r.links ? PLATFORMS.map(([k, n]) => [n, safeUrl(r.links[k])]).filter(x => x[1]) : [];
    const emb = embedOf(r);
    const act = el('div', 'panel-actions');
    const row = el('div', 'panel-row');   // eine Zeile unter dem Player: Schalter + „Öffnen in …“
    if (emb) {
      const btn = el('button', 'btn', t.listen); btn.type = 'button';
      const box = el('div', 'panel-player'); box.id = 'panel-player';
      btn.setAttribute('aria-controls', 'panel-player');
      // Einmalige Zustimmung (nur lokal im Browser gemerkt): danach erscheint der Player sofort
      const KEY = '4spur-spotify-player';
      let ok = false; try { ok = localStorage.getItem(KEY) === '1'; } catch (e) {}
      const seenBefore = ok;
      const setOpen = show => {
        if (show && !box.firstChild) {
          const f = document.createElement('iframe');
          f.src = emb.src; f.height = emb.h; f.loading = 'lazy'; f.title = `${r.title} – ${emb.name}`;
          f.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture'; f.allowFullscreen = true;
          box.appendChild(f);
          if (!seenBefore) box.appendChild(el('p', 'panel-note', t.consent(emb.name)));
        }
        box.hidden = !show; btn.setAttribute('aria-expanded', String(show)); btn.textContent = show ? t.hide : t.listen;
      };
      // Widerruf: gespeicherte Zustimmung löschen, Player entfernen
      const revoke = el('button', 'panel-revoke', t.revoke); revoke.type = 'button'; revoke.hidden = !ok;
      revoke.addEventListener('click', () => {
        ok = false; try { localStorage.removeItem(KEY); } catch (e) {}
        box.replaceChildren(); setOpen(false); revoke.hidden = true;
      });
      btn.addEventListener('click', () => {
        const show = box.hidden;
        if (show && !ok) { ok = true; try { localStorage.setItem(KEY, '1'); } catch (e) {} }
        setOpen(show); revoke.hidden = !ok;
      });
      act.append(box); row.append(btn); act.append(revoke);
      setOpen(ok);
    } else if (links.length) {
      const a = el('a', 'btn'); a.href = links[0][1]; a.target = '_blank'; a.rel = 'noopener';
      a.append(el('span', null, t.listen), el('span', 'visually-hidden', ` – ${links[0][0]}`));
      row.appendChild(a);
    } else {
      const b = el('span', 'btn btn-disabled', t.listen); b.setAttribute('aria-disabled', 'true');
      row.append(b); act.append(el('p', 'panel-note', t.soon));
    }
    if (links.length) {
      const p = el('p', 'panel-open', `${t.open} `);
      links.forEach(([n, u]) => {
        const l = el('a', null, `${n} ↗`); l.href = u; l.target = '_blank'; l.rel = 'noopener';
        if (n === 'The Orchard') l.dataset.tip = t.orchardTip;   // Hinweis im eigenen Tooltip (Schrift der Seite)
        p.appendChild(l);
      });
      row.appendChild(p);
    }
    act.appendChild(row);
    body.appendChild(act);

    const vids = (r.videos || []).map(v => [v.title, safeUrl(v.url)]).filter(v => v[1]);
    if (vids.length) {
      body.appendChild(el('h3', 'panel-h', t.video));
      const ul = el('ul', 'panel-links');
      vids.forEach(([n, u]) => ul.appendChild(linkItem(n, u)));
      body.appendChild(ul);
    }
    closeBtn.setAttribute('aria-label', t.close);
    closeLbl.textContent = t.close;
  }

  // Desktop: Seitenpanel ohne Sperre (Wand und Jahresleiste bleiben bedienbar). Handy: bildschirmfüllend und modal.
  const wide = window.matchMedia('(min-width: 701px)');
  // Seitenpanel: beginnt auf der Oberkante der Cover (nie im Hero, nie über dem Menü) und endet über dem Footer
  const siteNav = document.querySelector('.site-nav');
  const siteFooter = document.querySelector('footer');
  let syncQueued = false;
  function syncTop() {
    syncQueued = false;
    const rail = document.getElementById('year-nav'), hero = document.querySelector('.hero-deco');
    if (!document.body.classList.contains('panel-side')) { panel.style.removeProperty('--panel-top'); panel.style.removeProperty('--panel-bottom'); if (rail) rail.classList.remove('behind-hero'); return; }
    // Jahresleiste ausblenden, solange sie über dem Hero (und dessen Infobox) läge
    if (rail && hero) rail.classList.toggle('behind-hero', hero.getBoundingClientRect().bottom > rail.getBoundingClientRect().top);
    // Oberkante: Oberkante der Coverreihen, mindestens aber die Unterkante des Menüs
    const grid = document.querySelector('.release-grid');
    const navBottom = Math.max(siteNav ? Math.max(0, siteNav.getBoundingClientRect().bottom) : 0, grid ? grid.getBoundingClientRect().top : 0);
    const footTop = siteFooter ? siteFooter.getBoundingClientRect().top : innerHeight;
    panel.style.setProperty('--panel-top', navBottom + 'px');
    panel.style.setProperty('--panel-bottom', Math.max(0, innerHeight - footTop) + 'px');
  }
  const queueSync = () => { if (!syncQueued) { syncQueued = true; requestAnimationFrame(syncTop); } };
  window.addEventListener('scroll', queueSync, { passive: true });
  window.addEventListener('resize', queueSync);

  // Großansicht des Covers (Klick auf den Bildtitel)
  const lb = document.getElementById('lightbox'), lbImg = document.getElementById('lightbox-img'), lbCap = document.getElementById('lightbox-cap');
  let lbOpener = null;
  function openLightbox(r, from) {
    if (!lb || !r.cover) return;
    const size = r.cover.includes(1440) ? 1440 : Math.max(...r.cover);
    lbImg.src = `img/covers/${r.id}-${size}.webp`;
    lbImg.srcset = r.cover.map(s => `img/covers/${r.id}-${s}.webp ${s}w`).join(', ');
    lbImg.sizes = 'min(92vw, 84dvh)';
    lbImg.alt = `${r.art || r.artBy}: ${r.title}, ${r.artist}`;
    const who = r.artist + (r.feat ? ' feat. ' + r.feat : '');
    lbCap.textContent = `${who} \u00b7 ${r.title} \u00b7 ${r.cline}`;   // Trennpunkte in Zeilenmitte
    lbOpener = from || null;
    lb.showModal();
  }
  // Großansicht des Selbstporträts; Klick aufs große Bild wechselt zur Zeichnung (Easter Egg), noch ein Klick zurück
  function openArtistLightbox(r, from) {
    if (!lb) return;
    const en = lang() === 'en', art = lb.querySelector('.lightbox-art');
    let egg = false;
    const show = () => {
      const w = egg ? 1 : 960 / 1478;
      lb.classList.add('is-photo');
      art.style.setProperty('--ar', w.toFixed(4)); art.style.maxWidth = Math.round((egg ? 960 : 1478) * w * 1.6) + 'px';
      lbImg.removeAttribute('srcset'); lbImg.src = egg ? r.image2 : r.image;
      lbImg.sizes = 'min(92vw, 84dvh)';
      lbImg.alt = egg ? (en ? 'Maus (mouse), drawing by ' + r.name : 'Maus, Zeichnung von ' + r.name) : (en ? 'Self-portrait of ' + r.name : 'Selbstporträt von ' + r.name);
      lbCap.textContent = egg ? r.name + ' \u00b7 Maus' : r.name;   // Titel der Zeichnung: „Maus“
    };
    lbImg.onclick = r.image2 ? () => { egg = !egg; show(); } : null;
    lb.addEventListener('close', () => { lbImg.onclick = null; }, { once: true });
    show(); lbOpener = from || null; lb.showModal();
  }
  if (lb) {
    lb.addEventListener('click', e => { if (e.target !== lbImg) lb.close(); });
    document.getElementById('lightbox-close').addEventListener('click', () => lb.close());
    lb.addEventListener('close', () => { lb.classList.remove('is-photo'); lbImg.removeAttribute('src'); lbImg.removeAttribute('srcset'); if (lbOpener && document.contains(lbOpener)) lbOpener.focus({ preventScroll: true }); lbOpener = null; });
  }

  // Beim Öffnen die Wand so schieben, dass das Panel genug Platz hat und die gewählte Kachel im Bild bleibt
  function placeAfterOpen(from) {
    const grid = document.querySelector('.release-grid'); if (!grid) return;
    const navB = siteNav ? siteNav.getBoundingClientRect().bottom : 0, vh = innerHeight;
    const gridTop = grid.getBoundingClientRect().top;
    let target = scrollY;
    if (vh - Math.max(navB, gridTop) < vh * 0.6) target = scrollY + gridTop - (navB + 16);   // Panel wäre zu kurz
    const r = from.getBoundingClientRect(), top = r.top + scrollY;
    if (top - target < navB + 8 || top + r.height - target > vh - 8) target = top - navB - 24;   // Kachel nicht verlieren
    target = Math.max(0, Math.min(target, document.documentElement.scrollHeight - vh));
    if (Math.abs(target - scrollY) > 2) window.scrollTo({ top: target, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }

  function open(id, from) {
    currentId = id; opener = from || null;
    render(id);
    panel.scrollTop = 0;
    if (!panel.open) {
      if (wide.matches) { panel.show(); closeBtn.focus({ preventScroll: true }); } else panel.showModal();
      document.body.classList.toggle('panel-side', wide.matches);
      syncTop();
      if (wide.matches && from) placeAfterOpen(from);
    }
    try { history.replaceState(null, '', '#r-' + id); } catch (e) {}
  }
  // Aufräumen läuft sofort beim Schließen und noch einmal beim close-Ereignis (z. B. natives Escape im Modal)
  function cleanup() {
    if (currentId === null && !document.body.classList.contains('panel-side')) return;
    currentId = null;
    document.body.classList.remove('panel-side');
    panel.style.removeProperty('--panel-top'); panel.style.removeProperty('--panel-bottom');
    body.replaceChildren();
    try { history.replaceState(null, '', location.pathname + location.search + (activeArtist ? '#a-' + activeArtist : '')); } catch (e) {}
    const o = opener;
    if (o && document.contains(o)) { o.focus({ preventScroll: true }); requestAnimationFrame(() => o.scrollIntoView({ block: 'nearest' })); }
    opener = null;
  }
  function close() { if (panel.open) { panel.close(); cleanup(); } }
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && panel.open && !(lb && lb.open)) { e.preventDefault(); close(); } });
  panel.addEventListener('close', cleanup);
  closeBtn.addEventListener('click', close);
  panel.addEventListener('click', e => { if (e.target === panel) close(); }); // Klick auf Backdrop
  document.querySelectorAll('.release-open').forEach(b => b.addEventListener('click', () => open(b.dataset.id, b)));

  // Sprache: Datum und offenes Panel neu rendern
  const refreshDates = () => document.querySelectorAll('.release-date').forEach(t => { t.textContent = fmtDate(t.getAttribute('datetime')); });
  new MutationObserver(() => { refreshDates(); if (currentId) render(currentId); renderIntro(); }).observe(root, { attributes: true, attributeFilter: ['lang'] });
  refreshDates();

  // Artists: Menü im Hero filtert die Wand; ein Textblock zwischen Hero und Wand stellt den Artist vor
  const ARTISTS = (() => { try { return JSON.parse(document.getElementById('artist-data').textContent); } catch (e) { return []; } })();
  const intro = document.getElementById('artist-intro');
  const menu = document.getElementById('artist-menu');
  const menuBtn = document.getElementById('artist-btn');
  const AT = {
    de: { all: 'Alle Künstler anzeigen', one: 'Release', many: 'Releases', soon: n => `Zu ${n} folgt in Kürze ein Text.` },
    en: { all: 'Show all artists', one: 'release', many: 'releases', soon: n => `A text about ${n} is coming soon.` },
  };
  const shown = n => n.replace(/\s*&\s*/g, ' y ');   // die Display-Schrift hat für „&“ nur einen Schnörkel
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Die „808“ der Display-Schrift hat den dicken Bauch oben: vertikal gespiegelt steht er unten, wie beim 808-Logo
  const withFlip808 = (node, text) => {
    node.textContent = '';
    text.split('808').forEach((part, i) => { if (i) node.appendChild(el('span', 'n808', '808')); if (part) node.appendChild(document.createTextNode(part)); });
  };

  function renderIntro() {
    if (!intro) return;
    const a = ARTISTS.find(x => x.slug === activeArtist);
    intro.hidden = !a;
    if (!a) return;
    const t = AT[lang()], en = lang() === 'en';
    withFlip808(intro.querySelector('.artist-intro-name'), shown(a.name));
    intro.querySelector('.artist-intro-text').textContent = (en ? a.bioEn : a.bio) || t.soon(a.name);
    const n = [...document.querySelectorAll('.release[data-artists]')].filter(li => !li.hidden).length;
    intro.querySelector('.artist-intro-count').textContent = `${n} ${n === 1 ? t.one : t.many}`;
    const link = intro.querySelector('.artist-intro-link');
    const u = a.spotify && safeUrl(a.spotify); link.hidden = !u; if (u) link.href = u;
    intro.querySelector('.artist-intro-reset').textContent = t.all;
    const pb = intro.querySelector('.artist-intro-photo'), pi = pb.querySelector('img');
    pb.hidden = !a.photo;
    if (a.photo) {
      pi.src = a.photo.s; if (a.photo.s !== a.photo.l) pi.srcset = `${a.photo.s} ${a.photo.sw}w, ${a.photo.l} ${a.photo.lw}w`; else pi.removeAttribute('srcset'); pi.sizes = '(max-width: 800px) 92vw, 40vw';
      pi.alt = (en ? a.photoAltEn : a.photoAlt) || a.name;
      pb.setAttribute('aria-label', en ? 'Show photo large' : 'Foto groß anzeigen');
    }
    requestAnimationFrame(fitPhoto);
  }

  function setArtist(slug, scroll) {
    const a = ARTISTS.find(x => x.slug === slug); slug = a ? slug : null;
    if (panel.open) close();
    activeArtist = slug;
    document.body.classList.toggle('filtered', !!slug);
    document.querySelectorAll('.release').forEach(li => { li.hidden = !!slug && !(li.dataset.artists || '').split(' ').includes(slug); });
    // Jahresleiste: nur Jahre mit sichtbaren Kacheln
    document.querySelectorAll('#year-nav li').forEach(li => {
      const y = li.querySelector('a').getAttribute('href').slice(2);
      li.hidden = !!slug && !document.querySelector(`.release[data-year="${y}"]:not([hidden])`);
    });
    if (menu) menu.querySelectorAll('button[data-artist]').forEach(b => { const on = b.dataset.artist === (slug || ''); if (on) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    renderIntro();
    if (intro && slug) { intro.classList.remove('is-in'); void intro.offsetWidth; intro.classList.add('is-in'); }
    try { history.replaceState(null, '', location.pathname + location.search + (slug ? '#a-' + slug : '')); } catch (e) {}
    if (scroll) {
      const target = slug ? intro : document.getElementById('archiv');
      if (target) target.scrollIntoView({ block: 'start', behavior: reduced() ? 'auto' : 'smooth' });
    }
  }

  if (menu && menuBtn) {
    // Das Menü liegt im Top-Layer (Popover) und wird unter dem Knopf platziert; so schneidet der Hero es nicht ab
    menu.addEventListener('beforetoggle', e => {
      if (e.newState === 'open') {
        const r = menuBtn.getBoundingClientRect();
        menu.style.top = (r.bottom + scrollY + 8) + 'px';
        menu.style.left = Math.max(8, Math.min(r.left + scrollX, scrollX + innerWidth - 8 - Math.min(320, innerWidth * 0.92))) + 'px';
        menu.style.minWidth = Math.min(r.width, 320) + 'px';
      }
    });
    menu.addEventListener('toggle', e => {
      menuBtn.setAttribute('aria-expanded', String(e.newState === 'open'));
      if (e.newState === 'open') {
        const cur = menu.querySelector('[aria-current]') || menu.querySelector('button'); cur && cur.focus({ preventScroll: true });
        const b = menu.getBoundingClientRect(); if (b.bottom > innerHeight - 8) scrollBy({ top: Math.min(b.bottom - innerHeight + 16, b.top - 80), behavior: reduced() ? 'auto' : 'smooth' });   // Menü ganz ins Bild holen
      }
    });
    menu.addEventListener('click', e => {
      const b = e.target.closest('button[data-artist]'); if (!b) return;
      menu.hidePopover(); setArtist(b.dataset.artist || null, true);
    });
    menu.addEventListener('keydown', e => {
      const items = [...menu.querySelectorAll('button')], i = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
      else if (e.key === 'Home') { e.preventDefault(); items[0].focus(); }
      else if (e.key === 'End') { e.preventDefault(); items[items.length - 1].focus(); }
    });
    window.addEventListener('resize', () => { if (menu.matches(':popover-open')) menu.hidePopover(); });
  }
  // Großansicht des Artist-Fotos: dieselbe Lightbox wie bei den Covern, nur im Querformat
  // Foto so hoch wie der Text (4:3), im Abstand der Cover direkt neben dem Absatz
  function fitPhoto() {
    if (!intro || intro.hidden) return;
    const pb = intro.querySelector('.artist-intro-photo'), tx = intro.querySelector('.artist-intro-text');
    if (pb.hidden) return;
    if (matchMedia('(max-width: 800px)').matches) { pb.style.removeProperty('width'); pb.style.removeProperty('height'); return; }
    const lh = parseFloat(getComputedStyle(tx).lineHeight) || 26;
    const h = Math.round(Math.max(tx.getBoundingClientRect().height, lh * 8));   // mindestens acht Zeilen hoch, auch bei kurzem Text
    if (h > 0) { pb.style.height = h + 'px'; pb.style.width = Math.round(h * 4 / 3) + 'px'; }
  }
  if (intro && 'ResizeObserver' in window) new ResizeObserver(fitPhoto).observe(intro.querySelector('.artist-intro-text'));
  window.addEventListener('resize', fitPhoto);
  if (intro && lb) {
    intro.querySelector('.artist-intro-photo').addEventListener('click', e => {
      const a = ARTISTS.find(x => x.slug === activeArtist); if (!a || !a.photo) return;
      lb.classList.add('is-photo');
      const art = lb.querySelector('.lightbox-art');
      art.style.setProperty('--ar', (a.photo.w / a.photo.h).toFixed(4)); art.style.maxWidth = Math.round(a.photo.w * 1.6) + 'px';   // kleine Fotos nicht unscharf aufblasen
      lbImg.src = a.photo.l; if (a.photo.s !== a.photo.l) lbImg.srcset = `${a.photo.s} ${a.photo.sw}w, ${a.photo.l} ${a.photo.lw}w`; else lbImg.removeAttribute('srcset');
      lbImg.sizes = 'min(92vw, 112dvh)';
      lbImg.alt = (lang() === 'en' ? a.photoAltEn : a.photoAlt) || a.name;
      lbCap.textContent = shown(a.name);
      lbOpener = e.currentTarget; lb.showModal();
    });
    lb.addEventListener('close', () => { lb.classList.remove('is-photo'); const art = lb.querySelector('.lightbox-art'); art.style.removeProperty('--ar'); art.style.removeProperty('max-width'); });
  }
  // „… oder entdecke die Künstler“ im Einleitungssatz: zum Hero-Knopf scrollen und das Menü öffnen (Delegation, weil die Sprachumschaltung den Satz neu setzt)
  const wallIntro = document.querySelector('.release-wall .section-intro');
  if (wallIntro && menu && menuBtn) wallIntro.addEventListener('click', e => {
    if (!e.target.closest('.intro-artists')) return;
    menuBtn.scrollIntoView({ block: 'center', behavior: reduced() ? 'auto' : 'smooth' });
    setTimeout(() => { try { menu.showPopover(); } catch (err) {} }, reduced() ? 0 : 450);
  });
  if (intro) intro.querySelector('.artist-intro-reset').addEventListener('click', () => { setArtist(null, true); if (menuBtn) menuBtn.focus({ preventScroll: true }); });
  // Bei aktivem Filter fehlt oft der Jahresanker: zur ersten sichtbaren Kachel des Jahres springen
  document.querySelectorAll('#year-nav a').forEach(a => a.addEventListener('click', e => {
    if (!activeArtist) return;
    e.preventDefault();
    const t = document.querySelector(`.release[data-year="${a.getAttribute('href').slice(2)}"]:not([hidden])`);
    if (t) t.scrollIntoView({ block: 'start', behavior: reduced() ? 'auto' : 'smooth' });
  }));

  // Deep-Link #r-<id> beim Laden und bei Klick auf einen Link innerhalb der Seite (z. B. „Cover Art by“)
  const openFromHash = scroll => {
    const am = location.hash.match(/^#a-([\w-]+)$/);
    if (am) { if (ARTISTS.some(a => a.slug === am[1]) && am[1] !== activeArtist) setArtist(am[1], scroll); return; }
    const m = location.hash.match(/^#r-([\w-]+)$/);
    if (!m || !DATA[m[1]]) return;
    const b = document.querySelector(`.release-open[data-id="${m[1]}"]`);
    open(m[1], b);
    if (scroll && b) b.scrollIntoView({ block: 'center' });
  };
  openFromHash(false);
  window.addEventListener('hashchange', () => openFromHash(true));

  // Jahresnavigation: erst ab Archiv sichtbar, aktives Jahr markieren
  const nav = document.getElementById('year-nav');
  const wall = document.getElementById('archiv');
  const tiles = [...document.querySelectorAll('.release[data-year]')];
  if (nav && wall && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => nav.classList.toggle('visible', e.isIntersecting), { rootMargin: '-30% 0px -10% 0px' }).observe(wall);
    const links = new Map([...nav.querySelectorAll('a')].map(a => [a.getAttribute('href').slice(1), a]));
    const vis = new Set();
    let lockUntil = 0;                       // nach einem Klick auf die Leiste gilt das angeklickte Jahr, bis das Scrollen zur Ruhe kommt
    const setActive = id => links.forEach((a, k) => {
      const on = k === id;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    links.forEach((a, id) => a.addEventListener('click', () => { lockUntil = Date.now() + 1500; setActive(id); }));
    const io = new IntersectionObserver(es => {
      es.forEach(e => (e.isIntersecting ? vis.add(e.target) : vis.delete(e.target)));
      if (Date.now() < lockUntil) return;
      const firstTile = tiles.find(t => vis.has(t));
      const first = firstTile && { id: 'y' + firstTile.dataset.year };
      setActive(first ? first.id : null);
      const act = first && links.get(first.id);
      if (act && getComputedStyle(nav.querySelector('ul')).flexDirection === 'row') act.scrollIntoView({ inline: 'center', block: 'nearest' });
    }, { rootMargin: '-15% 0px -70% 0px' });
    tiles.forEach(t => io.observe(t));
  }
})();
