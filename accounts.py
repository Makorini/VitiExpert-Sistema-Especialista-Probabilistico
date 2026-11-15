"""Contas de usuário do VitiExpert: cadastro, verificação de e-mail, login,
histórico privado de consultas e exclusão da conta.

Segurança:
- senhas guardadas apenas como hash (werkzeug, scrypt);
- código de confirmação de 6 dígitos enviado por e-mail, válido por 15
  minutos, guardado só como hash, com no máximo 5 tentativas;
- token CSRF em todos os formulários;
- bloqueio de 15 minutos após 5 senhas erradas para o mesmo e-mail;
- cada consulta ao banco filtra pelo usuário da sessão (dados isolados).
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import threading
import time
from datetime import datetime, timedelta

from flask import (Blueprint, abort, current_app, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from html import escape

import account_store as store
from account_i18n import ACCOUNT_TEXT, MONTHS, MONTHS_FULL
from account_mail import send_mail
from sinta_i18n import disease_name

bp = Blueprint('accounts', __name__)

EMAIL_RE = re.compile(r'^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,}$')
CODE_MINUTES = 15          # validade do código de confirmação
CODE_MAX_ATTEMPTS = 5      # tentativas erradas antes de exigir novo código
MAX_FAILS, LOCK_SECONDS = 5, 15 * 60
_fails = {}
_fails_lock = threading.Lock()


# ----------------------------- utilidades -------------------------------

def _lang():
    return current_app.extensions['viti_lang']()


def _txt(key, **kw):
    text = ACCOUNT_TEXT[_lang()][key]
    return text.format(**kw) if kw else text


def _code_hash(user_id, code):
    """Hash do código (HMAC com a chave secreta): o código não fica no banco."""
    key = str(current_app.secret_key).encode()
    return hmac.new(key, f'{user_id}:{code}'.encode(), hashlib.sha256).hexdigest()


def _render(page, **ctx):
    code = _lang()
    return render_template('site.html', page=page, lang=code,
                           t=current_app.extensions['viti_translations'][code],
                           tcc_question_groups=[], tx={}, **ctx)


def _csrf_ok():
    sent = request.form.get('csrf_token', '')
    expected = session.get('csrf_token', '')
    return bool(expected) and secrets.compare_digest(sent, expected)


def _valid_password(password):
    return (8 <= len(password) <= 128 and re.search(r'[A-Za-zÀ-ÿ]', password)
            and re.search(r'\d', password))


def _safe_next(target):
    if target and target.startswith('/') and not target.startswith('//') and '\\' not in target:
        return target
    return None


def _send_verification(user_id, name, email):
    """Gera um novo código de 6 dígitos e envia por e-mail."""
    code = f'{secrets.randbelow(1_000_000):06d}'
    expires = store.now_utc() + timedelta(minutes=CODE_MINUTES)
    store.set_verify_code(user_id, _code_hash(user_id, code), expires)
    intro = _txt('mail_intro')
    expires_txt = _txt('mail_expires', minutes=CODE_MINUTES)
    ignore = _txt('mail_ignore')
    text = f'{intro}\n\n{code}\n\n{expires_txt}\n\n{ignore}\n\n— VitiExpert'
    return send_mail(email, _txt('mail_subject'), text,
                     html=_verification_html(intro, code, expires_txt, ignore))


def _verification_html(intro, code, expires_txt, ignore):
    """E-mail no mesmo formato do modelo: texto simples e código grande."""
    return f"""<!doctype html>
<html lang="{_lang()}"><body style="margin:0;padding:24px;background:#ffffff;">
<div style="max-width:560px;font-family:Arial,Helvetica,sans-serif;color:#222222;font-size:14px;line-height:1.6;">
  <p style="margin:0 0 22px;">{escape(intro)}</p>
  <p style="margin:0 0 26px;font-size:32px;font-weight:700;letter-spacing:10px;color:#222222;">{code}</p>
  <p style="margin:0 0 8px;">{escape(expires_txt)}</p>
  <p style="margin:0;">{escape(ignore)}</p>
</div>
</body></html>"""


def _mail_message(status, ok_key, **kw):
    if status == 'sent':
        return 'ok', _txt(ok_key, **kw)
    if status == 'not_configured':
        return 'warn', _txt('mail_not_configured')
    return 'error', _txt('mail_failed')


def _locked(email):
    with _fails_lock:
        fails, since = _fails.get(email, (0, 0.0))
        if fails >= MAX_FAILS and time.time() - since < LOCK_SECONDS:
            return True
        if time.time() - since >= LOCK_SECONDS:
            _fails.pop(email, None)
    return False


def _register_fail(email):
    with _fails_lock:
        fails, since = _fails.get(email, (0, time.time()))
        _fails[email] = (fails + 1, since)


def _login_session(user):
    lang = session.get('lang')
    session.clear()  # evita fixação de sessão
    if lang:
        session['lang'] = lang
    session['user_id'] = user['id']
    session.permanent = True


def login_required(view):
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('accounts.login', lang=_lang(), next=request.path))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


# ----------------------------- integração -------------------------------

def init_accounts(app, translations, lang_func):
    """Registra as contas no app Flask (chamado pelo app.py)."""
    app.extensions['viti_translations'] = translations
    app.extensions['viti_lang'] = lang_func
    for code, texts in ACCOUNT_TEXT.items():
        translations[code].update({k: v for k, v in texts.items() if not k.startswith('mail_')})
    store.init_db(app)
    app.register_blueprint(bp)

    @app.before_request
    def load_user():
        g.user = None
        uid = session.get('user_id')
        if uid is not None:
            user = store.find_user(uid)
            if user is not None and user['verified']:
                g.user = user
            else:
                session.pop('user_id', None)

    @app.context_processor
    def account_context():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return {'current_user': g.get('user'), 'csrf_token': session['csrf_token']}


def record_consultation(answers, certainties, report):
    """Chamado pela API de diagnóstico: grava só para usuário autenticado."""
    if g.get('user') is None:
        return False
    store.save_consultation(g.user['id'], answers, certainties, report)
    return True


# ------------------------------- rotas ----------------------------------

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect(url_for('accounts.account', lang=_lang()))
    message = None
    form = {'email': ''}
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()[:254]
        password = request.form.get('password', '')
        form['email'] = email
        if not _csrf_ok():
            message = ('error', _txt('err_csrf'))
        elif _locked(email):
            message = ('error', _txt('err_locked'))
        else:
            user = store.find_user_by_email(email)
            if user is None or not check_password_hash(user['password_hash'], password):
                _register_fail(email)
                message = ('error', _txt('err_login'))
            elif not user['verified']:
                # Senha certa, mas e-mail ainda não confirmado: vai digitar o código.
                session['account_flash'] = ('error', _txt('err_unverified'))
                return redirect(url_for('accounts.verify', lang=_lang(), email=email))
            else:
                with _fails_lock:
                    _fails.pop(email, None)
                _login_session(user)
                target = _safe_next(request.args.get('next')) or url_for('accounts.account', lang=_lang())
                return redirect(target)
    flash = session.pop('account_flash', None)
    return _render('login', message=message or flash, form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None:
        return redirect(url_for('accounts.account', lang=_lang()))
    message, errors = None, []
    form = {'name': '', 'email': ''}
    if request.method == 'POST':
        name = ' '.join(request.form.get('name', '').split())[:200]
        email = request.form.get('email', '').strip().lower()[:300]
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        form = {'name': name, 'email': email}
        if not _csrf_ok():
            errors.append(_txt('err_csrf'))
        else:
            if not 1 <= len(name) <= 80:
                errors.append(_txt('err_name'))
            if len(email) > 254 or not EMAIL_RE.match(email):
                errors.append(_txt('err_email'))
            if not _valid_password(password):
                errors.append(_txt('err_password'))
            elif password != password2:
                errors.append(_txt('err_password2'))
            if not errors and store.find_user_by_email(email) is not None:
                errors.append(_txt('err_exists'))
        if not errors:
            uid = store.create_user(name, email, generate_password_hash(password), _lang())
            status = _send_verification(uid, name, email)
            session['account_flash'] = _mail_message(status, 'ok_sent', email=email)
            return redirect(url_for('accounts.verify', lang=_lang(), email=email))
        message = ('error', ' '.join(errors))
    return _render('register', message=message, form=form)


@bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """Tela "Confirmar e-mail": o usuário digita o código recebido."""
    if g.user is not None:
        return redirect(url_for('accounts.account', lang=_lang()))
    email = (request.values.get('email') or '').strip().lower()[:254]
    message = None
    if request.method == 'POST':
        code = re.sub(r'\D', '', request.form.get('code', ''))[:6]
        user = store.find_user_by_email(email) if EMAIL_RE.match(email) else None
        if not _csrf_ok():
            message = ('error', _txt('err_csrf'))
        elif user is None or user['verified']:
            # Resposta genérica: não revela se o e-mail existe.
            message = ('error', _txt('err_code'))
        elif not user['verify_code_hash'] or not user['verify_expires'] \
                or datetime.fromisoformat(user['verify_expires']) < store.now_utc():
            message = ('error', _txt('err_code_expired'))
        elif user['verify_attempts'] >= CODE_MAX_ATTEMPTS:
            message = ('error', _txt('err_code_attempts'))
        elif len(code) != 6 or not hmac.compare_digest(
                _code_hash(user['id'], code), user['verify_code_hash']):
            store.add_verify_attempt(user['id'])
            message = ('error', _txt('err_code'))
        else:
            store.mark_verified(user['id'])
            _login_session(store.find_user(user['id']))  # já entra na conta
            session['account_flash'] = ('ok', _txt('ok_verified'))
            return redirect(url_for('accounts.account', lang=_lang()))
    flash = session.pop('account_flash', None)
    return _render('verify', message=message or flash, form={'email': email})


@bp.post('/resend')
def resend():
    if not _csrf_ok():
        session['account_flash'] = ('error', _txt('err_csrf'))
        return redirect(url_for('accounts.login', lang=_lang()))
    email = request.form.get('email', '').strip().lower()[:254]
    user = store.find_user_by_email(email) if EMAIL_RE.match(email or '') else None
    status = 'sent'
    if user is not None and not user['verified'] and not _locked('resend:' + email):
        _register_fail('resend:' + email)  # limita reenvios repetidos
        status = _send_verification(user['id'], user['name'], email)
    # Mesma resposta para e-mail existente ou não (não revela cadastros).
    session['account_flash'] = _mail_message(status, 'ok_resent')
    return redirect(url_for('accounts.verify', lang=_lang(), email=email))


@bp.post('/logout')
def logout():
    if _csrf_ok():
        lang = session.get('lang')
        session.clear()
        if lang:
            session['lang'] = lang
        session['account_flash'] = ('ok', _txt('ok_logout'))
    return redirect(url_for('accounts.login', lang=_lang()))


@bp.get('/account')
@login_required
def account():
    code = _lang()
    uid = g.user['id']
    years = store.available_years(uid)
    current_year = store.now_utc().astimezone(store.BRT).year
    if current_year not in years:
        years = sorted(set(years) | {current_year}, reverse=True)
    try:
        year = int(request.args.get('year', current_year))
    except ValueError:
        year = current_year
    if year not in years:
        year = current_year
    try:
        month = int(request.args.get('month', 0))
    except ValueError:
        month = 0
    if not 0 <= month <= 12:
        month = 0
    data = store.history(uid, year, month or None)
    max_disease = max((n for _, n in data['by_disease']), default=0)
    max_month = max((n for _, n, _ in data['by_month']), default=0)
    return _render(
        'account', year=year, month=month, years=years,
        months=MONTHS[code], months_full=MONTHS_FULL[code], hist=data,
        max_disease=max_disease, max_month=max_month,
        dname=lambda code_: disease_name(code_, _lang()) if code_ else _txt('no_hypothesis'),
        message=session.pop('account_flash', None),
    )


@bp.get('/settings')
@login_required
def settings():
    """Página Configurações: sair, excluir dados e excluir conta."""
    return _render('settings', message=session.pop('account_flash', None))


@bp.post('/account/delete-data')
@login_required
def delete_data():
    """Configurações > Excluir dados: apaga o histórico e mantém a conta."""
    if not _csrf_ok():
        abort(400)
    if not check_password_hash(g.user['password_hash'], request.form.get('password', '')):
        session['account_flash'] = ('error', _txt('err_delete_data'))
    else:
        store.delete_history(g.user['id'])
        session['account_flash'] = ('ok', _txt('ok_data_deleted'))
    return redirect(url_for('accounts.settings', lang=_lang()))


@bp.post('/account/delete')
@login_required
def delete_account():
    if not _csrf_ok():
        abort(400)
    if not check_password_hash(g.user['password_hash'], request.form.get('password', '')):
        session['account_flash'] = ('error', _txt('err_delete'))
        return redirect(url_for('accounts.settings', lang=_lang()))
    store.delete_user(g.user['id'])
    lang = session.get('lang')
    session.clear()
    if lang:
        session['lang'] = lang
    session['account_flash'] = ('ok', _txt('ok_deleted'))
    return redirect(url_for('accounts.login', lang=_lang()))
