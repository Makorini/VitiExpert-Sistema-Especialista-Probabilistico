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
