/* VitiExpert · Ficha da doença (painel) usada em dois lugares:
   no catálogo Doenças e Pragas e no resultado do Sistema Especialista.
   Dados: diseases-data.js, catalog-i18n.js e disease-treatments.js. */
(() => {
  'use strict';
  const dialog = document.getElementById('dv-dialog');
  const body = document.getElementById('dv-modal-body');
  const closeButton = document.getElementById('dv-close');
  if (!dialog || !body) return;

  const lang = ['pt', 'en', 'es'].includes(document.documentElement.lang) ? document.documentElement.lang : 'pt';
  const t = {
    pt: {
      symptoms:'Como reconhecer', differential:'Sinais parecidos e diferenças', observation:'O que observar no vinhedo', affected:'Partes afetadas',
      treatment:'Como tratar', treatmentNote:'Use apenas produtos registrados para a videira, com receituário de engenheiro agrônomo, e respeite o prazo de carência.',
      gallery:'Ver galeria oficial da Embrapa ↗︎', noPhoto:'Fotografia disponível na fonte oficial', imageCredit:'Foto: Embrapa Uva e Vinho',
      scientific:'Agente ou referência', notice:'A imagem, sozinha, não confirma a causa. Consulte um profissional quando necessário.',
      quarantineAlert:'ATENÇÃO: praga quarentenária ausente no Brasil; suspeitas devem ser comunicadas à defesa agropecuária.', close:'Fechar ficha',
      groups:{'Doenças':'Doenças','Pragas':'Pragas','Viroses':'Viroses','Nutrição':'Nutrição','Distúrbios':'Outros danos','Quarentenárias':'Alerta fitossanitário'}
    },
    en: {
      symptoms:'How to recognize', differential:'Similar signs and differences', observation:'What to check in the vineyard', affected:'Affected parts',
      treatment:'How to treat', treatmentNote:'Only use products registered for grapevines, prescribed by an agronomist, and respect the pre-harvest interval.',
      gallery:'See official Embrapa gallery ↗︎', noPhoto:'Photographs available at the official source', imageCredit:'Photo: Embrapa Uva e Vinho',
      scientific:'Agent / reference', notice:'A photograph alone cannot confirm the cause. Professional assessment may be necessary.',
      quarantineAlert:'WARNING: quarantine pest classified as absent from Brazil; suspected findings should be reported to the official plant-health authority.', close:'Close',
      groups:{'Doenças':'Diseases','Pragas':'Pests','Viroses':'Viruses','Nutrição':'Nutrition','Distúrbios':'Other damage','Quarentenárias':'Quarantine alert'}
    },
    es: {
      symptoms:'Cómo reconocer', differential:'Signos similares y diferencias', observation:'Qué observar en el viñedo', affected:'Partes afectadas',
      treatment:'Cómo tratar', treatmentNote:'Use solo productos registrados para la vid, con receta de un ingeniero agrónomo, y respete el plazo de seguridad.',
      gallery:'Ver galería oficial de Embrapa ↗︎', noPhoto:'Fotografías disponibles en la fuente oficial', imageCredit:'Foto: Embrapa Uva e Vinho',
      scientific:'Agente o referencia', notice:'Una fotografía por sí sola no confirma la causa. Puede ser necesaria una evaluación profesional.',
      quarantineAlert:'ATENCIÓN: plaga cuarentenaria ausente en Brasil; las sospechas deben comunicarse a las autoridades fitosanitarias.', close:'Cerrar',
      groups:{'Doenças':'Enfermedades','Pragas':'Plagas','Viroses':'Virus','Nutrição':'Nutrición','Distúrbios':'Otros daños','Quarentenárias':'Alerta fitosanitario'}
    }
  }[lang];

  const el = (tag, classes = '', text) => {
    const x = document.createElement(tag);
    if (classes) x.className = classes;
    if (text !== undefined) x.textContent = text;
    return x;
  };

  // Partes da planta: o catálogo guarda em português; traduz só para exibir.
  const translateOrgan = organ => {
    if (lang === 'pt') return organ;
    const source = {
      en:{'Folhas':'Leaves','Brotos':'Shoots','Ramos':'Shoots','Cachos':'Clusters','Bagas':'Berries','Raízes':'Roots','Tronco':'Trunk','Flores':'Flowers','Gemas':'Buds'},
      es:{'Folhas':'Hojas','Brotos':'Brotes','Ramos':'Ramas','Cachos':'Racimos','Bagas':'Bayas','Raízes':'Raíces','Tronco':'Tronco','Flores':'Flores','Gemas':'Yemas'}
    }[lang];
    let out = String(organ || '');
    for (const [pt, tr] of Object.entries(source)) out = out.replace(new RegExp(pt, 'gi'), tr);
    return out.replace(/Raízes/g, source['Raízes']).replace(/ e /g, lang === 'en' ? ' and ' : ' y ');
  };

  // Ficha no idioma da página, sem alterar os dados originais.
  const find = id => (window.VITI_DISEASES || []).find(item => item.id === id);
  const view = id => {
    const base = find(id);
    if (!base) return null;
    const item = {...base, ...((lang !== 'pt' && window.VITI_CATALOG_I18N?.[lang]?.[id]) || {})};
    item.organs = translateOrgan(base.organs_pt || base.organs);
    item.treatment = window.VITI_TREATMENTS?.[lang]?.[id] || '';
    return item;
  };

  function photo(item, large = false) {
    const wrap = el('div', large ? 'dv-modal-photo' : 'dv-card-photo');
    const fallback = el('div', 'dv-fallback');
    const official = el('a', 'dv-fallback-link', t.gallery);
    official.href = item.source; official.target = '_blank'; official.rel = 'noopener noreferrer';
    fallback.append(el('b', '', '❧'), el('span', '', t.noPhoto), official);
    wrap.append(fallback);
    if (item.photo) {
      const img = el('img');
      img.src = item.photo; img.alt = `${item.name} — ${t.imageCredit}`;
      img.loading = large ? 'eager' : 'lazy'; img.referrerPolicy = 'no-referrer';
      const credit = el('span', 'dv-photo-credit', t.imageCredit);
      img.onerror = () => { img.hidden = true; fallback.style.display = 'flex'; credit.hidden = true; };
      img.addEventListener('load', () => { fallback.style.display = 'none'; });
      wrap.append(img, credit);
    }
    return wrap;
  }

  const info = (title, content, classes = '') => {
    const section = el('section', 'dv-info' + (classes ? ' ' + classes : ''));
    section.append(el('h3', '', title), el('p', '', content));
    return section;
  };

  let trigger = null;
  function open(id, from) {
    const item = view(id);
    if (!item) return false;
    trigger = from || null;
    body.replaceChildren(photo(item, true));
    const inner = el('div', 'dv-modal-inner');
    const tag = el('span', 'dv-tag' + (item.quarantine ? ' quarantine' : ''), t.groups[item.group] || item.group);
    const title = el('h2', '', item.name);
    title.id = 'dv-modal-title';
    inner.append(tag, title, el('p', 'dv-agent', `${t.scientific}: ${item.agent}`));
    if (item.quarantine) inner.append(el('p', 'dv-alert', t.quarantineAlert));
    const columns = el('div', 'dv-modal-columns');
    columns.append(info(t.symptoms, item.signs), info(t.differential, item.differential),
      info(t.observation, item.monitoring), info(t.affected, item.organs));
    if (item.treatment) {
      const treat = info(t.treatment, item.treatment, 'dv-info-wide dv-info-treat');
      treat.append(el('small', 'dv-treat-note', t.treatmentNote));
      columns.append(treat);
    }
    inner.append(columns);
    const row = el('div', 'dv-source-row');
    const link = el('a', '', t.gallery);
    link.href = item.source; link.target = '_blank'; link.rel = 'noopener noreferrer';
    row.append(link, el('span', 'dv-source-note', t.notice));
    inner.append(row);
    body.append(inner);
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
    body.scrollTop = 0;
    closeButton?.focus();
    return true;
  }

  closeButton?.setAttribute('aria-label', t.close);
  closeButton?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { trigger?.focus(); trigger = null; });

  window.VitiSheet = {open, photo, has: id => Boolean(find(id))};
})();
