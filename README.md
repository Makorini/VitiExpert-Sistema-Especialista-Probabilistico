# VitiExpert — Sistema Especialista Probabilístico para Diagnóstico de Doenças em Videiras

Sistema web desenvolvido no Trabalho de Conclusão de Curso (TCC II) de Ciência da Computação da **Universidade do Oeste de Santa Catarina (Unoesc), campus Videira**, em 2026.

- **Acadêmicas:** Allana Vitória Zucco Paganini e Bianca Stefany Maccarini
- **Orientador:** Prof. Herculano De Biasi
- **Situação:** versão final do sistema para a entrega e a banca do TCC II (novembro de 2026)

O usuário responde perguntas sobre o que observa na videira e o sistema indica até três doenças prováveis, cada uma com um **nível de confiança** calculado por **fatores de certeza**. As regras foram modeladas no **Expert SINTA** e são executadas por um motor próprio em **Python**, numa aplicação web feita com **Flask**.

## Requisitos

- Python **3.11 ou superior**.
- Internet para a previsão do tempo, as notícias, o envio de e-mail e as fotos do catálogo. O Sistema Especialista funciona sem internet.

## Como executar

1. Baixe o projeto (`git clone` ou o ZIP do GitHub).
2. Abra um terminal **dentro da pasta do projeto** (onde está o arquivo `app.py`).
3. Instale as dependências e inicie o servidor:

```powershell
python -m pip install -r requirements.txt
python app.py
```

4. No navegador, acesse **http://127.0.0.1:5000**.
5. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

### Jeito mais fácil (Windows): dois cliques

Dê **dois cliques em `iniciar_vitiexpert.bat`**. Na primeira vez, ele cria o ambiente `.venv` e instala as bibliotecas (precisa de internet); depois liga o servidor e abre o site no navegador. Para encerrar, feche a janela preta.

### Apresentar em outro computador

1. Instale o **Python 3.11 ou mais novo** (<https://www.python.org/downloads/>), marcando **"Add python.exe to PATH"**.
2. Copie a pasta do projeto para o computador (`git clone`, pen drive ou HD externo).
3. Para o código de confirmação ir por e-mail, copie também o arquivo **`.env`** (ele não vai para o GitHub). Sem ele, o código aparece na janela preta, o que basta para demonstrar.
4. Para levar as contas e o histórico já cadastrados, copie a pasta **`instance`** junto.
5. Dê dois cliques em **`iniciar_vitiexpert.bat`**. **Faça isso uma vez antes do dia da apresentação**, com internet, para a instalação já ficar pronta.

### Publicar na internet em `/VitiExpert` (Cloudflare Tunnel)

O site pode rodar dentro de um caminho, como `https://makorini.com.br/VitiExpert`. Os links usam o prefixo automaticamente (`request.script_root`), então o mesmo código funciona na raiz (`python app.py`) e dentro de `/VitiExpert`.

1. Instale o servidor de produção: `python -m pip install waitress`.
2. Na pasta do projeto, inicie o site com o prefixo:
   ```powershell
   python -m waitress --listen=127.0.0.1:8080 wsgi_prefix:app
   ```
   Teste em <http://127.0.0.1:8080/VitiExpert/> (a raiz `http://127.0.0.1:8080/` redireciona para lá).
3. No `config.yml` do Cloudflare Tunnel, encaminhe o caminho para o servidor local:
   ```yaml
   ingress:
     - hostname: makorini.com.br
       path: ^/VitiExpert(/.*)?$
       service: http://127.0.0.1:8080
     - service: http_status:404
   ```
4. Crie o endereço uma única vez (`cloudflared tunnel route dns <nome-do-túnel> makorini.com.br`) e ligue o túnel (`cloudflared tunnel run <nome-do-túnel>`).

O computador precisa ficar ligado, com o Waitress e o túnel abertos. Antes de abrir o cadastro ao público, mantenha o `.env` fora do Git e faça cópias de segurança da pasta `instance`.

## O que o sistema faz

- **Sistema Especialista:** 28 perguntas, em quatro grupos (folhas, cachos, ramos e clima), respondidas com **Sim**, **Não** ou **Não sei**; em Sim ou Não, o usuário informa também o quanto tem certeza (0% a 100%). O resultado mostra até três hipóteses, com o percentual de confiança e os **sinais que levaram a cada uma**, além de perguntas que poderiam completar outras regras. Clicando no nome da doença, abre-se a **ficha** com foto, como reconhecer e **como tratar**.
- **Doenças e Pragas:** catálogo com 53 condições da videira (Embrapa Uva e Vinho), com pesquisa e filtros.
- **Clima:** condições atuais e previsão da semana, começando por Videira (SC).
- **Início:** apresentação do sistema e notícias de viticultura.
- **Contas (opcional):** histórico privado de consultas, com gráficos por mês e ano.
- **Interface:** português, inglês e espanhol, com temas claro e escuro.

Os percentuais são **níveis de confiança calculados pelas regras**, e não probabilidades estatísticas. O resultado é orientativo e não substitui a avaliação de um engenheiro agrônomo.

## As 10 doenças

Míldio, oídio, antracnose, podridão-cinzenta, podridão-da-uva-madura, podridão-ácida, escoriose, ferrugem, mancha-das-folhas e podridão-amarga.

## Como funciona por dentro

```
docs/BASE_SINTA_10_DOENCAS.md   projeto da base: 28 perguntas e 16 regras com CNF
        │  knowledge/gerar_vitiexpert10_bcm.py + bcm_writer.py
        ▼
knowledge/VitiExpert10.bcm      base no formato do Expert SINTA (abre no ExSINTA)
        │  sinta_bcm_import.py  (lê o arquivo binário e registra o SHA-256)
        ▼
knowledge/sinta_base_export.json
        │  sinta_inference.py   (motor: aplica as fórmulas do manual do SINTA)
        ▼
app.py  →  POST /api/diagnose  →  static/expert.js  (mostra o resultado no navegador)
```

- O Python **não chama o SINTA** em tempo de execução: os dois compartilham o mesmo arquivo de base.
- Antes de cada diagnóstico, o motor confere se o SHA-256 do `.bcm` ainda é o registrado no JSON. Se a base mudar, é preciso rodar `python sinta_bcm_import.py`.
- Cada regra tem uma única conclusão, e regras da mesma doença não compartilham sintomas, para que nenhum sinal seja contado duas vezes.

## Como o cálculo funciona (baseado no Expert SINTA)

O motor reproduz as funções **padrão** de fatores de confiança do manual do Expert SINTA (seção 1.4):

1. **Confiança na resposta (c1):** a certeza informada pelo usuário, de 0% a 100% (padrão 100%). **Não sei** deixa o fato desconhecido, e a regra não dispara; não é o mesmo que "Não".
2. **Confiança na regra (c2):** cada regra tem um CNF na base. Ex.: `SE manchas oleosas E mofo branco embaixo da folha ENTÃO míldio, CNF 90%`.
3. **Conectivo E:** multiplica as confianças das condições (80% e 70% → 56%).
4. **Confiança mínima:** como no SINTA, a regra só é aceita se a premissa chegar a **50%** (70% × 70% = 49% → recusada).
5. **Conclusão:** premissa × CNF. Ex.: os dois sinais da regra acima com 100% de certeza → 1 × 0,90 = **90%**.
6. **Acúmulo de evidências:** duas regras da mesma doença combinam-se por `x + y − x·y`. Ex.: 0,90 + 0,70 − 0,63 = **97%**.

## Resultados da avaliação

| Verificação | Resultado |
| --- | --- |
| Testes automáticos (`python -m pytest -q`) | **123 aprovados** |
| Cada regra sozinha dá exatamente o seu CNF | 17 de 17 |
| Consultas de referência (T01 a T11) | 11 de 11 |
| Sinais de duas doenças: as duas entre as três primeiras | 45 de 45 |
| Tempo médio por diagnóstico | 0,024 ms |
| Comparação com uma versão determinística com as mesmas regras: mostra as duas doenças / recusa evidência fraca (70% de certeza) | 45/45 × 0/45 e 13/13 × 0/13 |
| Relatos de casos publicados | 1 de 10 identificado, nenhum diagnóstico errado |
| Revisão por especialista da EPAGRI (18/11/2026) | 11 regras aprovadas, 5 com ajustes e 1 retirada; ajustes já aplicados |

Os testes comprovam a **consistência do software**, não a acurácia em campo: os cenários são sintéticos e os CNFs são heurísticos, definidos a partir das fichas da Embrapa. As regras foram revisadas por uma especialista da EPAGRI, e os ajustes já estão na base (veja `docs/BASE_SINTA_10_DOENCAS.md`); o próximo passo são casos de campo com diagnóstico confirmado. Detalhes em `docs/RESULTADOS_DOS_TESTES.md` e `docs/METODOLOGIA_E_VALIDACAO.md`.

## Contas de usuário e histórico

O login é **opcional**: sem conta, o Sistema Especialista funciona normalmente e nada é guardado. Com conta:

- **Cadastro com verificação de e-mail:** código de 6 dígitos, válido por 15 minutos.
- **Histórico privado:** em **Minha conta** aparecem as doenças mais frequentes, as consultas por mês e uma tabela por mês e ano, com filtro de período. No ano atual, as consultas ficam completas; dos anos anteriores fica um resumo por mês.
- **Dados isolados e seguros:** cada usuário vê só as próprias consultas; senhas e códigos são guardados apenas como *hash*; formulários protegidos contra CSRF; bloqueio após 5 senhas erradas.
- **Esqueci minha senha:** código por e-mail para criar uma senha nova.
- **Configurações** (menu "Minha conta"): excluir os dados do histórico ou a conta inteira, com confirmação.
- O banco SQLite fica em `instance/vitiexpert.db`, criado automaticamente e fora do git.

### Conta de demonstração (para apresentações)

```powershell
python criar_conta_demo.py
```

Cria a conta **demo@vitiexpert.local** (senha **Demo2026uva**) com consultas de exemplo do ano passado (já resumidas por mês) e do ano atual. Os dados são fictícios.

### Configurar o envio do código por e-mail

O código é enviado por um **Google Apps Script** na conta `makorini.dev@gmail.com`, com `MailApp.sendEmail`, **sem senha de app**.

1. Entre em <https://script.google.com> com a conta remetente e crie um **Novo projeto**.
2. Apague o código de exemplo e cole todo o conteúdo de `docs/enviar_email_apps_script.gs`.
3. Em **Configurações do projeto** (engrenagem) → **Propriedades do script**, adicione `VITIEXPERT_TOKEN` com um texto secreto qualquer (por exemplo, uma frase longa).
4. Selecione a função `autorizarEnvioEmail`, clique em **Executar** e aceite as permissões.
5. **Implantar → Nova implantação → App da Web**, com *Executar como: Eu* e *Quem pode acessar: Qualquer pessoa*. Copie a URL que termina em `/exec`.
6. Copie `.env.example` para `.env` e preencha:
   ```
   MAIL_SCRIPT_URL=https://script.google.com/macros/s/.../exec
   MAIL_SCRIPT_TOKEN=o mesmo texto secreto do passo 3
   ```
7. Reinicie o `python app.py`.

Alternativa: SMTP do Gmail com uma *senha de app* (`MAIL_PASSWORD` no `.env`). Sem nenhuma das duas configurações, o cadastro continua funcionando para testes locais: o código aparece no terminal.

## Testes do programa

```powershell
python -m pytest -q
```

São **123 testes** em `tests/`: 44 da base do SINTA e do motor, 49 das contas e 30 das rotas, páginas, traduções e recursos. As consultas de referência da base estão em `knowledge/cenarios_base_sinta.csv`, e o registro das verificações, em `docs/RESULTADOS_DOS_TESTES.md`.

## Principais arquivos

| Arquivo | Para que serve |
| --- | --- |
| `app.py` | Servidor e rotas Flask, incluindo `POST /api/diagnose` |
| `sinta_inference.py` | Motor de inferência (fatores de confiança do Expert SINTA) |
| `sinta_bcm_import.py` | Lê o arquivo do SINTA e gera `knowledge/sinta_base_export.json` |
| `sinta_i18n.py` | Textos das perguntas, nomes das doenças e grupos, em PT/EN/ES |
| `knowledge/VitiExpert10.bcm` | **Base do Expert SINTA** (10 doenças, 16 regras); `gerar_vitiexpert10_bcm.py` e `bcm_writer.py` geram esse arquivo a partir de `docs/BASE_SINTA_10_DOENCAS.md`. O `Teste.bcm` é a primeira base, guardada como histórico |
| `static/expert.js` | Questionário e tela de resultado do Sistema Especialista |
| `static/disease-sheet.js`, `static/disease-treatments.js` | Ficha da doença (usada no catálogo e no resultado) e textos de "Como tratar" |
| `static/diseases-data.js`, `static/catalog-i18n.js` | Catálogo Doenças e Pragas e suas traduções |
| `accounts.py`, `account_store.py`, `account_mail.py`, `account_i18n.py` | Contas, banco de dados, e-mail e textos da área de conta |
| `criar_conta_demo.py` | Cria a conta de demonstração |
| `iniciar_vitiexpert.bat` | Inicia o sistema com dois cliques (Windows) |
| `wsgi_prefix.py` | Publica o site dentro de `/VitiExpert` (usado com o Waitress e o Cloudflare Tunnel) |
| `templates/`, `static/` | Páginas, estilos, scripts e imagens |
| `tests/` | Testes automatizados |
| `docs/` | Projeto da base, metodologia, resultados dos testes e script de e-mail |
