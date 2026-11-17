# VitiExpert — Metodologia, rastreabilidade e validação

## Objetivo e escopo

Sistema especialista por regras SE/ENTÃO com Fatores de Confiança, construído no **Expert SINTA** e executado por um motor em **Python**, para indicar hipóteses de doenças da videira a partir de sinais observados. O usuário responde a 31 perguntas com Sim, Não ou Não sei e, em Sim/Não, informa o quanto tem certeza (0–100%). O resultado mostra até três hipóteses, o nível de confiança e os sinais que levaram a cada uma; o nome da doença abre a ficha do catálogo, com a área "Como tratar" (resumo das recomendações da Embrapa Uva e Vinho). As regras acionadas e os CNFs continuam no retorno da API (`/api/diagnose`), mas não são exibidos ao usuário final.

### As dez doenças

Míldio, oídio, antracnose, podridão-cinzenta, podridão-da-uva-madura, podridão-ácida, escoriose, ferrugem, mancha-das-folhas e podridão-amarga.

## Base de conhecimento (Expert SINTA)

- **Arquivo:** `knowledge/VitiExpert10.bcm` — 31 variáveis de sintomas (Sim/Não), a variável objetivo `diagnostico` (multivalorada, com as 10 doenças) e **17 regras**, cada uma com **uma** conclusão e um CNF.
- **Projeto da base:** `docs/BASE_SINTA_10_DOENCAS.md` (variáveis, perguntas, regras e consultas de teste).
- **Critérios de modelagem:** regras da mesma doença não compartilham sintomas e nenhuma regra está contida em outra, para que o acúmulo de evidências (x + y − xy) não conte o mesmo sintoma duas vezes.
- **Geração e importação:** o `.bcm` é gerado por `knowledge/gerar_vitiexpert10_bcm.py` (gravador `knowledge/bcm_writer.py`, verificado regravando o `Teste.bcm` original de forma idêntica) e exportado para `knowledge/sinta_base_export.json` por `sinta_bcm_import.py`, com SHA-256 para detectar alterações. O motor recusa iniciar se o `.bcm` e o JSON divergirem.
- **Histórico:** `knowledge/Teste.bcm` é a primeira base do projeto (8 regras, com duas conclusões por regra). Foi substituída pela base atual e mantida apenas como registro.
- **Fontes dos sinais:** páginas da Embrapa Uva e Vinho (`https://www.cnpuv.embrapa.br/uzum/uva/<doença>.html`). Os CNFs são **heurísticos**, escolhidos pelo grupo a partir dessas descrições; não são taxas de incidência nem probabilidades publicadas.

## Cálculo (funções padrão do manual do Expert SINTA)

| Situação | Fórmula | Referência no manual |
| --- | --- | --- |
| Conclusão de uma regra | CNF da premissa × CNF da regra | seção 1.4, caso 1 |
| Conectivo **E** | c1 × c2 (produto) | seção 1.4, caso 2 |
| Conectivo **OU** | c1 + c2 − c1·c2 | seção 1.4, caso 3 |
| Mesma doença por várias regras | x + y − x·y | seção 1.4, caso 4 |
| Aceitação da regra | premissa ≥ 50% (valor mínimo padrão) | seções 1.4 e 2.8 |

A confiança de cada resposta é a certeza informada pelo usuário (padrão 100%). "Não sei" deixa o fato desconhecido: a regra não dispara e o sistema sugere perguntas que poderiam completá-la. Esses valores são **fatores de confiança**, não probabilidades estatísticas.

**Por que "probabilístico":** no título do projeto, o termo indica o tratamento da incerteza, em oposição à versão determinística anterior (sintoma só verdadeiro ou falso). O modelo usado é o de fatores de certeza do MYCIN (Shortliffe e Buchanan, 1975), criado como aproximação do raciocínio probabilístico quando não há dados estatísticos suficientes, e adotado pelo Expert SINTA. Por isso os percentuais são graus de confiança, e não a chance estatística de a videira ter a doença.

## Contas e dados

- O uso sem conta não guarda respostas. Com conta (cadastro confirmado por código enviado por e-mail), cada consulta entra no histórico privado do usuário, isolado das demais contas.
- **Retenção:** no ano vigente, as consultas ficam completas. Quando o ano termina, os detalhes são apagados automaticamente e fica um resumo por mês (total e doenças mais frequentes).
- Senhas e códigos são guardados apenas como hash. O usuário pode excluir os dados ou a conta a qualquer momento.

## O que os testes de software provam

1. O arquivo do SINTA, o roteiro, o JSON exportado e o motor Python contêm as mesmas regras.
2. Cada regra dispara sozinha com o seu CNF, e as consultas de referência dão a doença e o percentual esperados.
3. O cálculo reproduz os exemplos do manual do SINTA.
4. "Não sei" não é tratado como "Não"; entradas inválidas são recusadas.
5. Perguntas e resultados aparecem traduzidos em PT, EN e ES.

Esses testes **não** medem acurácia agronômica: os cenários são sintéticos e derivados das mesmas descrições que originaram as regras.

## Pendências para uma validação conclusiva

- Abrir `VitiExpert10.bcm` no ExSINTA e repetir as consultas T01–T14, registrando os resultados do programa ao lado dos do Python.
- Revisão das regras e dos CNFs por agrônomo ou fitopatologista (avaliação externa, por exemplo pela EPAGRI), com data e identificação.
- Casos independentes com diagnóstico de referência, para calcular acerto (acurácia, acerto no top-3, matriz de confusão) em dados não usados para criar as regras.
