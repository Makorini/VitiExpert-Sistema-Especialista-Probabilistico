"""Rótulos de apresentação PT/EN/ES para os códigos originais do Teste.bcm.
Os nomes legíveis abaixo foram redigidos para a interface e não alteram os dados
ou as regras importadas do SINTA.
"""
from __future__ import annotations

QUESTION_LABELS = {
 'manchas_amarelas': ('As folhas apresentam manchas amareladas?', 'Are there yellow spots on the leaves?', '¿Las hojas tienen manchas amarillentas?'),
 'folhas_murchas': ('As folhas estão murchas?', 'Are the leaves wilted?', '¿Las hojas están marchitas?'),
 'chuva_continua': ('Choveu sem parar por vários dias seguidos?', 'Has it rained non-stop for several days in a row?', '¿Ha llovido sin parar durante varios días seguidos?'),
 'poeira_branca': ('Há uma camada de pó branco sobre folhas ou frutos?', 'Is there white powder on leaves or fruit?', '¿Hay una capa de polvo blanco en hojas o frutos?'),
 'chuva_frequente': ('Tem chovido em muitos dias nas últimas semanas, mesmo com intervalos?', 'Has it rained on many days over the last weeks, even with breaks?', '¿Ha llovido en muchos días en las últimas semanas, aunque con pausas?'),
 'manchas_marrons': ('Existem manchas marrons na planta?', 'Are there brown spots on the plant?', '¿Hay manchas marrones en la planta?'),
 'mofo_cinza': ('Existe mofo cinzento nos cachos?', 'Is gray mold visible on grape clusters?', '¿Hay moho gris en los racimos?'),
 'cacho_compacto': ('Os cachos são compactos, com bagas muito próximas?', 'Are the grape clusters tight and compact?', '¿Los racimos son compactos, con las bayas muy juntas?'),
 'lesoes_deprimidas_escuras': ('Existem lesões escuras e afundadas?', 'Are there dark, sunken lesions?', '¿Hay lesiones oscuras y hundidas?'),
 'halo_avermelhado': ('As lesões apresentam um halo avermelhado?', 'Do lesions show a reddish halo?', '¿Las lesiones presentan un halo rojizo?'),
 'frutos_escurecidos': ('As bagas estão escurecendo?', 'Are the berries turning dark?', '¿Las bayas se están oscureciendo?'),
 'lesoes_concentricas': ('As bagas apresentam lesões em círculos concêntricos?', 'Do berries have concentric-ring lesions?', '¿Las bayas presentan lesiones en anillos concéntricos?'),
 'maturacao': ('A videira está na fase de maturação dos cachos?', 'Are the grapes at the ripening stage?', '¿Las uvas están en fase de maduración?'),
 'frutos_moles': ('Existem bagas amolecidas?', 'Are any berries soft?', '¿Hay bayas blandas?'),
 'odor_acetico': ('Os cachos têm cheiro ácido semelhante a vinagre?', 'Do the clusters have a vinegary smell?', '¿Los racimos tienen olor agrio, similar al vinagre?'),
 'solo_encharcado': ('O solo está encharcado?', 'Is the soil waterlogged?', '¿El suelo está encharcado?'),
 'manchas_foliares_tipicas': ('Há manchas foliares típicas de doenças?', 'Are typical disease spots visible on leaves?', '¿Hay manchas foliares típicas de enfermedades?'),
 'galhos_quebradicos': ('Os ramos estão secos ou quebradiços?', 'Are the branches dry or brittle?', '¿Las ramas están secas o quebradizas?'),
 'brotacao_fraca': ('A brotação da planta está fraca?', 'Is shoot growth weak?', '¿La brotación es débil?'),
}

# Perguntas adicionais de base documental, não do arquivo SINTA original.
QUESTION_LABELS.update({
 'manchas_oleosas': ('Há manchas amareladas com aspecto de óleo nas folhas?', 'Are there yellowish oil-like patches on leaves?', '¿Hay manchas amarillentas de aspecto aceitoso en las hojas?'),
 'mofo_branco_inferior': ('Há mofo branco na parte de baixo das folhas?', 'Is there white mold on the underside of the leaves?', '¿Hay moho blanco en el envés de las hojas?'),
 'bagas_rachadas': ('Há bagas com rachaduras na casca?', 'Are there grape berries with cracked skins?', '¿Hay bayas con la piel agrietada?'),
 'folhas_jovens_pontos_escuros': ('Folhas jovens apresentam pequenas manchas escuras?', 'Do young leaves show small dark spots?', '¿Las hojas jóvenes presentan pequeñas manchas oscuras?'),
 'folhas_deformadas': ('As folhas jovens estão deformadas ou encarquilhadas?', 'Are the young leaves distorted or crumpled?', '¿Las hojas jóvenes están deformadas o arrugadas?'),
 'escoriacoes_ramos_base': ('Há lesões alongadas e escuras na base dos ramos novos?', 'Are there long, dark lesions at the base of new shoots?', '¿Hay lesiones alargadas y oscuras en la base de los brotes?'),
 'pustulas_amarelas_inferiores': ('Existem pequenas pústulas amarelas na face inferior das folhas?', 'Are there yellow pustules on the underside of the leaves?', '¿Hay pequeñas pústulas amarillas en el envés de las hojas?'),
 'manchas_angulares_superiores': ('A parte superior das folhas tem pequenas lesões angulares?', 'Are there small angular lesions on the upper leaf surface?', '¿La cara superior de las hojas tiene lesiones angulares pequeñas?'),
 'manchas_irregulares_halo_amarelo': ('Há manchas irregulares escuras com halo amarelo-esverdeado nas folhas?', 'Are there irregular dark leaf spots with a yellow-green halo?', '¿Hay manchas oscuras irregulares con halo amarillo verdoso?'),
 'folhas_maduras_afetadas': ('As manchas aparecem principalmente em folhas maduras?', 'Do the spots occur mainly on mature leaves?', '¿Las manchas aparecen principalmente en hojas maduras?'),
 'pustulas_escuras_bagas': ('Há pontuações ou pústulas escuras na casca das bagas?', 'Are there dark pustules or dots on grape skins?', '¿Hay pústulas o puntos oscuros sobre las bayas?'),
 'bagas_mumificadas': ('Há bagas enrugadas, secas ou mumificadas?', 'Are some berries shriveled, dried out or mummified?', '¿Hay bayas arrugadas, secas o momificadas?'),
 'exsudato_rosado': ('Há pontuações nas bagas que liberam massa rosada ou salmão?', 'Do berry lesions produce a pink or salmon-colored spore mass?', '¿Las lesiones de las bayas liberan una masa rosada o salmón?'),
 'moscas_vinagre': ('Há pequenas moscas semelhantes às do vinagre próximas aos cachos?', 'Are there small vinegar flies near the clusters?', '¿Hay mosquitas del vinagre cerca de los racimos?'),
 'bagas_vazando_suco': ('Existem bagas rachadas liberando suco?', 'Are cracked berries leaking juice?', '¿Hay bayas rajadas que pierden jugo?'),
})

GROUPS = {
 'leaves':('Folhas e brotos','Leaves and shoots','Hojas y brotes'),
 'clusters':('Bagas e cachos','Berries and clusters','Bayas y racimos'),
 'branches':('Ramos e raízes','Branches and roots','Ramas y raíces'),
 'environment':('Clima e desenvolvimento','Weather and growth stage','Clima y desarrollo'),
}
GROUP_FIELDS = {
 'leaves':['manchas_amarelas','folhas_murchas','poeira_branca','manchas_marrons','lesoes_deprimidas_escuras','halo_avermelhado','manchas_foliares_tipicas'],
 'clusters':['mofo_cinza','cacho_compacto','frutos_escurecidos','lesoes_concentricas','frutos_moles','odor_acetico'],
 'branches':['solo_encharcado','galhos_quebradicos','brotacao_fraca'],
 'environment':['chuva_continua','chuva_frequente','maturacao'],
}

# Preserva perguntas originais e acrescenta sinais discriminantes ao fim de cada grupo.
GROUP_FIELDS['leaves'].extend(['manchas_oleosas','mofo_branco_inferior','folhas_jovens_pontos_escuros','folhas_deformadas','pustulas_amarelas_inferiores','manchas_angulares_superiores','manchas_irregulares_halo_amarelo','folhas_maduras_afetadas'])
GROUP_FIELDS['clusters'].extend(['bagas_rachadas','pustulas_escuras_bagas','bagas_mumificadas','exsudato_rosado','moscas_vinagre','bagas_vazando_suco'])
GROUP_FIELDS['branches'].append('escoriacoes_ramos_base')

DISEASE_NAMES = {
 'mildio':('Míldio','Downy mildew','Mildiu'),
 'oidio':('Oídio','Powdery mildew','Oídio'),
 'antracnose':('Antracnose','Anthracnose','Antracnosis'),
 'podridao_cinzenta':('Podridão-cinzenta','Gray mold / Botrytis bunch rot','Podredumbre gris'),
 'podridao_madura':('Podridão-da-uva-madura','Ripe rot','Podredumbre de la uva madura'),
 'podridao_acida':('Podridão-ácida','Sour rot','Podredumbre ácida'),
 'asfixia_radicular':('Asfixia radicular','Root asphyxia / waterlogging','Asfixia radicular'),
 'declinio_morte':('Declínio ou morte da videira','Grapevine decline / dieback','Declive o muerte de la vid'),
}

DISEASE_NAMES.update({
 'escoriose': ('Escoriose', 'Phomopsis cane and leaf spot', 'Escoriosis'),
 'ferrugem': ('Ferrugem', 'Grapevine rust', 'Roya de la vid'),
 'mancha_folhas': ('Mancha-das-folhas', 'Leaf spot', 'Mancha de las hojas'),
 'podridao_amarga': ('Podridão-amarga', 'Bitter rot', 'Podredumbre amarga'),
})

UI = {
 'pt':{
  'start_assessment':'Iniciar avaliação',
  'hero_kicker':'VITIEXPERT · SISTEMA ESPECIALISTA',
  'hero_before':'Sistema', 'hero_accent':'Especialista',
  'hero_description':'Responda às perguntas sobre a videira. O motor Python analisa sinais e condições observados e apresenta hipóteses com níveis percentuais de confiança.',
  'form_aria':'Questionário de diagnóstico da videira', 'step1':'01 / OBSERVAÇÃO DA VIDEIRA',
  'question_title':'O que você observa na planta?',
  'instructions_prefix':'Responda', 'yes':'Sim', 'no':'Não', 'or':'ou', 'unknown':'Não sei',
  'instructions_suffix':'Se não souber a resposta, selecione “Não sei”. Isso não equivale a responder “Não”.',
  'analyze':'Analisar respostas', 'clear':'Limpar respostas',
  'warning':'Os percentuais representam níveis de confiança calculados pelo sistema com base nas respostas. A análise é orientativa e não substitui avaliação de engenheiro agrônomo ou exame laboratorial.',
  'result_step':'02 / RESULTADO DA INFERÊNCIA', 'result_title':'Hipóteses identificadas',
  'result_intro':'A análise considera os sinais informados e apresenta até três hipóteses compatíveis com as respostas.',
  'probability_title':'Nível de confiança do sistema (CNF)', 'main_hypothesis':'Hipótese principal', 'tied_highest':'Maior confiança — empate',
  'rules_title':'Regras utilizadas na análise',
  'rules_intro':'As regras acionadas e os fatores utilizados podem ser consultados nos detalhes dos resultados.',
  'fired_rules':'regra(s) acionada(s)', 'associated_signs':'Condições observadas:',
  'show_rules':'Ver regras e fatores considerados', 'suggestions':'Perguntas que podem completar uma regra',
  'no_results':'Nenhuma regra completa foi acionada pelas respostas fornecidas.',
  'below_minimum':'Há regras com todas as condições respondidas, mas a certeza combinada ficou abaixo do mínimo de 50% exigido pelo Expert SINTA, por isso não foram aceitas.',
  'need_symptom':'Informe os sintomas e condições observados.',
  'loading':'Analisando as respostas...', 'analysis_error':'Não foi possível analisar as respostas:',
  'confidence_method':'Nível de confiança calculado pelas regras',
  'rule_confidences':'Fatores da regra', 'other_note':'As hipóteses não precisam somar 100%.',
  'certainty':'Sua certeza', 'certainty_hint':'Ao marcar Sim ou Não, indique o quanto tem certeza (0% a 100%), como no Expert SINTA. Como no SINTA, uma regra só é aceita quando a certeza combinada das respostas fica em pelo menos 50%.',
  'premise':'Certeza combinada das respostas (produto)',
  'saved_note':'Consulta salva no seu histórico (Minha conta).', 'login_to_save':'Entre na sua conta para salvar as consultas e ver o histórico por mês e ano.',
 },
 'en':{
  'start_assessment':'Start assessment',
  'hero_kicker':'VITIEXPERT · EXPERT SYSTEM',
  'hero_before':'Expert', 'hero_accent':'System',
  'hero_description':'Answer questions about the grapevine. The Python engine evaluates observed signs and conditions and presents hypotheses with percentage-based confidence levels.',
  'form_aria':'Grapevine diagnostic questionnaire', 'step1':'01 / OBSERVING THE GRAPEVINE',
  'question_title':'What do you observe on the plant?',
  'instructions_prefix':'Answer', 'yes':'Yes', 'no':'No', 'or':'or', 'unknown':'Not sure',
  'instructions_suffix':'Choose “Not sure” when information is missing. This does not mean “No”.',
  'analyze':'Analyze answers', 'clear':'Clear answers',
  'warning':'Percentages indicate confidence levels calculated from your answers. This is guidance only and does not replace an agronomist’s assessment or laboratory examination.',
  'result_step':'02 / INFERENCE RESULTS', 'result_title':'Identified hypotheses',
  'result_intro':'The analysis considers the reported signs and presents up to three hypotheses consistent with your answers.',
  'probability_title':'System certainty factor (CF)', 'main_hypothesis':'Main hypothesis', 'tied_highest':'Highest confidence — tie',
  'rules_title':'Rules used in the analysis',
  'rules_intro':'Triggered rules and their factors are available in the result details.',
  'fired_rules':'triggered rule(s)', 'associated_signs':'Observed conditions:',
  'show_rules':'View rules and confidence factors', 'suggestions':'Questions that could complete a rule',
  'no_results':'No complete rule was triggered by the provided answers.',
  'below_minimum':'Some rules had all conditions answered, but the combined certainty was below the 50% minimum required by Expert SINTA, so they were not accepted.',
  'need_symptom':'Provide the symptoms and conditions you observed.',
  'loading':'Analyzing answers...', 'analysis_error':'Could not analyze the answers:',
  'confidence_method':'Rule-based confidence level',
  'rule_confidences':'Rule factors', 'other_note':'Certainty values do not need to add up to 100%.',
  'certainty':'Your certainty', 'certainty_hint':'When you choose Yes or No, indicate how certain you are (0% to 100%), as in Expert SINTA. As in SINTA, a rule is only accepted when the combined certainty of the answers is at least 50%.',
  'premise':'Combined answer certainty (product)',
  'saved_note':'Consultation saved to your history (My account).', 'login_to_save':'Sign in to save consultations and see your history by month and year.',
 },
 'es':{
  'start_assessment':'Iniciar evaluación',
  'hero_kicker':'VITIEXPERT · SISTEMA EXPERTO',
  'hero_before':'Sistema', 'hero_accent':'Experto',
  'hero_description':'Responda preguntas sobre la vid. El motor de Python evalúa las señales y condiciones observadas y presenta hipótesis con niveles porcentuales de confianza.',
  'form_aria':'Cuestionario de diagnóstico de la vid', 'step1':'01 / OBSERVACIÓN DE LA VID',
  'question_title':'¿Qué observa en la planta?',
  'instructions_prefix':'Responda', 'yes':'Sí', 'no':'No', 'or':'o', 'unknown':'No sé',
  'instructions_suffix':'Si no conoce la respuesta, elija “No sé”. Esto no equivale a “No”.',
  'analyze':'Analizar respuestas', 'clear':'Borrar respuestas',
  'warning':'Los porcentajes indican niveles de confianza calculados a partir de sus respuestas. Este análisis es orientativo y no sustituye la evaluación agronómica ni los análisis de laboratorio.',
  'result_step':'02 / RESULTADO DE LA INFERENCIA', 'result_title':'Hipótesis identificadas',
  'result_intro':'El análisis considera los signos informados y presenta hasta tres hipótesis compatibles con sus respuestas.',
  'probability_title':'Factor de certeza del sistema (FC)', 'main_hypothesis':'Hipótesis principal', 'tied_highest':'Mayor confianza — empate',
  'rules_title':'Reglas utilizadas en el análisis',
  'rules_intro':'Puede consultar las reglas activadas y sus factores en los detalles de los resultados.',
  'fired_rules':'regla(s) activada(s)', 'associated_signs':'Condiciones observadas:',
  'show_rules':'Ver reglas y factores de confianza', 'suggestions':'Preguntas que pueden completar una regla',
  'no_results':'Ninguna regla completa fue activada por las respuestas indicadas.',
  'below_minimum':'Algunas reglas tenían todas las condiciones respondidas, pero la certeza combinada quedó por debajo del mínimo de 50% exigido por Expert SINTA, por eso no fueron aceptadas.',
  'need_symptom':'Indique los síntomas y las condiciones observados.',
  'loading':'Analizando respuestas...', 'analysis_error':'No se pudieron analizar las respuestas:',
  'confidence_method':'Nivel de confianza calculado por reglas',
  'rule_confidences':'Factores de la regla', 'other_note':'Los valores de certeza no necesitan sumar 100%.',
  'certainty':'Su certeza', 'certainty_hint':'Al marcar Sí o No, indique cuánta certeza tiene (0% a 100%), como en Expert SINTA. Como en SINTA, una regla solo se acepta cuando la certeza combinada de las respuestas es de al menos 50%.',
  'premise':'Certeza combinada de las respuestas (producto)',
  'saved_note':'Consulta guardada en su historial (Mi cuenta).', 'login_to_save':'Ingrese a su cuenta para guardar las consultas y ver el historial por mes y año.',
 }
}


def label(variable, locale='pt'):
    return QUESTION_LABELS[variable][{'pt':0,'en':1,'es':2}.get(locale,0)]


def disease_name(code, locale='pt'):
    return DISEASE_NAMES[code][{'pt':0,'en':1,'es':2}.get(locale,0)]


def question_groups(variables, locale='pt'):
    seen=set()
    groups=[]
    for group, codes in GROUP_FIELDS.items():
        items=[]
        for code in codes:
            if code in variables and code!='diagnostico':
                seen.add(code)
                items.append({'id':code, 'pergunta':label(code,locale), 'codigo_original':code})
        groups.append({'id':group, 'label':GROUPS[group][{'pt':0,'en':1,'es':2}.get(locale,0)], 'items':items})
    missing=set(variables)-{'diagnostico'}-seen
    if missing: raise ValueError(f'Campos do SINTA sem apresentação: {missing}')
    return groups
