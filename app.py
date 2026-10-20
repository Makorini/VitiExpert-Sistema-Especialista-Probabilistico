
"""
============================================================
VITIEXPERT — APLICAÇÃO PRINCIPAL
============================================================

Projeto:
    Sistema Especialista Probabilístico para Diagnóstico
    de Doenças em Videiras.

Tecnologias:
    Python e Flask.

Status:
    Protótipo web em desenvolvimento e testagem.

IMPORTANTE:
    Os escores apresentados nesta versão são heurísticos
    e demonstrativos. Não representam probabilidades
    calibradas ou fatores de certeza validados.

    A base científica está sendo desenvolvida e testada
    no Expert SINTA.
============================================================
"""


# ============================================================
# 1. IMPORTAÇÕES
# ============================================================

import os
import threading
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    session,
)


# ============================================================
# 2. CONFIGURAÇÃO DA APLICAÇÃO FLASK
# ============================================================

app = Flask(__name__)

# Chave de sessão para o ambiente de desenvolvimento.
# Em produção, definir SECRET_KEY como variável de ambiente.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-only-change-before-deployment"
)


# ============================================================
# 3. TRADUÇÕES DA INTERFACE
# ============================================================

# Idiomas disponíveis:
# pt = Português
# en = Inglês
# es = Espanhol

TRANSLATIONS = {

    # --------------------------------------------------------
    # 3.1. PORTUGUÊS
    # --------------------------------------------------------

    "pt": {

        # Navegação
        "home": "Início",
        "expert": "Sistema Especialista",
        "climate": "Clima",
        "diseases": "Doenças e Pragas",
        "login": "Entrar",
        "navopen": "Abrir menu",

        # Página inicial
        "eyebrow": "CONHECIMENTO QUE CULTIVA",
        "headline": "Ciência e tecnologia para a saúde das videiras.",
        "subtitle": (
            "Conhecimento agrícola e apoio inteligente para "
            "um cultivo mais saudável e sustentável."
        ),
        "explore": "Explorar o sistema",
        "welcome": "Tecnologia a serviço do vinhedo",
        "intro": (
            "Uma plataforma educativa de apoio à identificação "
            "de doenças da videira, baseada em sintomas "
            "relatados pelo usuário."
        ),

        # Funcionalidades
        "feature1": "Análise de sintomas",
        "feature1body": (
            "Responda a um questionário sobre sinais "
            "observados na videira."
        ),
        "feature2": "Informações climáticas",
        "feature2body": (
            "Espaço preparado para integração futura "
            "com dados meteorológicos confiáveis."
        ),
        "feature3": "Conhecimento agrícola",
        "feature3body": (
            "Conheça doenças frequentes e características "
            "que ajudam a diferenciá-las."
        ),

        # Sistema especialista
        "expert_title": "Análise de sintomas",
        "expert_sub": (
            "Protótipo experimental: os escores apresentados "
            "não representam probabilidades clínicas ou "
            "agronômicas validadas."
        ),
        "expert_kicker": "UMA ANÁLISE POR ETAPAS",
        "question": "Selecione os sintomas observados",
        "unknown": "Não sei",
        "submit": "Analisar sintomas",
        "result": "Hipóteses sugeridas",
        "results_title": "O que os sinais indicam",
        "none": "Selecione ao menos um sintoma observado.",
        "score": "Escore ilustrativo",
        "reasons": "Sinais considerados",
        "demo": "DEMONSTRAÇÃO",
        "demo_note": (
            "Este questionário é ilustrativo. A base de regras "
            "científica será incorporada após os testes "
            "no Expert SINTA."
        ),
        "not_calibrated": (
            "Os valores são escores heurísticos relativos, "
            "não probabilidades nem fatores de certeza validados."
        ),

        # Doenças
        "d1": "Míldio",
        "d2": "Oídio",
        "d3": "Antracnose",
        "library_kicker": "GUIA DE CAMPO",
        "library_title": "Doenças da videira",
        "library_sub": (
            "Informações introdutórias; confirmar sinais "
            "com profissional especializado."
        ),

        # Clima
        "climate_kicker": "AMBIENTE E CULTIVO",
        "climate_title": "Clima e viticultura",
        "climate_body": (
            "Acompanhamento climático previsto para versões "
            "futuras. Nenhuma informação meteorológica em "
            "tempo real é apresentada nesta versão."
        ),

        # Notícias
        "news_eyebrow": "ATUALIZAÇÕES DO SETOR",
        "news_title": "A viticultura em pauta",
        "news_intro": (
            "Notícias recentes sobre uvas, videiras e "
            "viticultura no Brasil, obtidas de fontes externas."
        ),
        "news_loading": "Consultando notícias recentes…",
        "news_unavailable": (
            "Não foi possível consultar as notícias agora. "
            "Tente novamente mais tarde."
        ),
        "news_source": (
            "Notícias via Google Notícias · Atualização periódica"
        ),

        # Funcionamento
        "how_eyebrow": "O MÉTODO",
        "how_title": "Da observação à orientação",
        "how_intro": (
            "Uma experiência simples, fundamentada em "
            "conhecimento agrícola e regras especializadas."
        ),
        "step1": "Observe a videira",
        "step1body": (
            "Identifique sinais nas folhas, nos ramos ou "
            "nos cachos e informe o que está vendo."
        ),
        "step2": "Informe os sintomas",
        "step2body": (
            "Responda ao questionário. Você poderá indicar "
            "quando não souber uma resposta."
        ),
        "step3": "Entenda o resultado",
        "step3body": (
            "Consulte hipóteses e evidências. A versão "
            "científica será validada a partir das regras "
            "desenvolvidas no SINTA."
        ),

        # Apresentação institucional
        "approach_title": "Conhecimento agrícola, com clareza.",
        "approach_body": (
            "O VitiExpert nasce de um projeto acadêmico em "
            "Ciência da Computação aplicado à viticultura "
            "de Videira, Santa Catarina. O objetivo é tornar "
            "o conhecimento especializado mais acessível, "
            "sem substituir a orientação de profissionais."
        ),
        "approach_link": "Conhecer o sistema",

        # Login e privacidade
        "login_kicker": "ÁREA PESSOAL",
        "login_note": (
            "O acesso por e-mail e o histórico privado de "
            "análises estão previstos para uma próxima etapa."
        ),
        "privacy": "Privacidade",
        "soon": "Em desenvolvimento",

        # Rodapé e avisos
        "warning": (
            "Ferramenta educativa. Não substitui avaliação "
            "de engenheiro agrônomo ou diagnóstico laboratorial."
        ),
        "all": "Todos os direitos reservados",
    },

    # --------------------------------------------------------
    # 3.2. INGLÊS
    # --------------------------------------------------------

    "en": {

        # Navigation
        "home": "Home",
        "expert": "Expert System",
        "climate": "Weather",
        "diseases": "Diseases & Pests",
        "login": "Sign in",
        "navopen": "Open menu",

        # Homepage
        "eyebrow": "KNOWLEDGE THAT GROWS",
        "headline": "Science and technology for healthier grapevines.",
        "subtitle": (
            "Agricultural knowledge and intelligent support "
            "for healthier, sustainable vineyards."
        ),
        "explore": "Explore the system",
        "welcome": "Technology for vineyards",
        "intro": (
            "An educational platform to support identification "
            "of grapevine diseases from user-reported symptoms."
        ),

        # Features
        "feature1": "Symptom assessment",
        "feature1body": (
            "Answer questions about visible signs on the vine."
        ),
        "feature2": "Weather information",
        "feature2body": (
            "Prepared for future integration with reliable "
            "meteorological data."
        ),
        "feature3": "Agricultural knowledge",
        "feature3body": (
            "Learn about common diseases and distinguishing signs."
        ),

        # Expert system
        "expert_title": "Symptom assessment",
        "expert_sub": (
            "Experimental prototype: scores are not validated "
            "diagnostic probabilities."
        ),
        "expert_kicker": "A STEP-BY-STEP ASSESSMENT",
        "question": "Select observed symptoms",
        "unknown": "Not sure",
        "submit": "Assess symptoms",
        "result": "Suggested hypotheses",
        "results_title": "What the signs suggest",
        "none": "Select at least one observed symptom.",
        "score": "Illustrative score",
        "reasons": "Evidence considered",
        "demo": "DEMONSTRATION",
        "demo_note": (
            "This questionnaire is illustrative. The scientific "
            "rule base will be added after Expert SINTA testing."
        ),
        "not_calibrated": (
            "Values are relative heuristic scores, not "
            "probabilities or validated certainty factors."
        ),

        # Diseases
        "d1": "Downy mildew",
        "d2": "Powdery mildew",
        "d3": "Anthracnose",
        "library_kicker": "FIELD GUIDE",
        "library_title": "Grapevine diseases",
        "library_sub": (
            "Introductory information; confirm signs with "
            "a qualified specialist."
        ),

        # Weather
        "climate_kicker": "WEATHER AND GROWING",
        "climate_title": "Weather and viticulture",
        "climate_body": (
            "Weather monitoring is planned for future releases. "
            "No live weather data are shown."
        ),

        # News
        "news_eyebrow": "INDUSTRY UPDATES",
        "news_title": "From the vineyard",
        "news_intro": (
            "Recent grape and viticulture news in Brazil "
            "from external sources."
        ),
        "news_loading": "Loading recent news…",
        "news_unavailable": (
            "News is temporarily unavailable. "
            "Please try again later."
        ),
        "news_source": (
            "News via Google News · Periodically updated"
        ),

        # How it works
        "how_eyebrow": "THE PROCESS",
        "how_title": "From observation to guidance",
        "how_intro": (
            "A straightforward experience based on "
            "agricultural knowledge and expert rules."
        ),
        "step1": "Observe the vine",
        "step1body": (
            "Look for visible signs on leaves, shoots, and grapes."
        ),
        "step2": "Describe the symptoms",
        "step2body": (
            "Answer the questionnaire, including when you are unsure."
        ),
        "step3": "Understand the findings",
        "step3body": (
            "Review hypotheses and evidence. The scientific "
            "engine will be validated using Expert SINTA rules."
        ),

        # Institutional presentation
        "approach_title": "Agricultural knowledge, made clear.",
        "approach_body": (
            "VitiExpert is a Computer Science academic project "
            "focused on viticulture in Videira, Santa Catarina, "
            "Brazil. It supports learning without replacing "
            "professional advice."
        ),
        "approach_link": "Explore the system",

        # Login and privacy
        "login_kicker": "PERSONAL AREA",
        "login_note": (
            "Email access and private assessment history "
            "are planned for a later version."
        ),
        "privacy": "Privacy",
        "soon": "Under development",

        # Footer
        "warning": (
            "Educational tool. Not a substitute for professional "
            "agronomic or laboratory diagnosis."
        ),
        "all": "All rights reserved",
    },

    # --------------------------------------------------------
    # 3.3. ESPANHOL
    # --------------------------------------------------------

    "es": {

        # Navegación
        "home": "Inicio",
        "expert": "Sistema Experto",
        "climate": "Clima",
        "diseases": "Enfermedades y Plagas",
        "login": "Ingresar",
        "navopen": "Abrir menú",

        # Página principal
        "eyebrow": "CONOCIMIENTO QUE CULTIVA",
        "headline": "Ciencia y tecnología para la salud de las vides.",
        "subtitle": (
            "Conocimiento agrícola y apoyo inteligente para "
            "un cultivo más saludable y sostenible."
        ),
        "explore": "Explorar el sistema",
        "welcome": "Tecnología para los viñedos",
        "intro": (
            "Plataforma educativa de apoyo a la identificación "
            "de enfermedades de la vid a partir de síntomas reportados."
        ),

        # Funcionalidades
        "feature1": "Análisis de síntomas",
        "feature1body": (
            "Responda preguntas sobre señales visibles en la vid."
        ),
        "feature2": "Información climática",
        "feature2body": (
            "Preparado para integrar datos meteorológicos "
            "fiables en el futuro."
        ),
        "feature3": "Conocimiento agrícola",
        "feature3body": (
            "Conozca enfermedades comunes y sus características."
        ),

        # Sistema experto
        "expert_title": "Análisis de síntomas",
        "expert_sub": (
            "Prototipo experimental: las puntuaciones no son "
            "probabilidades diagnósticas validadas."
        ),
        "expert_kicker": "UN ANÁLISIS PASO A PASO",
        "question": "Seleccione los síntomas observados",
        "unknown": "No sé",
        "submit": "Analizar síntomas",
        "result": "Hipótesis sugeridas",
        "results_title": "Qué indican las señales",
        "none": "Seleccione al menos un síntoma observado.",
        "score": "Puntuación ilustrativa",
        "reasons": "Señales consideradas",
        "demo": "DEMOSTRACIÓN",
        "demo_note": (
            "Este cuestionario es ilustrativo. Las reglas "
            "científicas se incorporarán tras las pruebas "
            "en Expert SINTA."
        ),
        "not_calibrated": (
            "Los valores son puntuaciones heurísticas relativas, "
            "no probabilidades ni factores de certeza validados."
        ),

        # Enfermedades
        "d1": "Mildiu",
        "d2": "Oídio",
        "d3": "Antracnosis",
        "library_kicker": "GUÍA DE CAMPO",
        "library_title": "Enfermedades de la vid",
        "library_sub": (
            "Información introductoria; confirme los síntomas "
            "con un especialista."
        ),

        # Clima
        "climate_kicker": "CLIMA Y CULTIVO",
        "climate_title": "Clima y viticultura",
        "climate_body": (
            "Seguimiento climático previsto para versiones futuras. "
            "No hay datos meteorológicos en tiempo real."
        ),

        # Noticias
        "news_eyebrow": "ACTUALIDAD DEL SECTOR",
        "news_title": "La viticultura en foco",
        "news_intro": (
            "Noticias recientes sobre uvas y viticultura "
            "en Brasil procedentes de fuentes externas."
        ),
        "news_loading": "Consultando noticias recientes…",
        "news_unavailable": (
            "No se pudieron cargar las noticias. "
            "Inténtelo más tarde."
        ),
        "news_source": (
            "Noticias vía Google Noticias · Actualización periódica"
        ),

        # Funcionamiento
        "how_eyebrow": "EL PROCESO",
        "how_title": "De la observación a la orientación",
        "how_intro": (
            "Una experiencia sencilla basada en conocimientos "
            "agrícolas y reglas expertas."
        ),
        "step1": "Observe la vid",
        "step1body": (
            "Identifique señales en hojas, brotes y racimos."
        ),
        "step2": "Indique los síntomas",
        "step2body": (
            "Responda al cuestionario, incluso cuando "
            "no esté seguro."
        ),
        "step3": "Comprenda el resultado",
        "step3body": (
            "Consulte hipótesis y evidencias. El motor "
            "científico se validará con reglas de Expert SINTA."
        ),

        # Presentación institucional
        "approach_title": "Conocimiento agrícola, con claridad.",
        "approach_body": (
            "VitiExpert es un proyecto académico de Informática "
            "dedicado a la viticultura de Videira, Santa Catarina, "
            "Brasil. No sustituye el asesoramiento profesional."
        ),
        "approach_link": "Explorar el sistema",

        # Acceso y privacidad
        "login_kicker": "ÁREA PERSONAL",
        "login_note": (
            "El acceso por correo y el historial privado "
            "se añadirán en otra etapa."
        ),
        "privacy": "Privacidad",
        "soon": "En desarrollo",

        # Avisos
        "warning": (
            "Herramienta educativa. No sustituye una "
            "evaluación agronómica profesional."
        ),
        "all": "Todos los derechos reservados",
    },
}


# ============================================================
# 4. SINTOMAS DO QUESTIONÁRIO DEMONSTRATIVO
# ============================================================

# Os sintomas abaixo são utilizados na interface web.
# Ainda não representam a base de regras validada no SINTA.

SYMPTOMS = {

    "manchas_oleosas": {
        "pt": "Manchas amareladas ou oleosas nas folhas",
        "en": "Yellowish or oily leaf spots",
        "es": "Manchas amarillentas o aceitosas en hojas",
    },

    "mofo_face_inferior": {
        "pt": "Crescimento esbranquiçado na face inferior das folhas",
        "en": "Whitish growth on leaf undersides",
        "es": "Crecimiento blanquecino en el envés de hojas",
    },

    "po_branco": {
        "pt": "Pó branco sobre folhas ou cachos",
        "en": "White powder on leaves or clusters",
        "es": "Polvo blanco sobre hojas o racimos",
    },

    "deformacao": {
        "pt": "Deformação de folhas ou brotos",
        "en": "Distorted leaves or shoots",
        "es": "Deformación de hojas o brotes",
    },

    "lesoes_escuras": {
        "pt": "Lesões escuras e deprimidas nos ramos ou bagas",
        "en": "Dark sunken lesions on shoots or berries",
        "es": "Lesiones oscuras y hundidas en brotes o bayas",
    },

    "manchas_necroticas": {
        "pt": "Manchas necróticas com bordas escuras",
        "en": "Necrotic spots with dark borders",
        "es": "Manchas necróticas con bordes oscuros",
    },
}


# ============================================================
# 5. REGRAS E PESOS DEMONSTRATIVOS
# ============================================================

# ATENÇÃO:
# Estes pesos são exclusivamente ilustrativos.
#
# Não foram estimados a partir de amostras, especialistas
# ou experimentos científicos.
#
# Não representam probabilidades ou fatores de certeza.
#
# d1 = Míldio
# d2 = Oídio
# d3 = Antracnose

RULES = {

    "d1": {
        "manchas_oleosas": 2,
        "mofo_face_inferior": 3,
    },

    "d2": {
        "po_branco": 3,
        "deformacao": 1,
    },

    "d3": {
        "lesoes_escuras": 3,
        "manchas_necroticas": 2,
    },
}


# ============================================================
# 6. CONTROLE DE IDIOMA
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
# 8. API DE NOTÍCIAS SOBRE VITICULTURA
# ============================================================

@app.get("/api/news")
def grape_news():
    """
    Consulta manchetes públicas relacionadas à viticultura.

    Fonte:
        RSS do Google Notícias.

    Cache:
        15 minutos após uma consulta bem-sucedida.
        3 minutos após uma falha de consulta.

    Retorna:
        JSON com notícias, data de atualização
        e indicação de disponibilidade.
    """

    now = datetime.now(timezone.utc)

    with _news_lock:

        # ----------------------------------------------------
        # 8.1. VERIFICAÇÃO DO CACHE
        # ----------------------------------------------------

        if now < _news_cache["until"]:

            return jsonify({
                "items": _news_cache["items"],
                "updated_at": _news_cache.get("updated_at"),
                "available": bool(_news_cache["items"]),
            })

        try:

            # ------------------------------------------------
            # 8.2. CONFIGURAÇÃO DA CONSULTA
            # ------------------------------------------------

            query = quote(
                "(uva OR videira OR viticultura OR vinhedo) "
                "(Brasil OR Santa Catarina)"
            )

            feed_url = (
                "https://news.google.com/rss/search"
                f"?q={query}"
                "&hl=pt-BR"
                "&gl=BR"
                "&ceid=BR:pt-419"
            )

            # Identificação da aplicação na requisição.
            req = Request(
                feed_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 VitiExpert/0.2 (+educational)"
                    )
                },
            )

            # ------------------------------------------------
            # 8.3. OBTENÇÃO DAS NOTÍCIAS
            # ------------------------------------------------

            with urlopen(req, timeout=5) as response:
                data = response.read(350000)

            # Converte o conteúdo RSS em XML.
            root = ET.fromstring(data)

            items = []

            # Limita a quantidade de notícias exibidas.
            for item in root.findall("./channel/item")[:6]:

                # Título da notícia.
                title = (
                    item.findtext("title") or ""
                ).strip()

                # Endereço da notícia.
                link = (
                    item.findtext("link") or ""
                ).strip()

                # Data de publicação.
                published = (
                    item.findtext("pubDate") or ""
                ).strip()

                # Fonte responsável pela publicação.
                source = item.find("source")

                source_name = (
                    source.text.strip()
                    if source is not None and source.text
                    else "Google Notícias"
                )

                # Adiciona apenas notícias com dados válidos.
                if title and link.startswith("https://"):

                    items.append({
                        "title": title[:220],
                        "url": link,
                        "source": source_name[:100],
                        "published": published,
                    })

            # ------------------------------------------------
            # 8.4. ATUALIZAÇÃO DO CACHE
            # ------------------------------------------------

            _news_cache.update(
                items=items,
                until=now + timedelta(minutes=15),
                updated_at=now.isoformat(),
            )

        except (OSError, ValueError, ET.ParseError):

            # Aguarda três minutos antes de tentar novamente.
            _news_cache["until"] = (
                now + timedelta(minutes=3)
            )

        # ----------------------------------------------------
        # 8.5. RESPOSTA DA API
        # ----------------------------------------------------

        return jsonify({
            "items": _news_cache["items"],
            "updated_at": _news_cache.get("updated_at"),
            "available": bool(_news_cache["items"]),
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
        /login     - Login
        /privacy   - Privacidade
    """

    # Páginas permitidas.
    allowed_pages = (
        "home",
        "expert",
        "climate",
        "diseases",
        "login",
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
        symptoms=SYMPTOMS,
        rules=RULES,
    )


# ============================================================
# 10. API DE DIAGNÓSTICO DEMONSTRATIVO
# ============================================================

@app.post("/api/diagnose")
def diagnose():
    """
    Recebe sintomas informados pelo usuário.

    Calcula somente escores heurísticos ilustrativos.

    IMPORTANTE:
        Esta função ainda não utiliza o motor científico
        de inferência baseado no Expert SINTA.

    Retorna:
        JSON com hipóteses, escores e sinais considerados.
    """

    # --------------------------------------------------------
    # 10.1. RECEBIMENTO DOS DADOS
    # --------------------------------------------------------

    payload = request.get_json(silent=True) or {}

    # Obtém a lista de sintomas.
    chosen = payload.get("symptoms", [])

    # --------------------------------------------------------
    # 10.2. VALIDAÇÃO DOS SINTOMAS
    # --------------------------------------------------------

    invalid_input = (
        not isinstance(chosen, list)
        or len(chosen) > len(SYMPTOMS)
        or any(
            not isinstance(item, str)
            for item in chosen
        )
    )

    if invalid_input:

        return jsonify({
            "error": "Invalid symptoms"
        }), 400

    # Considera somente sintomas cadastrados.
    chosen = set(chosen) & set(SYMPTOMS)

    # Obtém o idioma selecionado.
    code = lang()

    # --------------------------------------------------------
    # 10.3. TRATAMENTO DE LISTA VAZIA
    # --------------------------------------------------------

    if not chosen:

        return jsonify({
            "results": [],
            "message": TRANSLATIONS[code]["none"],
        })

    # Armazena as hipóteses encontradas.
    results = []

    # --------------------------------------------------------
    # 10.4. CÁLCULO DOS ESCORES ILUSTRATIVOS
    # --------------------------------------------------------

    for disease, weights in RULES.items():

        # Identifica sintomas relacionados à doença.
        matches = [
            symptom
            for symptom in weights
            if symptom in chosen
        ]

        # Ignora doenças sem sintomas correspondentes.
        if not matches:
            continue

        # Soma os pesos demonstrativos.
        score = sum(
            weights[symptom]
            for symptom in matches
        )

        # Adiciona a hipótese ao resultado.
        results.append({

            "id": disease,

            "name": TRANSLATIONS[code][disease],

            "score": score,

            "evidence": [
                SYMPTOMS[symptom][code]
                for symptom in matches
            ],
        })

    # --------------------------------------------------------
    # 10.5. ORDENAÇÃO DAS HIPÓTESES
    # --------------------------------------------------------

    # Ordena do maior para o menor escore.
    # Em caso de empate, utiliza o identificador da doença.
    results.sort(
        key=lambda result: (
            -result["score"],
            result["id"],
        )
    )

    # --------------------------------------------------------
    # 10.6. RESPOSTA DA API
    # --------------------------------------------------------

    return jsonify({

        "results": results,

        "disclaimer": (
            TRANSLATIONS[code]["not_calibrated"]
        ),
    })


# ============================================================
# 11. INICIALIZAÇÃO DO SERVIDOR
# ============================================================

# Executa o servidor local somente quando app.py
# é iniciado diretamente.

if __name__ == "__main__":

    app.run(debug=True)
