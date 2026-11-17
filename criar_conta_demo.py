"""Cria (ou recria) a conta de DEMONSTRAÇÃO do VitiExpert, com histórico de exemplo.

Uso, na pasta VitiExpert:
    python criar_conta_demo.py

Depois entre no site com:
    E-mail: demo@vitiexpert.local
    Senha:  Demo2026uva

A conta recebe consultas fictícias do ano passado (que o sistema resume por
mês, como faz na virada do ano) e do ano atual (que aparecem completas), para
mostrar os gráficos e o resumo anual na apresentação. Os dados são de exemplo:
não representam casos reais. Para apagar, use Configurações > Excluir conta.
"""

from __future__ import annotations

import json
import sqlite3

from werkzeug.security import generate_password_hash

import account_store as store
from app import app

EMAIL = "demo@vitiexpert.local"
SENHA = "Demo2026uva"
NOME = "Demonstração"

# (mês, doença em 1º lugar, quantas consultas, confiança %)
ANO_PASSADO = [
    (1, "mildio", 6, 90.0),
    (1, "oidio", 3, 80.0),
    (2, "mildio", 4, 90.0),
    (3, "podridao_cinzenta", 5, 85.0),
    (3, "oidio", 2, 80.0),
    (5, "antracnose", 3, 85.0),
    (8, "ferrugem", 2, 85.0),
    (10, "mildio", 7, 97.0),
    (11, "oidio", 4, 80.0),
    (12, "podridao_acida", 3, 90.0),
]
ANO_ATUAL = [
    (1, "mildio", 3, 90.0),
    (2, "oidio", 2, 80.0),
    (3, "podridao_cinzenta", 2, 85.0),
    (4, "antracnose", 1, 85.0),
    (6, "escoriose", 1, 80.0),
    (9, "mildio", 2, 70.0),
    (10, "mancha_folhas", 1, 85.0),
    (11, "podridao_amarga", 2, 85.0),
]


def criar():
    ano = store.current_year()
    db = sqlite3.connect(app.config["DATABASE"])
    db.execute("PRAGMA foreign_keys = ON")
    with app.app_context():
        store.ensure_schema(db)
    antigo = db.execute("SELECT id FROM users WHERE email = ?", (EMAIL,)).fetchone()
    if antigo:
        for tabela in ("consultations", "monthly_summaries"):
            db.execute(f"DELETE FROM {tabela} WHERE user_id = ?", antigo)
        db.execute("DELETE FROM users WHERE id = ?", antigo)
    agora = store.now_utc().isoformat()
    uid = db.execute(
        "INSERT INTO users (name, email, password_hash, verified, lang, created_at, verified_at)"
        " VALUES (?, ?, ?, 1, ?, ?, ?)",
        (NOME, EMAIL, generate_password_hash(SENHA), "pt", agora, agora),
    ).lastrowid

    def inserir(year, dados):
        for mes, doenca, vezes, conf in dados:
            for dia in range(vezes):
                resultados = [{"id": doenca, "confidence_percent": conf}]
                db.execute(
                    "INSERT INTO consultations (user_id, created_at, year, month, top_disease,"
                    " top_confidence, answered, results_json, answers_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        uid,
                        f"{year}-{mes:02d}-{dia + 5:02d}T10:00:00-03:00",
                        year,
                        mes,
                        doenca,
                        conf,
                        2,
                        json.dumps(resultados),
                        json.dumps({"answers": {}, "certainties": {}}),
                    ),
                )

    inserir(ano - 1, ANO_PASSADO)
    inserir(ano, ANO_ATUAL)
    db.commit()
    resumidas = store.archive_past_years(db)  # ano passado vira resumo mensal
    db.close()
    print(f"Conta de demonstração criada: {EMAIL} / senha {SENHA}")
    print(
        f"  {ano - 1}: {resumidas} consultas resumidas por mês | {ano}: "
        f"{sum(v for _, _, v, _ in ANO_ATUAL)} consultas completas"
    )


if __name__ == "__main__":
    criar()
