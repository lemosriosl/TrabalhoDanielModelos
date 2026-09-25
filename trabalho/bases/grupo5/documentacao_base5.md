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
fronteira são usadas 1.757 linhas de treino e 586 de teste, de 2003-01-17 a
2014-04-04. As 49 features incluem estado atual, cobertura, taxas, variações,
lags, janelas defasadas e calendário cíclico. Datas-alvo, preço futuro e todas
as derivações entregues no CSV ficam fora de `X`.

A busca revisada usa `for` explícito, três dobras temporais com purga e nove
configurações planejadas para investigar todos os hiperparâmetros exigidos:

- `n_estimators`: 100 ou 250;
- `max_depth`: 6, 12 ou ilimitada;
- `min_samples_split`: 2, 5 ou 10;
- `min_samples_leaf`: 1, 2 ou 3;
- `max_features`: `sqrt` ou 0,7.

Melhores parâmetros: `n_estimators=250`, `max_depth=6`,
`min_samples_split=2`, `min_samples_leaf=3` e `max_features='sqrt'`. A busca
levou 24,44 segundos nesta execução.
O walk-forward manteve os parâmetros fixos, reajustou a cada 26 semanas em 23
blocos e levou 22,78 segundos nesta execução.

O notebook agora registra também a importância nativa média e sua variação
entre os 23 reajustes. As primeiras posições incluem retorno corrente,
volatilidade e dispersão históricas, lags de retorno e defasagens da Fed Funds,
permitindo separar contribuição autorregressiva, de risco e das taxas externas.

## 6. Métricas fora da amostra

| Modelo | MAE retorno | RMSE retorno | MedAE retorno | R² | Acurácia direcional | MAE preço |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0,021467 | 0,029660 | 0,016777 | -0,0947 | 0,4625 | 20,0356 |
| Retorno zero / persistência | 0,020101 | 0,028434 | 0,016044 | -0,0061 | 0,1092* | 18,9520 |

`*` A previsão zero só acerta o sinal quando o retorno observado também é
zero; o valor é elevado pelas semanas sem nova cotação e não mede capacidade
de prever alta ou queda.

O Random Forest não superou a persistência. O notebook mantém as 586 previsões
e resíduos individuais, com datas, valores reais, previstos, erros absolutos e
quadráticos.

Como análise de sensibilidade, o notebook separa as 523 origens cuja semana-alvo
possui nova cotação. Nesse recorte, o MAE de preço foi 21,9011 no Random Forest
e 21,2349 na persistência; portanto, a conclusão de que o RF não supera o
baseline não decorre apenas das semanas com preço carregado.

## 7. ACF residual e Ljung–Box

| Lag | Estatística | p-valor | Rejeita ruído branco a 5% |
|---:|---:|---:|---|
| 1 | 1,6266 | 0,202175 | Não |
| 4 | 11,1770 | 0,024645 | Sim |
| 13 | 31,1506 | 0,003205 | Sim |
| 26 | 54,6488 | 0,000840 | Sim |

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
- O preenchimento de semanas vazias cria retornos zero e deve ser considerado
  na interpretação das métricas.
- SARIMAX, Holt-Winters e o modelo de especialização devem usar exatamente as
  mesmas origens, horizonte e teste para comparação final.
