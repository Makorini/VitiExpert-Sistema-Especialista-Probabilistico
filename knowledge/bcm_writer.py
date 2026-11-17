"""Gravador de bases do Expert SINTA (.bcm) — formato verificado no Teste.bcm.

O formato foi deduzido comparando Teste.bcm e Attendance.bcm (gerados pelo
próprio ExSINTA). Estrutura, a partir do cabeçalho de 0x713 bytes:

    u16 nº variáveis   + registros de 260 bytes: id u16, nome (string Pascal de 256),
                         u16 multivalorada (0/1)
    u16 nº valores     + registros de 262 bytes: id u16, nome (256), u16 variável dona,
                         u16 ordem do valor na variável
    u16 nº conclusões  + registros de 12 bytes: regra u16, variável u16, valor u16, CNF (REAL48)
    u16 nº premissas   + registros de 12 bytes: regra u16, variável u16, 0x01, u16 '=',
                         valor u16, conector u16 (0 = E, 1 = OU, 2 = fim), 0x00
    u16 nº regras      + registros de 260 bytes: id u16, nome (256), u16 posição
    final: u16 0, u16 nº perguntas + registros de 261 bytes (variável u16, texto (256),
           00 00 01), u16 nº objetivos + (variável u16, mostrar resultados u8),
           11 bytes de opções (copiados do Teste.bcm).

O resultado deve SEMPRE ser aberto e conferido no ExSINTA.
"""

from __future__ import annotations

import math
import struct


def real48(value):
    """Codifica um número no formato REAL48 do Turbo Pascal (6 bytes)."""
    if value == 0:
        return bytes(6)
    if value < 0:
        raise ValueError("CNF negativo")
    exp = math.floor(math.log2(value))
    mantissa = value / (2**exp) - 1.0  # 0 <= m < 1
    frac = round(mantissa * (1 << 39))
    if frac >= (1 << 39):  # arredondou para cima
        frac = 0
        exp += 1
    return bytes([exp + 129]) + frac.to_bytes(5, "little")


def pascal_string(text, size=256):
    raw = text.encode("cp1252")
    if len(raw) > size - 1:
        raise ValueError(f"texto longo demais ({len(raw)} bytes): {text[:40]}")
    return bytes([len(raw)]) + raw + bytes(size - 1 - len(raw))


def u16(n):
    return struct.pack("<H", n)


def build_bcm(
    header, variables, values, heads, tails, rules, questions, objectives, options, trailer_prefix=0
):
    """Monta o arquivo .bcm.

    variables:  [(id, nome, multivalorada)]
    values:     [(id, nome, var_id, ordem)]
    heads:      [(regra, var_id, valor_id, cnf)]
    tails:      [(regra, var_id, valor_id, conector)]   conector: 0=E, 1=OU, 2=fim
    rules:      [(id, nome, posicao)]
    questions:  [(var_id, texto)]
    objectives: [(var_id, mostrar_resultados)]
    """
    if len(header) != 0x713:
        raise ValueError("cabeçalho precisa ter 0x713 bytes")
    out = bytearray(header)
    out += u16(len(variables))
    for vid, name, multi in variables:
        out += u16(vid) + pascal_string(name) + u16(1 if multi else 0)
    out += u16(len(values))
    for vid, name, owner, order in values:
        out += u16(vid) + pascal_string(name) + u16(owner) + u16(order)
    out += u16(len(heads))
    for rid, var, val, cnf in heads:
        out += u16(rid) + u16(var) + u16(val) + real48(cnf)
    out += u16(len(tails))
    for rid, var, val, link in tails:
        out += u16(rid) + u16(var) + b"\x01" + u16(ord("=")) + u16(val) + u16(link) + b"\x00"
    out += u16(len(rules))
    for rid, name, position in rules:
        out += u16(rid) + pascal_string(name) + u16(position)
    out += u16(trailer_prefix) + u16(len(questions))
    for var, text in questions:
        out += u16(var) + pascal_string(text) + b"\x00\x00\x01"
    out += u16(len(objectives))
    for var, show in objectives:
        out += u16(var) + bytes([1 if show else 0])
    if len(options) != 11:
        raise ValueError("bloco de opções deve ter 11 bytes")
    out += options
    return bytes(out)
