"""Banco de dados SQLite das contas e do histórico de consultas.

Isolamento por usuário: TODA consulta ao histórico recebe o user_id da sessão
autenticada e filtra por ele. Nenhuma rota aceita o id de outro usuário, então
uma conta nunca enxerga os dados de outra.

Retenção: no ano vigente cada consulta fica guardada com todos os detalhes.
Quando o ano termina, as consultas daquele ano viram um RESUMO MENSAL
(total do mês e quantas vezes cada doença ficou em 1º lugar) e os detalhes
são apagados, para não acumular dados que não serão mais usados.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import current_app, g

# Horário de Brasília (sem horário de verão desde 2019).
BRT = timezone(timedelta(hours=-3), 'BRT')

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    lang TEXT NOT NULL DEFAULT 'pt',
    created_at TEXT NOT NULL,
    verified_at TEXT,
    verify_code_hash TEXT,
    verify_expires TEXT,
    verify_attempts INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    top_disease TEXT,
    top_confidence REAL,
    answered INTEGER NOT NULL,
    results_json TEXT NOT NULL,
    answers_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_consultations_user_date
    ON consultations(user_id, year, month);
CREATE TABLE IF NOT EXISTS monthly_summaries (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    total INTEGER NOT NULL,
    diseases_json TEXT NOT NULL,
    PRIMARY KEY (user_id, year, month)
);
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(_exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Colunas acrescentadas depois da primeira versão (migração automática).
_NEW_USER_COLUMNS = {
    'verify_code_hash': 'TEXT',
    'verify_expires': 'TEXT',
    'verify_attempts': 'INTEGER NOT NULL DEFAULT 0',
}


def ensure_schema(db):
    db.executescript(SCHEMA)
    existing = {row[1] for row in db.execute('PRAGMA table_info(users)')}
    for column, kind in _NEW_USER_COLUMNS.items():
        if column not in existing:
            db.execute(f'ALTER TABLE users ADD COLUMN {column} {kind}')


def init_db(app):
    with sqlite3.connect(app.config['DATABASE']) as db:
        ensure_schema(db)
        archive_past_years(db)  # resume anos que já terminaram
    app.teardown_appcontext(close_db)


def now_utc():
    return datetime.now(timezone.utc)


# ----------------------------- usuários ---------------------------------

def find_user_by_email(email):
    return get_db().execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()


def find_user(user_id):
    return get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


def create_user(name, email, password_hash, lang):
    db = get_db()
    cur = db.execute(
        'INSERT INTO users (name, email, password_hash, lang, created_at) VALUES (?, ?, ?, ?, ?)',
        (name, email, password_hash, lang, now_utc().isoformat()),
    )
    db.commit()
    return cur.lastrowid


def mark_verified(user_id):
    db = get_db()
    db.execute('UPDATE users SET verified = 1, verified_at = ?, verify_code_hash = NULL,'
               ' verify_expires = NULL, verify_attempts = 0 WHERE id = ?',
               (now_utc().isoformat(), user_id))
    db.commit()


def set_verify_code(user_id, code_hash, expires):
    """Guarda o código de confirmação (só o hash) e zera as tentativas."""
    db = get_db()
    db.execute('UPDATE users SET verify_code_hash = ?, verify_expires = ?, verify_attempts = 0'
               ' WHERE id = ?', (code_hash, expires.isoformat(), user_id))
    db.commit()


def set_password(user_id, password_hash):
    """Troca a senha (hash) e invalida qualquer código pendente."""
    db = get_db()
    db.execute('UPDATE users SET password_hash = ?, verify_code_hash = NULL, verify_expires = NULL,'
               ' verify_attempts = 0 WHERE id = ?', (password_hash, user_id))
    db.commit()


def add_verify_attempt(user_id):
    db = get_db()
    db.execute('UPDATE users SET verify_attempts = verify_attempts + 1 WHERE id = ?', (user_id,))
    db.commit()


def delete_history(user_id):
    """Apaga todas as consultas e resumos do usuário, mantendo a conta."""
    db = get_db()
    cur = db.execute('DELETE FROM consultations WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM monthly_summaries WHERE user_id = ?', (user_id,))
    db.commit()
    return cur.rowcount


def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM consultations WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM monthly_summaries WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()


# ------------------------ retenção: resumo anual -------------------------

NO_HYPOTHESIS = '_sem_hipotese'


def current_year():
    return now_utc().astimezone(BRT).year


def archive_past_years(db=None, user_id=None, year=None):
    """Transforma as consultas de anos anteriores ao vigente em resumo mensal.

    Para cada usuário e mês guarda o total e a contagem por doença (1º lugar);
    depois apaga as consultas detalhadas daqueles anos. Pode ser chamada
    várias vezes: se já houver resumo do mês, os números são somados.
    Retorna quantas consultas foram resumidas.
    """
    db = db or get_db()
    year = year or current_year()
    where, params = 'year < ?', [year]
    if user_id is not None:
        where += ' AND user_id = ?'
        params.append(user_id)
    rows = db.execute(
        f'SELECT user_id, year, month, top_disease, COUNT(*) AS n FROM consultations'
        f' WHERE {where} GROUP BY user_id, year, month, top_disease', params,
    ).fetchall()
    if not rows:
        return 0
    months = {}
    for uid, y, m, disease, n in rows:
        months.setdefault((uid, y, m), {})[disease or NO_HYPOTHESIS] = n
    archived = 0
    for (uid, y, m), counts in months.items():
        old = db.execute('SELECT total, diseases_json FROM monthly_summaries'
                         ' WHERE user_id = ? AND year = ? AND month = ?', (uid, y, m)).fetchone()
        total = sum(counts.values())
        if old:
            merged = json.loads(old[1])
            for disease, n in counts.items():
                merged[disease] = merged.get(disease, 0) + n
            db.execute('UPDATE monthly_summaries SET total = ?, diseases_json = ?'
                       ' WHERE user_id = ? AND year = ? AND month = ?',
                       (old[0] + total, json.dumps(merged), uid, y, m))
        else:
            db.execute('INSERT INTO monthly_summaries (user_id, year, month, total, diseases_json)'
                       ' VALUES (?, ?, ?, ?, ?)', (uid, y, m, total, json.dumps(counts)))
        archived += total
    db.execute(f'DELETE FROM consultations WHERE {where}', params)
    db.commit()
    return archived


# ----------------------------- histórico --------------------------------

def save_consultation(user_id, answers, certainties, report):
    """Grava uma consulta do Sistema Especialista para o usuário dono."""
    local = now_utc().astimezone(BRT)
    results = report.get('results') or []
    top = results[0] if results else None
    compact = [{'id': r['id'], 'confidence_percent': r['confidence_percent']} for r in results]
    answered = {k: v for k, v in answers.items() if v != 'nao_sei'}
    db = get_db()
    db.execute(
        'INSERT INTO consultations (user_id, created_at, year, month, top_disease, top_confidence,'
        ' answered, results_json, answers_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, local.isoformat(timespec='seconds'), local.year, local.month,
         top['id'] if top else None, top['confidence_percent'] if top else None,
         len(answered), json.dumps(compact),
         json.dumps({'answers': answered, 'certainties': certainties or {}})),
    )
    db.commit()


def available_years(user_id):
    rows = get_db().execute(
        'SELECT year FROM consultations WHERE user_id = ?'
        ' UNION SELECT year FROM monthly_summaries WHERE user_id = ? ORDER BY year DESC',
        (user_id, user_id),
    ).fetchall()
    return [r['year'] for r in rows]


def history(user_id, year, month=None):
    """Resumo do período (ano, ou ano + mês) do usuário informado."""
    db = get_db()
    where, params = 'user_id = ? AND year = ?', [user_id, year]
    if month:
        where += ' AND month = ?'
        params.append(month)

    total = db.execute(f'SELECT COUNT(*) FROM consultations WHERE {where}', params).fetchone()[0]
    by_disease = db.execute(
        f'SELECT top_disease AS disease, COUNT(*) AS n FROM consultations WHERE {where}'
        ' AND top_disease IS NOT NULL GROUP BY top_disease ORDER BY n DESC, top_disease',
        params,
    ).fetchall()
    # Meses do ano inteiro (o gráfico mensal ignora o filtro de mês).
    by_month_rows = db.execute(
        'SELECT month, COUNT(*) AS n FROM consultations WHERE user_id = ? AND year = ?'
        ' GROUP BY month', (user_id, year),
    ).fetchall()
    top_by_month = {}
    for row in db.execute(
        'SELECT month, top_disease, COUNT(*) AS n FROM consultations WHERE user_id = ? AND year = ?'
        ' AND top_disease IS NOT NULL GROUP BY month, top_disease ORDER BY month, n DESC, top_disease',
        (user_id, year),
    ):
        top_by_month.setdefault(row['month'], row['top_disease'])
    recent = db.execute(
        f'SELECT * FROM consultations WHERE {where} ORDER BY created_at DESC, id DESC LIMIT 50',
        params,
    ).fetchall()
    last = db.execute(
        f'SELECT created_at FROM consultations WHERE {where} ORDER BY created_at DESC, id DESC LIMIT 1',
        params,
    ).fetchone()
    counts = {r['month']: r['n'] for r in by_month_rows}
    disease_totals = {r['disease']: r['n'] for r in by_disease}
    # Doenças por mês (para a tabela "Histórico por mês").
    month_detail = {}
    for row in db.execute(
        'SELECT month, top_disease, COUNT(*) AS n FROM consultations WHERE user_id = ? AND year = ?'
        ' AND top_disease IS NOT NULL GROUP BY month, top_disease', (user_id, year),
    ):
        month_detail.setdefault(row['month'], {})[row['top_disease']] = row['n']

    # Anos que já terminaram: os números vêm do resumo mensal.
    summaries = db.execute(
        'SELECT month, total, diseases_json FROM monthly_summaries WHERE user_id = ? AND year = ?',
        (user_id, year),
    ).fetchall()
    for row in summaries:
        diseases = json.loads(row['diseases_json'])
        counts[row['month']] = counts.get(row['month'], 0) + row['total']
        detail = month_detail.setdefault(row['month'], {})
        for disease, n in diseases.items():
            if disease == NO_HYPOTHESIS:
                continue
            detail[disease] = detail.get(disease, 0) + n
            if not month or row['month'] == month:
                disease_totals[disease] = disease_totals.get(disease, 0) + n
        if not month or row['month'] == month:
            total += row['total']

    def ranked(mapping):
        return sorted(mapping.items(), key=lambda item: (-item[1], item[0]))

    month_ranked = {m: ranked(d) for m, d in month_detail.items()}
    return {
        'total': total,
        'archived': bool(summaries),
        'by_disease': ranked(disease_totals),
        'by_month': [(m, counts.get(m, 0), (month_ranked.get(m) or [(top_by_month.get(m), 0)])[0][0])
                     for m in range(1, 13)],
        'month_diseases': {m: month_ranked.get(m, [])[:3] for m in range(1, 13)},
        'recent': [{
            'created_at': datetime.fromisoformat(r['created_at']),
            'top_disease': r['top_disease'],
            'top_confidence': r['top_confidence'],
            'answered': r['answered'],
            'results': json.loads(r['results_json']),
        } for r in recent],
        'last': datetime.fromisoformat(last['created_at']) if last else None,
    }
