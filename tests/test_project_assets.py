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


def test_original_sinta_knowledge_is_unmodified():
    data = (ROOT / 'knowledge/Teste.bcm').read_bytes()
    export = json.loads((ROOT / 'knowledge/sinta_teste_export.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(data).hexdigest() == export['sha256']


def test_final_complementary_knowledge_covers_ten_diseases():
    extension = json.loads((ROOT / 'knowledge/regras_complementares.json').read_text(encoding='utf-8'))
    assert len(extension['regras']) == 22
    assert len(extension['doencas_previstas']) == 10
    assert len(extension['novas_perguntas']) == 15
