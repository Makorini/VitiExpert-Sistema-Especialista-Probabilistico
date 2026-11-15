"""Regressões da extensão das dez doenças. Cenários fixos com referência técnica.
Isto verifica código e não equivale a validação agronômica independente.
"""
import csv
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from complementary_inference import get_extension
from sinta_inference import infer, sanitize_answers, knowledge
from sinta_i18n import question_groups

SCENARIO_FILE = Path(__file__).resolve().parents[1] / 'knowledge' / 'cenarios_sinteticos_10_doencas.csv'
with SCENARIO_FILE.open(encoding='utf-8-sig', newline='') as source:
    SCENARIOS = list(csv.DictReader(source, delimiter=';'))


def test_scenarios_cover_all_ten_diseases():
    expected = [case['doenca_esperada'] for case in SCENARIOS]
    assert sorted(expected) == sorted(get_extension()['doencas_previstas'])


@pytest.mark.parametrize('case', SCENARIOS, ids=[case['cenario'] for case in SCENARIOS])
def test_expected_disease_ranks_first(case):
    answers = {}
    for column, value in [('variaveis_sim', 'sim'), ('variaveis_nao', 'nao')]:
        for symptom in filter(None, case[column].split(',')):
            answers[symptom] = value
    first = infer(answers)['results'][0]
    assert first['id'] == case['doenca_esperada']
    assert first['fired_rules']
    assert first['confidence_percent'] > 0


def test_complementary_rules_count_toward_total():
    result = infer({'poeira_branca': 'sim', 'bagas_rachadas': 'sim'})
    assert result['fired_rule_count'] == 2
    assert {rule['id'] for rule in result['results'][0]['fired_rules']} == {'COMP-R12', 'COMP-R13'}


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
    assert infer({'poeira_branca':'sim','chuva_frequente':'nao'})['results'][0]['confidence_percent']==99.4
    assert infer({'poeira_branca':'sim','chuva_frequente':'sim'})['results'][0]['confidence_percent']==68.0


def test_same_hypothesis_accumulates_like_sinta():
    # COMP-R09 78%, COMP-R10 67%, COMP-R11 65% -> x + y - x*y = 97,5%
    out=infer({'manchas_oleosas':'sim','mofo_branco_inferior':'sim','chuva_frequente':'sim'})
    chosen=next(x for x in out['results'] if x['id']=='mildio')
    assert chosen['confidence_percent']==97.5
    assert any(r['id']=='COMP-R09' for r in chosen['fired_rules'])
    assert len(chosen['fired_rules'])>=2


def test_no_spurious_rule_when_inputs_conflict():
    # R09 exige as duas características. Contradição explícita desliga R09.
    out=infer({'manchas_oleosas':'sim','mofo_branco_inferior':'nao'})
    assert not any(r['id']=='COMP-R09' for x in out['results'] for r in x['fired_rules'])


def test_invalid_extension_answer_rejected():
    for value in ('yes',True,50,None):
        with pytest.raises(ValueError):sanitize_answers({'manchas_oleosas':value})
