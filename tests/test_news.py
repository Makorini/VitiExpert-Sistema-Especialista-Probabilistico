from unittest.mock import patch
from datetime import datetime, timezone
from app import app, _news_cache


def test_news_fallback_when_external_feed_unavailable():
    _news_cache.update(items=[], until=datetime.min.replace(tzinfo=timezone.utc))
    with patch('app.urlopen', side_effect=OSError('network unavailable')):
        with app.test_client() as client:
            response = client.get('/api/news')
            assert response.status_code == 200
            assert response.get_json()['items'] == []
            assert response.get_json()['available'] is False


def _story(title):
    return {'title': title, 'url': 'https://exemplo.com.br/uva', 'source': 'Veículo',
            'feed': 'Notícias Agrícolas', 'published': '', 'image': '', 'image_original': '',
            'description': 'Produção de uvas'}


def test_news_translated_for_english_and_spanish():
    from datetime import timedelta
    _news_cache.update(items=[_story('Festa da Uva tem data marcada')],
                       until=datetime.now(timezone.utc) + timedelta(minutes=5))
    fake = lambda text, target: f'[{target}] {text}'
    with patch('app._translate_text', side_effect=fake):
        with app.test_client() as client:
            pt = client.get('/api/news?lang=pt').get_json()['items'][0]
            en = client.get('/api/news?lang=en').get_json()['items'][0]
            es = client.get('/api/news?lang=es').get_json()['items'][0]
    assert pt['title'] == 'Festa da Uva tem data marcada' and 'translated' not in pt
    assert en['title'] == '[en] Festa da Uva tem data marcada' and en['translated'] is True
    assert en['title_original'] == 'Festa da Uva tem data marcada'
    assert es['description'] == '[es] Produção de uvas'
    # O cache compartilhado continua em português.
    assert _news_cache['items'][0]['title'] == 'Festa da Uva tem data marcada'


def test_news_keeps_portuguese_when_translation_fails():
    from datetime import timedelta
    _news_cache.update(items=[_story('Safra de uva cresce')],
                       until=datetime.now(timezone.utc) + timedelta(minutes=5))
    with patch('app._translate_text', return_value=None):
        with app.test_client() as client:
            item = client.get('/api/news?lang=en').get_json()['items'][0]
    assert item['title'] == 'Safra de uva cresce' and item['translated'] is False


def test_translate_text_rejects_quota_warning():
    from app import _translate_text, _translation_cache
    import io, json as _json
    _translation_cache.clear()
    body = _json.dumps({'responseData': {'translatedText': 'MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS'},
                        'responseStatus': 429}).encode()
    class R(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return None
    with patch('app.urlopen', return_value=R(body)):
        assert _translate_text('Uva', 'en') is None
