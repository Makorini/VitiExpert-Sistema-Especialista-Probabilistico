"""Contas: cadastro, verificação de e-mail, login, histórico isolado e exclusão.

Usa um banco SQLite temporário e captura o e-mail em vez de enviá-lo.
"""
import re
import sqlite3
from unittest.mock import patch

import pytest

import account_store
import accounts
from app import app

PASSWORD = 'uvaSegura123'


@pytest.fixture()
def client(tmp_path):
    db = tmp_path / 'teste.db'
    with sqlite3.connect(db) as conn:
        conn.executescript(account_store.SCHEMA)
    old = app.config['DATABASE']
    app.config.update(DATABASE=str(db), TESTING=True)
    accounts._fails.clear()
    with app.test_client() as c:
        yield c
    app.config['DATABASE'] = old


def csrf(client, path='/login'):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def register(client, email='ana@exemplo.com', name='Ana', password=PASSWORD):
    sent = []
    with patch('accounts.send_mail', side_effect=lambda to, s, b, **kw: sent.append((to, s, b)) or 'sent'):
        r = client.post('/register?lang=pt', data={
            'csrf_token': csrf(client, '/register'), 'name': name, 'email': email,
            'password': password, 'password2': password})
    return r, sent


def mail_code(body):
    """Código de 6 dígitos do e-mail de confirmação."""
    return re.search(r'\b(\d{6})\b', body).group(1)


def confirm(client, code, email='ana@exemplo.com'):
    return client.post('/verify?lang=pt', data={
        'csrf_token': csrf(client, '/verify?email=' + email), 'email': email, 'code': code})


def login(client, email='ana@exemplo.com', password=PASSWORD):
    return client.post('/login?lang=pt', data={
        'csrf_token': csrf(client), 'email': email, 'password': password})


def full_signup(client, email='ana@exemplo.com', name='Ana'):
    """Cadastra, digita o código do e-mail e já entra na conta."""
    _, sent = register(client, email, name)
    return confirm(client, mail_code(sent[0][2]), email)


def test_register_sends_6_digit_code_by_email(client):
    r, sent = register(client)
    assert r.status_code == 302 and '/verify' in r.headers['Location']
    assert len(sent) == 1
    to, subject, body = sent[0]
    assert to == 'ana@exemplo.com' and subject == 'Código de confirmação de cadastro — VitiExpert'
    assert re.search(r'\b\d{6}\b', body) and 'http' not in body
    page = client.get(r.headers['Location']).get_data(as_text=True)
    assert 'Enviamos um código de confirmação' in page and 'name="code"' in page


def test_code_is_stored_only_as_hash(client):
    _, sent = register(client)
    code = mail_code(sent[0][2])
    with sqlite3.connect(app.config['DATABASE']) as conn:
        stored = conn.execute('SELECT verify_code_hash FROM users').fetchone()[0]
    assert stored and code not in stored


def test_password_is_hashed_never_plain(client):
    register(client)
    with sqlite3.connect(app.config['DATABASE']) as conn:
        stored = conn.execute('SELECT password_hash FROM users').fetchone()[0]
    assert PASSWORD not in stored and stored.startswith(('scrypt:', 'pbkdf2:'))


def test_unverified_account_cannot_login(client):
    register(client)
    r = login(client)
    assert r.status_code == 302 and '/verify' in r.headers['Location']
    assert 'Confirme seu e-mail' in client.get(r.headers['Location']).get_data(as_text=True)
    assert client.get('/account').status_code == 302


def test_verify_then_login_and_logout(client):
    r = full_signup(client)
    assert r.status_code == 302 and '/account' in r.headers['Location']
    page = client.get('/account?lang=pt').get_data(as_text=True)
    visible = re.sub(r'<[^>]+>', '', page)  # só o texto visível, sem tags
    assert 'Olá, Ana' in visible and 'Minha conta' in visible
    client.post('/logout', data={'csrf_token': csrf(client, '/settings')})
    assert client.get('/account').status_code == 302


def test_wrong_code_rejected_and_attempts_limited(client):
    _, sent = register(client)
    code = mail_code(sent[0][2])
    wrong = '000000' if code != '000000' else '111111'
    for _ in range(5):
        r = confirm(client, wrong)
        assert 'Código incorreto' in r.get_data(as_text=True)
    r = confirm(client, code)  # código certo, mas tentativas esgotadas
    assert 'Muitas tentativas' in r.get_data(as_text=True)
    assert client.get('/account').status_code == 302


def test_expired_code_rejected(client):
    _, sent = register(client)
    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.execute("UPDATE users SET verify_expires = '2000-01-01T00:00:00+00:00'")
    r = confirm(client, mail_code(sent[0][2]))
    assert 'expirou' in r.get_data(as_text=True)


def test_resend_sends_new_code_and_old_one_stops_working(client):
    _, sent = register(client)
    old = mail_code(sent[0][2])
    mails = []
    with patch('accounts.send_mail', side_effect=lambda to, s, b, **kw: mails.append(b) or 'sent'):
        client.post('/resend', data={'csrf_token': csrf(client, '/verify?email=ana@exemplo.com'),
                                     'email': 'ana@exemplo.com'})
    new = mail_code(mails[0])
    if new != old:
        assert 'Código incorreto' in confirm(client, old).get_data(as_text=True)
    r = confirm(client, new)
    assert r.status_code == 302 and '/account' in r.headers['Location']


def test_code_with_spaces_or_dashes_is_accepted(client):
    _, sent = register(client)
    code = mail_code(sent[0][2])
    r = confirm(client, code[:3] + ' - ' + code[3:])
    assert r.status_code == 302 and '/account' in r.headers['Location']


def test_wrong_password_and_lockout(client):
    full_signup(client)
    client.post('/logout', data={'csrf_token': csrf(client, '/settings')})
    for _ in range(5):
        r = login(client, password='errada123')
        assert 'E-mail ou senha incorretos' in r.get_data(as_text=True)
    r = login(client)  # senha certa, mas bloqueado
    assert 'Muitas tentativas' in r.get_data(as_text=True)


@pytest.mark.parametrize('fields,error', [
    ({'name': ''}, 'Informe seu nome'),
    ({'email': 'sem-arroba'}, 'e-mail válido'),
    ({'password': 'curta1', 'password2': 'curta1'}, 'pelo menos 8'),
    ({'password': 'somenteletras', 'password2': 'somenteletras'}, 'pelo menos 8'),
    ({'password2': 'outraSenha123'}, 'não coincidem'),
])
def test_register_validation(client, fields, error):
    data = {'csrf_token': csrf(client, '/register'), 'name': 'Ana', 'email': 'ana@exemplo.com',
            'password': PASSWORD, 'password2': PASSWORD}
    data.update(fields)
    with patch('accounts.send_mail', return_value='sent') as send:
        r = client.post('/register', data=data)
    assert r.status_code == 200 and error in r.get_data(as_text=True)
    send.assert_not_called()


def test_duplicate_email_rejected(client):
    register(client)
    r, sent = register(client)
    assert r.status_code == 200 and 'Já existe uma conta' in r.get_data(as_text=True)
    assert sent == []


def test_forms_require_csrf(client):
    with patch('accounts.send_mail', return_value='sent') as send:
        r = client.post('/register', data={'name': 'Ana', 'email': 'ana@exemplo.com',
                                           'password': PASSWORD, 'password2': PASSWORD})
    assert 'expirou' in r.get_data(as_text=True)
    send.assert_not_called()


def test_resend_does_not_reveal_accounts(client):
    token = csrf(client)
    with patch('accounts.send_mail', return_value='sent') as send:
        r = client.post('/resend', data={'csrf_token': token, 'email': 'ninguem@exemplo.com'})
    send.assert_not_called()
    assert 'Se houver uma conta' in client.get(r.headers['Location']).get_data(as_text=True)


def test_mail_not_configured_message(client):
    with patch('account_mail.mail_settings', return_value={'username': 'x', 'password': '', 'server': 's', 'port': 465, 'script_url': '', 'script_token': ''}):
        client.post('/register', data={'csrf_token': csrf(client, '/register'), 'name': 'Ana',
                                       'email': 'ana@exemplo.com', 'password': PASSWORD, 'password2': PASSWORD})
    assert 'MAIL_SCRIPT_URL' in client.get('/verify?email=ana@exemplo.com').get_data(as_text=True)


def test_diagnosis_saved_only_when_logged_in(client):
    answers = {'answers': {'poeira_branca': 'sim'}}
    assert client.post('/api/diagnose', json=answers).get_json()['saved'] is False
    full_signup(client)
    r = client.post('/api/diagnose', json={**answers, 'certainties': {'poeira_branca': 80}})
    assert r.get_json()['saved'] is True
    page = client.get('/account?lang=pt').get_data(as_text=True)
    assert 'Oídio' in page and 'Consultas no período' in page


def test_users_never_see_each_other_history(client):
    full_signup(client, 'ana@exemplo.com', 'Ana')
    client.post('/api/diagnose', json={'answers': {'poeira_branca': 'sim'}})
    client.post('/logout', data={'csrf_token': csrf(client, '/settings')})
    full_signup(client, 'bia@exemplo.com', 'Bia')
    client.post('/api/diagnose', json={'answers': {'odor_acetico': 'sim', 'moscas_vinagre': 'sim'}})
    page = client.get('/account?lang=pt').get_data(as_text=True)
    assert 'Podridão-ácida' in page and 'Oídio' not in page
    with sqlite3.connect(app.config['DATABASE']) as conn:
        rows = conn.execute('SELECT u.email, c.top_disease FROM consultations c JOIN users u ON u.id = c.user_id ORDER BY c.id').fetchall()
    assert rows == [('ana@exemplo.com', 'oidio'), ('bia@exemplo.com', 'podridao_acida')]


def test_history_by_month_and_year(client):
    full_signup(client)
    for _ in range(2):
        client.post('/api/diagnose', json={'answers': {'poeira_branca': 'sim'}})
    client.post('/api/diagnose', json={'answers': {'manchas_oleosas': 'sim', 'mofo_branco_inferior': 'sim'}})
    uid = 1
    with app.app_context():
        year = account_store.now_utc().astimezone(account_store.BRT).year
        month = account_store.now_utc().astimezone(account_store.BRT).month
        data = account_store.history(uid, year)
        assert data['total'] == 3
        assert data['by_disease'][0] == ('oidio', 2)
        assert data['by_month'][month - 1] == (month, 3, 'oidio')
        other = month % 12 + 1
        assert account_store.history(uid, year, other)['total'] == 0
    page = client.get(f'/account?year={year}&month={month}').get_data(as_text=True)
    assert 'acc-hbar' in page and 'acc-col' in page


def test_account_filters_reject_garbage(client):
    full_signup(client)
    for q in ('year=abc&month=99', 'year=1900', 'month=-3'):
        assert client.get('/account?' + q).status_code == 200


def test_delete_account_removes_all_data(client):
    full_signup(client)
    client.post('/api/diagnose', json={'answers': {'poeira_branca': 'sim'}})
    token = csrf(client, '/settings')
    r = client.post('/account/delete', data={'csrf_token': token, 'password': 'errada123'})
    assert client.get(r.headers['Location']).status_code == 200
    with sqlite3.connect(app.config['DATABASE']) as conn:
        assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 1
    client.post('/account/delete', data={'csrf_token': token, 'password': PASSWORD})
    with sqlite3.connect(app.config['DATABASE']) as conn:
        assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0
        assert conn.execute('SELECT COUNT(*) FROM consultations').fetchone()[0] == 0
    assert login(client).status_code == 200


def test_login_next_only_allows_local_paths(client):
    _, sent = register(client)
    confirm(client, mail_code(sent[0][2]))
    client.post('/logout', data={'csrf_token': csrf(client, '/settings')})
    r = client.post('/login?next=https://malicioso.com', data={
        'csrf_token': csrf(client), 'email': 'ana@exemplo.com', 'password': PASSWORD})
    assert r.headers['Location'].startswith('/account')


@pytest.mark.parametrize('lang,word', [('pt', 'Entrar'), ('en', 'Sign in'), ('es', 'Ingresar')])
def test_header_shows_login_button_in_each_language(client, lang, word):
    assert word in client.get(f'/?lang={lang}').get_data(as_text=True)


def test_settings_page_is_separate_and_private(client):
    assert client.get('/settings').status_code == 302  # exige login
    full_signup(client)
    account = client.get('/account?lang=pt').get_data(as_text=True)
    settings = client.get('/settings?lang=pt').get_data(as_text=True)
    # Menu "Minha conta" do cabeçalho: Minha conta, Configurações e Sair (com confirmação).
    for page in (account, settings):
        assert 'id="account-menu"' in page and 'href="/settings?lang=pt"' in page
        assert 'action="/logout?lang=pt" data-confirm="Deseja mesmo sair da sua conta?"' in page
    # Exclusões ficam só em Configurações, também com confirmação.
    assert '/account/delete' not in account
    for action in ('/account/delete-data', '/account/delete'):
        assert f'action="{action}?lang=pt" class="acc-delete" data-confirm=' in settings
    assert 'Excluir dados' in settings and 'Excluir conta' in settings
    assert 'id="viti-confirm"' in settings


def test_delete_data_keeps_account(client):
    full_signup(client)
    client.post('/api/diagnose', json={'answers': {'poeira_branca': 'sim'}})
    token = csrf(client, '/settings')
    r = client.post('/account/delete-data', data={'csrf_token': token, 'password': 'errada123'})
    assert 'Os dados não foram excluídos' in client.get(r.headers['Location']).get_data(as_text=True)
    with sqlite3.connect(app.config['DATABASE']) as conn:
        assert conn.execute('SELECT COUNT(*) FROM consultations').fetchone()[0] == 1
    r = client.post('/account/delete-data', data={'csrf_token': token, 'password': PASSWORD})
    assert r.headers['Location'].startswith('/settings')
    with sqlite3.connect(app.config['DATABASE']) as conn:
        assert conn.execute('SELECT COUNT(*) FROM consultations').fetchone()[0] == 0
        assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 1
    assert client.get('/account').status_code == 200  # continua logado


def test_verification_email_is_html_like_model(client):
    """Monta a mensagem real (sem enviar): remetente, assunto, texto e HTML."""
    sent = {}

    class FakeSMTP:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): return None
        def login(self, user, password): sent['login'] = user
        def send_message(self, msg): sent['msg'] = msg

    cfg = {'username': 'makorini.dev@gmail.com', 'password': 'x' * 16, 'server': 's',
           'port': 465, 'from_name': 'VitiExpert', 'script_url': '', 'script_token': ''}
    with patch('account_mail.mail_settings', return_value=cfg), \
         patch('account_mail.smtplib.SMTP_SSL', FakeSMTP):
        client.post('/register?lang=pt', data={
            'csrf_token': csrf(client, '/register'), 'name': 'Ana', 'email': 'ana@exemplo.com',
            'password': PASSWORD, 'password2': PASSWORD})
    msg = sent['msg']
    assert sent['login'] == 'makorini.dev@gmail.com'
    assert msg['From'] == 'VitiExpert <makorini.dev@gmail.com>'
    assert msg['Subject'] == 'Código de confirmação de cadastro — VitiExpert'
    text = msg.get_body(('plain',)).get_content()
    html = msg.get_body(('html',)).get_content()
    code = mail_code(text)
    assert 'Seu código de confirmação de cadastro é:' in text and 'expira em 15 minutos' in text
    assert code in html and 'letter-spacing' in html and 'ignore este e-mail' in html


def test_code_sent_through_apps_script_like_salon_project(client):
    """Com MAIL_SCRIPT_URL, o VitiExpert pede ao Apps Script (MailApp) que envie."""
    import io, json as _json
    calls = []

    class Resp(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return None

    def fake_urlopen(req, timeout=0):
        calls.append((req.full_url, _json.loads(req.data.decode())))
        return Resp(b'{"ok": true}')

    cfg = {'username': 'makorini.dev@gmail.com', 'password': '', 'server': 's', 'port': 465,
           'from_name': 'VitiExpert', 'script_token': 'segredo-teste',
           'script_url': 'https://script.google.com/macros/s/ABC123/exec'}
    with patch('account_mail.mail_settings', return_value=cfg),          patch('account_mail.urlopen', side_effect=fake_urlopen):
        r = client.post('/register?lang=pt', data={
            'csrf_token': csrf(client, '/register'), 'name': 'Ana', 'email': 'ana@exemplo.com',
            'password': PASSWORD, 'password2': PASSWORD})
    page = client.get(r.headers['Location']).get_data(as_text=True)
    assert 'Enviamos um código de confirmação' in page
    url, data = calls[0]
    assert url.endswith('/exec') and data['token'] == 'segredo-teste' and data['para'] == 'ana@exemplo.com'
    assert data['assunto'] == 'Código de confirmação de cadastro — VitiExpert'
    assert mail_code(data['texto']) in data['html']


def test_apps_script_rejects_non_google_url():
    import account_mail
    cfg = {'script_url': 'https://site-qualquer.com/exec', 'script_token': 't', 'from_name': 'V'}
    assert account_mail._send_via_apps_script(cfg, 'a@b.com', 's', 'b', '') == 'failed'
