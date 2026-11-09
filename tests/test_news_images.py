"""Testes das fotografias da seção Notícias da Viticultura (sem acessar a rede)."""
from unittest.mock import patch
import io
from app import (
    app, _ArticlePhotoParser, _lookup_article_photo, _prepare_photo_news,
    _news_photo_sources, _news_photo_cache, _news_cache,
    _safe_news_url, _is_grape_news,
)
from datetime import datetime, timezone


class FakeResponse:
    def __init__(self, data, url, mime='text/html'):
        self.data = data
        self.url = url
        self.headers = {'Content-Type': mime}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def geturl(self):
        return self.url
    def read(self, max_bytes=-1):
        return self.data[:max_bytes] if max_bytes >= 0 else self.data


def make_item(title, image=''):
    return {
        'title': title,
        'url': 'https://exemplo.com.br/noticia/uva',
        'source': 'Veículo exemplo', 'feed': 'Notícias Agrícolas',
        'published': 'Fri, 06 Nov 2026 19:00:00 GMT',
        'image': image, 'description': 'Produção e cultivo de uvas',
    }


def test_og_image_read_from_original_news():
    data = b'<html><head><meta property="og:image" content="https://imagens.exemplo.com.br/uva.jpg"></head></html>'
    item = make_item('Pesquisa melhora a qualidade da uva brasileira')
    with patch('app.urlopen', return_value=FakeResponse(data, item['url'])):
        result = _lookup_article_photo(item)
    assert result['image'] == 'https://imagens.exemplo.com.br/uva.jpg'


def test_photo_missing_does_not_get_invented():
    data = b'<html><head><title>Noticia</title></head></html>'
    item = make_item('Tecnologia amplia o cultivo de videiras')
    with patch('app.urlopen', return_value=FakeResponse(data, item['url'])):
        assert _lookup_article_photo(item)['image'] == ''


def test_reject_local_remote_urls_and_irrelevant_news():
    assert not _safe_news_url('http://localhost/admin')
    assert not _safe_news_url('https://127.0.0.1/admin')
    assert not _safe_news_url('file:///etc/passwd')
    assert _safe_news_url('https://site.exemplo.com.br/noticia')
    assert _is_grape_news('Nova variedade de uva amplia a safra')
    assert not _is_grape_news('Prefeitura abre concurso público em Videira')


def test_news_list_keeps_stories_without_original_photos():
    original = make_item('Cooperativa apresenta nova variedade de uvas')
    unrelated = make_item('Praga afeta produtores de videiras')
    with patch('app._lookup_article_photo', side_effect=lambda item: {
        **item, 'image': 'https://imagens.exemplo.com.br/uva.jpg' if item == original else ''
    }):
        result = _prepare_photo_news([original, unrelated])
    assert len(result) == 2
    assert result[0]['title'] == original['title']
    assert result[0]['image'].startswith('/api/news/photo/')
    assert result[0]['image_original'].endswith('/uva.jpg')
    assert result[1]['title'] == unrelated['title']
    assert result[1]['image'] == ''
    assert result[1]['image_original'] == ''



def test_proxy_serves_image_of_same_news():
    token = 'a' * 24
    original = 'https://imagens.exemplo.com.br/uva.jpg'
    link = 'https://site.exemplo.com.br/uva'
    body = b'\xff\xd8\xff' + b'0' * 120
    _news_photo_sources[token] = (original, link)
    _news_photo_cache.pop(token, None)
    try:
        with patch('app.urlopen', return_value=FakeResponse(body, original, 'image/jpeg')):
            with app.test_client() as client:
                resp = client.get('/api/news/photo/' + token)
                assert resp.status_code == 200
                assert resp.data == body
                assert resp.mimetype == 'image/jpeg'
    finally:
        _news_photo_sources.pop(token, None)
        _news_photo_cache.pop(token, None)


def test_google_news_without_photos_is_still_listed():
    story = make_item('Viticultura cresce no Brasil')
    story['feed'] = 'Google Notícias'
    story['url'] = 'https://news.google.com/rss/articles/123'
    with patch('app._lookup_article_photo') as lookup:
        result = _prepare_photo_news([story])
    lookup.assert_not_called()
    assert len(result) == 1
    assert result[0]['image'] == ''
    assert result[0]['title'] == story['title']


def test_fallback_illustrations_exist_and_have_valid_webp_headers():
    from pathlib import Path
    root = Path(__file__).parents[1] / 'static' / 'news-fallback'
    for index in range(1, 6):
        data = (root / f'vitiexpert-noticia-{index}.webp').read_bytes()
        assert data[:4] == b'RIFF'
        assert data[8:12] == b'WEBP'
        assert len(data) > 10_000
