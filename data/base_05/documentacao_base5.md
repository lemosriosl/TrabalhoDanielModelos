# Base 5 — ouro semanal

## 1. Identificação e proveniência

| Campo | Definição usada |
|---|---|
| Arquivo local | `trabalho/bases/grupo5/grupo5.csv` |
| SHA-256 | `c852759b32f534918f76f9c3a31342228bf0bbc8a61fc5a26a63e61bf93ee64f` |
| Base adaptada | [TheoMGtech/pls-regration-comparation — grupo5](https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5) |
| Tratamento informado | [TheoMGtech/pls-regration-comparation — grupo5-tratamento](https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5-tratamento) |
| Série histórica indicada como oficial | [gold.daily.prices.csv](https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv) |
| Período diário disponível | 1968-04-29 a 2014-04-09 |
| Frequência do experimento | Semanal, regra `W-FRI` |
| Preço semanal | Último preço disponível até o encerramento da semana |
| Alvo | Retorno logarítmico da semana seguinte |
| Divisão | 75% treino / 25% teste, cronológica |
| Semente | 42 |

O CSV não declara fornecedor primário, unidade ou moeda do preço, nem a
proveniência exata e o horário de publicação das taxas. O notebook assume que
cada valor datado já estava disponível até o encerramento da respectiva semana.

## 2. Estrutura e auditoria do novo CSV

O arquivo atual usa vírgula, possui 9.864 linhas, 16 colunas, datas únicas e
ordenadas, nenhum valor nulo e preços positivos. As colunas primitivas usadas
na reconstrução são:

- `DATE`: data da observação;
- `GOLD_PRICE`: preço do ouro na unidade de origem;
- `TREASURY_10Y`: taxa nominal de Treasury de 10 anos;
- `FED_FUNDS_RATE`: taxa Fed Funds.

As demais colunas (`DAY_OF_WEEK`, `MONTH`, senos, cossenos, lags, janelas e
`TARGET`) foram produzidas antes da entrega. Elas são auditadas, mas não entram
no modelo. No arquivo atual, `TARGET` coincide com o preço da próxima linha em
95,66% dos casos e `GOLD_LAG_1` coincide com o `shift(1)` da tabela em 95,68%.
Isso indica que linhas foram removidas depois da criação dessas variáveis ou
que elas usam outra grade temporal. Reutilizá-las misturaria definições.

## 3. Limpeza e preparação semanal

O notebook `grupo5_RF.ipynb` preserva o CSV e executa por código:

1. valida esquema, tipos, datas, duplicidades, ausências e hash;
2. mantém somente as quatro colunas primitivas para reconstruir a base;
3. cria uma grade semanal completa `W-FRI`;
4. usa a última observação da semana quando disponível;
5. nas semanas vazias, carrega somente o último estado já conhecido;
6. registra cobertura, carregamento e idade da última cotação;
7. cria retorno, alvo, lags e janelas sem consultar o futuro.

A série possui 2.398 semanas, de 1968-05-03 a 2014-04-11. Há 254 semanas sem
linha de origem; a maior idade da cotação na origem é 17 dias. A grade final é
regular, sem lacunas. O carregamento para a frente representa o último estado
conhecido e não usa observações posteriores.

## 4. EDA, STL e estacionariedade

O notebook apresenta preço, retorno, taxas, volatilidade, idade da cotação e
distribuições. A STL usa `period=52` e `robust=True`. A força sazonal é
`max(0, 1 - Var(resíduo) / Var(sazonalidade + resíduo))`; a força da tendência
usa a fórmula análoga.

| Diagnóstico | Resultado verificado |
|---|---:|
| Força da sazonalidade | 0,0000 |
| Força da tendência | 0,9275 |
| ADF do log-preço no treino | p = 0,1128; não rejeita raiz unitária a 5% |
| ADF do retorno semanal no treino | p < 0,001; rejeita raiz unitária |

ACF e PACF são calculadas sobre o retorno semanal do treino.

## 5. Random Forest e otimização

O conjunto modelável possui 2.344 origens. Depois do corte e da purga da
fronteira, a grade contém 1.757 linhas de treino e 586 origens de teste, de
2003-01-17 a 2014-04-04. Somente as 1.570 linhas de treino cuja semana-alvo
possui cotação nova entram no tuning e no ajuste. As 49 features incluem estado
atual, cobertura, taxas, variações, lags, janelas defasadas e calendário
cíclico. Datas-alvo, preço futuro, `target_has_new_quote` e todas as derivações
entregues no CSV ficam fora de `X`.

A busca revisada usa `for` explícito, três dobras temporais com purga e nove
configurações planejadas para investigar todos os hiperparâmetros exigidos:

- `n_estimators`: 100 ou 250;
- `max_depth`: 6, 12 ou ilimitada;
- `min_samples_split`: 2, 5 ou 10;
- `min_samples_leaf`: 1, 2 ou 3;
- `max_features`: `sqrt` ou 0,7.

Melhores parâmetros para o RF de retorno: `n_estimators=250`, `max_depth=6`,
`min_samples_split=2`, `min_samples_leaf=3` e `max_features='sqrt'`. A busca
levou 11,03 segundos nesta execução. O walk-forward manteve os parâmetros
fixos, reajustou a cada 26 semanas em 23 blocos e levou 12,19 segundos.

O notebook agora registra também a importância nativa média e sua variação
entre os 23 reajustes. As primeiras posições incluem retorno corrente,
volatilidade e dispersão históricas, lags de retorno e defasagens da Fed Funds,
permitindo separar contribuição autorregressiva, de risco e das taxas externas.

## 6. Métricas fora da amostra

| Modelo | MAE retorno | RMSE retorno | MedAE retorno | R² | Acurácia direcional | MAE preço |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0,023132 | 0,030884 | 0,018354 | -0,0601 | 0,5010 | 21,6735 |
| Retorno zero / persistência | 0,022522 | 0,030098 | 0,018257 | -0,0068 | 0,0019* | 21,2349 |

`*` A previsão zero só acerta o sinal quando o retorno observado também é
zero e não mede capacidade de prever alta ou queda.

O Random Forest de retorno não superou a persistência. A tabela usa como
avaliação principal as 523 origens cuja semana-alvo possui cotação nova. O
notebook mantém previsões para as 586 origens e apresenta a grade completa
somente como sensibilidade; nesse recorte, o MAE de preço foi 19,7933 no RF e
18,9520 na persistência.

O RF direto no preço também foi reajustado apenas com alvos observados e teve
MAE de preço 59,7932 nas 523 observações, contra 21,2349 da persistência. Ele é
mantido como alternativa documentada, mas seu desempenho é claramente pior
que o RF de retorno.

## 7. ACF residual e Ljung–Box

| Lag | Estatística | p-valor | Rejeita ruído branco a 5% |
|---:|---:|---:|---|
| 1 | 0,8220 | 0,364583 | Não |
| 4 | 16,5438 | 0,002370 | Sim |
| 13 | 36,8079 | 0,000444 | Sim |
| 26 | 52,1312 | 0,001735 | Sim |

Há autocorrelação residual conjunta a partir do lag 4. O modelo ainda deixa
dependência temporal sem explicar.

## 8. Itens concluídos

- [x] Revisão da documentação e do dicionário externo.
- [x] Limpeza e preparação semanal.
- [x] Gráficos exploratórios.
- [x] STL e força da sazonalidade.
- [x] Random Forest e otimização por `for`.
- [x] Importância das features entre reajustes.
- [x] Registro de parâmetros, versões, hash e tempos.
- [x] MAE e métricas complementares.
- [x] Resíduos individuais, ACF e Ljung–Box.

## 9. Limitações

- Confirmar unidade, moeda, fornecedor, licença e data de obtenção do preço.
- Confirmar fonte, convenção e horário de disponibilidade das duas taxas.
- O preenchimento de semanas vazias cria retornos zero nas features históricas;
  esses estados são identificados por indicadores de cobertura, mas não entram
  como alvos de ajuste nem na métrica principal.
- SARIMAX, Holt-Winters e o modelo de especialização devem usar exatamente as
  mesmas origens, horizonte e teste para comparação final.
