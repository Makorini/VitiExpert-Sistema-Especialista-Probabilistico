/* VitiExpert — alternância exclusiva da foto de fundo da página Início. */
(() => {
  'use strict';
  const script = document.currentScript;
  const hero = document.querySelector('body.page-home .hero');
  if (!script || !hero) return;

  const photos = ['home-01.jpg', 'home-02.jpg', 'home-03.jpg', 'home-04.jpg', 'home-05.jpg']
    .map(name => new URL(`home-slides/${name}`, script.src).href);
  const CHANGE_INTERVAL_MS = 3 * 60 * 1000;
  const FADE_DURATION_MS = 1700;
  let currentIndex = 0;
  let activeLayer = null;
  let changing = false;

  function rotateBackground() {
    if (changing || document.hidden) return;
    changing = true;
    const nextIndex = (currentIndex + 1) % photos.length;
    const nextImage = new Image();
    nextImage.onload = () => {
      const nextLayer = document.createElement('div');
      nextLayer.className = 'home-slide';
      nextLayer.setAttribute('aria-hidden', 'true');
      nextLayer.style.backgroundImage = `url("${photos[nextIndex]}")`;
      const shade = hero.querySelector('.hero-shade');
      if (!shade) { changing = false; return; }
      hero.insertBefore(nextLayer, shade);
      // Wait two frames so the new background fades over the previous one.
      requestAnimationFrame(() => requestAnimationFrame(() => {
        nextLayer.classList.add('is-visible');
      }));
      window.setTimeout(() => {
        if (activeLayer) activeLayer.remove();
        activeLayer = nextLayer;
        currentIndex = nextIndex;
        changing = false;
      }, FADE_DURATION_MS);
    };
    nextImage.onerror = () => { changing = false; };
    nextImage.src = photos[nextIndex];
  }

  window.setInterval(rotateBackground, CHANGE_INTERVAL_MS);
})();
