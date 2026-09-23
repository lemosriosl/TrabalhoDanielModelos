# Decisoes pendentes

Preencher antes do inicio da modelagem. Nao deixar agentes de IA assumirem estas respostas.

- [ ] Numero do grupo.
- [ ] Nomes dos integrantes.
- [ ] Modelo de especializacao correspondente ao grupo.
- [ ] Identidade e versao congelada das cinco bases.
- [ ] Variavel-alvo e pelo menos duas variaveis externas por base.
- [ ] Disponibilidade temporal de cada variavel externa.
- [ ] Horizonte comum de previsao.
- [ ] Origens de previsao e periodo de teste comum.
- [ ] Tamanho da janela inicial e uso de janela expansiva ou deslizante.
- [ ] Formula exata da forca da sazonalidade apresentada em sala.
- [ ] Estrategia e orcamento de busca de hiperparametros.
- [ ] Base 5: confirmar fonte, calendario e disponibilidade temporal de `IS_HOLIDAY` no `grupo5_new.csv`.
- [ ] Base 5: confirmar origem e finalidade de `TARGET_UP`; o arquivo codifica como 0 comparacoes com cotacao ausente.
- [ ] Base 5: confirmar unidade, moeda e fornecedor de `VALUE`.
- [ ] Base 1: confirmar proveniencia direta pela Bitget, data de download, unidade/metodologia de `Volume` e disponibilidade temporal de `Open`.
- [ ] Base 2: definir a agregacao dos 5.445 timestamps repetidos e confirmar fuso local e tratamento de horario de verao.
- [ ] Base 3: definir imputacao sem futuro para cada dobra de treino e excluir `No` como feature; a grade horaria ja esta completa.
- [ ] Base 4: confirmar fonte/licenca, tratar `-9999.00`, resolver duplicidades e lacunas e aprovar a frequencia final.
- [ ] Bases 1 a 5: classificar corretamente covariaveis internas, variaveis derivadas de calendario e exogenas externas; nao tratar colunas da propria base como externas sem justificativa temporal.

