import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import app

def test_pages():
    client=app.test_client()
    for page in ['/','/expert','/climate','/diseases','/login']:
        assert client.get(page).status_code==200

def test_locales():
    client=app.test_client()
    for lang in ['pt','en','es']:
        assert client.get('/?lang='+lang).status_code==200

def test_diagnosis():
    client=app.test_client()
    r=client.post('/api/diagnose',json={'symptoms':['manchas_oleosas','mofo_face_inferior']})
    assert r.status_code==200
    assert r.json['results'][0]['id']=='d1'
    assert r.json['results'][0]['score']==5

def test_unknown_does_not_generate_diagnosis():
    client=app.test_client()
    assert client.post('/api/diagnose',json={'symptoms':[]}).json['results']==[]

def test_invalid_input():
    client=app.test_client()
    assert client.post('/api/diagnose',json={'symptoms':'foo'}).status_code==400
