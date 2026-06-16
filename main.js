// Nav toggle
const toggle = document.getElementById('nav-toggle');
const nav = document.getElementById('nav-links');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    toggle.classList.toggle('open');
    nav.classList.toggle('open');
  });
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
