"""Motor de Fatores de Certeza do VitiExpert, transposto do Expert SINTA para Python.

A base de conhecimento é o arquivo do SINTA knowledge/VitiExpert10.bcm
(10 doenças, 28 sintomas, 16 regras), exportado para
knowledge/sinta_base_export.json por sinta_bcm_import.py. Todas as regras
vêm desse arquivo; cada conclusão mantém o CNF gravado no SINTA.

Este cálculo reproduz as funções padrão do manual do Expert SINTA
(seção 1.4 "Fatores de confiança" e seção 2.8 "Opções"):
- c1 = confiança do usuário na resposta (0% a 100%; padrão 100%);
- conectivo E  = produto: c1 * c2              (manual, caso 2);
- conectivo OU = c1 + c2 - c1 * c2             (manual, caso 3);
- conclusão    = CNF da premissa * CNF da regra (manual, caso 1);
- mesma hipótese obtida por várias regras = x + y - x*y (manual, caso 4);
- a regra só é aceita se a confiança da premissa atingir o valor
  mínimo do SINTA, 50% por padrão (CONFIANCA_MINIMA).
"Não sei" deixa o fato desconhecido, então a regra não dispara.
"""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import json
from sinta_i18n import label, disease_name, question_groups, UI

SOURCE = Path(__file__).resolve().parent / "knowledge" / "sinta_base_export.json"
BCM_FILE = "VitiExpert10.bcm"
ALLOWED = {"sim", "nao", "nao_sei"}
# Valor mínimo de confiança para uma regra ser aceita (padrão do Expert SINTA,
# configurável no SINTA em Exibir > Opções > Fatores de confiança).
CONFIANCA_MINIMA = 0.5


@lru_cache(maxsize=1)
def knowledge():
    with SOURCE.open(encoding="utf-8") as fp:
        kb = json.load(fp)
    if kb["arquivo_origem"] != BCM_FILE or len(kb["hipoteses"]) != 10:
        raise ValueError("A base JSON não corresponde ao VitiExpert10.bcm (10 doenças)")
    original = SOURCE.parent / BCM_FILE
    if original.exists() and sha256(original.read_bytes()).hexdigest() != kb["sha256"]:
        raise ValueError(
            f"{BCM_FILE} foi modificado: execute python sinta_bcm_import.py para sincronizar a base"
        )
    return kb


def sanitize_answers(raw):
    if not isinstance(raw, dict):
        raise ValueError("O campo 'answers' deve ser um objeto com respostas")
    valid = set(knowledge()["variaveis"]) - {"diagnostico"}
    if len(raw) > len(valid) or any(
        key not in valid or type(value) is not str or value not in ALLOWED
        for key, value in raw.items()
    ):
        raise ValueError("Pergunta ou resposta inválida")
    return {key: raw.get(key, "nao_sei") for key in valid}


def sanitize_certainties(raw, answers):
    """Confiança do usuário (c1) por pergunta, em 0..100 -> 0..1.

    Ausente = 100% (compatível com respostas só Sim/Não). Só vale para
    perguntas respondidas com Sim ou Não.
    """
    result = {key: 1.0 for key, value in answers.items() if value != "nao_sei"}
    if raw is None:
        return result
    if not isinstance(raw, dict):
        raise ValueError("O campo 'certainties' deve ser um objeto")
    for key, value in raw.items():
        if key not in answers or type(value) not in (int, float) or not (0 <= value <= 100):
            raise ValueError("Grau de certeza inválido (use 0 a 100)")
        if key in result:
            result[key] = value / 100
    return result


def premise_and(values):
    """Conectivo E do SINTA (padrão do manual): produto das confianças."""
    result = 1.0
    for value in values:
        result *= value
    return result


def premise_or(values):
    """Conectivo OU do SINTA (padrão do manual): c1 + c2 - c1*c2."""
    result = 0.0
    for value in values:
        result = result + value - result * value
    return result


def rule_accepted(premise):
    """A regra é aceita quando a premissa atinge a confiança mínima."""
    return premise >= CONFIANCA_MINIMA - 1e-9


def combine_certainties(a, b):
    if not (0 <= a <= 1 and 0 <= b <= 1):
        raise ValueError("Fatores de certeza fora de [0, 1]")
    return a + b - a * b


def infer(raw, locale="pt", certainties=None):
    if locale not in UI:
        locale = "pt"
    answers = sanitize_answers(raw)
    trust = sanitize_certainties(certainties, answers)
    kb = knowledge()
    hits = {}
    partial = []
    rejected = []  # regras completas recusadas por ficarem abaixo da confiança mínima
    for rule in kb["regras"]:
        clauses = rule["se_todas"]
        yes = []
        no = []
        unknown = []
        for clause in clauses:
            key = clause["variavel"]
            answer = answers[key]
            required = (
                "sim" if clause["valor"] == "sim" else "nao" if clause["valor"] == "não" else None
            )
            if required is None:
                raise ValueError("Valor SINTA fora da lista binária esperada")
            if answer == "nao_sei":
                unknown.append(key)
            elif answer == required:
                yes.append(key)
            else:
                no.append(key)
        premise = (
            premise_and([trust[key] for key in yes]) if yes and not no and not unknown else 0.0
        )
        if not no and not unknown and rule_accepted(premise):
            # CNF da premissa (E = produto) multiplicado pelo CNF de cada conclusão
            hypothesis = rule["entao"][0]["valor"]
            entry = hits.setdefault(
                hypothesis, {"id": hypothesis, "confidence": 0.0, "evidence": [], "fired_rules": []}
            )
            rule_result = 0.0
            raw_factors = []
            for conclusion in rule["entao"]:
                if conclusion["valor"] != hypothesis:
                    raise ValueError("Conclusões distintas exigem análise")
                factor = conclusion["cnf"]
                raw_factors.append(round(factor * 100, 1))
                rule_result = combine_certainties(rule_result, premise * factor)
            entry["confidence"] = combine_certainties(entry["confidence"], rule_result)
            for key in yes:
                if key not in entry["evidence"]:
                    entry["evidence"].append(key)
            entry["fired_rules"].append(
                {
                    "id": rule["id"],
                    "conditions": [
                        {
                            "id": cl["variavel"],
                            "description": label(cl["variavel"], locale),
                            "value": cl["valor"],
                        }
                        for cl in clauses
                    ],
                    "conclusion_factors_percent": raw_factors,
                    "premise_percent": round(premise * 100, 1),
                    "confidence_percent": round(rule_result * 100, 1),
                }
            )
        elif not no and not unknown and yes:
            rejected.append({"id": rule["id"], "premise_percent": round(premise * 100, 1)})
        elif not no and yes and unknown:
            partial.append({"id": rule["id"], "missing": unknown, "matched": len(yes)})

    # Regras que concluem a mesma hipótese já foram acumuladas (x + y - x*y).
    for item in hits.values():
        item["name"] = disease_name(item["id"], locale)
        item["evidence"] = [label(k, locale) for k in item["evidence"]]
        item["confidence_percent"] = round(item["confidence"] * 100, 1)
        item["certainty_factor"] = round(item["confidence"], 6)
        del item["confidence"]
    results = sorted(hits.values(), key=lambda item: (-item["confidence_percent"], item["id"]))
    todo = []
    for item in sorted(partial, key=lambda x: (-x["matched"], len(x["missing"]))):
        for key in item["missing"]:
            if key not in todo:
                todo.append(key)
    suggestions = [{"id": code, "text": label(code, locale)} for code in todo[:4]]
    report = {
        "results": results[:3],
        "matched_hypotheses": len(results),
        "analyzed_hypotheses": len(kb["hipoteses"]),
        "diseases_assessed": len(kb["hipoteses"]),
        "rule_count": len(kb["regras"]),
        "fired_rule_count": sum(len(item["fired_rules"]) for item in results),
        "suggested_questions": suggestions,
        "engine": "sinta_cf_python",
        "source_file": kb["arquivo_origem"],
        "source_sha256": kb["sha256"],
        "method": "SINTA CF (manual defaults): AND=product, conclusion=premise*CNF, same hypothesis x+y-x*y, minimum premise 50%",
        "rejected_rules": rejected,
        "minimum_confidence_percent": round(CONFIANCA_MINIMA * 100, 1),
        "message": None if results else UI[locale]["below_minimum" if rejected else "no_results"],
        "disclaimer": UI[locale]["warning"],
    }
    return report
