"""Motor de Fatores de Certeza transposto de Teste.bcm para Python.

A fonte original permanece em knowledge/Teste.bcm e seu equivalente JSON
fiel em knowledge/sinta_teste_export.json. As regras são interpretadas sem
pesos inventados, e cada conclusão mantém o CNF gravado pelo SINTA.

Este cálculo reproduz o modelo possibilista descrito no manual do Expert
SINTA: E = produto dos fatores; conclusão = premissa * CNF da regra;
conclusões repetidas da mesma hipótese = a + b - a*b.
As respostas do formulário são fatos certos para Sim/Não e desconhecidos
para Não sei. Não constitui um diagnóstico agronômico validado.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import json
from sinta_i18n import label, disease_name, question_groups, UI
from complementary_inference import evaluate_extension, get_extension

SOURCE = Path(__file__).resolve().parent / 'knowledge' / 'sinta_teste_export.json'
ALLOWED = {'sim','nao','nao_sei'}

@lru_cache(maxsize=1)
def knowledge():
    with SOURCE.open(encoding='utf-8') as fp:
        kb=json.load(fp)
    if len(kb['regras']) != 8 or len(kb['hipoteses']) != 8:
        raise ValueError('A base JSON não corresponde à fonte SINTA de oito regras')
    original = SOURCE.parent / 'Teste.bcm'
    if original.exists() and sha256(original.read_bytes()).hexdigest() != kb['sha256']:
        raise ValueError('Teste.bcm foi modificado: execute python sinta_bcm_import.py para sincronizar a base')
    return kb


def sanitize_answers(raw):
    if not isinstance(raw, dict):
        raise ValueError("O campo 'answers' deve ser um objeto com respostas")
    valid=(set(knowledge()['variaveis'])-{'diagnostico'}) | set(get_extension()['novas_perguntas'])
    if len(raw)>len(valid) or any(key not in valid or type(value) is not str or value not in ALLOWED for key,value in raw.items()):
        raise ValueError('Pergunta ou resposta inválida')
    return {key:raw.get(key,'nao_sei') for key in valid}


def combine_certainties(a,b):
    if not (0 <= a <= 1 and 0 <= b <= 1):
        raise ValueError('Fatores de certeza fora de [0, 1]')
    return a+b-a*b


def infer(raw, locale='pt'):
    if locale not in UI: locale='pt'
    answers=sanitize_answers(raw)
    kb=knowledge()
    hits={}
    partial=[]
    examined=[]
    for rule in kb['regras']:
        clauses=rule['se_todas']
        yes=[]
        no=[]
        unknown=[]
        for clause in clauses:
            key=clause['variavel']
            answer=answers[key]
            required='sim' if clause['valor']=='sim' else 'nao' if clause['valor']=='não' else None
            if required is None:
                raise ValueError('Valor SINTA fora da lista binária esperada')
            if answer=='nao_sei':unknown.append(key)
            elif answer==required:yes.append(key)
            else:no.append(key)
        if not no and not unknown:
            # Todas as condições atendidas com certeza =1 (Sim ou Não)
            hypothesis=rule['entao'][0]['valor']
            entry=hits.setdefault(hypothesis,{'id':hypothesis,'confidence':0.0,'evidence':[], 'fired_rules':[]})
            rule_result=0.0
            raw_factors=[]
            for conclusion in rule['entao']:
                if conclusion['valor'] != hypothesis:
                    raise ValueError('Conclusões distintas exigem análise')
                factor=conclusion['cnf']
                raw_factors.append(round(factor*100,1))
                rule_result=combine_certainties(rule_result,factor)
            entry['confidence']=combine_certainties(entry['confidence'],rule_result)
            for key in yes:
                if key not in entry['evidence']:entry['evidence'].append(key)
            entry['fired_rules'].append({
                'id':rule['id'], 'conditions':[{
                    'id':cl['variavel'], 'description':label(cl['variavel'],locale),
                    'value':cl['valor']
                } for cl in clauses],
                'conclusion_factors_percent':raw_factors,
                'confidence_percent':round(rule_result*100,1),
            })
            examined.append(rule['id'])
        elif not no and yes and unknown:
            partial.append({'id':rule['id'], 'missing':unknown,'matched':len(yes)})

    results=sorted(hits.values(),key=lambda r:(-r['confidence'],r['id']))
    for item in results:
        item['name']=disease_name(item['id'],locale)
        item['confidence_percent']=round(item['confidence']*100,1)
        item['certainty_factor']=round(item['confidence'],6)
        item['evidence']=[label(k,locale) for k in item['evidence']]
        del item['confidence']
    # Regras originais são imutáveis. A extensão não fabrica a combinação
    # a+b-a*b em evidências sobrepostas: adota o MAIOR fator por hipótese.
    extra, extra_questions=evaluate_extension(answers,locale)
    indexed={item['id']:item for item in results}
    for disease, candidate in extra.items():
        if disease not in indexed:
            indexed[disease]=candidate
            continue
        entry=indexed[disease]
        if candidate['confidence_percent']>entry['confidence_percent']:
            entry['confidence_percent']=candidate['confidence_percent']
            entry['certainty_factor']=candidate['certainty_factor']
        entry['fired_rules'].extend(candidate['fired_rules'])
        entry['evidence'].extend(t for t in candidate['evidence'] if t not in entry['evidence'])
    results=sorted(indexed.values(),key=lambda item:(-item['confidence_percent'],item['id']))
    todo=[]
    for item in sorted(partial,key=lambda x:(-x['matched'],len(x['missing']))):
        for key in item['missing']:
            if key not in todo:todo.append(key)
    for code in extra_questions:
        if code not in todo: todo.append(code)
    suggestions=[{'id':code,'text':label(code,locale)} for code in todo[:4]]
    report={
        'results':results[:3], 'matched_hypotheses':len(results),
        'analyzed_hypotheses':len(set(kb['hipoteses']) | set(get_extension()['doencas_previstas'])),
        'diseases_assessed':len(get_extension()['doencas_previstas']),
        'complementary_rule_count':len(get_extension()['regras']),
        'fired_rule_count':len(examined),
        'suggested_questions':suggestions,
        'engine':'sinta_cf_python',
        'source_file':kb['arquivo_origem'],'source_sha256':kb['sha256'],
        'method':'Original SINTA CF rules plus documented heuristic alternatives; max across overlapping paths',
        'message':None if results else UI[locale]['no_results'],
        'disclaimer':UI[locale]['warning'],
    }
    return report
