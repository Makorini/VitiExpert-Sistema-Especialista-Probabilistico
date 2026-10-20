# Plano de execução e evidências — VitiExpert

## Tema e objetivo
Sistema especialista probabilístico para diagnóstico de doenças em videiras, aplicado à região de Videira, SC. Protótipo Expert SINTA, implementação Python/Experta e interface Flask.

## Escopo validado até aqui
A autora executou três casos didáticos em Expert SINTA, com uma única regra que associa manchas nas folhas a míldio. O objetivo era validar fluxo e sintaxe; a regra não constitui conhecimento agronômico validado.

## Próximas entregas obrigatórias
1. Delimitar doenças relevantes à região e obter literatura especializada (Epagri/EPAMIG e outras fontes).
2. Construir matriz rastreável de sintomas, doenças, regras, referências, parâmetros e justificativas; submeter a especialistas.
3. Modelar incerteza: escolher fatores de certeza **ou** probabilidades calibradas; documentar diferenças, combinação de evidências e casos desconhecidos.
4. Expandir `.BCM` no Expert SINTA; capturar regras, consultas e resultados com IDs e datas.
5. Implementar a mesma base de regras em Python/Experta; validar paridade de inferências.
6. Definir base de casos de referência, classes, distribuição, critérios de inclusão e fonte dos rótulos.
7. Medir acurácia, precisão, sensibilidade, F1, tempo; se houver probabilidades calibradas, avaliar calibração (Brier Score).
8. Apresentar resultados medidos, limitações e hipóteses H1/H2 sem afirmar superioridade antes dos experimentos.
9. Acrescentar autenticação, confirmação por e-mail, histórico com retenção, i18n integral e integrações externas mediante autorização.

## Modelo de registro de testes
ID | data | versão | ambiente | entradas | regra(s) acionada(s) | saída | resultado esperado | passou? | evidência (captura) | observações.

## Nota editorial para o artigo
É permitido redigir o texto final como estrutura pronta, com campos **[INSERIR RESULTADO REAL]**. Não atribuir valores de métricas, validação agronômica ou comparação Python x SINTA sem execução comprovada.
