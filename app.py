
"""VitiExpert — aplicação web Flask para apoio à identificação de doenças da videira.

Motor de regras SE/ENTÃO com Fatores de Certeza e base de conhecimento
proveniente do Expert SINTA, ampliada com regras complementares documentadas.
"""


# ============================================================
# 1. IMPORTAÇÕES
# ============================================================

import os
import threading
import hashlib
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from html import unescape
import re
from email.utils import parsedate_to_datetime

from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    session,
)

from sinta_inference import infer as infer_sinta, sanitize_answers as sanitize_sinta_answers, knowledge as get_sinta_knowledge
from complementary_inference import get_extension as get_complementary_rules
from sinta_i18n import UI as SINTA_UI, question_groups as get_sinta_question_groups


# ============================================================
# 2. CONFIGURAÇÃO DA APLICAÇÃO FLASK
# ============================================================

app = Flask(__name__)

# Assinatura da sessão para a preferência de idioma.
# Em hospedagem, SECRET_KEY permite persistência entre reinicializações.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    os.urandom(32)
)


# ============================================================
# 3. TRADUÇÕES DA INTERFACE
# ============================================================

# Idiomas disponíveis:
# pt = Português
# en = Inglês
# es = Espanhol

TRANSLATIONS = {'pt': {'home': 'Início',
        'expert': 'Sistema Especialista',
        'climate': 'Clima',
        'diseases': 'Doenças e Pragas',
        'navopen': 'Abrir menu',
        'eyebrow': 'CONHECIMENTO QUE CULTIVA',
        'headline': 'Ciência e tecnologia para a saúde das videiras.',
        'subtitle': 'Conhecimento agrícola e apoio inteligente para um cultivo mais saudável '
                    'e sustentável.',
        'explore': 'Explorar o sistema',
        'news_eyebrow': 'ATUALIDADES DO VINHEDO',
        'news_title': 'Notícias da Viticultura',
        'news_intro': 'Notícias de todo o Brasil sobre uvas, videiras e vinhedos, com fotos '
                      'das matérias e imagens ilustrativas quando necessário.',
        'news_loading': 'Consultando notícias recentes…',
        'news_unavailable': 'Não foi possível carregar notícias de viticultura agora. Tente '
                            'novamente mais tarde.',
        'news_source': 'Notícias de veículos externos · Atualização periódica · Fotos: fontes '
                       'originais · Ilustrações: IA',
        'privacy': 'Privacidade',
        'warning': 'Ferramenta educativa. Não substitui avaliação de engenheiro agrônomo ou '
                   'diagnóstico laboratorial.',
        'all': 'Todos os direitos reservados',
        'privacy_intro': 'O VitiExpert não exige cadastro e não guarda as respostas do '
                         'questionário em banco de dados.',
        'privacy_preferences': 'A preferência de idioma é mantida durante a sessão. O tema '
                               'visual e a cidade escolhida no clima podem ficar salvos no '
                               'navegador.',
        'privacy_external': 'A previsão do tempo e as notícias dependem de serviços externos, '
                            'que possuem suas próprias políticas de privacidade.'},
 'en': {'home': 'Home',
        'expert': 'Expert System',
        'climate': 'Weather',
        'diseases': 'Diseases & Pests',
        'navopen': 'Open menu',
        'eyebrow': 'KNOWLEDGE THAT GROWS',
        'headline': 'Science and technology for healthier grapevines.',
        'subtitle': 'Agricultural knowledge and intelligent support for healthier, '
                    'sustainable vineyards.',
        'explore': 'Explore the system',
        'news_eyebrow': 'VINEYARD UPDATES',
        'news_title': 'Viticulture News',
        'news_intro': 'News about grapes, grapevines and vineyards across Brazil, with '
                      'original photographs or illustrative images when needed.',
        'news_loading': 'Loading recent news…',
        'news_unavailable': 'News is temporarily unavailable. Please try again later.',
        'news_source': 'News from external publishers · Periodically updated · Original '
                       'photos: publishers · Illustrations: AI',
        'privacy': 'Privacy',
        'warning': 'Educational tool. Not a substitute for professional agronomic or '
                   'laboratory diagnosis.',
        'all': 'All rights reserved',
        'privacy_intro': 'VitiExpert does not require registration and does not store '
                         'questionnaire answers in a database.',
        'privacy_preferences': 'Language preference is kept for the session. Your chosen '
                               'theme and weather city may be saved in the browser.',
        'privacy_external': 'Weather forecasts and news use external services with their own '
                            'privacy policies.'},
 'es': {'home': 'Inicio',
        'expert': 'Sistema Experto',
        'climate': 'Clima',
        'diseases': 'Enfermedades y Plagas',
        'navopen': 'Abrir menú',
        'eyebrow': 'CONOCIMIENTO QUE CULTIVA',
        'headline': 'Ciencia y tecnología para la salud de las vides.',
        'subtitle': 'Conocimiento agrícola y apoyo inteligente para un cultivo más saludable '
                    'y sostenible.',
        'explore': 'Explorar el sistema',
        'news_eyebrow': 'ACTUALIDAD DEL VIÑEDO',
        'news_title': 'Noticias de Viticultura',
        'news_intro': 'Noticias de todo Brasil sobre uvas, vides y viñedos, con fotografías '
                      'originales o imágenes ilustrativas cuando sea necesario.',
        'news_loading': 'Consultando noticias recientes…',
        'news_unavailable': 'No hay noticias de viticultura disponibles en este momento. '
                            'Inténtelo más tarde.',
        'news_source': 'Noticias de medios externos · Actualización periódica · Fotos: '
                       'publicaciones originales · Ilustraciones: IA',
        'privacy': 'Privacidad',
        'warning': 'Herramienta educativa. No sustituye una evaluación agronómica '
                   'profesional.',
        'all': 'Todos los derechos reservados',
        'privacy_intro': 'VitiExpert no requiere registro ni guarda las respuestas del '
                         'cuestionario en una base de datos.',
        'privacy_preferences': 'El idioma se mantiene durante la sesión. El tema visual y la '
                               'ciudad del clima pueden guardarse en el navegador.',
        'privacy_external': 'El pronóstico del tiempo y las noticias utilizan servicios '
                            'externos con sus propias políticas de privacidad.'}}


# ============================================================
# CONTROLE DE IDIOMA
# ============================================================

def lang():
    """
    Obtém o idioma solicitado pelo usuário.

    Prioridade:
        1. Parâmetro lang da URL.
        2. Idioma salvo na sessão.
        3. Português como idioma padrão.

    Retorna:
        Código do idioma: pt, en ou es.
    """

    code = (
        request.args.get("lang")
        or session.get("lang", "pt")
    )

    # Impede o uso de idiomas não cadastrados.
    if code not in TRANSLATIONS:
        code = "pt"

    # Mantém a preferência durante a navegação.
    session["lang"] = code

    return code


# ============================================================
# 7. CONFIGURAÇÃO DO CACHE DE NOTÍCIAS
# ============================================================

# O cache reduz a quantidade de consultas externas.
# Nenhuma notícia é fabricada ou armazenada permanentemente.

_news_cache = {
    "until": datetime.min.replace(tzinfo=timezone.utc),
    "items": [],
}

# Evita acessos simultâneos ao cache.
_news_lock = threading.Lock()


# ============================================================
# 8. NOTÍCIAS DE UVA E VITICULTURA (SOMENTE A PÁGINA INÍCIO)
# ============================================================

# Fontes externas: somente matérias relacionadas a videiras/uvas.
# Notícias Agrícolas costuma disponibilizar imagens nos elementos RSS;
# o Google Notícias amplia a cobertura temática, mas frequentemente
# não fornece fotografias no RSS. Nunca associar imagem de outra matéria.
_NEWS_FEEDS = (
    ("https://www.noticiasagricolas.com.br/conteudo.rss", "Notícias Agrícolas"),
    ("https://www.noticiasagricolas.com.br/noticias.rss", "Notícias Agrícolas"),
    ("https://www.agrolink.com.br/rss/noticias.rss", "Agrolink"),
    (
        "https://news.google.com/rss/search?q=" + quote(
            '(uva OR videira OR vinhedos OR viticultura OR vitivinicultura OR vinícola) when:30d'
        ) + "&hl=pt-BR&gl=BR&ceid=BR:pt-419", "Google Notícias"
    ),
)
_MEDIA_NS = "{http://search.yahoo.com/mrss/}"
_CONTENT_NS = "{http://purl.org/rss/1.0/modules/content/}"

# Filtro no título, não no nome do veículo (que pode conter "Vinho" sem
# relação com a manchete). 'Vinhedo' sozinho também é nome de município.
_GRAPE_TITLE_RE = re.compile(
    r"\b(?:uvas?|videiras|vinhedos|viticultur\w*|vitivinicultur\w*|"
    r"vitivin[ií]col\w*|vin[ií]colas?|vindima|enoturism\w*|"
    r"grapevines?|vineyards?|grapes?)\b",
    re.IGNORECASE,
)
_WINE_TITLE_RE = re.compile(r"\b(?:vinhos?|espumantes?|wine)\b", re.IGNORECASE)
_WINE_PRODUCTION_RE = re.compile(
    r"\b(?:produ\w+|cultiv\w+|safra\w*|vin[ií]cola\w*|"
    r"viticultur\w*|vitivinicultur\w*|vinhed\w*|uva\w*|"
    r"exporta\w*|colheit\w*|plantio|pesquisa\w*|"
    r"produtor\w*|ind[uú]stria\w*|setor\w*|mercado)\b",
    re.IGNORECASE,
)


def _is_grape_news(title, description=""):
    """Rejeita política, concursos e notícias rurais sem relação com uvas.

    O título precisa mencionar diretamente a cultura; matérias apenas sobre
    vinho só entram quando tratam da cadeia produtiva vitivinícola.
    """
    if not title:
        return False
    # Evita tratar 'Vinhedo' (município de SP) como referência à cultura.
    without_town = re.sub(r"\bVinhedo\s*\(SP\)\b", "", title, flags=re.I)
    if (_GRAPE_TITLE_RE.search(without_town)
            or re.search(r"\b(?:videira|vinhedo)\b", without_town)):
        return True
    if _WINE_TITLE_RE.search(title):
        return bool(_WINE_PRODUCTION_RE.search(title + " " + description))
    return False


class _NewsImageHTMLParser(HTMLParser):
    """Recupera foto e texto do HTML publicado pelo próprio RSS."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.image = ""
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "img" and not self.image:
            attributes = dict(attrs)
            self.image = attributes.get("src") or attributes.get("data-src") or ""

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and len(self.text) < 250:
            self.text.append(data)


def _news_image(item):
    """Foto real fornecida no próprio RSS; nunca foto genérica inventada."""
    candidates = []
    for tag in (_MEDIA_NS + "thumbnail", _MEDIA_NS + "content", "enclosure"):
        for element in item.iter(tag):
            media_type = element.attrib.get("type", "").lower()
            medium = element.attrib.get("medium", "").lower()
            if tag.endswith("content") and medium and medium != "image":
                continue
            if media_type and not media_type.startswith("image/"):
                continue
            candidates.append(element.attrib.get("url", ""))
    candidates.append(item.findtext("image") or "")

    for field in (_CONTENT_NS + "encoded", "description"):
        html_content = item.findtext(field) or ""
        if html_content:
            parser = _NewsImageHTMLParser()
            parser.feed(html_content[:200000])
            candidates.append(parser.image)

    for candidate in candidates:
        candidate = unescape(candidate.strip())
        if (candidate.startswith("https://") and len(candidate) < 1800
                and not re.search(r"(?:favicon|sprite|tracking|pixel|logo)[._/-]", candidate, re.I)):
            return candidate
    return ""


def _news_excerpt(item):
    """Resumo da própria publicação (não gera texto artificial)."""
    source_html = item.findtext("description") or ""
    parser = _NewsImageHTMLParser()
    parser.feed(source_html[:20000])
    excerpt = " ".join(" ".join(parser.text).split())
    return excerpt[:185].rsplit(" ", 1)[0] + "…" if len(excerpt) > 185 else excerpt


def _parse_news_feed(data, publisher):
    """Filtra RSS por assunto, associando a fotografia à matéria correta."""
    root = ET.fromstring(data)
    articles = []
    for item in root.findall("./channel/item")[:150]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link.startswith("https://"):
            continue
        description = "" if publisher == "Google Notícias" else _news_excerpt(item)
        if not _is_grape_news(title, description):
            continue
        source = item.find("source")
        source_name = (
            source.text.strip() if source is not None and source.text
            else publisher
        )
        articles.append({
            "title": title[:220], "url": link,
            "source": source_name[:100],
            "published": (item.findtext("pubDate") or "").strip(),
            "image": _news_image(item),
            "description": description,
            "feed": publisher,
        })
    return articles


def _news_timestamp(article):
    try:
        return parsedate_to_datetime(article["published"]).timestamp()
    except (TypeError, ValueError, IndexError):
        return 0


def _combine_grape_news(feeds):
    """Seleciona notícias diretamente ligadas à uva e prefere o link do veículo."""
    found = [item for feed in feeds for item in feed]
    # Duplicatas do Google e de veículos: preservar o link da fonte original.
    found.sort(
        key=lambda item: (item.get("feed") != "Google Notícias", _news_timestamp(item)),
        reverse=True,
    )
    unique = {}
    for item in found:
        key = re.sub(r"\W+", "", item["title"].casefold())[:100]
        unique.setdefault(key, item)
    return sorted(unique.values(), key=_news_timestamp, reverse=True)


class _ArticlePhotoParser(HTMLParser):
    """Localiza a foto compartilhada pela própria página da notícia."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "meta":
            name = (data.get("property") or data.get("name") or "").lower()
            if name in ("og:image", "og:image:url", "twitter:image", "twitter:image:src"):
                self.images.append(data.get("content", ""))
        elif tag == "link" and "image_src" in (data.get("rel") or "").lower():
            self.images.append(data.get("href", ""))


def _safe_news_url(url):
    """Não aceita IPs locais, protocolos não seguros ou URLs suspeitas."""
    if not isinstance(url, str) or len(url) > 2200:
        return False
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        if parts.scheme != "https" or not host or parts.username or parts.password:
            return False
        if host in ("localhost", "localhost.localdomain") or host.endswith(".local"):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            pass  # Hostname público, não um IP literal.
        return "." in host
    except ValueError:
        return False


def _valid_photo_url(url, page_url=""):
    """Seleciona imagens HTTPS da mesma matéria, excluindo logotipos e pixels."""
    result = urljoin(page_url, unescape(url.strip())) if url else ""
    if (not _safe_news_url(result)
        or re.search(r"(?:favicon|logo|sprite|tracking|1x1|pixel|default-avatar)", result, re.I)
        or re.search(r"\.(?:svg|ico)(?:[?#]|$)", result, re.I)):
        return ""
    return result


def _read_feed(feed):
    url, publisher = feed
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; VitiExpert/0.3; educational news reader)",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9,*/*;q=0.7",
        })
        with urlopen(req, timeout=4) as response:
            payload = response.read(850_000)
        return _parse_news_feed(payload, publisher)
    except (OSError, ValueError, ET.ParseError):
        return []


def _lookup_article_photo(article):
    """Procura og:image / twitter:image na notícia quando o RSS não inclui foto.

    O feed do Google Notícias raramente tem fotografia. Não usamos a miniatura
    da página intermediária do Google como se fosse a da reportagem.
    """
    existing = _valid_photo_url(article.get("image", ""))
    if existing:
        return {**article, "image": existing}

    link = article["url"]
    if not _safe_news_url(link):
        return {**article, "image": ""}
    if urlsplit(link).hostname in {"news.google.com", "google.com", "www.google.com"}:
        return {**article, "image": ""}

    try:
        req = Request(link, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pt-BR,pt;q=0.9",
        })
        with urlopen(req, timeout=4) as response:
            resolved = response.geturl()
            if not _safe_news_url(resolved):
                return {**article, "image": ""}
            mime = response.headers.get("Content-Type", "").lower()
            if mime and not ("html" in mime or "xml" in mime):
                return {**article, "image": ""}
            source = response.read(300_000).decode("utf-8", errors="replace")
        parser = _ArticlePhotoParser()
        parser.feed(source)
        for candidate in parser.images:
            photo = _valid_photo_url(candidate, resolved)
            if photo:
                return {**article, "image": photo}
    except (OSError, ValueError, UnicodeError):
        pass
    return {**article, "image": ""}


# As imagens são vinculadas a tokens criados pelo servidor, nunca a uma URL
# fornecida diretamente pelo visitante. O navegador não depende de hotlinking.
_news_photo_sources = {}
_news_photo_cache = {}
_news_photo_lock = threading.Lock()
_NEWS_IMAGE_TYPES = {
    "image/jpeg": "image/jpeg", "image/png": "image/png",
    "image/webp": "image/webp", "image/avif": "image/avif",
    "image/gif": "image/gif",
}


def _image_token(photo, referer):
    return hashlib.sha256((photo + "\n" + referer).encode("utf-8")).hexdigest()[:24]


def _prepare_photo_news(articles):
    """Mantém as notícias relevantes mesmo quando não existe fotografia real.

    A interface primeiro tenta a foto publicada pela fonte. Sem foto, ou quando
    o carregamento falha, usa imagens locais ilustrativas em sequência.
    Nunca atribui uma fotografia de outra reportagem à matéria.
    """
    selected = [dict(item) for item in articles[:8]]
    # Só consultamos páginas originais de publicações; links intermediários
    # do Google Notícias continuam válidos, mas não fornecem foto.
    pending_indices = [
        index for index, item in enumerate(selected)
        if not _valid_photo_url(item.get("image", ""))
        and urlsplit(item["url"]).hostname not in {
            "news.google.com", "google.com", "www.google.com"
        }
    ]
    if pending_indices:
        with ThreadPoolExecutor(max_workers=min(7, len(pending_indices))) as executor:
            augmented = list(executor.map(
                _lookup_article_photo,
                [selected[index] for index in pending_indices],
            ))
        for index, updated in zip(pending_indices, augmented):
            selected[index] = updated

    results = []
    for item in selected:
        photo_url = _valid_photo_url(item.get("image", ""))
        if photo_url:
            token = _image_token(photo_url, item["url"])
            _news_photo_sources[token] = (photo_url, item["url"])
            results.append({**item, "image": "/api/news/photo/" + token,
                            "image_original": photo_url})
        else:
            # O app.js mostra a próxima das cinco imagens locais.
            results.append({**item, "image": "", "image_original": ""})
    return results


@app.get("/api/news/photo/<token>")
def grape_news_photo(token):
    """Exibe foto original da matéria via cache temporário para evitar hotlink bloqueado."""
    if not re.fullmatch(r"[0-9a-f]{24}", token):
        return ("Not found", 404)
    with _news_photo_lock:
        photo_source = _news_photo_sources.get(token)
        cached = _news_photo_cache.get(token)
    if not photo_source:
        return ("Not found", 404)
    if cached:
        data, mime = cached
    else:
        photo_url, article_url = photo_source
        if not _safe_news_url(photo_url) or not _safe_news_url(article_url):
            return ("Not found", 404)
        try:
            req = Request(photo_url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/png,image/jpeg,image/*;q=0.8",
                "Referer": article_url,
            })
            with urlopen(req, timeout=5) as response:
                mime = response.headers.get("Content-Type", "").split(";", 1)[0].lower().strip()
                if mime not in _NEWS_IMAGE_TYPES:
                    return ("Not found", 404)
                data = response.read(3_000_001)
            if len(data) > 3_000_000 or len(data) < 100:
                return ("Not found", 404)
            # Checagem de assinatura reduz o risco de servir HTML com MIME de foto.
            signatures = {
                "image/jpeg": data[:3] == b"\xff\xd8\xff",
                "image/png": data[:8] == b"\x89PNG\r\n\x1a\n",
                "image/gif": data[:6] in (b"GIF87a", b"GIF89a"),
                "image/webp": data[:4] == b"RIFF" and data[8:12] == b"WEBP",
                "image/avif": b"ftyp" in data[:24] and b"avif" in data[:32],
            }
            if not signatures.get(mime, False):
                return ("Not found", 404)
            with _news_photo_lock:
                if len(_news_photo_cache) > 80:
                    _news_photo_cache.clear()
                _news_photo_cache[token] = (data, mime)
        except (OSError, ValueError):
            return ("Not found", 404)
    response = Response(data, mimetype=mime)
    response.headers["Cache-Control"] = "public, max-age=900"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/news")
def grape_news():
    """Notícias nacionais de viticultura com fotos originais ou ilustrações locais."""
    now = datetime.now(timezone.utc)
    with _news_lock:
        if now < _news_cache["until"]:
            return jsonify({
                "items": _news_cache["items"],
                "updated_at": _news_cache.get("updated_at"),
                "available": bool(_news_cache["items"]),
            })

        with ThreadPoolExecutor(max_workers=len(_NEWS_FEEDS)) as executor:
            feeds = list(executor.map(_read_feed, _NEWS_FEEDS))
        articles = _combine_grape_news(feeds)
        items = _prepare_photo_news(articles)
        _news_cache.update(
            items=items,
            until=now + timedelta(minutes=20 if items else 5),
            updated_at=now.isoformat() if items else _news_cache.get("updated_at"),
        )
        return jsonify({
            "items": items,
            "updated_at": _news_cache.get("updated_at"),
            "available": bool(items),
        })


# ============================================================
# 9. ROTAS DAS PÁGINAS
# ============================================================

@app.route("/")
@app.route("/<page>")
def pages(page="home"):
    """
    Renderiza as páginas do VitiExpert.

    Páginas disponíveis:
        /          - Página inicial
        /expert    - Sistema especialista
        /climate   - Clima
        /diseases  - Doenças e pragas
        /privacy   - Privacidade
    """

    # Páginas permitidas.
    allowed_pages = (
        "home",
        "expert",
        "climate",
        "diseases",
        "privacy",
    )

    # Retorna erro 404 para páginas inexistentes.
    if page not in allowed_pages:
        return ("Not found", 404)

    # Obtém o idioma selecionado.
    code = lang()

    # Renderiza o template com os dados necessários.
    return render_template(
        "site.html",
        page=page,
        lang=code,
        t=TRANSLATIONS[code],
        tcc_question_groups=get_sinta_question_groups(get_sinta_knowledge()["variaveis"] + list(get_complementary_rules()["novas_perguntas"]),code) if page == "expert" else [],
        tx=SINTA_UI[code] if page == "expert" else {},
    )



# ============================================================
# API DE DIAGNÓSTICO — BASE DE CONHECIMENTO E INFERÊNCIA
# ============================================================

@app.post("/api/diagnose")
def diagnose():
    """Inferência em Python utilizando regras originais e complementares.

    O campo answers aceita as 19 perguntas originais e 15 complementares.
    Fatos não informados recebem 'nao_sei', nunca 'nao'. Os CNFs provêm
    do arquivo original e seguem as fórmulas possibilistas do manual SINTA.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or 'answers' not in payload:
        return jsonify({'error':'Envie um objeto JSON com o campo answers.'}), 400
    try:
        answers = sanitize_sinta_answers(payload['answers'])
        result = infer_sinta(answers, lang())
    except (ValueError, TypeError) as exc:
        return jsonify({'error':str(exc)}), 400
    return jsonify(result)


# ============================================================
# 11. INICIALIZAÇÃO DO SERVIDOR
# ============================================================

# Executa o servidor local somente quando app.py
# é iniciado diretamente.

if __name__ == "__main__":

    app.run(debug=False)
