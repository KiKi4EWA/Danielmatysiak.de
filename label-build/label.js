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
    de: { close: 'Schließen', listen: 'Anhören', soon: 'Streaming-Link folgt.', hide: 'Player schließen', consent: n => `Player von ${n}. Beim Laden werden Daten an ${n} übertragen.`, open: 'Öffnen in', tracks: 'Tracks', credits: 'Credits', video: 'Video', feat: 'feat.' },
    en: { close: 'Close', listen: 'Listen', soon: 'Streaming link coming soon.', hide: 'Close player', consent: n => `Player from ${n}. Loading it sends data to ${n}.`, open: 'Open in', tracks: 'Tracks', credits: 'Credits', video: 'Video', feat: 'feat.' },
  };
  const PLATFORMS = [['spotify', 'Spotify'], ['apple', 'Apple Music'], ['bandcamp', 'Bandcamp'], ['youtube', 'YouTube'], ['soundcloud', 'SoundCloud'], ['other', 'Web']];
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

  let opener = null, currentId = null;

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
    const u = safeUrl((r.links || {}).spotify), m = u && u.match(/open\.spotify\.com\/(?:intl-[a-z]+\/)?album\/([A-Za-z0-9]+)/);
    return m ? { name: 'Spotify', src: `https://open.spotify.com/embed/album/${m[1]}?utm_source=generator`, h: 152 } : null;
  }

  function renderArtist(r) {
    const t = T[lang()], en = lang() === 'en';
    body.replaceChildren();
    const wrap = el('div', 'panel-cover is-portrait');
    const img = document.createElement('img');
    img.src = r.imageSmall; img.srcset = `${r.imageSmall} 480w, ${r.image} 960w`; img.sizes = '(max-width: 700px) 70vw, 300px';
    img.alt = en ? 'Self-portrait of ' + r.name : 'Selbstporträt von ' + r.name; img.width = 480; img.height = 739;
    wrap.appendChild(img); body.appendChild(wrap);
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
    const title = el('h2', 'panel-title', tm ? tm[1] : r.title); title.id = 'panel-title';
    if (tm) title.appendChild(el('span', 'title-ver', tm[2]));
    const meta = el('p', 'panel-meta');
    const time = el('time', null, fmtDate(r.date)); time.dateTime = r.date;
    meta.append(time, document.createTextNode(` · ${r.format}`));
    if (r.duration) meta.append(document.createTextNode(` · ${r.duration}`));
    head.append(artist, title, meta);
    if (r.art) { const art = el('p', 'panel-art'); art.append(el('span', null, lang() === 'en' ? 'Cover art' : 'Cover'), document.createTextNode(' ' + r.art)); head.appendChild(art); }
    body.appendChild(head);

    const links = r.links ? PLATFORMS.map(([k, n]) => [n, safeUrl(r.links[k])]).filter(x => x[1]) : [];
    const emb = embedOf(r);
    const act = el('div', 'panel-actions');
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
      btn.addEventListener('click', () => {
        const show = box.hidden;
        if (show && !ok) { ok = true; try { localStorage.setItem(KEY, '1'); } catch (e) {} }
        setOpen(show);
      });
      act.append(btn, box);
      setOpen(ok);
    } else if (links.length) {
      const a = el('a', 'btn'); a.href = links[0][1]; a.target = '_blank'; a.rel = 'noopener';
      a.append(el('span', null, t.listen), el('span', 'visually-hidden', ` – ${links[0][0]}`));
      act.appendChild(a);
    } else {
      const b = el('span', 'btn btn-disabled', t.listen); b.setAttribute('aria-disabled', 'true');
      act.append(b, el('p', 'panel-note', t.soon));
    }
    if (links.length) {
      const p = el('p', 'panel-open', `${t.open} `);
      links.forEach(([n, u]) => { const l = el('a', null, `${n} ↗`); l.href = u; l.target = '_blank'; l.rel = 'noopener'; p.appendChild(l); });
      act.appendChild(p);
    }
    body.appendChild(act);

    const desc = lang() === 'en' && r.descriptionEn ? r.descriptionEn : r.description;
    if (desc) body.appendChild(el('p', 'panel-desc', desc));
    if (r.tracks && r.tracks.length) {
      body.appendChild(el('h3', 'panel-h', t.tracks));
      const ol = el('ol', 'panel-tracks');
      r.tracks.forEach(x => { const li = el('li'); li.appendChild(el('span', null, x.title)); if (x.duration) li.appendChild(el('span', 'track-dur', x.duration)); ol.appendChild(li); });
      body.appendChild(ol);
    }
    const vids = (r.videos || []).map(v => [v.title, safeUrl(v.url)]).filter(v => v[1]);
    if (vids.length) {
      body.appendChild(el('h3', 'panel-h', t.video));
      const ul = el('ul', 'panel-links');
      vids.forEach(([n, u]) => ul.appendChild(linkItem(n, u)));
      body.appendChild(ul);
    }
    if (r.credits && r.credits.length) {
      body.appendChild(el('h3', 'panel-h', t.credits));
      const dl = el('dl', 'panel-credits');
      r.credits.forEach(c => dl.append(el('dt', null, c.role), el('dd', null, c.name)));
      body.appendChild(dl);
    }
    closeBtn.setAttribute('aria-label', t.close);
    closeLbl.textContent = t.close;
  }

  // Desktop: Seitenpanel ohne Sperre (Wand und Jahresleiste bleiben bedienbar). Handy: bildschirmfüllend und modal.
  const wide = window.matchMedia('(min-width: 701px)');
  // Seitenpanel: darf über den Hero, bleibt aber immer unter dem Menü und über dem Footer frei
  const siteNav = document.querySelector('.site-nav');
  const siteFooter = document.querySelector('footer');
  let syncQueued = false;
  function syncTop() {
    syncQueued = false;
    const rail = document.getElementById('year-nav'), hero = document.querySelector('.hero-deco');
    if (!document.body.classList.contains('panel-side')) { panel.style.removeProperty('--panel-top'); panel.style.removeProperty('--panel-bottom'); if (rail) rail.classList.remove('behind-hero'); return; }
    // Jahresleiste ausblenden, solange sie über dem Hero (und dessen Infobox) läge
    if (rail && hero) rail.classList.toggle('behind-hero', hero.getBoundingClientRect().bottom > rail.getBoundingClientRect().top);
    const navBottom = siteNav ? Math.max(0, siteNav.getBoundingClientRect().bottom) : 0;
    const footTop = siteFooter ? siteFooter.getBoundingClientRect().top : innerHeight;
    panel.style.setProperty('--panel-top', navBottom + 'px');
    panel.style.setProperty('--panel-bottom', Math.max(0, innerHeight - footTop) + 'px');
  }
  const queueSync = () => { if (!syncQueued) { syncQueued = true; requestAnimationFrame(syncTop); } };
  window.addEventListener('scroll', queueSync, { passive: true });
  window.addEventListener('resize', queueSync);

  function open(id, from) {
    currentId = id; opener = from || null;
    render(id);
    panel.scrollTop = 0;
    if (!panel.open) {
      if (wide.matches) { panel.show(); closeBtn.focus({ preventScroll: true }); } else panel.showModal();
      document.body.classList.toggle('panel-side', wide.matches);
      syncTop();
      if (wide.matches && from) requestAnimationFrame(() => from.scrollIntoView({ block: 'nearest' })); // Kachel bleibt nach dem Umbruch im Bild
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
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    const o = opener;
    if (o && document.contains(o)) { o.focus({ preventScroll: true }); requestAnimationFrame(() => o.scrollIntoView({ block: 'nearest' })); }
    opener = null;
  }
  function close() { if (panel.open) { panel.close(); cleanup(); } }
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && panel.open) { e.preventDefault(); close(); } });
  panel.addEventListener('close', cleanup);
  closeBtn.addEventListener('click', close);
  panel.addEventListener('click', e => { if (e.target === panel) close(); }); // Klick auf Backdrop
  document.querySelectorAll('.release-open').forEach(b => b.addEventListener('click', () => open(b.dataset.id, b)));

  // Sprache: Datum und offenes Panel neu rendern
  const refreshDates = () => document.querySelectorAll('.release-date').forEach(t => { t.textContent = fmtDate(t.getAttribute('datetime')); });
  new MutationObserver(() => { refreshDates(); if (currentId) render(currentId); }).observe(root, { attributes: true, attributeFilter: ['lang'] });
  refreshDates();

  // Deep-Link #r-<id> beim Laden und bei Klick auf einen Link innerhalb der Seite (z. B. „Cover Art by“)
  const openFromHash = scroll => {
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
