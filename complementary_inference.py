"""Regras complementares do VitiExpert; nunca substituem o Teste.bcm.

Os sintomas têm suporte documental Embrapa. Os pesos heurísticos
NÃO são parâmetros validados cientificamente, nem probabilidades.
Regras alternativas correlacionadas são agregadas com MAX, para
não elevar artificialmente a confiança reutilizando a mesma evidência.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import json

FILE = Path(__file__).resolve().parent / 'knowledge' / 'regras_complementares.json'

@lru_cache(maxsize=1)
def get_extension():
    with FILE.open(encoding='utf-8') as f:
        data=json.load(f)
    if len(data['regras'])!=22 or len(data['doencas_previstas'])!=10:
        raise ValueError('Base complementar com quantidade inesperada de doenças ou regras')
    assert len({r['id'] for r in data['regras']})==len(data['regras'])
    return data


def evaluate_extension(answers, locale='pt'):
    """Retorna hipóteses, regras disparadas e próximas perguntas úteis.

    Uma regra só dispara quando TODAS suas condições são satisfeitas.
    Regras alternativas evitam exigir condições que não foram registradas.
    """
    from sinta_i18n import label, disease_name
    ext=get_extension()
    hits={}
    pending=[]
    for rule in ext['regras']:
        matched=[]
        missing=[]
        contradicted=False
        for condition in rule['conditions']:
            a=answers.get(condition['id'],'nao_sei')
            if a=='nao_sei': missing.append(condition['id'])
            elif a==condition['value']: matched.append(condition['id'])
            else: contradicted=True
        if contradicted:
            continue
        if missing:
            if matched: pending.append((len(matched),len(missing),tuple(missing)))
            continue
        disease=rule['disease']
        it=hits.setdefault(disease,{
            'id':disease,'name':disease_name(disease,locale),
            'confidence_percent':0,'certainty_factor':0,'evidence':[], 'fired_rules':[],
        })
        score=round(100*rule['cf'],1)
        # Usar MAX: caminhos alternativos derivam de evidências sobrepostas.
        if score>it['confidence_percent']:
            it['confidence_percent']=score
            it['certainty_factor']=rule['cf']
        for variable in matched:
            evidence=label(variable,locale)
            if evidence not in it['evidence']:
                it['evidence'].append(evidence)
        it['fired_rules'].append({
            'id':rule['id'],'conditions':[
                {'id':p['id'],'description':label(p['id'],locale),'value':p['value']}
                for p in rule['conditions']
            ],
            'conclusion_factors_percent':[score],
            'confidence_percent':score,
            'source_type':'complementar',
            'source_url':rule['reference'],
            'basis':rule['basis'],
            'estimated_factor':True,
        })
    suggestions=[]
    for _matched,_unknown,missing in sorted(pending,key=lambda v:(-v[0],v[1],v[2])):
        for variable in missing:
            if variable not in suggestions:
                suggestions.append(variable)
    return hits,suggestions
