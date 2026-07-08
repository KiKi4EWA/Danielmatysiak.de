// Hero — seitenspezifische Bildrotation + randomisierte Anker-Position
const heroDecoEl = document.querySelector('.hero-deco-full, .hero-deco-portrait');
const noMotionGlobal = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (heroDecoEl) {
  const imgSets = {
    'page-home':    ['img/index_hero3.webp'],
    'page-audio':   ['img/audio_neve.webp', 'img/audio_hero3.webp', 'img/audio_hero4.webp', 'img/audio_hero5.webp', 'img/audio_hero6.webp'],
    'page-lab':     ['img/lab_hero3.webp', 'img/lab_hero4.webp'],
    'page-faq':     ['img/faq_hero1.webp', 'img/faq_hero2.webp', 'img/faq_hero3.webp'],
    'page-contact': ['img/kontakt_hero1.webp', 'img/kontakt_hero3.webp', 'img/kontakt_hero5.webp'],
    'page-about':   ['img/about_hero.webp'],
  };
  const key = Object.keys(imgSets).find(k => document.body.classList.contains(k));
  if (key) {
    heroDecoEl.src = imgSets[key][Math.floor(Math.random() * imgSets[key].length)];

    // Für home: zufällig right center oder center
    if (key === 'page-home') {
      heroDecoEl.style.objectPosition = Math.random() > 0.4 ? 'right center' : 'center';
    }
    // Für audio: feste Position je Bild; Pro Tools (hero5) zufällig left/right
    if (key === 'page-audio') {
      const src = heroDecoEl.src;
      if (src.includes('audio_neve'))  heroDecoEl.style.objectPosition = 'center right';
      else if (src.includes('audio_hero3')) heroDecoEl.style.objectPosition = Math.random() > 0.5 ? 'center' : 'right top';
      else if (src.includes('audio_hero4')) heroDecoEl.style.objectPosition = Math.random() > 0.5 ? 'left center' : 'right center';
      else if (src.includes('audio_hero5')) heroDecoEl.style.objectPosition = Math.random() > 0.5 ? 'left center' : 'right center';
      else if (src.includes('audio_hero6')) heroDecoEl.style.objectPosition = 'center';
    }
    // Lab: drei Optionen gleichverteilt, immer top damit oben nichts abgeschnitten wird
    if (key === 'page-lab') {
      const labPositions = ['right top', 'center top', 'left top'];
      heroDecoEl.style.objectPosition = labPositions[Math.floor(Math.random() * labPositions.length)];
    }
  }
}

// Parallax — subtiler Tiefeneffekt für home/audio/lab full-bleed hero (nur Desktop)
(function () {
  const parallaxPages = ['page-home', 'page-audio', 'page-lab'];
  if (!parallaxPages.some(k => document.body.classList.contains(k))) return;
  if (noMotionGlobal) return;
  if (window.matchMedia('(pointer: coarse)').matches) return; // kein Parallax auf Touch
  const img = document.querySelector('.hero-deco-img.hero-deco-full');
  if (!img) return;

  // Bild größer als Container, Überlauf unten → Parallax nach oben (oben nie abgeschnitten)
  img.style.height = '115%';
  img.style.top = '0';
  img.style.willChange = 'transform';

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      img.style.transform = `translateY(${-window.scrollY * 0.12}px)`;
      ticking = false;
    });
  }, { passive: true });
})();

// Swipe navigation — spring-based drag (Emil: page follows finger, spring-snap on release)
(function () {
  const ORDER = ['index.html', 'leistungen.html', 'lab.html', 'about.html', 'faq.html', 'kontakt.html'];
  const CLASS_MAP = {
    'page-home':    'index.html',
    'page-audio':   'leistungen.html',
    'page-lab':     'lab.html',
    'page-about':   'about.html',
    'page-faq':     'faq.html',
    'page-contact': 'kontakt.html',
  };

  const pageEl   = document.querySelector('.page');
  const noMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const SPRING   = 'cubic-bezier(0.32, 0.72, 0, 1)';

  // Entry animation: incoming page slides in from correct side
  const entryDir = sessionStorage.getItem('swipe-dir');
  if (entryDir && pageEl && !noMotion) {
    pageEl.dataset.entering = entryDir;
    pageEl.addEventListener('animationend', () => delete pageEl.dataset.entering, { once: true });
  }
  sessionStorage.removeItem('swipe-dir');

  const cur = Object.entries(CLASS_MAP).find(([c]) => document.body.classList.contains(c))?.[1];
  const idx = ORDER.indexOf(cur);
  if (idx === -1) return;

  let x0 = 0, y0 = 0, t0 = 0, active = false;

  function springBack() {
    if (!pageEl || noMotion) return;
    pageEl.style.transition = `transform 420ms ${SPRING}`;
    pageEl.style.transform  = '';
    setTimeout(() => { pageEl.style.transition = ''; }, 440);
  }

  document.addEventListener('touchstart', e => {
    if (e.target.closest('input, textarea, select, details, [data-no-swipe]')) return;
    x0 = e.touches[0].clientX;
    y0 = e.touches[0].clientY;
    t0 = Date.now();
    active = true;
    if (pageEl) pageEl.style.transition = '';
  }, { passive: true });

  document.addEventListener('touchmove', e => {
    if (!active) return;
    const dx = e.touches[0].clientX - x0;
    const dy = Math.abs(e.touches[0].clientY - y0);
    if (dy > Math.abs(dx) + 8) { active = false; springBack(); return; }
    if (noMotion || !pageEl) return;
    // Page follows finger; extra damping at first/last page boundary
    const atEdge = (dx > 0 && idx === 0) || (dx < 0 && idx === ORDER.length - 1);
    pageEl.style.transform = `translateX(${dx * (atEdge ? 0.15 : 0.45)}px)`;
  }, { passive: true });

  document.addEventListener('touchend', e => {
    if (!active) { active = false; return; }
    active = false;
    const dx  = e.changedTouches[0].clientX - x0;
    const dy  = e.changedTouches[0].clientY - y0;
    const vel = Math.abs(dx) / (Date.now() - t0);

    if (Math.abs(dy) > Math.abs(dx) || (Math.abs(dx) < 55 && vel < 0.35)) {
      springBack(); return;
    }
    const next = dx < 0 ? idx + 1 : idx - 1;
    if (next < 0 || next >= ORDER.length) { springBack(); return; }

    // Save direction so incoming page knows which side to enter from
    sessionStorage.setItem('swipe-dir', dx < 0 ? 'from-right' : 'from-left');

    if (pageEl && !noMotion) {
      pageEl.style.transition = `transform 300ms ${SPRING}`;
      pageEl.style.transform  = `translateX(${dx < 0 ? -window.innerWidth : window.innerWidth}px)`;
      setTimeout(() => { location.href = ORDER[next]; }, 280);
    } else {
      location.href = ORDER[next];
    }
  }, { passive: true });
})();

// Nav toggle
const toggle = document.getElementById('nav-toggle');
const nav = document.getElementById('nav-links');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    toggle.classList.toggle('open');
    nav.classList.toggle('open');
  });
}

// Language toggle
const langBtn = document.getElementById('lang-btn');
if (langBtn) {
  let lang = localStorage.getItem('lang') || 'de';
  const deCache = new Map();

  const dePlaceholderCache = new Map();

  function applyLang(l) {
    lang = l;
    localStorage.setItem('lang', l);
    document.documentElement.lang = l;
    langBtn.textContent = l === 'de' ? 'EN' : 'DE';
    document.querySelectorAll('[data-en]').forEach(el => {
      if (!deCache.has(el)) deCache.set(el, el.innerHTML);
      el.innerHTML = l === 'en' ? el.dataset.en : deCache.get(el);
    });
    document.querySelectorAll('[data-en-placeholder]').forEach(el => {
      if (!dePlaceholderCache.has(el)) dePlaceholderCache.set(el, el.placeholder);
      el.placeholder = l === 'en' ? el.dataset.enPlaceholder : dePlaceholderCache.get(el);
    });
  }

  // Cache original DE before any swap
  document.querySelectorAll('[data-en]').forEach(el => {
    deCache.set(el, el.innerHTML);
  });
  document.querySelectorAll('[data-en-placeholder]').forEach(el => {
    dePlaceholderCache.set(el, el.placeholder);
  });

  langBtn.addEventListener('click', () => applyLang(lang === 'de' ? 'en' : 'de'));
  langBtn.textContent = lang === 'de' ? 'EN' : 'DE';
  if (lang === 'en') applyLang('en');
}

// Scroll reveal — skip if reduced motion preferred
if (window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
  const sel = [
    '.section h2',
    '.section .eyebrow',
    '.section .section-intro',
    '.lab-module',
    '.lab-phase',
    '.price-row',
    '.pillar',
    '.value-item',
    '.releases-block',
  ].join(', ');

  const els = [...document.querySelectorAll(sel)];

  // Stagger siblings within the same parent container
  const seen = new Set();
  els.forEach(el => {
    const p = el.parentElement;
    if (seen.has(p)) return;
    seen.add(p);
    const group = els.filter(e => e.parentElement === p);
    if (group.length > 1) {
      group.forEach((e, i) => { e.style.transitionDelay = `${i * 45}ms`; });
    }
  });

  els.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) {
        target.classList.add('is-visible');
        io.unobserve(target);
      }
    });
  }, { threshold: 0.08 });

  els.forEach(el => io.observe(el));
}

// Mobile tap-highlight für erste 3 Seiten (divs bekommen kein iOS hover)
if (window.matchMedia('(pointer: coarse)').matches) {
  const tapMap = {
    'page-home':  '.chapter-item',
    'page-audio': '.price-row',
    'page-lab':   '.lab-module',
  };
  const pageKey = Object.keys(tapMap).find(k => document.body.classList.contains(k));
  if (pageKey) {
    const els = [...document.querySelectorAll(tapMap[pageKey])];
    els.forEach(el => {
      el.addEventListener('touchstart', () => {
        const already = el.classList.contains('tapped');
        els.forEach(o => o.classList.remove('tapped'));
        if (!already) el.classList.add('tapped');
      }, { passive: true });
    });
  }
}

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
