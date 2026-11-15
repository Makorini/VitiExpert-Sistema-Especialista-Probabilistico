# Registro de verificações — VitiExpert

**Data:** 15/11/2026
**Escopo:** base do Expert SINTA com 10 doenças (`knowledge/VitiExpert10.bcm`: 31 sintomas, 17 regras), motor Python, interface em PT/EN/ES, contas de usuário e histórico.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| Suíte completa (`python -m pytest -q`) | **120 testes aprovados** |
| Base SINTA: integridade, regras do roteiro e cada regra disparando sozinha com o seu CNF (`tests/test_base_sinta.py`) | 45 testes aprovados |
| Consultas de referência do roteiro (T01–T11, `knowledge/cenarios_base_sinta.csv`) | 11 de 11 com a doença e o CNF esperados |
| Cálculo do manual do SINTA: E = produto, OU = c1 + c2 − c1·c2, conclusão = premissa × CNF, acúmulo x + y − xy, mínimo de 50% | Aprovado (exemplos do próprio manual: 56% e 94%) |
| Contas: cadastro com código por e-mail, login, esqueci minha senha, isolamento entre usuários, retenção anual, exclusão de dados e da conta (`tests/test_accounts.py`) | 45 testes aprovados |
| API, páginas, página 404, traduções, notícias e recursos visuais | 30 testes aprovados |
| Gravador do formato `.bcm` (`knowledge/bcm_writer.py`) | Regravando o `Teste.bcm` original, o resultado é idêntico (variáveis, valores, CNFs byte a byte, regras e opções) |
| Integridade da base | `VitiExpert10.bcm`, SHA-256 `a5f535008cdeeba5ce7822dd574fff0d8a1c1f491c1fc0be1a38d70bcda72623`, igual ao registrado em `sinta_base_export.json` |
| Execução em computador "limpo" (`iniciar_vitiexpert.bat`) | Ambiente criado, bibliotecas instaladas e site no ar |

## Como reproduzir

Com Python 3.11 ou superior, na pasta `VitiExpert`:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

## Pendência de verificação no programa SINTA

O arquivo `VitiExpert10.bcm` foi gerado por `knowledge/gerar_vitiexpert10_bcm.py` a partir do roteiro `docs/BASE_SINTA_10_DOENCAS.md`. Ainda deve ser **aberto no ExSINTA** para confirmar que o programa o aceita e repetir nele as consultas T01–T14, conferindo se o SINTA mostra os mesmos percentuais do Python.

## Limite da avaliação

Os testes verificam o software, não a acurácia agronômica. Os cenários são sintéticos e os CNFs das regras são heurísticos (escolhidos a partir das descrições da Embrapa). Para avaliar o desempenho em plantas reais são necessários casos independentes com diagnóstico de referência e a revisão das regras por especialista (ver `docs/METODOLOGIA_E_VALIDACAO.md`).
