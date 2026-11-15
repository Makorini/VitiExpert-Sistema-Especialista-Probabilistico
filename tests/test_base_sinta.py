"""Base do Expert SINTA com as 10 doenças (knowledge/VitiExpert10.bcm).

Confere: o arquivo do SINTA, o roteiro docs/BASE_SINTA_10_DOENCAS.md, o JSON
exportado e o motor Python dão os mesmos resultados; e o cálculo segue as
funções padrão do manual do Expert SINTA. Cenários sintéticos: verificam o
software, não a acurácia agronômica em campo.
"""
import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'knowledge'))

import sinta_bcm_import
from gerar_vitiexpert10_bcm import ler_roteiro
from sinta_i18n import question_groups
from sinta_inference import (combine_certainties, infer, knowledge, premise_and, premise_or,
                             sanitize_answers)

DISEASES = {'mildio', 'oidio', 'antracnose', 'podridao_cinzenta', 'podridao_madura',
            'podridao_acida', 'escoriose', 'ferrugem', 'mancha_folhas', 'podridao_amarga'}
with (ROOT / 'knowledge' / 'cenarios_base_sinta.csv').open(encoding='utf-8') as fp:
    SCENARIOS = list(csv.DictReader(fp, delimiter=';'))


# ----------------------------- integridade ------------------------------

def test_base_has_ten_diseases_31_symptoms_17_rules():
    kb = knowledge()
    assert kb['arquivo_origem'] == 'VitiExpert10.bcm'
    assert set(kb['hipoteses']) == DISEASES
    assert len(set(kb['variaveis']) - {'diagnostico'}) == 31
    assert len(kb['regras']) == 17


def test_json_export_is_identical_to_bcm_file():
    fresh = sinta_bcm_import.decode(ROOT / 'knowledge' / 'VitiExpert10.bcm')
    kb = knowledge()
    for key in ('sha256', 'variaveis', 'hipoteses', 'regras'):
        assert fresh[key] == kb[key]


def test_bcm_rules_match_the_roteiro():
    _, roteiro = ler_roteiro()
    rules = {r['id']: r for r in knowledge()['regras']}
    for num, conditions, disease, cnf in roteiro:
        rule = rules[f'SINTA-R{num:02d}']
        assert [(c['variavel'], c['valor']) for c in rule['se_todas']] == conditions
        assert len(rule['entao']) == 1                     # uma conclusão por regra
        assert rule['entao'][0]['valor'] == disease
        assert rule['entao'][0]['cnf'] == pytest.approx(cnf)


def test_rules_of_same_disease_do_not_share_symptoms_or_contain_each_other():
    by_disease = {}
    for rule in knowledge()['regras']:
        symptoms = {c['variavel'] for c in rule['se_todas']}
        for other in by_disease.get(rule['entao'][0]['valor'], []):
            assert not (symptoms & other)
        by_disease.setdefault(rule['entao'][0]['valor'], []).append(symptoms)


# ----------------------------- cada regra --------------------------------

@pytest.mark.parametrize('rule', knowledge()['regras'], ids=lambda r: r['id'])
def test_each_rule_fires_alone_with_its_cnf(rule):
    answers = {c['variavel']: ('sim' if c['valor'] == 'sim' else 'nao') for c in rule['se_todas']}
    report = infer(answers)
    top = report['results'][0]
    assert top['id'] == rule['entao'][0]['valor']
    assert top['confidence_percent'] == pytest.approx(rule['entao'][0]['cnf'] * 100)
    assert [r['id'] for r in top['fired_rules']] == [rule['id']]


@pytest.mark.parametrize('case', SCENARIOS, ids=[c['cenario'] for c in SCENARIOS])
def test_roteiro_scenarios(case):
    answers = {k: 'sim' for k in case['variaveis_sim'].split(',') if k}
    answers.update({k: 'nao' for k in case['variaveis_nao'].split(',') if k})
    top = infer(answers)['results'][0]
    assert top['id'] == case['doenca_esperada']
    assert round(top['confidence_percent']) == int(case['cnf_esperado'])


# ----------------------------- cálculo do SINTA -------------------------

def test_manual_examples_and_combination():
    assert premise_and([.8, .7]) == pytest.approx(.56)        # manual, caso 2
    assert premise_or([.8, .7]) == pytest.approx(.94)         # manual, caso 3
    assert combine_certainties(.9, .7) == pytest.approx(.97)  # caso 4 (T11)
    with pytest.raises(ValueError):
        combine_certainties(1.2, .3)


def test_user_certainty_multiplies_rule_cnf():
    out = infer({'poeira_branca': 'sim'}, certainties={'poeira_branca': 70})   # T12
    assert out['results'][0]['confidence_percent'] == 56.0      # 0,70 x 0,80


def test_rule_below_minimum_confidence_is_rejected():
    out = infer({'manchas_oleosas': 'sim', 'mofo_branco_inferior': 'sim'},
                certainties={'manchas_oleosas': 70, 'mofo_branco_inferior': 70})   # T13
    assert out['results'] == []
    assert {'id': 'SINTA-R01', 'premise_percent': 49.0} in out['rejected_rules']
    assert 'mínimo de 50%' in out['message']
    exact = infer({'poeira_branca': 'sim'}, certainties={'poeira_branca': 50})     # T14
    assert exact['results'][0]['confidence_percent'] == 40.0


def test_negative_condition_rule():
    assert infer({'bagas_rachadas': 'sim', 'chuva_frequente': 'nao'})['results'][0]['id'] == 'oidio'
    assert infer({'bagas_rachadas': 'sim', 'chuva_frequente': 'sim'})['results'] == []


def test_unknown_is_not_no_and_suggests_missing_questions():
    out = infer({'manchas_oleosas': 'sim'})
    assert out['results'] == []
    assert 'mofo_branco_inferior' in [q['id'] for q in out['suggested_questions']]


def test_independent_diseases_are_ranked():
    out = infer({'poeira_branca': 'sim', 'odor_acetico': 'sim', 'moscas_vinagre': 'sim'})
    assert [(r['id'], r['confidence_percent']) for r in out['results']] == [
        ('podridao_acida', 90.0), ('oidio', 80.0)]


@pytest.mark.parametrize('bad', [{'S99': 'sim'}, {'poeira_branca': 'talvez'}, ['poeira_branca'],
                                 {'solo_encharcado': 'sim'}])
def test_invalid_answers_rejected(bad):
    with pytest.raises(ValueError):
        sanitize_answers(bad)


# ----------------------------- interface --------------------------------

@pytest.mark.parametrize('locale', ['pt', 'en', 'es'])
def test_31_questions_translated_in_each_language(locale):
    groups = question_groups(knowledge()['variaveis'], locale)
    questions = [q for g in groups for q in g['items']]
    assert len(questions) == 31
    assert all(q['id'] not in q['pergunta'] for q in questions)
    names = {r['name'] for r in infer({'poeira_branca': 'sim'}, locale)['results']}
    assert names == {{'pt': 'Oídio', 'en': 'Powdery mildew', 'es': 'Oídio'}[locale]}
