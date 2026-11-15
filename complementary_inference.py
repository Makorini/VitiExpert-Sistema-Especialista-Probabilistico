"""Regras complementares do VitiExpert; nunca substituem o Teste.bcm.

Os sintomas têm suporte documental Embrapa. Os pesos heurísticos
NÃO são parâmetros validados cientificamente, nem probabilidades.
O cálculo segue o padrão do Expert SINTA: premissa E = produto das
confianças do usuário, regra aceita só com premissa >= 50%,
conclusão = premissa * cf, mesma hipótese acumulada por x + y - x*y.
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


def evaluate_extension(answers, locale='pt', certainties=None, rejected=None):
    """Retorna hipóteses, regras disparadas e próximas perguntas úteis.

    Uma regra só dispara quando TODAS suas condições são satisfeitas.
    Regras alternativas evitam exigir condições que não foram registradas.
    """
    from sinta_i18n import label, disease_name
    from sinta_inference import combine_certainties, premise_and, rule_accepted
    trust=certainties or {}
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
        premise=premise_and([trust.get(variable,1.0) for variable in matched])
        if not rule_accepted(premise):
            if rejected is not None:
                rejected.append({'id':rule['id'],'premise_percent':round(premise*100,1)})
            continue
        disease=rule['disease']
        it=hits.setdefault(disease,{
            'id':disease,'name':disease_name(disease,locale),
            'confidence':0.0,'evidence':[], 'fired_rules':[],
        })
        value=premise*rule['cf']
        it['confidence']=combine_certainties(it['confidence'],value)
        for variable in matched:
            evidence=label(variable,locale)
            if evidence not in it['evidence']:
                it['evidence'].append(evidence)
        it['fired_rules'].append({
            'id':rule['id'],'conditions':[
                {'id':p['id'],'description':label(p['id'],locale),'value':p['value']}
                for p in rule['conditions']
            ],
            'conclusion_factors_percent':[round(100*rule['cf'],1)],
            'premise_percent':round(premise*100,1),
            'confidence_percent':round(value*100,1),
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
