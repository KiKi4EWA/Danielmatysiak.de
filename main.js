// Hero — seitenspezifische Bildrotation + randomisierte Anker-Position
const heroDecoEl = document.querySelector('.hero-deco-full, .hero-deco-portrait');
const noMotionGlobal = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (heroDecoEl) {
  const imgSets = {
    'page-home':    ['img/index_hero2.png', 'img/index_hero3.png'],
    'page-audio':   ['img/audio_hero2.png', 'img/audio_hero3.png', 'img/audio_hero4.png', 'img/audio_hero5.png', 'img/audio_hero6.png'],
    'page-lab':     ['img/lab_hero3.png', 'img/lab_hero4.png'],
    'page-faq':     ['img/faq_hero1.png', 'img/faq_hero2.png', 'img/faq_hero3.png'],
    'page-contact': ['img/kontakt_hero1.png', 'img/kontakt_hero3.png', 'img/kontakt_hero5.png'],
    'page-about':   ['img/about_hero.png'],
  };
  const key = Object.keys(imgSets).find(k => document.body.classList.contains(k));
  if (key) {
    heroDecoEl.src = imgSets[key][Math.floor(Math.random() * imgSets[key].length)];

    // Für home/audio/lab: rechte Seite dominant, zufällig center oder right center
    if (['page-home', 'page-audio', 'page-lab'].includes(key)) {
      heroDecoEl.style.objectPosition = Math.random() > 0.4 ? 'right center' : 'center';
    }
  }
}

// Parallax — subtiler Tiefeneffekt für home/audio/lab full-bleed hero
(function () {
  const parallaxPages = ['page-home', 'page-audio', 'page-lab'];
  if (!parallaxPages.some(k => document.body.classList.contains(k))) return;
  if (noMotionGlobal) return;
  const img = document.querySelector('.hero-deco-img.hero-deco-full');
  if (!img) return;

  // Bild etwas größer als Container → Parallax-Spielraum
  img.style.height = '115%';
  img.style.top = '-7.5%';
  img.style.willChange = 'transform';

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      img.style.transform = `translateY(${window.scrollY * 0.2}px)`;
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
