"""Envio do e-mail com o código de confirmação de cadastro.

Duas formas de enviar pela conta makorini.dev@gmail.com (configure no .env):

1) Google Apps Script — RECOMENDADO, mesmo método do projeto do salão.
   O script docs/enviar_email_apps_script.gs roda dentro da conta Google e
   envia com MailApp.sendEmail, sem senha de app.
       MAIL_SCRIPT_URL   = URL do "App da Web" (termina em /exec)
       MAIL_SCRIPT_TOKEN = o mesmo texto secreto salvo no script (VITIEXPERT_TOKEN)

2) SMTP do Gmail — alternativa, exige "senha de app" de 16 letras.
       MAIL_USERNAME = conta remetente (padrão: makorini.dev@gmail.com)
       MAIL_PASSWORD = senha de app (Conta Google > Segurança > Senhas de app)
       MAIL_SERVER   = smtp.gmail.com (padrão)
       MAIL_PORT     = 465 (SSL, padrão)

MAIL_FROM_NAME = nome que aparece como remetente (padrão: VitiExpert).

Sem nenhuma das duas configurações o e-mail não é enviado: o código aparece
no terminal do servidor, para testes locais.
"""
from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULT_SENDER = 'makorini.dev@gmail.com'


def mail_settings():
    return {
        'username': os.environ.get('MAIL_USERNAME', DEFAULT_SENDER).strip(),
        'password': os.environ.get('MAIL_PASSWORD', '').replace(' ', '').strip(),
        'server': os.environ.get('MAIL_SERVER', 'smtp.gmail.com').strip(),
        'port': int(os.environ.get('MAIL_PORT', '465')),
        'from_name': os.environ.get('MAIL_FROM_NAME', 'VitiExpert').strip() or 'VitiExpert',
        'script_url': os.environ.get('MAIL_SCRIPT_URL', '').strip(),
        'script_token': os.environ.get('MAIL_SCRIPT_TOKEN', '').strip(),
    }


def _valid_script_url(url):
    parts = urlsplit(url or '')
    return (parts.scheme == 'https' and parts.hostname == 'script.google.com'
            and parts.path.endswith('/exec'))


def mail_configured():
    cfg = mail_settings()
    return bool((cfg.get('script_url') and cfg.get('script_token')) or cfg['password'])


def _print_to_terminal(to, body):
    try:  # acentos corretos no terminal do Windows
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    print('\n[VitiExpert] E-mail NÃO configurado (MAIL_SCRIPT_URL ou MAIL_PASSWORD no .env).'
          ' Mensagem para', to)
    print(body, '\n', flush=True)


def _send_via_apps_script(cfg, to, subject, body, html):
    """Pede ao Google Apps Script (conta makorini.dev) que envie o e-mail."""
    if not _valid_script_url(cfg.get('script_url')):
        print('[VitiExpert] MAIL_SCRIPT_URL inválida: use a URL do App da Web que termina em /exec.',
              flush=True)
        return 'failed'
    payload = json.dumps({
        'token': cfg.get('script_token', ''), 'para': to, 'assunto': subject,
        'texto': body, 'html': html or '', 'nome': cfg.get('from_name', 'VitiExpert'),
    }).encode('utf-8')
    req = Request(cfg['script_url'], data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        # O Google responde com um redirecionamento; o urllib segue sozinho.
        with urlopen(req, timeout=20) as response:
            answer = json.loads(response.read(20_000).decode('utf-8') or '{}')
    except (OSError, ValueError) as exc:
        print('[VitiExpert] Falha ao chamar o Apps Script:', type(exc).__name__, exc, flush=True)
        return 'failed'
    if isinstance(answer, dict) and answer.get('ok') is True:
        return 'sent'
    print('[VitiExpert] Apps Script recusou o envio:',
          answer.get('erro', answer) if isinstance(answer, dict) else answer, flush=True)
    return 'failed'


def _send_via_smtp(cfg, to, subject, body, html):
    msg = EmailMessage()
    msg['From'] = formataddr((cfg.get('from_name', 'VitiExpert'), cfg['username']))
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)  # texto simples, para programas sem HTML
    if html:
        msg.add_alternative(html, subtype='html')
    try:
        with smtplib.SMTP_SSL(cfg['server'], cfg['port'], context=ssl.create_default_context(),
                              timeout=15) as smtp:
            smtp.login(cfg['username'], cfg['password'])
            smtp.send_message(msg)
        return 'sent'
    except (smtplib.SMTPException, OSError) as exc:
        print('[VitiExpert] Falha ao enviar e-mail:', type(exc).__name__, exc, flush=True)
        return 'failed'


def send_mail(to, subject, body, html=None):
    """Envia o e-mail (texto + versão HTML opcional).

    Retorna 'sent', 'not_configured' ou 'failed'.
    """
    cfg = mail_settings()
    if cfg.get('script_url') and cfg.get('script_token'):
        return _send_via_apps_script(cfg, to, subject, body, html)
    if cfg['password']:
        return _send_via_smtp(cfg, to, subject, body, html)
    _print_to_terminal(to, body)
    return 'not_configured'
