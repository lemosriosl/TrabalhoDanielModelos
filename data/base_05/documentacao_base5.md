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

Os notebooks comparáveis de Holt-Winters, Random Forest de retorno, XGBoost e
SARIMAX compartilham a preparação de `src/series_temporais/data/preparacao_base5.py`.
O RF direto no preço usa a mesma grade, mas é explicitamente auxiliar. Todos
preservam o CSV e executam por código:

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

O conjunto modelável possui 2.344 origens. Depois do corte cronológico, a grade
contém 1.758 linhas de treino e 586 origens de teste, de 2003-01-17 a
2014-04-04. Todas as 1.758 linhas entram no tuning e no ajuste dos quatro
modelos comparáveis. As 49 features incluem estado
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
levou 16,13 segundos nesta execução. O walk-forward manteve os parâmetros
fixos e reajustou em cada uma das 586 origens, levando 533,99 segundos.

Para o RF direto no preço, a busca selecionou `n_estimators=250`,
`max_depth=6`, `min_samples_split=10`, `min_samples_leaf=3` e
`max_features=0,7`. Seus 586 reajustes levaram 669,41 segundos.

O notebook agora registra também a importância nativa média e sua variação
entre os 586 reajustes. As primeiras posições incluem retorno corrente,
volatilidade e dispersão históricas, lags de retorno e defasagens da Fed Funds,
permitindo separar contribuição autorregressiva, de risco e das taxas externas.

## 6. Métricas fora da amostra

| Modelo | MAE retorno | RMSE retorno | MedAE retorno | R² | Acurácia direcional | MAE preço |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0,020517 | 0,028857 | 0,015934 | -0,0362 | 0,4676 | 19,3924 |
| Retorno zero / persistência | 0,020101 | 0,028434 | 0,016044 | -0,0061 | 0,1092* | 18,9520 |

`*` A previsão zero só acerta o sinal quando o retorno observado também é
zero e não mede capacidade de prever alta ou queda.

O Random Forest de retorno não superou a persistência: o skill principal de
MAE de retorno foi -2,07%. A avaliação principal usa as 586 origens da grade
completa. O recorte de 523 origens cuja semana-alvo possui cotação nova é
mantido apenas como análise de robustez.

No recorte de robustez com cotação tanto na origem quanto no alvo, são 469
observações: o MAE de preço foi 20,3699 no RF e 20,1714 na persistência. Na
grade completa principal, os valores foram 19,3924 e 18,9520, respectivamente.

O RF direto no preço também foi reajustado apenas com alvos observados e teve
MAE de preço 29,1180 nas 523 observações, contra 21,2349 da persistência. Ele é
mantido como benchmark auxiliar e não participa da comparação final.

Holt-Winters, RF-retorno, XGBoost e SARIMAX foram reexecutados com o alvo
`target_log_return_t_plus_1`, a grade `W-FRI`, o corte 75/25 e as mesmas 586
origens. Cada notebook valida em tempo de execução que origem, instante-alvo e
valor real coincidem com o quadro canônico. O RF-preço conserva as mesmas
origens apenas para análise de sensibilidade.

## 7. ACF residual e Ljung–Box

| Lag | Estatística | p-valor | Rejeita ruído branco a 5% |
|---:|---:|---:|---|
| 1 | 0,8950 | 0,344135 | Não |
| 4 | 19,2371 | 0,000706 | Sim |
| 13 | 38,7564 | 0,000219 | Sim |
| 26 | 55,6902 | 0,000619 | Sim |

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
- O preenchimento de semanas vazias cria retornos zero. Esses estados são
  identificados por indicadores de cobertura e permanecem no protocolo
  principal para que os quatro modelos usem exatamente a mesma grade.
- A execução registrada de XGBoost e SARIMAX usa modo reduzido de busca para
  validação do fluxo; a busca completa permanece configurada nos notebooks e
  deve ser usada para os números definitivos da entrega.
