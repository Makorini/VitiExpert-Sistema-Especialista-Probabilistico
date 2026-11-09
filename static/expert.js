/* VitiExpert — interface para regras originais e complementares em Python.
 * O browser apenas apresenta dados retornados pelo motor Python.
 * Executa exclusivamente na página /expert.
 */
(() => {
  "use strict";
  const form = document.getElementById('tcc-diagnose-form');
  const output = document.getElementById('tcc-diagnosis-results');
  if (!form || !output) return;
  const locale = (document.documentElement.lang || 'pt').slice(0, 2);
  const meta = document.getElementById('viti-config');
  let dict = {};
  try { dict = JSON.parse(meta?.dataset.expertTranslations || '{}'); } catch (_) {}
  const tr = (key, fallback) => dict[key] || fallback;
  const format = {pt:'pt-BR',en:'en-US',es:'es-ES'}[locale] || 'pt-BR';
  const make = (tag, name, content) => {
    const el = document.createElement(tag);
    if (name) el.className = name;
    if (content !== undefined) el.textContent = String(content);
    return el;
  };
  const percent = value => Number(value).toLocaleString(format, {maximumFractionDigits:1}) + '%';

  const showResult = data => {
    output.replaceChildren();
    output.hidden = false;
    output.append(make('p','tcc-eyebrow',tr('result_step','02 / RESULTADO')));
    output.append(make('h2','',tr('result_title','Hipóteses identificadas')));
    output.append(make('p','tcc-results-note',tr('result_intro','A análise considera os sintomas informados e apresenta hipóteses compatíveis.')));

    const items = data.results || [];
    if (!items.length) {
      output.append(make('p','tcc-warning',data.message || tr('no_results','Nenhuma regra completa foi acionada.')));
    } else {
      output.append(make('h3','tcc-sinta-section-title',tr('probability_title','Nível de confiança do sistema (CNF)')));
      const list = make('div','tcc-result-list');
      items.forEach((item,index) => {
        const card = make('article','tcc-result-card');
        if (index === 0) card.append(make('div','tcc-result-tag',tr('main_hypothesis','Hipótese principal')));
        const head = make('div','tcc-sinta-head');
        head.append(make('h3','',item.name));
        head.append(make('strong','tcc-sinta-confidence',percent(item.confidence_percent)));
        card.append(head);
        const track = make('div','tcc-probability-track');
        const fill = make('span','tcc-probability-fill');
        fill.style.width = Math.max(0,Math.min(100,Number(item.confidence_percent)))+'%';
        track.append(fill); card.append(track);
        card.append(make('p','tcc-sinta-subtitle',tr('confidence_method','Fatores de Certeza do Expert SINTA')));
        card.append(make('p','tcc-sinta-evidence-title',tr('associated_signs','Condições observadas:')));
        const ul = make('ul','');
        (item.evidence || []).forEach(e => ul.append(make('li','',e)));
        card.append(ul);
        const detail = make('details','tcc-rules-summary');
        detail.append(make('summary','',tr('show_rules','Ver regras e fatores considerados')));
        (item.fired_rules || []).forEach(rule => {
          const segment=make('div','tcc-rule-detail');
          segment.append(make('strong','',rule.id + ' · ' + tr('rule_confidences','Fatores da regra') + ': ' + (rule.conclusion_factors_percent || []).map(percent).join(' + ')));
          const conditions = make('ul','');
          (rule.conditions || []).forEach(c => {
            const required = c.value === 'sim' ? tr('yes','Sim') : tr('no','Não');
            conditions.append(make('li','',c.description + ' — ' + required));
          });
          segment.append(conditions);
          detail.append(segment);
        });
        card.append(detail);
        list.append(card);
      });
      output.append(list);
      output.append(make('p','tcc-probability-disclaimer',tr('other_note','Os valores não precisam somar 100%.')));
    }
    if (data.suggested_questions?.length) {
      const div=make('section','tcc-suggestions');
      div.append(make('h3','',tr('suggestions','Perguntas que podem completar uma regra')));
      const ul=make('ul','');
      data.suggested_questions.forEach(s => ul.append(make('li','',s.text)));
      div.append(ul);output.append(div);
    }
    output.append(make('p','tcc-warning',data.disclaimer || tr('warning','Ferramenta educativa.')));
    output.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  };

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const answers = {};
    form.querySelectorAll('input[type="radio"]:checked').forEach(input => {answers[input.name] = input.value;});
    output.hidden = false;
    output.replaceChildren(make('p','tcc-results-note',tr('loading','Analisando respostas...')));
    try {
      const response = await fetch('/api/diagnose?lang=' + encodeURIComponent(locale),{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers})
      });
      const data=await response.json();
      if (!response.ok) throw new Error(data.error || String(response.status));
      showResult(data);
    } catch (e) {
      output.replaceChildren(make('p','tcc-warning',tr('analysis_error','Não foi possível analisar as respostas:')+' '+e.message));
    }
  });
  form.addEventListener('reset',()=>{output.hidden=true;output.replaceChildren();});
})();
