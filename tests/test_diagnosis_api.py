"""Integração da API Flask com a base Expert SINTA transposta ao Python."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import app


def test_expert_page_and_scripts():
    client=app.test_client()
    response=client.get('/expert')
    assert response.status_code == 200
    html=response.get_data(as_text=True)
    assert 'id="tcc-diagnose-form"' in html
    assert 'expert.css' in html and 'expert.js' in html
    assert html.count('type="radio"') == 34*3
    assert 'Teste.bcm' not in html
    assert 'dataset_note' not in html
    assert 'tcc-source-note' not in html
    assert 'seis doenças adicionais' not in html.lower()
    for page in ['/','/climate','/diseases']:
        assert client.get(page).status_code == 200


def test_sinta_mildio_and_negative_rule():
    client=app.test_client()
    result=client.post('/api/diagnose?lang=pt',json={'answers':{
        'manchas_amarelas':'sim','folhas_murchas':'sim','chuva_continua':'sim'}})
    assert result.status_code==200
    data=result.get_json()
    assert data['engine']=='sinta_cf_python'
    assert data['results'][0]['id']=='mildio'
    assert data['results'][0]['confidence_percent']==98
    assert data['analyzed_hypotheses']==12
    assert data['diseases_assessed']==10
    assert data['source_file']=='Teste.bcm'

    o=client.post('/api/diagnose',json={'answers':{'poeira_branca':'sim','chuva_frequente':'nao'}}).json
    assert o['results'][0]['id']=='oidio'
    assert o['results'][0]['confidence_percent']==98


def test_unknown_does_not_count_as_absent():
    client=app.test_client()
    for answers in ({}, {'mofo_branco_inferior':'sim'}):
        r=client.post('/api/diagnose',json={'answers':answers})
        assert r.status_code == 200
        assert r.json['results']==[]


def test_translated_diagnosis():
    c=app.test_client()
    answer={'answers':{'poeira_branca':'sim','chuva_frequente':'nao'}}
    assert c.post('/api/diagnose?lang=en',json=answer).json['results'][0]['name']=='Powdery mildew'
    assert c.post('/api/diagnose?lang=es',json=answer).json['results'][0]['name']=='Oídio'


def test_validation_errors():
    client=app.test_client()
    for body in ({'answers':{'S99':'sim'}},{'answers':[]},{'answers':{'poeira_branca':'talvez'}},{'symptoms':['foo']}):
        assert client.post('/api/diagnose',json=body).status_code==400
