# Registro de verificações — VitiExpert

**Data:** 08/11/2026  
**Escopo:** projeto entregue neste pacote, com 10 doenças, duas condições diferenciais, 34 perguntas e regras originais do Expert SINTA e regras complementares.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| Testes Python independentes do Flask (`test_extended_inference.py`, `test_sinta_integration.py`, `test_expert_question_labels.py`, `test_project_assets.py`) | **30 aprovados de 30** |
| Compilação sintática dos módulos Python | Aprovada |
| Sintaxe dos arquivos JavaScript (`node --check`) | **8 arquivos aprovados** |
| Renderização isolada do HTML/Jinja (5 páginas × 3 idiomas) | **15 renderizações aprovadas** |
| Verificação de recursos referenciados nos arquivos CSS | **24 referências locais resolvidas** |
| Integridade do arquivo de conhecimento `Teste.bcm` | Preservado, SHA-256: `8467bee583bb842db0dcadc52994fdad0b9cca80d0c731697a035470b91fe8cf` |
| Regras complementares | **22 regras** preservadas integralmente da base definida |

Os testes automatizados de inferência usam **cenários construídos a partir das regras**. Eles avaliam a execução do software, não a acurácia agronômica em campo.

## Como reproduzir os testes completos

Com Python 3.11 ou superior, na pasta principal do projeto:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

Os testes de rotas e APIs que dependem do Flask foram **mantidos em `tests/`**, mas não puderam ser executados neste ambiente de preparação porque o pacote Flask não estava instalado e não foi possível acessá-lo pelo gerenciador de pacotes. Por isso não há alegação de que a execução HTTP completa tenha sido validada aqui. Execute os comandos acima em um ambiente que tenha acesso às dependências antes da demonstração.

## Limite da avaliação

A validação técnica é distinta de uma avaliação agronômica independente: para comprovar desempenho diagnóstico em plantas reais, são necessários casos externos com diagnóstico de referência e revisão profissional das regras complementares. O procedimento recomendado está em `docs/METODOLOGIA_E_VALIDACAO.md`.
