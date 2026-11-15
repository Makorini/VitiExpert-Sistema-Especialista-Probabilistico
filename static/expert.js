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

  const formatCondition = condition => {
    const answer = condition.value === 'sim' ? tr('yes','Sim') : tr('no','Não');
    return condition.description + ' — ' + answer;
  };

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
      const highest = items[0].confidence_percent;
      const tied = items.length > 1 && items[1].confidence_percent === highest;
      items.forEach(item => {
        const card = make('article','tcc-result-card');
        if (item.confidence_percent === highest) {
          const badge = tied ? tr('tied_highest','Maior confiança — empate') : tr('main_hypothesis','Hipótese principal');
          card.append(make('div','tcc-result-tag',badge));
        }
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
        const observed = new Set();
        for (const rule of item.fired_rules) {
          for (const condition of rule.conditions) {
            if (observed.has(condition.id)) continue;
            observed.add(condition.id);
            ul.append(make('li','',formatCondition(condition)));
          }
        }
        card.append(ul);
        const detail = make('details','tcc-rules-summary');
        detail.append(make('summary','',tr('show_rules','Ver regras e fatores considerados')));
        (item.fired_rules || []).forEach(rule => {
          const segment=make('div','tcc-rule-detail');
          segment.append(make('strong','',rule.id + ' · ' + tr('rule_confidences','Fatores da regra') + ': ' + (rule.conclusion_factors_percent || []).map(percent).join(' + ')));
          if (rule.premise_percent !== undefined) {
            segment.append(make('p','',tr('premise','Certeza combinada das respostas (produto)') + ': ' + percent(rule.premise_percent) + ' → ' + percent(rule.confidence_percent)));
          }
          const conditions = make('ul','');
          (rule.conditions || []).forEach(c => {
            conditions.append(make('li','',formatCondition(c)));
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
    // Histórico: confirma o salvamento ou convida a entrar na conta.
    const saved = make('p','tcc-saved-note');
    if (data.saved) {
      saved.textContent = tr('saved_note','Consulta salva no seu histórico.');
      saved.append(' ');
      const link = make('a','',tr('account_link','↗'));
      link.href = '/account?lang=' + encodeURIComponent(locale);
      saved.append(link);
    } else {
      const link = make('a','',tr('login_to_save','Entre na sua conta para salvar as consultas.'));
      link.href = '/login?lang=' + encodeURIComponent(locale) + '&next=' + encodeURIComponent('/expert?lang=' + locale);
      saved.append(link);
    }
    output.append(saved);
    output.append(make('p','tcc-warning',data.disclaimer || tr('warning','Ferramenta educativa.')));
    output.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  };

  // Certeza do usuário (c1): aparece só quando a resposta é Sim ou Não.
  const syncCertainty = question => {
    const box = question.querySelector('.tcc-certainty');
    const checked = question.querySelector('input[type="radio"]:checked');
    if (box) box.hidden = !checked || checked.value === 'nao_sei';
  };
  form.addEventListener('change', event => {
    const question = event.target.closest('.tcc-question');
    if (question && event.target.type === 'radio') syncCertainty(question);
  });
  form.addEventListener('input', event => {
    if (event.target.matches('input[data-certainty-for]')) {
      event.target.nextElementSibling.textContent = event.target.value + '%';
    }
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const answers = {};
    const certainties = {};
    form.querySelectorAll('input[type="radio"]:checked').forEach(input => {answers[input.name] = input.value;});
    form.querySelectorAll('input[data-certainty-for]').forEach(input => {
      const id = input.dataset.certaintyFor;
      if (answers[id] && answers[id] !== 'nao_sei') certainties[id] = Number(input.value);
    });
    output.hidden = false;
    output.replaceChildren(make('p','tcc-results-note',tr('loading','Analisando respostas...')));
    try {
      const response = await fetch('/api/diagnose?lang=' + encodeURIComponent(locale),{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers, certainties})
      });
      const data=await response.json();
      if (!response.ok) throw new Error(data.error || String(response.status));
      showResult(data);
    } catch (e) {
      output.replaceChildren(make('p','tcc-warning',tr('analysis_error','Não foi possível analisar as respostas:')+' '+e.message));
    }
  });
  form.addEventListener('reset',()=>{
    output.hidden=true;output.replaceChildren();
    setTimeout(()=>form.querySelectorAll('.tcc-question').forEach(q=>{
      syncCertainty(q);
      const out=q.querySelector('.tcc-certainty output'); if (out) out.textContent='100%';
    }));
  });
})();
