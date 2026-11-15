/* VitiExpert — área de conta.
 * 1. Botão de olho: mostra/oculta a senha (login e cadastro).
 * 2. Tooltip dos gráficos do histórico (hover e foco por teclado).
 */
(() => {
  'use strict';

  /* ---------- 1. Mostrar / ocultar senha ---------- */
  document.querySelectorAll('.acc-eye').forEach(button => {
    const input = document.getElementById(button.getAttribute('aria-controls'));
    if (!input) return;
    button.addEventListener('click', () => {
      const showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';
      const label = showing ? button.dataset.show : button.dataset.hide;
      button.setAttribute('aria-pressed', String(!showing));
      button.setAttribute('aria-label', label);
      button.title = label;
      // Mantém o cursor no campo, no fim do texto digitado.
      input.focus({ preventScroll: true });
      const end = input.value.length;
      try { input.setSelectionRange(end, end); } catch (_) { /* tipos sem seleção */ }
    });
  });
  // Por segurança, a senha volta a ficar oculta ao enviar o formulário.
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      form.querySelectorAll('.acc-pass input').forEach(input => { input.type = 'password'; });
    });
  });

  /* ---------- 2. Tamanho das barras dos gráficos ----------
   * O servidor envia a porcentagem em data-width / data-height (sem CSS
   * inline no template); aqui ela vira a largura ou a altura da barra. */
  const percent = value => {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(100, Math.max(0, number)) + '%' : '0%';
  };
  document.querySelectorAll('[data-width]').forEach(bar => { bar.style.width = percent(bar.dataset.width); });
  document.querySelectorAll('[data-height]').forEach(bar => { bar.style.height = percent(bar.dataset.height); });

  /* ---------- 3. Tooltip dos gráficos ---------- */
  const tip = document.getElementById('acc-tooltip');
  if (!tip) return;
  const marks = document.querySelectorAll('[data-tip]');

  const show = (el, x, y) => {
    tip.textContent = el.dataset.tip;
    tip.hidden = false;
    const box = tip.getBoundingClientRect();
    const left = Math.min(Math.max(8, x - box.width / 2), window.innerWidth - box.width - 8);
    const top = y - box.height - 12 < 8 ? y + 16 : y - box.height - 12;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  };
  const hide = () => { tip.hidden = true; };

  marks.forEach(el => {
    el.addEventListener('mousemove', e => show(el, e.clientX, e.clientY));
    el.addEventListener('mouseleave', hide);
    el.addEventListener('focus', () => {
      const r = el.getBoundingClientRect();
      show(el, r.left + r.width / 2, r.top);
    });
    el.addEventListener('blur', hide);
  });
  window.addEventListener('scroll', hide, { passive: true });
})();
