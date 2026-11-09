"""Regression: SINTA question IDs must not appear in visible producer labels."""
from pathlib import Path
import sys

from html import unescape
import re
from jinja2 import Template

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from sinta_i18n import question_groups
from sinta_inference import knowledge
from complementary_inference import get_extension


def test_expert_question_ids_are_hidden_in_all_languages():
    html = (PROJECT / 'templates' / 'site.html').read_text(encoding='utf-8')
    start = html.index('<div class="tcc-question">')
    end = html.index('</div>', start)  # includes the question text only
    label_markup = html[start:end]
    assert '<span>{{ question.id }}</span>' not in label_markup

    # Render the same label found in the page template with actual SINTA questions.
    label_start = html.index('<p id="q-label-{{ question.id }}">', start)
    label_end = html.index('</p>', label_start) + len('</p>')
    markup = Template(html[label_start:label_end])

    for lang in ('pt', 'en', 'es'):
        questions = [q for group in question_groups(knowledge()['variaveis']+list(get_extension()['novas_perguntas']), lang)
                     for q in group['items']]
        assert len(questions) == 34
        for question in questions:
            rendered = markup.render(question=question)
            p = re.fullmatch(r'<p id="([^"]+)">(.*?)</p>', rendered, flags=re.DOTALL)
            assert p is not None
            assert p.group(1) == f'q-label-{question["id"]}'
            text = unescape(p.group(2)).strip()
            assert text == question['pergunta']
            assert question['id'] not in text

    assert 'name="{{ question.id }}"' in html
    assert 'aria-labelledby="q-label-{{ question.id }}"' in html
