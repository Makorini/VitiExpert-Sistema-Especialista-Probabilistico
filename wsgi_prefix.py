"""Publica o VitiExpert dentro de /VitiExpert (ex.: https://makorini.com.br/VitiExpert).

Uso, na pasta do projeto:
    python -m waitress --listen=127.0.0.1:8080 wsgi_prefix:app

O Cloudflare Tunnel encaminha https://makorini.com.br/VitiExpert/... para 127.0.0.1:8080.
Os links do site usam request.script_root, então funcionam com e sem o prefixo:
rodando direto (python app.py), o site continua na raiz, como antes.
"""
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.utils import redirect
from werkzeug.wrappers import Response

from app import app as vitiexpert_app

PREFIXO = "/VitiExpert"


def _fora_do_prefixo(environ, start_response):
    """Fora de /VitiExpert: a raiz leva ao sistema; o resto não existe."""
    if environ.get("PATH_INFO", "") in ("", "/"):
        return redirect(PREFIXO + "/")(environ, start_response)
    return Response("Página não encontrada", status=404)(environ, start_response)


def _sistema(environ, start_response):
    """/VitiExpert sem a barra final vira /VitiExpert/."""
    if environ.get("PATH_INFO", "") == "":
        return redirect(PREFIXO + "/")(environ, start_response)
    return vitiexpert_app(environ, start_response)


app = DispatcherMiddleware(_fora_do_prefixo, {PREFIXO: _sistema})
