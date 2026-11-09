# VitiExpert — Metodologia, rastreabilidade e validação

## Objetivo e escopo

Aplicação de sistema especialista por regras SE/ENTÃO com Fatores de Certeza para classificação orientativa de hipóteses de doenças e condições de videiras. O questionário possui 34 variáveis observáveis, respostas Sim/Não/Não sei; resultado: até três hipóteses e rastreabilidade das regras acionadas.

### Dez doenças cobertas

Míldio, oídio, antracnose, podridão-cinzenta, podridão-da-uva-madura, podridão-ácida, escoriose, ferrugem, mancha-das-folhas e podridão-amarga. Asfixia radicular e declínio/morte da videira foram mantidos **como condições diferenciais** da base original, não contadas como duas das dez doenças.

## Fontes e proveniência

O arquivo `knowledge/Teste.bcm` foi fornecido pela autora; importado em JSON por `sinta_bcm_import.py` com digest SHA-256 para detectar alterações. São oito regras originais e oito hipóteses. Os valores CNF originalmente registrados são preservados. O motor usa a combinação original `C=a+b-a*b` quando há múltiplas conclusões da mesma hipótese.

As **22 regras adicionais** de `knowledge/regras_complementares.json` descrevem sinais baseados em publicações da Embrapa, acessíveis na URL `reference` de cada regra. A associação entre sintomas e doença deriva dessas descrições; já os pesos `cf` foram escolhidos de forma **heurística para o software**, não são taxas de incidência, probabilidades clínicas ou coeficientes publicados pela Embrapa. Sempre identificar essa diferença na defesa.

Um caminho alternativo só é acionado quando **todas** as suas condições estão satisfeitas. Se uma variável estiver marcada Não sei, ela não vale como Não. Entre regras que compartilham evidências não se soma o mesmo sintoma diversas vezes: usa-se o maior fator da hipótese. Essa escolha evita inflação, mas continua precisando de avaliação e ajuste externo.

Referências básicas de sinais:

- https://www.cnpuv.embrapa.br/uzum/uva/mildio.html
- https://www.cnpuv.embrapa.br/uzum/uva/oidio.html
- https://www.cnpuv.embrapa.br/uzum/uva/antracnose.html
- https://www.cnpuv.embrapa.br/uzum/uva/pod_cinzenta.html
- https://www.cnpuv.embrapa.br/uzum/uva/pod_uva_madura.html
- https://www.cnpuv.embrapa.br/uzum/uva/pod_acida.html
- https://www.cnpuv.embrapa.br/uzum/uva/escoriose.html
- https://www.cnpuv.embrapa.br/uzum/uva/ferrugem.html
- https://www.cnpuv.embrapa.br/uzum/uva/mancha_folhas.html
- https://www.cnpuv.embrapa.br/uzum/uva/pod_amarga.html

## O que os testes de software efetivamente provam

1. Integridade do arquivo-base e reprodução das condições do SINTA em Python.
2. Fatores de certeza originais reproduzidos matematicamente.
3. Acionamento das dez doenças em cenários artificiais construídos a partir das próprias regras.
4. Tratamento de respostas ausentes, contraditórias e inválidas, sem conversão automática de Não sei em Não.
5. Tradução e integridade das perguntas nos três idiomas.

Esses testes **não** medem acurácia agronômica: os cenários sintéticos são gerados a partir das próprias condições e, portanto, não são independentes. Nenhum percentual apresentado como hipótese de doença deve ser interpretado como chance calibrada em uma população de plantas.

## Pendências externas necessárias para uma validação agronômica conclusiva

- Revisão e aceite/ajuste das 22 regras e de seus pesos por agrônomo ou fitopatologista competente, registrado com data e identificação profissional.
- Coleta de casos independentes com diagnóstico de referência (avaliação especializada, laboratório ou evidência verificável), com respostas completas para o questionário, inclusive negativos observados.
- Avaliação em dados reservados, não usados para desenhar/ajustar regras. Calcular matriz de confusão, acurácia, macro-F1, precisão e recall por classe, taxa de abstenção e acerto no top-3. Divulgar N por doença e intervalos de confiança quando pertinente.
- Execução dos mesmos cenários no Expert SINTA original e no Python com capturas de resultados (não confundir reprodução matemática com execução real no programa Windows).
- Se o trabalho pretender chamar CNF de probabilidade estatística, comprovar calibração separadamente por faixas de confiança, por exemplo Brier score/reliability; se não, manter o termo correto de fator/nível de confiança.

O conjunto de relatos publicados analisado anteriormente é **exploratório e possui informações incompletas**. Não substitui casos independentes com questionário preenchido. Uma avaliação documental exploratória foi realizada separadamente, sem substituir uma avaliação independente com questionários completos.

## Exemplo de demonstração reproduzível

POST `/api/diagnose`, JSON: `{"answers":{"manchas_oleosas":"sim","mofo_branco_inferior":"sim"}}`. O motor deve apresentar Míldio com CNF heurístico de 78% por `COMP-R09`. Não afirmar que essa é a probabilidade real de uma planta estar doente.

Para o Míldio SINTA original, `{"answers":{"manchas_amarelas":"sim","folhas_murchas":"sim","chuva_continua":"sim"}}` deve apresentar 98% (a combinação de CNFs originais de 90% e 80%). Essa é apenas a reprodução do fator do arquivo.
