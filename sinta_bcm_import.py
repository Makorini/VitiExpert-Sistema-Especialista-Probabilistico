"""Importador verificável da base Expert SINTA Teste.bcm.

O arquivo .BCM usa registros Pascal (strings com comprimento, registros de
variáveis/valores de tamanho fixo) e REAL48 para os CNFs. Este parser valida
o formato efetivamente encontrado na base Teste.bcm fornecida pela autora;
não se apresenta como conversor universal de todas as versões do Expert SINTA.

Uso: python sinta_bcm_import.py
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'knowledge' / 'Teste.bcm'
TARGET = ROOT / 'knowledge' / 'sinta_teste_export.json'


def u16(data, start):
    return struct.unpack_from('<H', data, start)[0]


def real48(data):
    """Decodifica REAL48 do Pascal: expoente com viés 129 e mantissa 39 bits."""
    if len(data) != 6:
        raise ValueError('REAL48 requer 6 bytes')
    if data[0] == 0:
        return 0.0
    fraction = int.from_bytes(data[1:], 'little') & ((1 << 39) - 1)
    sign = -1 if data[5] & 0x80 else 1
    return sign * (1 + fraction / (1 << 39)) * (2 ** (data[0] - 129))


def read_fixed_name(data, pos, length):
    number = u16(data, pos)
    size = data[pos + 2]
    if not 0 < size < 180:
        raise ValueError(f'Comprimento de string inválido em {pos:#x}')
    name = data[pos + 3:pos + 3 + size].decode('cp1252')
    if not name.strip():
        raise ValueError('Nome vazio')
    return number, name


def decode(source=SOURCE):
    data = Path(source).read_bytes()
    if data[:10] != bytes.fromhex('2d 0c bd 16 63 28 f3 97 ca 22'):
        raise ValueError('Assinatura da base BCM não reconhecida')
    # Deslocamento observado e verificado em Teste.bcm, sem inferir nomes
    # a partir de memória residual em strings de tamanho fixo.
    pos = 0x713
    nvars = u16(data, pos); pos += 2
    if not 1 <= nvars <= 250:
        raise ValueError('Quantidade de variáveis inválida')
    variables = {}
    for index in range(nvars):
        id_, name = read_fixed_name(data, pos, 260)
        if id_ in variables:
            raise ValueError('Código duplicado de variável')
        variables[id_] = name
        pos += 260

    nvals = u16(data, pos); pos += 2
    if not 1 <= nvals <= 1000:
        raise ValueError('Quantidade de valores inválida')
    values = {}
    for index in range(nvals):
        id_, name = read_fixed_name(data, pos, 262)
        if id_ in values:
            raise ValueError('Código de valor repetido')
        values[id_] = name
        pos += 262

    nheads = u16(data, pos); pos += 2
    if not 1 <= nheads <= 500:
        raise ValueError('Quantidade de conclusões inválida')
    heads = defaultdict(list)
    for _ in range(nheads):
        rid, vid, valueid = struct.unpack_from('<HHH', data, pos)
        cf = round(real48(data[pos + 6:pos + 12]), 6)
        if vid not in variables or valueid not in values or not (0 <= cf <= 1):
            raise ValueError('Conclusão inválida')
        heads[rid].append({
            'variavel':variables[vid], 'valor': values[valueid], 'cnf':cf
        })
        pos += 12

    ntails = u16(data, pos); pos += 2
    if not 1 <= ntails <= 1000:
        raise ValueError('Quantidade de condições inválida')
    tails = defaultdict(list)
    for _ in range(ntails):
        rid, vid = struct.unpack_from('<HH', data, pos)
        op_tag = data[pos + 4]
        operator = chr(u16(data, pos + 5))
        valueid, link = struct.unpack_from('<HH', data, pos + 7)
        pad = data[pos + 11]
        if vid not in variables or valueid not in values or op_tag != 1 or operator != '=' or link not in (0, 2) or pad != 0:
            raise ValueError(f'Premissa inválida na posição {pos:#x}')
        tails[rid].append({'variavel':variables[vid], 'operador':operator, 'valor':values[valueid], 'fim':link==2})
        pos += 12

    nrules = u16(data, pos); pos += 2
    if not 1 <= nrules <= 200:
        raise ValueError('Quantidade de regras inválida')
    rules=[]
    for _ in range(nrules):
        rid, name = read_fixed_name(data, pos, 260)
        if rid not in heads or rid not in tails:
            raise ValueError('Regra sem antecedente ou conclusão')
        if len({(c['variavel'],c['valor']) for c in heads[rid]}) != 1:
            raise ValueError('Conclusões diferentes no mesmo bloco — requer revisão')
        if tails[rid][-1]['fim'] is not True or any(x['fim'] for x in tails[rid][:-1]):
            raise ValueError('Marcadores de fim de condições inconsistentes')
        rules.append({'id':f'SINTA-R{rid:02d}', 'numero_original':rid, 'nome_original':name,
                      'se_todas':tails[rid], 'entao':heads[rid]})
        pos += 260

    if set(heads) != {x['numero_original'] for x in rules} or set(tails) != set(heads):
        raise ValueError('Referências órfãs')
    # Campos remanescentes do .BCM representam outras configurações/marcadores,
    # não são presumidos como parte do conteúdo das regras.
    diagnostics = sorted({c['valor'] for r in rules for c in r['entao']})
    return {
        'formato':'Expert SINTA BCM / extração específica verificada',
        'arquivo_origem':Path(source).name,
        'sha256':sha256(data).hexdigest(),
        'quantidades':{'variaveis':len(variables),'valores':len(values),'regras':len(rules),
                       'premissas':ntails,'conclusoes':nheads,'hipoteses':len(diagnostics)},
        'variaveis':list(variables.values()),
        'valores':list(values.values()),
        'hipoteses':diagnostics,
        'regras':sorted(rules,key=lambda x:x['numero_original']),
        'observacao':('Cada regra possui duas conclusões para o mesmo diagnóstico com CNFs distintos, '
                      'como gravado no Teste.bcm. O motor calcula e combina ambas usando a fórmula '
                      'de atualização de fator de certeza descrita no manual do SINTA. '
                      'Isso é confiança possibilista, não probabilidade estatística.'),
    }


def export(source=SOURCE, target=TARGET):
    contents = decode(source)
    Path(target).write_text(json.dumps(contents,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return contents

if __name__ == '__main__':
    kb = export()
    print('Extraídos:', kb['quantidades'])
    for rule in kb['regras']:
        clauses = ' E '.join(c['variavel']+'='+c['valor'] for c in rule['se_todas'])
        print(rule['id'],clauses,'=>',rule['entao'])
