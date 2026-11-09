/* VitiExpert · Catálogo isolado da seção /diseases.
   Sem modificar ou depender do mecanismo de inferência do Sistema Especialista. */
(() => {
  'use strict';
  const lead = ['mildio','oidio','antracnose','pod_cinzenta','pod_uva_madura','ferrugem','cancro','cocho_farinhenta','perola','tripes','defic_mg','defic_k'];
  const items = Array.isArray(window.VITI_DISEASES) ? [...window.VITI_DISEASES].sort((a,b) => {
    const ai=lead.indexOf(a.id),bi=lead.indexOf(b.id);
    return ai>=0 && bi>=0 ? ai-bi : ai>=0 ? -1 : bi>=0 ? 1 : a.name.localeCompare(b.name,'pt');
  }) : [];
  const root = document.querySelector('.page-diseases');
  const grid = document.getElementById('dv-grid');
  if (!root || !grid) return;

  const lang = ['pt', 'en', 'es'].includes(document.documentElement.lang) ? document.documentElement.lang : 'pt';
  const dictionary = {
    pt: {
      eyebrow:'CONHECIMENTO QUE CULTIVA', titleA:'Doenças', titleB:'Pragas', heroIntro:'Uma biblioteca visual para identificar sinais, comparar sintomas e conhecer os principais problemas que afetam a videira em todo o Brasil.', explore:'Explorar biblioteca',
      library:'GUIA VISUAL DA VIDEIRA', catalog:'Catálogo de identificação', catalogIntro:'Explore imagens de referência e compare sintomas nas folhas, cachos, ramos e raízes.', entries:'condições catalogadas',
      all:'Todas', diseases:'Doenças', pests:'Pragas', viruses:'Viroses', nutrition:'Nutrição', disorders:'Outros danos', quarantine:'Quarentenárias',
      where:'Parte afetada:', anyPart:'Todas', leaves:'Folhas', bunches:'Cachos', branches:'Ramos', roots:'Raízes',
      noResults:'Nenhuma condição encontrada', tryAnother:'Experimente outro sintoma ou remova os filtros.', reset:'Limpar filtros',
      guidanceEyebrow:'ORIENTAÇÃO AO PRODUTOR',guidanceTitle:'Fotografias ajudam a reconhecer, mas não confirmam o diagnóstico.',
      guidanceText:'Sinais semelhantes podem ser causados por doenças, insetos, deficiência nutricional ou estresse. Observe mais de uma parte da planta, compare a evolução e procure assistência agronômica quando necessário. Produtos fitossanitários devem ter registro válido para a cultura e recomendação profissional.',
      expertLink:'Consultar o Sistema Especialista ↗',credits:'Conteúdo educacional baseado no UZUM-Uva da Embrapa. Fotos externas dependem de conexão à internet e das condições de uso da fonte; consulte a galeria original em cada ficha.',
      search:'Pesquisar por doença, praga ou sintoma...', view:'Ver ficha completa', results:'resultados', result:'resultado',
      symptoms:'Como reconhecer', differential:'Sinais parecidos e diferenças', observation:'O que observar no vinhedo', affected:'Partes afetadas',
      gallery:'Ver galeria oficial da Embrapa ↗', noPhoto:'Fotografia disponível na fonte oficial', imageCredit:'Foto: Embrapa Uva e Vinho',
      scientific:'Agente ou referência', notice:'A imagem, sozinha, não confirma a causa. Consulte um profissional quando necessário.', quarantineAlert:'ATENÇÃO: praga quarentenária ausente no Brasil; suspeitas devem ser comunicadas à defesa agropecuária.',
      close:'Fechar ficha', tags:{'Quarentenárias':'Alerta fitossanitário'}
    },
    en: {
      eyebrow:'KNOWLEDGE THAT GROWS',titleA:'Diseases',titleB:'Pests',heroIntro:'A visual guide to compare symptoms and learn about grapevine disorders across Brazil.',explore:'Explore library',
      library:'GRAPEVINE VISUAL GUIDE', catalog:'Identification catalogue',catalogIntro:'Browse reference photos and compare symptoms on leaves, bunches, shoots and roots.',entries:'listed conditions',
      all:'All',diseases:'Diseases',pests:'Pests',viruses:'Viruses',nutrition:'Nutrition',disorders:'Other damage',quarantine:'Quarantine',
      where:'Affected part:',anyPart:'All',leaves:'Leaves',bunches:'Bunches',branches:'Shoots',roots:'Roots',
      noResults:'No matching conditions',tryAnother:'Try another term or clear the filters.',reset:'Clear filters',
      guidanceEyebrow:'GROWER GUIDANCE',guidanceTitle:'Photos help identify symptoms but cannot confirm a diagnosis.',
      guidanceText:'Similar symptoms may be caused by infections, insects, nutrition or environmental stress. Examine multiple parts of the plant and seek professional confirmation. Only use plant protection products registered for the crop under professional guidance.',
      expertLink:'Open Expert System ↗', credits:'Educational content based on Embrapa UZUM-Uva. External reference photos require internet access and are subject to source permissions.',
      search:'Search by disease, pest or symptom...',view:'View detailed sheet',results:'results',result:'result',
      symptoms:'How to recognize',differential:'Similar signs and differences',observation:'What to check in the vineyard',affected:'Affected parts',
      gallery:'See official Embrapa gallery ↗',noPhoto:'Photographs available at the official source',imageCredit:'Photo: Embrapa Uva e Vinho',scientific:'Agent / reference',
      notice:'A photograph alone cannot confirm the cause. Professional assessment may be necessary.',quarantineAlert:'WARNING: quarantine pest classified as absent from Brazil; suspected findings should be reported to the official plant-health authority.',close:'Close',tags:{'Quarentenárias':'Quarantine alert'}
    },
    es: {
      eyebrow:'CONOCIMIENTO QUE CULTIVA',titleA:'Enfermedades',titleB:'Plagas',heroIntro:'Una biblioteca visual para comparar síntomas y conocer problemas de la vid en todo Brasil.',explore:'Explorar biblioteca',
      library:'GUÍA VISUAL DE LA VID',catalog:'Catálogo de identificación',catalogIntro:'Compare fotografías y síntomas en hojas, racimos, ramas y raíces.',entries:'condiciones catalogadas',
      all:'Todas',diseases:'Enfermedades',pests:'Plagas',viruses:'Virus',nutrition:'Nutrición',disorders:'Otros daños',quarantine:'Cuarentenarias',
      where:'Parte afectada:',anyPart:'Todas',leaves:'Hojas',bunches:'Racimos',branches:'Ramas',roots:'Raíces',
      noResults:'No se encontraron resultados',tryAnother:'Pruebe otro síntoma o borre los filtros.',reset:'Borrar filtros',
      guidanceEyebrow:'ORIENTACIÓN AL PRODUCTOR',guidanceTitle:'Las fotografías orientan, pero no confirman un diagnóstico.',
      guidanceText:'Los síntomas semejantes pueden deberse a enfermedades, insectos, nutrición o estrés. Observe varias partes de la planta y busque asesoramiento profesional. Use solamente productos registrados para el cultivo, con orientación técnica.',
      expertLink:'Consultar el Sistema Experto ↗',credits:'Contenido educativo basado en Embrapa UZUM-Uva. Las imágenes externas requieren internet y están sujetas a permisos de la fuente.',
      search:'Buscar enfermedad, plaga o síntoma...',view:'Ver ficha completa',results:'resultados',result:'resultado',
      symptoms:'Cómo reconocer',differential:'Signos similares y diferencias',observation:'Qué observar en el viñedo',affected:'Partes afectadas',
      gallery:'Ver galería oficial de Embrapa ↗',noPhoto:'Fotografías disponibles en la fuente oficial',imageCredit:'Foto: Embrapa Uva e Vinho',scientific:'Agente o referencia',
      notice:'Una fotografía por sí sola no confirma la causa. Puede ser necesaria una evaluación profesional.',quarantineAlert:'ATENCIÓN: plaga cuarentenaria ausente en Brasil; las sospechas deben comunicarse a las autoridades fitosanitarias.',close:'Cerrar',tags:{'Quarentenárias':'Alerta fitosanitario'}
    }
  };
  const t = dictionary[lang];
  // Nas traduções, preserva o texto original para pesquisa e filtros.
  const translateOrgan = (organ) => {
    if (lang === 'pt') return organ;
    const source = {
      en:{'Folhas':'Leaves','Brotos':'Shoots','Ramos':'Shoots','Cachos':'Clusters','Bagas':'Berries','Raízes':'Roots','Tronco':'Trunk','Flores':'Flowers','Gemas':'Buds'},
      es:{'Folhas':'Hojas','Brotos':'Brotes','Ramos':'Ramas','Cachos':'Racimos','Bagas':'Bayas','Raízes':'Raíces','Tronco':'Tronco','Flores':'Flores','Gemas':'Yemas'}
    }[lang];
    let out = organ;
    for (const [pt,tr] of Object.entries(source)) out=out.replace(new RegExp(pt,'gi'), tr);
    // JavaScript word boundaries do not match accents reliably; direct fallback for Raízes.
    out=out.replace(/Raízes/g,source['Raízes']).replace(/ e /g,lang === 'en' ? ' and ' : ' y ');
    return out;
  };
  items.forEach(item => {
    item.organs_pt=item.organs;
    item.name_pt=item.name;
    item.signs_pt=item.signs;
    if (lang !== 'pt') {
      const details=window.VITI_CATALOG_I18N?.[lang]?.[item.id];
      if (details) Object.assign(item,details);
      item.organs = translateOrgan(item.organs_pt);
    }
  });
  const ui = {search:document.getElementById('dv-search'),clear:document.getElementById('dv-clear'),count:document.getElementById('dv-count'),empty:document.getElementById('dv-empty'),reset:document.getElementById('dv-reset'),dialog:document.getElementById('dv-dialog'),modal:document.getElementById('dv-modal-body'),close:document.getElementById('dv-close')};
  const state={text:'',group:'all',organ:'all'};
  const normal = value => String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const groupLabel = item => (t.tags&&t.tags[item.group]) || ({'Doenças':t.diseases,'Pragas':t.pests,'Viroses':t.viruses,'Nutrição':t.nutrition,'Distúrbios':t.disorders,'Quarentenárias':t.quarantine}[item.group]||item.group);
  const el=(tag,classes='',text)=>{const x=document.createElement(tag);if(classes)x.className=classes;if(text!==undefined)x.textContent=text;return x;};

  document.querySelectorAll('.page-diseases [data-i18n]').forEach(node=>{let key=node.dataset.i18n;if(typeof t[key]==='string')node.textContent=t[key];});
  ui.search.placeholder=t.search;
  ui.search.setAttribute('aria-label',t.search);
  ui.close.setAttribute('aria-label',t.close);

  function makePhoto(item,large=false) {
    const wrap=el('div',large?'dv-modal-photo':'dv-card-photo');
    const fallback=el('div','dv-fallback');
    const official=el('a','dv-fallback-link',t.gallery); official.href=item.source;official.target='_blank';official.rel='noopener noreferrer';
    fallback.append(el('b','','❧'),el('span','',t.noPhoto),official);
    wrap.append(fallback);
    if (item.photo) {
      const img=el('img');img.src=item.photo;img.alt=`${item.name} — ${t.imageCredit}`;
      img.loading=large?'eager':'lazy';img.referrerPolicy='no-referrer';
      img.onerror=()=>{img.hidden=true;fallback.style.display='flex';const credit=wrap.querySelector('.dv-photo-credit');if(credit)credit.hidden=true;};
      wrap.append(img);
      const credit=el('span','dv-photo-credit',t.imageCredit);wrap.append(credit);
      // Some browsers do not support :has; manually hide fallback when image actually loads.
      img.addEventListener('load',()=>{fallback.style.display='none'});
    }
    return wrap;
  }
  function createCard(item) {
    const card=el('article','dv-card');
    card.append(makePhoto(item));
    const body=el('div','dv-card-body');
    const meta=el('div','dv-meta');
    const tag=el('span','dv-tag'+(item.group==='Pragas'?' pest':'')+(item.quarantine?' quarantine':''),groupLabel(item));
    meta.append(tag,el('span','dv-part',item.organs));
    body.append(meta,el('h3','',item.name),el('p','dv-card-text',item.signs));
    const button=el('button','dv-card-btn',t.view+'  ↗');button.type='button';button.addEventListener('click',()=>showDetails(item));
    body.append(button); card.append(body);
    return card;
  }
  function info(title,content,wide=false){const section=el('section','dv-info'+(wide?' dv-info-wide':''));section.append(el('h3','',title),el('p','',content));return section;}
  function showDetails(item) {
    ui.modal.replaceChildren();
    ui.modal.append(makePhoto(item,true));
    const inner=el('div','dv-modal-inner');
    inner.append(el('span','dv-tag'+(item.quarantine?' quarantine':''),groupLabel(item)),el('h2','',item.name),el('p','dv-agent',`${t.scientific}: ${item.agent}`));
    if(item.quarantine)inner.append(el('p','dv-alert',t.quarantineAlert));
    const columns=el('div','dv-modal-columns');
    columns.append(info(t.symptoms,item.signs),info(t.differential,item.differential),info(t.observation,item.monitoring),info(t.affected,item.organs));
    inner.append(columns);
    const row=el('div','dv-source-row');
    const link=el('a','',t.gallery);link.href=item.source;link.target='_blank';link.rel='noopener noreferrer';
    row.append(link,el('span','dv-source-note',t.notice));inner.append(row);
    ui.modal.append(inner);
    if(typeof ui.dialog.showModal==='function')ui.dialog.showModal();else ui.dialog.setAttribute('open','');
    ui.close.focus();
  }
  function filterItems() {
    const text=normal(state.text.trim());
    return items.filter(item=>{
      if(state.group!=='all'&&item.group!==state.group)return false;
      if(state.organ!=='all'&&!normal(item.organs_pt || item.organs).includes(normal(state.organ)))return false;
      if(!text)return true;
      return normal([item.name,item.name_pt,item.signs,item.signs_pt,item.differential,item.monitoring,item.agent,item.organs,item.organs_pt,item.group].join(' ')).includes(text);
    });
  }
  function render() {
    const shown=filterItems();const fragment=document.createDocumentFragment();
    shown.forEach(item=>fragment.append(createCard(item)));
    grid.replaceChildren(fragment);
    ui.empty.hidden=shown.length!==0;
    if(ui.count) ui.count.textContent=`${shown.length} ${shown.length===1?t.result:t.results}`;
    ui.clear.hidden=!ui.search.value;
  }
  function updateButtons(){
    document.querySelectorAll('.dv-chip').forEach(b=>{const active=b.dataset.group===state.group;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
    document.querySelectorAll('.dv-organ').forEach(b=>{const active=b.dataset.organ===state.organ;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
  }
  function reset(){state.text='';state.group='all';state.organ='all';ui.search.value='';updateButtons();render();}
  ui.search.addEventListener('input',event=>{state.text=event.target.value;render()});
  ui.clear.addEventListener('click',()=>{state.text='';ui.search.value='';render();ui.search.focus()});
  ui.reset.addEventListener('click',reset);
  document.querySelectorAll('.dv-chip').forEach(button=>button.addEventListener('click',()=>{state.group=button.dataset.group;updateButtons();render()}));
  document.querySelectorAll('.dv-organ').forEach(button=>button.addEventListener('click',()=>{state.organ=button.dataset.organ;updateButtons();render()}));
  ui.close.addEventListener('click',()=>ui.dialog.close());
  ui.dialog.addEventListener('click',event=>{if(event.target===ui.dialog)ui.dialog.close()});
  render();
})();
