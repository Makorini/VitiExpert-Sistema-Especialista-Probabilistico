"""Regressões da extensão das dez doenças. Casos derivados das próprias regras.
Isto verifica código e não equivale a validação agronômica independente.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from complementary_inference import get_extension
from sinta_inference import infer, sanitize_answers, knowledge
from sinta_i18n import question_groups

@pytest.mark.parametrize('disease',get_extension()['doencas_previstas'])
def test_ten_diseases_are_recognized_from_rule_scenarios(disease):
    r=max((r for r in get_extension()['regras'] if r['disease']==disease),
          key=lambda r:(len(r['conditions']),r['cf']))
    answers={c['id']:c['value'] for c in r['conditions']}
    result=infer(answers)
    ids={x['id'] for x in result['results']}
    assert disease in ids, (disease,ids)
    picked=next(x for x in result['results'] if x['id']==disease)
    assert picked['confidence_percent']>=round(r['cf']*100,1)

@pytest.mark.parametrize('locale',('pt','en','es'))
def test_localized_questionnaire_has_34_questions(locale):
    params=knowledge()['variaveis'] + list(get_extension()['novas_perguntas'])
    groups=question_groups(params,locale)
    q=[q for g in groups for q in g['items']]
    assert len(q)==34
    assert all(x['id'] not in x['pergunta'] for x in q)


def test_original_unchanged_and_noninfectious_distinct():
    assert len(knowledge()['regras'])==8
    assert len(knowledge()['hipoteses'])==8
    assert infer({'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'})['results'][0]['confidence_percent']==98.0
    output=infer({'solo_encharcado':'sim','folhas_murchas':'sim','manchas_foliares_tipicas':'nao'})
    assert output['results'][0]['id']=='asfixia_radicular'
    assert output['diseases_assessed']==10
    assert output['analyzed_hypotheses']==12


def test_nonanswers_do_not_act_as_negatives():
    assert infer({})['results']==[]
    assert infer({'poeira_branca':'sim'})['results'][0]['confidence_percent']==68.0
    assert infer({'poeira_branca':'sim','chuva_frequente':'nao'})['results'][0]['confidence_percent']==98.0
    assert infer({'poeira_branca':'sim','chuva_frequente':'sim'})['results'][0]['confidence_percent']==68.0


def test_overlapping_rules_use_max_not_sum():
    out=infer({'manchas_oleosas':'sim','mofo_branco_inferior':'sim','chuva_frequente':'sim'})
    chosen=next(x for x in out['results'] if x['id']=='mildio')
    assert chosen['confidence_percent']==78.0
    assert any(r['id']=='COMP-R09' for r in chosen['fired_rules'])
    assert len(chosen['fired_rules'])>=2


def test_no_spurious_rule_when_inputs_conflict():
    # R09 exige as duas características. Contradição explícita desliga R09.
    out=infer({'manchas_oleosas':'sim','mofo_branco_inferior':'nao'})
    assert not any(r['id']=='COMP-R09' for x in out['results'] for r in x['fired_rules'])


def test_invalid_extension_answer_rejected():
    for value in ('yes',True,50,None):
        with pytest.raises(ValueError):sanitize_answers({'manchas_oleosas':value})
