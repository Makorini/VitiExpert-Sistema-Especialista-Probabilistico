# VitiExpert — Sistema Especialista para Doenças em Videiras

Sistema web desenvolvido como projeto de Trabalho de Conclusão de Curso (TCC) em Ciência da Computação. Usa **Python e Flask** para analisar sintomas de videiras por meio de regras SE/ENTÃO e Fatores de Certeza.

## Requisitos

- Python **3.11 ou superior**.
- Conexão à internet para consultar a previsão do tempo e as notícias.

## Como executar

1. Extraia o arquivo ZIP.
2. Abra um terminal **dentro da pasta `VitiExpert`** (onde está o arquivo `app.py`).
3. Instale as dependências e inicie o servidor:

```powershell
python -m pip install -r requirements.txt
python app.py
```

4. No navegador, acesse **http://127.0.0.1:5000**.
5. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

### Jeito mais fácil (Windows): dois cliques

Na pasta `VitiExpert`, dê **dois cliques em `iniciar_vitiexpert.bat`**. Ele prepara tudo sozinho (na primeira vez cria o ambiente `.venv` e instala as bibliotecas, o que precisa de internet), liga o servidor e abre o site no navegador. Para encerrar, feche a janela preta.

### Apresentar em outro computador

1. Instale o **Python 3.11 ou mais novo** (<https://www.python.org/downloads/>), marcando **"Add python.exe to PATH"**.
2. Copie a pasta do projeto para o computador (pelo `git clone` ou por pen drive/HD externo).
3. Para o código de confirmação ir por e-mail, copie também o arquivo **`.env`** (ele não vai pelo GitHub). Sem ele, o código aparece na janela preta, o que basta para demonstrar.
4. Para levar as contas e o histórico já cadastrados, copie a pasta **`instance`** junto.
5. Dê dois cliques em **`iniciar_vitiexpert.bat`**. **Faça isso uma vez antes do dia da apresentação**, com internet, para a instalação já ficar pronta.

O Clima, as Notícias, o envio de e-mail e as fotos do catálogo (vindas da Embrapa) precisam de internet; o Sistema Especialista, os textos do catálogo e as contas funcionam sem.

## Como funciona

- **Início:** apresentação do VitiExpert e notícias ligadas à viticultura.
- **Sistema Especialista:** responda às 34 perguntas com **Sim**, **Não** ou **Não sei** (em Sim/Não, ajuste também o seu grau de certeza) e clique em **Analisar sintomas**. O sistema apresenta até três hipóteses, percentuais de confiança, sinais considerados e regras acionadas. É possível limpar as respostas e realizar nova análise.
- **Doenças e Pragas:** catálogo com descrição de sinais e informações de referência, com pesquisa e filtros.
- **Clima:** condições atuais e previsão para a semana, com fundos que mudam de acordo com horário e tempo; a cidade inicial é Videira (SC) e pode ser alterada.
- **Interface:** oferece português, inglês e espanhol, além de temas claro e escuro.

Os percentuais são **níveis de confiança calculados pelas regras**; o resultado é orientativo e não substitui uma avaliação agronômica.

## Como o cálculo funciona (baseado no Expert SINTA)

O motor em Python reproduz as funções **padrão** de Fatores de Confiança descritas no manual do Expert SINTA (seção 1.4):

1. **Confiança na resposta do usuário (c1):** ao responder **Sim** ou **Não**, o usuário indica quanto tem certeza, de 0% a 100% (padrão 100%). **Não sei** deixa o fato desconhecido, e a regra não dispara.
2. **Confiança na regra (c2):** cada regra tem um CNF definido na base de conhecimento (ex.: `SE pó branco ENTÃO oídio CNF 100`).
3. **Conectivos:** condições ligadas por **E** multiplicam as confianças (80% e 70% → 56%); ligadas por **OU**, combinam-se por `c1 + c2 − c1·c2`.
4. **Confiança mínima:** como no SINTA, a regra só é aceita se a confiança da premissa for de pelo menos **50%**.
5. **Inferência:** conclusão = c1 × c2. Ex.: pó branco com 70% de certeza × CNF 100% = **70%**.
6. **Acúmulo de evidências:** quando duas regras concluem a mesma doença com fatores x e y, combina-se `x + y − (x · y)`.

## Contas de usuário e histórico

O login é **opcional**: sem conta, o Sistema Especialista funciona normalmente e nada é guardado. Com conta:

- **Cadastro com verificação de e-mail:** o usuário recebe um código de 6 dígitos (válido por 15 minutos) e só consegue entrar depois de digitá-lo na tela "Confirmar e-mail".
- **Histórico privado:** cada análise feita com a conta aberta é salva. Em **Minha conta** aparecem as doenças mais frequentes, as consultas por mês e uma tabela por mês e ano, com filtro de período.
- **Dados isolados:** cada usuário vê só as próprias consultas. Senhas são guardadas apenas como *hash*. A conta e todo o histórico podem ser excluídos pelo próprio usuário.
- O banco SQLite fica em `instance/vitiexpert.db`, criado automaticamente e fora do git.

### Configurar o envio do código por e-mail

O código sai da conta `makorini.dev@gmail.com`. A forma recomendada é a mesma do projeto do salão: um **Google Apps Script** na própria conta, que envia com `MailApp.sendEmail` **sem senha de app**.

1. Entre em <https://script.google.com> com a conta `makorini.dev@gmail.com` e crie um **Novo projeto**.
2. Apague o código de exemplo e cole todo o conteúdo de `docs/enviar_email_apps_script.gs`.
3. Em **Configurações do projeto** (engrenagem) → **Propriedades do script**, adicione `VITIEXPERT_TOKEN` com um texto secreto qualquer (por exemplo, uma frase longa).
4. Selecione a função `autorizarEnvioEmail` e clique em **Executar**; aceite as permissões (igual ao projeto do salão).
5. **Implantar → Nova implantação → App da Web**, com *Executar como: Eu* e *Quem pode acessar: Qualquer pessoa*. Copie a URL que termina em `/exec`.
6. Copie `.env.example` para `.env` (na pasta `VitiExpert`) e preencha:
   ```
   MAIL_SCRIPT_URL=https://script.google.com/macros/s/.../exec
   MAIL_SCRIPT_TOKEN=o mesmo texto secreto do passo 3
   ```
7. Reinicie o `python app.py`.

Alternativa: em vez do script, é possível usar o SMTP do Gmail com uma *senha de app* (`MAIL_PASSWORD` no `.env`).

Sem nenhuma das duas configurações, o cadastro continua funcionando para testes locais: o código aparece no terminal onde o `python app.py` está rodando.

## Testes do programa

Execute na pasta do projeto:

```powershell
python -m pytest -q
```

Os testes de software estão em `tests/`, os cenários automatizados em `knowledge/cenarios_sinteticos_10_doencas.csv`, e os resultados da verificação da entrega em `docs/RESULTADOS_DOS_TESTES.md`.

## Principais arquivos

- `app.py` — servidor e rotas Flask.
- `sinta_inference.py` e `complementary_inference.py` — motor de inferência.
- `knowledge/` — base original Expert SINTA e regras complementares.
- `accounts.py`, `account_store.py`, `account_mail.py` e `account_i18n.py` — contas, banco de dados, e-mail e textos da área de conta.
- `templates/` e `static/` — interface e recursos visuais.
- `tests/` — testes automatizados.
- `docs/METODOLOGIA_E_VALIDACAO.md` — referência metodológica e limites de avaliação.
