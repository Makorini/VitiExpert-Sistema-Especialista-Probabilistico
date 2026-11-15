# Registro de verificações — VitiExpert

**Data:** 10/11/2026  
**Escopo:** projeto entregue neste pacote, com 10 doenças, duas condições diferenciais, 34 perguntas e regras originais do Expert SINTA e regras complementares.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| Suíte completa do pacote, incluindo rotas e APIs Flask | **51 testes aprovados** |
| Primeira hipótese nos cenários fixos do CSV | **10 acertos em 10 cenários sintéticos** |
| Respostas e rótulo de empate em português, inglês e espanhol | 6 verificações de interface por simulação de DOM com respostas reais da API |
| Compilação sintática dos módulos Python | Aprovada |
| Sintaxe dos arquivos JavaScript (`node --check`) | **8 arquivos aprovados** |
| Renderização isolada do HTML/Jinja (5 páginas × 3 idiomas) | **15 renderizações aprovadas** |
| Verificação de recursos referenciados nos arquivos CSS | **24 referências locais resolvidas** |
| Integridade do arquivo de conhecimento `Teste.bcm` | Preservado, SHA-256: `8467bee583bb842db0dcadc52994fdad0b9cca80d0c731697a035470b91fe8cf` |
| Regras complementares | **22 regras** preservadas integralmente da base definida |

Os testes automatizados de inferência usam **cenários sintéticos**. Os dez casos de classificação leem entradas e hipóteses esperadas de um CSV fixo com referências da Embrapa. Eles avaliam a execução do software, não a acurácia agronômica em campo.

## Como reproduzir os testes completos

Com Python 3.11 ou superior, na pasta principal do projeto:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

## Limite da avaliação

A validação técnica é distinta de uma avaliação agronômica independente: para comprovar desempenho diagnóstico em plantas reais, são necessários casos externos com diagnóstico de referência e revisão profissional das regras complementares. O procedimento recomendado está em `docs/METODOLOGIA_E_VALIDACAO.md`.
