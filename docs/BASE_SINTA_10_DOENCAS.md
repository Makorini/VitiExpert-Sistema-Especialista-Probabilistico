# Base Expert SINTA — VitiExpert 10 doenças

Roteiro para cadastrar no **Expert SINTA** (`DoctorSinta-main/ExSINTA.exe`) a base nova que substitui o `Teste.bcm` e as regras complementares. Depois de salva, o motor Python passa a ler **só este arquivo**: a base criada no SINTA é a única fonte de regras.

Salvar como: `VitiExpert/knowledge/VitiExpert10.bcm`

## O que muda em relação ao Teste.bcm

| Problema no Teste.bcm + regras complementares | Na base nova |
|---|---|
| Cada regra tinha **duas conclusões** da mesma doença (ex.: míldio CNF 90 e CNF 80), e o resultado virava 98% | **Uma conclusão por regra** |
| Regras de um sintoma contidas em outras (ex.: "mofo cinzento" dentro de "mofo cinzento + cacho compacto"), contando o mesmo sintoma várias vezes e chegando a 99,9% | Regras da mesma doença **não compartilham sintomas**, e nenhuma regra está contida em outra |
| 8 regras no SINTA + 22 em JSON fora do SINTA | **17 regras, todas no SINTA** |
| Asfixia radicular e declínio contados junto com as doenças | Só as **10 doenças** do escopo |

> Os valores de CNF são **heurísticos** (escolhidos pelo grupo a partir das descrições da Embrapa Uva e Vinho). Eles precisam ser revisados por especialista, como na avaliação planejada com a EPAGRI.

## 1. Variáveis (botão **Variáveis**)

Pelo manual (seção 2.3, Obs. 3), **uma variável sem valores cadastrados é lógica (Sim/Não)**. Então basta digitar o nome de cada variável abaixo e teclar ENTER. Não é preciso cadastrar valores, exceto para `diagnostico`.

Digite os nomes **exatamente assim** (minúsculas, sem acento, com `_`), porque o Python usa esses nomes para achar o texto das perguntas em PT/EN/ES.

| # | Variável | Pergunta (para a janela Interface) |
|---|---|---|
| 1 | manchas_oleosas | Há manchas amareladas com aspecto de óleo nas folhas? |
| 2 | mofo_branco_inferior | Há mofo branco na parte de baixo das folhas? |
| 3 | manchas_amarelas | As folhas apresentam manchas amareladas? |
| 4 | folhas_murchas | As folhas estão murchas? |
| 5 | chuva_continua | Houve chuva contínua nos últimos dias? |
| 6 | poeira_branca | Há uma camada de pó branco sobre folhas ou frutos? |
| 7 | bagas_rachadas | Há bagas com rachaduras na casca? |
| 8 | chuva_frequente | Tem chovido frequentemente? |
| 9 | lesoes_deprimidas_escuras | Existem lesões escuras e afundadas? |
| 10 | halo_avermelhado | As lesões apresentam um halo avermelhado? |
| 11 | folhas_jovens_pontos_escuros | Folhas jovens apresentam pequenas manchas escuras? |
| 12 | folhas_deformadas | As folhas jovens estão deformadas ou encarquilhadas? |
| 13 | mofo_cinza | Existe mofo cinzento nos cachos? |
| 14 | cacho_compacto | Os cachos são compactos, com bagas muito próximas? |
| 15 | exsudato_rosado | Há pontuações nas bagas que liberam massa rosada ou salmão? |
| 16 | maturacao | A videira está na fase de maturação dos cachos? |
| 17 | frutos_escurecidos | As bagas estão escurecendo? |
| 18 | lesoes_concentricas | As bagas apresentam lesões em círculos concêntricos? |
| 19 | odor_acetico | Os cachos têm cheiro ácido semelhante a vinagre? |
| 20 | moscas_vinagre | Há pequenas moscas semelhantes às do vinagre próximas aos cachos? |
| 21 | frutos_moles | Existem bagas amolecidas? |
| 22 | bagas_vazando_suco | Existem bagas rachadas liberando suco? |
| 23 | escoriacoes_ramos_base | Há lesões alongadas e escuras na base dos ramos novos? |
| 24 | galhos_quebradicos | Os ramos estão secos ou quebradiços? |
| 25 | brotacao_fraca | A brotação da planta está fraca? |
| 26 | pustulas_amarelas_inferiores | Existem pequenas pústulas amarelas na face inferior das folhas? |
| 27 | manchas_angulares_superiores | A parte superior das folhas tem pequenas lesões angulares? |
| 28 | folhas_maduras_afetadas | As manchas aparecem principalmente em folhas maduras? |
| 29 | manchas_irregulares_halo_amarelo | Há manchas irregulares escuras com halo amarelo-esverdeado nas folhas? |
| 30 | pustulas_escuras_bagas | Há pontuações ou pústulas escuras na casca das bagas? |
| 31 | bagas_mumificadas | Há bagas enrugadas, secas ou mumificadas? |
| 32 | **diagnostico** | (variável objetivo, sem pergunta) |

Valores de `diagnostico` (marque como **multivalorada**, para o SINTA mostrar todas as doenças encontradas):
`mildio`, `oidio`, `antracnose`, `podridao_cinzenta`, `podridao_madura`, `podridao_acida`, `escoriose`, `ferrugem`, `mancha_folhas`, `podridao_amarga`

## 2. Objetivo (botão **Objetivos**)

Mova `diagnostico` para a lista de variáveis objetivo e deixe marcado **Mostrar resultados**.

## 3. Regras (botão **Nova Regra**)

Todas as condições usam o operador `=`, ligadas por **E**. Cada regra tem **uma** conclusão `diagnostico = <doença> CNF <valor>`.

| Regra | SE (todas verdadeiras) | ENTÃO diagnostico = | CNF |
|---|---|---|---|
| R01 | manchas_oleosas = Sim **E** mofo_branco_inferior = Sim | mildio | 90 |
| R02 | manchas_amarelas = Sim **E** folhas_murchas = Sim **E** chuva_continua = Sim | mildio | 70 |
| R03 | poeira_branca = Sim | oidio | 80 |
| R04 | bagas_rachadas = Sim **E** chuva_frequente = Não | oidio | 55 |
| R05 | lesoes_deprimidas_escuras = Sim **E** halo_avermelhado = Sim | antracnose | 85 |
| R06 | folhas_jovens_pontos_escuros = Sim **E** folhas_deformadas = Sim | antracnose | 70 |
| R07 | mofo_cinza = Sim **E** cacho_compacto = Sim | podridao_cinzenta | 85 |
| R08 | exsudato_rosado = Sim **E** maturacao = Sim | podridao_madura | 85 |
| R09 | frutos_escurecidos = Sim **E** lesoes_concentricas = Sim | podridao_madura | 60 |
| R10 | odor_acetico = Sim **E** moscas_vinagre = Sim | podridao_acida | 90 |
| R11 | frutos_moles = Sim **E** bagas_vazando_suco = Sim | podridao_acida | 60 |
| R12 | escoriacoes_ramos_base = Sim | escoriose | 80 |
| R13 | galhos_quebradicos = Sim **E** brotacao_fraca = Sim | escoriose | 55 |
| R14 | pustulas_amarelas_inferiores = Sim | ferrugem | 85 |
| R15 | manchas_angulares_superiores = Sim **E** folhas_maduras_afetadas = Sim | ferrugem | 55 |
| R16 | manchas_irregulares_halo_amarelo = Sim **E** folhas_maduras_afetadas = Sim | mancha_folhas | 85 |
| R17 | pustulas_escuras_bagas = Sim **E** bagas_mumificadas = Sim | podridao_amarga | 85 |

Fontes dos sintomas: páginas da Embrapa Uva e Vinho (`https://www.cnpuv.embrapa.br/uzum/uva/<doença>.html`), já citadas em `docs/METODOLOGIA_E_VALIDACAO.md`.

## 4. Perguntas (botão **Interface**)

Para cada variável de 1 a 31, cole o texto da coluna "Pergunta" da tabela do passo 1.

## 5. Opções de fator de confiança (menu **Exibir → Opções**)

**Mantenha o padrão do SINTA.** É o que o Python reproduz (decisão do grupo: seguir o manual):
- função da **conjunção (E)**: padrão = produto `cnf1 * cnf2`; **não** troque por `Min(cnf1, cnf2)`;
- função da **disjunção (OU)**: padrão = `cnf1 + cnf2 - cnf1 * cnf2`;
- **valor mínimo de confiança** para aceitar uma regra: **50**.

Se alguém mudar essas opções no SINTA, o Python deixa de dar os mesmos números.

## 6. Salvar e conferir

1. Salve como `VitiExpert10.bcm` na pasta `VitiExpert/knowledge/`.
2. Faça no SINTA as consultas de teste da tabela abaixo e anote o percentual que o SINTA mostra para cada uma. Esses valores viram os testes automáticos do Python, que precisam dar **o mesmo número do SINTA**.

| Teste | Responder Sim (100%) | Esperado (1º lugar) |
|---|---|---|
| T01 | manchas_oleosas, mofo_branco_inferior | mildio 90% |
| T02 | poeira_branca | oidio 80% |
| T03 | lesoes_deprimidas_escuras, halo_avermelhado | antracnose 85% |
| T04 | mofo_cinza, cacho_compacto | podridao_cinzenta 85% |
| T05 | exsudato_rosado, maturacao | podridao_madura 85% |
| T06 | odor_acetico, moscas_vinagre | podridao_acida 90% |
| T07 | escoriacoes_ramos_base | escoriose 80% |
| T08 | pustulas_amarelas_inferiores | ferrugem 85% |
| T09 | manchas_irregulares_halo_amarelo, folhas_maduras_afetadas | mancha_folhas 85% |
| T10 | pustulas_escuras_bagas, bagas_mumificadas | podridao_amarga 85% |
| T11 | T01 + manchas_amarelas, folhas_murchas, chuva_continua | mildio 97% (0,90 + 0,70 − 0,90·0,70) |
| T12 | poeira_branca com certeza **70%** | oidio: 56% (70% × 80%) |
| T13 | manchas_oleosas **70%** e mofo_branco_inferior **70%** | míldio **não** aparece pela R01: 0,7 × 0,7 = 49%, abaixo do mínimo de 50% |
| T14 | poeira_branca com certeza **50%** | confere se o SINTA aceita exatamente 50% (o Python aceita: oidio 40%) |

Nas consultas, responda "Não" ou deixe "Desconhecido" nas perguntas que não estão na linha.
