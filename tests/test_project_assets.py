"""Testes de integridade dos recursos do projeto entregue."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'static'


def test_climate_final_scenes_and_overlays_exist():
    assert not (STATIC / 'climate-scenes').exists()
    css = (STATIC / 'climate.css').read_text(encoding='utf-8')
    for condition in ('clear', 'partly', 'cloudy', 'fog', 'rain', 'snow', 'storm'):
        for period in ('day', 'night'):
            image = f'climate-backgrounds/{condition}-{period}.webp'
            assert (STATIC / image).is_file()
            assert image in css
    for image in ('climate-backgrounds/hot-day.webp',
                  'climate-backgrounds/weather-clouds.svg',
                  'climate-backgrounds/weather-snow.webp',
                  'climate-backgrounds/weather-stars.webp'):
        assert (STATIC / image).is_file()
        assert image in css


def test_every_css_local_image_exists():
    for css_path in STATIC.glob('*.css'):
        css = css_path.read_text(encoding='utf-8')
        for value in re.findall(r'''url\(\s*['"]?([^)'\"]+)''', css):
            value = value.strip()
            if value.startswith(('data:', 'http:', 'https:')):
                continue
            if value.startswith('/static/'):
                path = STATIC / value.removeprefix('/static/')
            else:
                path = css_path.parent / value
            assert path.is_file(), (css_path.name, value)


def test_sinta_base_export_matches_bcm_file():
    data = (ROOT / 'knowledge/VitiExpert10.bcm').read_bytes()
    export = json.loads((ROOT / 'knowledge/sinta_base_export.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(data).hexdigest() == export['sha256']
    assert len(export['hipoteses']) == 10 and len(export['regras']) == 17


def test_tab_icon_is_original_and_favicon_route_works():
    from app import app
    client = app.test_client()
    html = client.get('/').get_data(as_text=True)
    assert 'favicon-vitiexpert.png' in html and 'apple-touch-icon.png' in html
    r = client.get('/favicon.ico')
    assert r.status_code == 200 and r.mimetype == 'image/png'
