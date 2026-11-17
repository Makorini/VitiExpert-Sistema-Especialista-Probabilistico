"""Gera knowledge/VitiExpert10.bcm (base do Expert SINTA com as 10 doenças).

Lê as tabelas de docs/BASE_SINTA_10_DOENCAS.md (variáveis, perguntas e as 17
regras) e grava o arquivo no formato do ExSINTA usando bcm_writer.py. O
cabeçalho (título "VitiExpert") e o bloco de opções são copiados do Teste.bcm.

Uso (na pasta VitiExpert):  python knowledge/gerar_vitiexpert10_bcm.py

IMPORTANTE: abra o arquivo gerado no ExSINTA e confira as regras antes de usar.
"""

from __future__ import annotations

import re
from pathlib import Path

from bcm_writer import build_bcm

ROOT = Path(__file__).resolve().parent.parent
ROTEIRO = ROOT / "docs" / "BASE_SINTA_10_DOENCAS.md"
MODELO = ROOT / "knowledge" / "Teste.bcm"
SAIDA = ROOT / "knowledge" / "VitiExpert10.bcm"

DOENCAS = [
    "mildio",
    "oidio",
    "antracnose",
    "podridao_cinzenta",
    "podridao_madura",
    "podridao_acida",
    "escoriose",
    "ferrugem",
    "mancha_folhas",
    "podridao_amarga",
]


def ler_roteiro():
    texto = ROTEIRO.read_text(encoding="utf-8")
    variaveis = []  # (nome, pergunta)
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*([a-z_]+)\s*\|\s*(.+?)\s*\|\s*$", texto, re.M):
        variaveis.append((m.group(2), m.group(3)))
    regras = []  # (numero, [(var, valor)], doenca, cnf)
    for m in re.finditer(
        r"^\|\s*R(\d+)\s*\|\s*(.+?)\s*\|\s*([a-z_]+)\s*\|\s*(\d+)\s*\|\s*$", texto, re.M
    ):
        condicoes = []
        for parte in re.split(r"\*\*E\*\*", m.group(2)):
            var, valor = [x.strip() for x in parte.split("=")]
            condicoes.append((var, "sim" if valor.lower() == "sim" else "não"))
        regras.append((int(m.group(1)), condicoes, m.group(3), int(m.group(4)) / 100))
    if len(variaveis) != 31 or len(regras) != 17:
        raise SystemExit(f"Roteiro inesperado: {len(variaveis)} variáveis, {len(regras)} regras")
    return variaveis, regras


def gerar():
    variaveis, regras = ler_roteiro()
    modelo = MODELO.read_bytes()
    cabecalho = modelo[:0x713]
    opcoes = modelo[-11:]

    # Variáveis: 1..31 sintomas (univaloradas) + diagnóstico (multivalorada).
    var_id = {nome: i for i, (nome, _) in enumerate(variaveis, start=1)}
    diag = len(variaveis) + 1
    vars_bcm = [(var_id[n], n, False) for n, _ in variaveis] + [(diag, "diagnostico", True)]

    # Valores: sim / não para cada sintoma; as 10 doenças para o diagnóstico.
    valores, val_id, prox = [], {}, 1
    for nome, _ in variaveis:
        for ordem, v in enumerate(("sim", "não"), start=1):
            valores.append((prox, v, var_id[nome], ordem))
            val_id[(nome, v)] = prox
            prox += 1
    for ordem, d in enumerate(DOENCAS, start=1):
        valores.append((prox, d, diag, ordem))
        val_id[("diagnostico", d)] = prox
        prox += 1

    heads, tails, rules = [], [], []
    for num, condicoes, doenca, cnf in regras:
        if doenca not in DOENCAS:
            raise SystemExit(f"R{num:02d}: doença desconhecida {doenca}")
        for i, (var, valor) in enumerate(condicoes):
            conector = 2 if i == len(condicoes) - 1 else 0  # E ... fim
            tails.append((num, var_id[var], val_id[(var, valor)], conector))
        heads.append((num, diag, val_id[("diagnostico", doenca)], cnf))
        rules.append((num, f"Regra {num}", num))

    perguntas = [(var_id[n], p) for n, p in variaveis]
    dados = build_bcm(
        cabecalho, vars_bcm, valores, heads, tails, rules, perguntas, [(diag, True)], opcoes
    )
    SAIDA.write_bytes(dados)
    print(
        f"Gerado {SAIDA.name}: {len(vars_bcm)} variáveis, {len(valores)} valores, "
        f"{len(rules)} regras, {len(tails)} premissas, {len(perguntas)} perguntas, {len(dados)} bytes"
    )


if __name__ == "__main__":
    gerar()
