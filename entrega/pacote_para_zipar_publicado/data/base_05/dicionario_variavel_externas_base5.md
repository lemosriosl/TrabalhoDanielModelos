# Dicionário de variáveis externas — Base 5 (ouro semanal)

**Arquivo-alvo:** `data/base_05/raw.csv`

**Série modelada:** último estado conhecido por semana (`W-FRI`)

**Alvo canônico atual:** retorno logarítmico da semana seguinte (`target_log_return_t_plus_1`), conforme a preparação compartilhada incorporada de `origin/main` no commit `248fcb5`.

**Período semanal:** 1968-05-03 a 2014-04-11

## Variáveis externas presentes no arquivo

| ID | Coluna | Interpretação | Disponibilidade adotada | Uso |
|---|---|---|---|---|
| G5_TREASURY_10Y | `TREASURY_10Y` | FRED DGS10; Treasury de vencimento constante de 10 anos, percentual | Já defasada uma observação do calendário original do ouro após ffill; última taxa datada até a origem semanal | Nível atual, variação semanal e lags 1, 4 e 13 |
| G5_FED_FUNDS | `FED_FUNDS_RATE` | FRED DFF; taxa efetiva de federal funds, percentual | Já defasada uma observação do calendário original do ouro após ffill; última taxa datada até a origem semanal | Nível atual, variação semanal e lags 1, 4 e 13 |

A auditoria de 2026-10-03 comprovou fonte identificada, unidade e transformação
por coincidência nas 9.864 linhas com a origem versionada. Horários históricos
de publicação, fuso da origem e revisões/vintages ainda precisam de confirmação.
Evidências e limites estão em [auditoria_taxas_base5.md](auditoria_taxas_base5.md).

## Demais colunas do arquivo

| Grupo | Colunas | Decisão |
|---|---|---|
| Chave temporal | `DATE` | Usada para ordenar, agregar e controlar disponibilidade |
| Série principal | `GOLD_PRICE` | Último valor conhecido na origem; base dos retornos e lags semanais |
| Calendário entregue | `DAY_OF_WEEK`, `MONTH`, `DOW_SIN`, `DOW_COS`, `MONTH_SIN`, `MONTH_COS` | Excluído; calendário semanal é recalculado no notebook |
| Lags diários entregues | `GOLD_LAG_1`, `GOLD_LAG_5`, `GOLD_LAG_20` | Excluídos; não correspondem integralmente aos shifts da tabela atual |
| Janelas entregues | `GOLD_ROLLING_MEAN_5`, `GOLD_ROLLING_STD_5` | Excluídas; reconstruídas em frequência semanal e com defasagem explícita |
| Alvo entregue | `TARGET` | Excluído de `X` e do alvo; coincide com a próxima linha em apenas 95,66% e representa horizonte diário incerto |

## Disponibilidade e junção sem vazamento

1. Para cada origem semanal, usar somente linhas com `DATE` até aquela origem.
2. Em semana vazia, carregar o último valor conhecido e registrar a cobertura.
3. Calcular diferenças, lags e janelas depois da agregação semanal.
4. Ajustar seleção e hiperparâmetros apenas no treino e nas dobras temporais.
5. Nunca usar `TARGET`, datas-alvo ou valores da semana seguinte como feature.
6. Preservar as mesmas origens e features compatíveis no Random Forest e no
   modelo de especialização.

## Variáveis candidatas ainda não incorporadas

| ID | Variável | Regra mínima de disponibilidade | Status |
|---|---|---|---|
| G5_USD_INDEX | Índice amplo do dólar | Último fechamento publicado até a origem | Fonte pendente |
| G5_REAL_RATE | Juro real com vencimento definido | Último valor publicado até a origem | Fonte pendente |
| G5_INFLATION | Índice de inflação definido | Usar somente após a data de divulgação | Fonte pendente |
| G5_VIX | Índice de volatilidade | Último fechamento conhecido na semana | Fonte pendente |
| G5_SP500 | Índice acionário amplo | Último fechamento conhecido na semana | Fonte pendente |
| G5_OIL | Petróleo com contrato e rolagem definidos | Último fechamento conhecido na semana | Fonte pendente |

Para qualquer candidata, registrar fonte, identificador, unidade, moeda, fuso,
licença, data de acesso, checksum e uma coluna `available_from`.
