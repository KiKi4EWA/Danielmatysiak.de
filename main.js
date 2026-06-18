// Hero — seitenspezifische Bildrotation
const heroDecoEl = document.querySelector('.hero-deco-full, .hero-deco-portrait');
if (heroDecoEl) {
  const imgSets = {
    'page-home':  ['img/index_hero2.png', 'img/index_hero3.png'],
    'page-audio': ['img/audio_hero2.png', 'img/audio_hero3.png', 'img/audio_hero4.png', 'img/audio_hero5.png'],
    'page-lab':   ['img/lab_hero3.png', 'img/lab_hero4.png'],
    'page-faq':   ['img/faq_hero1.png', 'img/faq_hero2.png', 'img/faq_hero3.png'],
  };
  const key = Object.keys(imgSets).find(k => document.body.classList.contains(k));
  if (key) heroDecoEl.src = imgSets[key][Math.floor(Math.random() * imgSets[key].length)];
}

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
