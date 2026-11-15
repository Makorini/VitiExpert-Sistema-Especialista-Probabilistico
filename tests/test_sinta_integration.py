"""Verificação reprodutível da transposição do Teste.bcm para Python."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from sinta_bcm_import import decode, SOURCE
from sinta_inference import infer, knowledge, combine_certainties, sanitize_answers
from sinta_i18n import question_groups, UI


def test_bcm_exact_parsing():
    raw = decode(SOURCE)
    written = knowledge()
    assert raw == written
    assert raw['quantidades'] == {'variaveis':20,'valores':65,'regras':8,'premissas':21,'conclusoes':16,'hipoteses':8}
    assert len(raw['sha256']) == 64
    assert {r['numero_original'] for r in raw['regras']} == set(range(1,9))


def test_every_sinta_rule_triggers_with_recorded_values():
    for rule in knowledge()['regras']:
        answers={c['variavel']:('sim' if c['valor']=='sim' else 'nao') for c in rule['se_todas']}
        report=infer(answers)
        expected=rule['entao'][0]['valor']
        assert any(r['id']==expected and r['confidence_percent']>0 for r in report['results']), rule['id']
        matched=next(r for r in report['results'] if r['id']==expected)
        assert any(fr['id']==rule['id'] for fr in matched['fired_rules'])


def test_mildio_and_negative_answers():
    d=infer({'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'})
    assert d['results'][0]['id']=='mildio'
    assert d['results'][0]['confidence_percent']==98.0
    o=infer({'poeira_branca':'sim','chuva_frequente':'nao'})
    assert o['results'][0]['id']=='oidio'
    assert o['results'][0]['confidence_percent']==99.4
    a=infer({'folhas_murchas':'sim','solo_encharcado':'sim','manchas_foliares_tipicas':'nao'})
    assert a['results'][0]['id']=='asfixia_radicular'
    assert a['results'][0]['confidence_percent']==88.0


def test_unknown_is_not_no_and_incomplete_does_not_fire():
    # A nova regra COMP-R12 identifica oídio com pó branco isolado.
    # Isso NÃO dispara indevidamente a antiga regra SINTA que exige chuva=Não.
    for a in ({'poeira_branca':'sim'}, {'poeira_branca':'sim','chuva_frequente':'nao_sei'},
              {'poeira_branca':'sim','chuva_frequente':'sim'}):
        r=infer(a)['results'][0]
        assert r['id']=='oidio'
        assert r['confidence_percent']==68.0
        assert all(not hit['id'].startswith('SINTA-') for hit in r['fired_rules'])
    assert infer({})['results']==[]
    assert len(infer({'poeira_branca':'sim'})['suggested_questions'])>=1


def test_sinta_certainty_combination():
    assert round(combine_certainties(.9,.8),6)==.98
    assert round(combine_certainties(.7,.6),6)==.88
    with pytest.raises(ValueError): combine_certainties(1.4,.4)


def test_interface_groups_and_translation():
    ids={p['id'] for lang in ('pt','en','es') for g in question_groups(knowledge()['variaveis'],lang) for p in g['items']}
    assert ids == set(knowledge()['variaveis'])-{'diagnostico'}
    for lang in ('pt','en','es'):
        assert sum(len(g['items']) for g in question_groups(knowledge()['variaveis'],lang))==19
        assert UI[lang]['analyze']
        assert infer({'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'},lang)['results'][0]['name']


def test_strict_answer_validation():
    for data in ({'a':'sim'}, {'poeira_branca':'yes'}, {'poeira_branca':True}, []):
        with pytest.raises(ValueError):sanitize_answers(data)


# ---- Confiança do usuário (c1), como no Expert SINTA ----
from sinta_inference import premise_and, premise_or


def test_and_is_product_or_is_probabilistic_sum():
    # Exemplos do próprio manual do Expert SINTA (seção 1.4).
    assert round(premise_and([.8, .7]), 6) == .56
    assert round(premise_or([.8, .7]), 6) == .94


def test_user_certainty_times_rule_cnf():
    # SINTA-R01: 3 condições, CNFs 90% e 80%. Certezas 70%, 90% e 100%.
    answers={'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'}
    out=infer(answers, certainties={'manchas_amarelas':70,'folhas_murchas':90})
    rule=next(r for r in out['results'][0]['fired_rules'] if r['id']=='SINTA-R01')
    # E = produto: 0,7 * 0,9 * 1,0 = 0,63
    assert rule['premise_percent']==63.0
    # 0,63*0,9=0,567 ; 0,63*0,8=0,504 ; 0,567+0,504-0,567*0,504 = 0,7852
    assert rule['confidence_percent']==78.5


def test_rule_below_minimum_confidence_is_rejected():
    answers={'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'}
    # 0,7 * 0,7 = 0,49 < 50% -> regra rejeitada, como no SINTA
    out=infer(answers, certainties={'manchas_amarelas':70,'folhas_murchas':70})
    assert not any(r['id']=='SINTA-R01' for x in out['results'] for r in x['fired_rules'])
    assert {'id':'SINTA-R01','premise_percent':49.0} in out['rejected_rules']
    assert 'mínimo de 50%' in out['message']
    # exatamente 50% é aceito
    out=infer({'poeira_branca':'sim'}, certainties={'poeira_branca':50})
    assert out['results'][0]['id']=='oidio'


def test_default_certainty_is_100_percent():
    answers={'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'}
    assert infer(answers)['results'][0]['confidence_percent']==infer(answers, certainties={})['results'][0]['confidence_percent']==98.0


def test_zero_certainty_does_not_fire_rule():
    out=infer({'poeira_branca':'sim'}, certainties={'poeira_branca':0})
    assert out['results']==[]


@pytest.mark.parametrize('bad',[{'poeira_branca':150},{'poeira_branca':-1},{'poeira_branca':'70'},{'inexistente':50},[70]])
def test_invalid_certainty_rejected(bad):
    with pytest.raises(ValueError):
        infer({'poeira_branca':'sim'}, certainties=bad)
