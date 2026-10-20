# VitiExpert — VERSÃO BASE EM TESTAGEM (não definitiva)

**Status:** protótipo visual e funcional, sem validação científica. **Não apresentar como versão final.**

# VitiExpert — Protótipo Web v0.2.0

Aplicação Flask demonstrativa para apoio educativo à identificação de doenças em videiras. Interface inspirada no layout aprovado, com imagem de vinhedo gerada por IA, cabeçalho translúcido, Times New Roman, paleta uva/folha e três idiomas (PT/EN/ES).

## Como executar (Windows)

```powershell
cd VitiExpert
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

## Testes automatizados

```powershell
python -m pytest -q
```

## Limitações e integridade acadêmica

- A interface e o motor demonstrativo estão implementados; as regras usam **pesos ilustrativos não validados**, e o resultado é um **escore**, não uma probabilidade calibrada nem um fator de certeza científico.
- O sistema **não** implementa ainda a biblioteca Experta nem uma comparação executada com Expert SINTA.
- Login, histórico, e-mail de confirmação, notícias e dados climáticos ao vivo estão **planejados, não implementados**.
- Não utilizar resultados desta versão para orientar aplicação de defensivos ou substituir avaliação agronômica.
- Para produção: configurar `SECRET_KEY` via ambiente, autenticação segura, CSRF, rate limiting, persistência e privacidade/LGPD.

## Testes SINTA já observados pela usuária

- ERRO-001: referência incorreta `manchas-nas-folhas` em vez de `manchas_nas_folhas`; corrigido.
- TESTE-001: entrada Sim => `mildio`, CNF 100%, em regra puramente didática.
- TESTE-002: entrada Não => nenhum valor encontrado.
- TESTE-003: entrada Não sei => nenhum valor encontrado.

O arquivo `.BCM` do protótipo feito no Windows não foi incluído; deverá ser copiado pela autora quando disponível.

Veja `docs/PLANO_TCC.md` para o plano de validação científica.

## Atualização visual 0.2 (20/10/2026)
- Hero em altura de viewport (`100svh`), sem faixa de fundo antes da próxima seção.
- Cabeçalho, idiomas e acesso redesenhados com controles discretos; navegação mobile.
- Seções editoriais: recursos, funcionamento em 3 etapas, notícias e contextualização acadêmica.
- Notícias: `/api/news` consulta o RSS do Google Notícias (busca sobre uva, videira e viticultura no Brasil), atualiza cache a cada 15 minutos e informa indisponibilidade quando a fonte não responde. Depende de internet; manchetes são de terceiros e podem não ser exclusivamente sobre uva. Não é atualização em tempo real contínua.
- Telas internas harmonizadas com a página inicial: tipografia, espaçamento, linhas finas e sem grandes caixas.
- Motor de diagnóstico continua demonstrativo; a base científica será migrada do Expert SINTA após validação.
- O botão Entrar é apenas a rota de apresentação; autenticação ainda não implementada.

Para atualizar: substitua os arquivos antigos pelos do novo ZIP, pare o servidor com Ctrl+C e execute `python app.py`. Faça Ctrl+F5 no navegador para atualizar o CSS.

## Organização do código

- `app.py`: Flask, traduções, notícias e pontuação ilustrativa.
- `templates/site.html`: HTML das páginas, com blocos Jinja.
- `static/style.css`: identidade visual e responsividade.
- `static/app.js`: menu, idiomas, notícias e formulário.
- `static/icone-vitiexpert.png`: ícone atualizado sem faixa branca.
- `tests/`: testes automatizados básicos.
- `docs/PLANO_TCC.md`: próximos passos científicos.

Os comentários no código indicam a função dos principais blocos. Não há necessidade de comentar cada tag ou instrução trivial; a documentação prioriza os pontos importantes para manutenção e apresentação acadêmica.
