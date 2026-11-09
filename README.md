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

## Como funciona

- **Início:** apresentação do VitiExpert e notícias ligadas à viticultura.
- **Sistema Especialista:** responda às 34 perguntas com **Sim**, **Não** ou **Não sei** e clique em **Analisar sintomas**. O sistema apresenta até três hipóteses, percentuais de confiança, sinais considerados e regras acionadas. É possível limpar as respostas e realizar nova análise.
- **Doenças e Pragas:** catálogo com descrição de sinais e informações de referência, com pesquisa e filtros.
- **Clima:** condições atuais e previsão para a semana, com fundos que mudam de acordo com horário e tempo; a cidade inicial é Videira (SC) e pode ser alterada.
- **Interface:** oferece português, inglês e espanhol, além de temas claro e escuro.

Os percentuais são **níveis de confiança calculados pelas regras**; o resultado é orientativo e não substitui uma avaliação agronômica.

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
- `templates/` e `static/` — interface e recursos visuais.
- `tests/` — testes automatizados.
- `docs/METODOLOGIA_E_VALIDACAO.md` — referência metodológica e limites de avaliação.
