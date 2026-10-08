'use strict';
(() => {
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 const easing = 'cubic-bezier(.22,1,.36,1)';
 // Keep native scrolling, touch momentum, keyboard navigation and browser history.
 // Progressive enhancement: content stays visible without JavaScript.
 const language = document.querySelector('.language-switch');
 if (language) {
  const summary = language.querySelector('summary');
  const panel = language.querySelector('.language-panel');
  let animation = null, desired = language.open;
  const setOpen = (open) => {
   desired = open;
   if (animation) { animation.cancel(); animation = null; }
   summary.setAttribute('aria-expanded', String(open));
   if (reduced.matches || !panel.animate) { language.open = open; return; }
   if (open) language.open = true;
   else if (!language.open) return;
   animation = panel.animate(open
    ? [{opacity:0,transform:'translateY(-8px) scale(.985)'},{opacity:1,transform:'translateY(0) scale(1)'}]
    : [{opacity:1,transform:'translateY(0) scale(1)'},{opacity:0,transform:'translateY(-5px) scale(.99)'}],
    {duration:open ? 260 : 170,easing,fill:'both'});
   const current = animation;
   animation.onfinish = () => { if (animation !== current) return; language.open = desired; animation.cancel(); animation = null; };
  };
  summary.setAttribute('aria-expanded',String(language.open));
  summary.addEventListener('click',event => { event.preventDefault(); setOpen(!desired); });
  document.addEventListener('click',event => { if (!language.contains(event.target) && desired) setOpen(false); });
  language.addEventListener('keydown',event => { if (event.key === 'Escape') { setOpen(false); summary.focus(); } });
  language.querySelectorAll('a').forEach(link => link.addEventListener('click',() => { link.hash = window.location.hash; }));
 }
 // Native details remains the semantic control; animate the actual height in both directions.
 document.querySelectorAll('.faq details, details.schedule').forEach(detail => {
  const summary = detail.querySelector('summary');
  let animation = null, desired = detail.open;
  summary.setAttribute('aria-expanded',String(desired));
  summary.addEventListener('click',event => {
   if (reduced.matches || !detail.animate) return;
   event.preventDefault();
   const start = detail.getBoundingClientRect().height;
   desired = !desired;
   if (animation) { animation.cancel(); animation = null; }
   detail.style.height = '';
   detail.open = desired;
   const end = detail.getBoundingClientRect().height;
   // Retain the content throughout a closing transition.
   detail.open = true;
   summary.setAttribute('aria-expanded',String(desired));
   detail.style.overflow = 'hidden';
   animation = detail.animate([{height:start+'px'},{height:end+'px'}],{duration:380,easing,fill:'both'});
   const current = animation;
   animation.onfinish = () => {
    if (animation !== current) return;
    detail.open = desired; animation.cancel(); animation = null;
    detail.style.removeProperty('overflow');
   };
  });
  detail.addEventListener('toggle',() => { if (!animation) { desired = detail.open; summary.setAttribute('aria-expanded',String(desired)); } });
 });
 if (reduced.matches || !('IntersectionObserver' in window)) return;
 const targets = document.querySelectorAll('.intro > *, .split > *, .section-head > *, .residence-row, .gallery .visual, .amenities > div, .payment-card, .benefits > article, .faq > div, .enquire > div, .article-content > h2, .article-content > p, .steps > li, .type-details > *, .type-related > a');
 const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
   if (!entry.isIntersecting) return;
   entry.target.classList.add('motion-visible');
   observer.unobserve(entry.target);
  });
 }, {threshold:0.08,rootMargin:'0px 0px -24px 0px'});
 targets.forEach(element => {
  const rect = element.getBoundingClientRect();
  // No flash or invisible current section on restored scroll positions / direct anchors.
  if (rect.bottom <= 0 || rect.top < window.innerHeight * .94) return;
  element.classList.add('motion-reveal');
  const parent = element.parentElement;
  if (parent.matches('.gallery,.payment-grid,.benefits,.amenities')) {
   const index = [...parent.children].indexOf(element);
   element.style.setProperty('--reveal-delay', Math.min(index % 3 * 75,150)+'ms');
  }
  observer.observe(element);
 });
 const hero = document.querySelector('.hero-copy, .type-hero-copy');
 if (hero && window.scrollY < 100 && hero.animate) {
  [...hero.children].forEach((el,i) => el.animate([
   {opacity:0,transform:'translateY(24px)'},{opacity:1,transform:'translateY(0)'}
  ],{duration:950,delay:100+i*130,easing,fill:'backwards'}));
 }
 // Small image drift only on a desktop pointer. At most one update per animation frame,
 // and only images in view are measured. No scroll interception or mobile parallax.
 const desktop = window.matchMedia('(min-width: 900px) and (pointer: fine)');
 const active = new Set();
 const images = [...document.querySelectorAll('.hero > .visual, .fullbleed > .visual, .split > .visual, .type-hero > .visual')];
 let frame = 0;
 const updateImages = () => {
  frame = 0;
  if (!desktop.matches || reduced.matches) return;
  active.forEach(visual => {
   const r = visual.getBoundingClientRect();
   const progress = Math.max(-1,Math.min(1,(innerHeight / 2 - (r.top+r.height/2)) / innerHeight));
   visual.style.setProperty('--image-drift',(progress*24).toFixed(2)+'px');
  });
 };
 const requestFrame = () => { if (!frame && desktop.matches && !reduced.matches) frame = requestAnimationFrame(updateImages); };
 const imageObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => entry.isIntersecting ? active.add(entry.target) : active.delete(entry.target));
  requestFrame();
 });
 images.forEach(image => { image.classList.add('motion-image'); imageObserver.observe(image); });
 window.addEventListener('scroll',requestFrame,{passive:true});
 window.addEventListener('resize',requestFrame,{passive:true});
 reduced.addEventListener('change',event => {
  if (!event.matches) return;
  observer.disconnect(); imageObserver.disconnect();
  document.querySelectorAll('.motion-reveal').forEach(el => el.classList.add('motion-visible'));
  images.forEach(el => el.style.removeProperty('--image-drift'));
  document.getAnimations().forEach(animation => animation.finish());
 });
})();
