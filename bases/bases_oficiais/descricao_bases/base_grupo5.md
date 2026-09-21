# Base 5 — Preços diários do ouro: detalhamento técnico

## 1. Identificação da base

| Campo | Descrição |
|---|---|
| Nome de trabalho | Preços diários do ouro |
| Arquivo | `gold.daily.prices.csv` |
| Repositório de acesso | [dengyishuo/quantitative-finance](https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv) |
| Tipo de dado | Série temporal financeira univariada |
| Frequência observada | Diária de calendário de mercado; não há cotação em parte dos fins de semana e feriados |
| Período observado no arquivo referenciado | 1968-04-01 a 2014-04-10 |
| Tamanho aproximado | 12.010 linhas, incluindo cabeçalho |
| Colunas | `DATE` e `VALUE` |
| Configuração experimental | 80% treino / 20% teste, corte cronológico; `random_state = 42` apenas em etapas estocásticas auxiliares |

## 2. O que a base representa

A base registra uma única cotação diária do ouro ao longo de aproximadamente 46 anos. Cada linha representa uma data e seu respectivo valor de preço. O arquivo é útil como uma série histórica financeira longa, com ciclos econômicos distintos, períodos de alta e baixa volatilidade e mudanças estruturais relevantes.

Ela é uma base **univariada**: não oferece, no arquivo original, variáveis macroeconômicas, volume, abertura/máxima/mínima/fechamento nem metadados que expliquem diretamente cada variação diária. Por isso, serve bem para estabelecer um *benchmark* de previsão a partir do próprio histórico de preços, mas requer fontes adicionais se o objetivo for atribuir causalidade ou construir uma previsão multivariada.

> A coluna `VALUE` não traz unidade, moeda nem fornecedor explicitamente documentados dentro do arquivo. Embora os valores sejam compatíveis com uma cotação de ouro em dólar por onça troy, essa unidade não deve ser assumida como fato no relatório até que a proveniência original seja confirmada. Trate-a inicialmente como **índice/valor de preço na unidade de origem**.

## 3. Estrutura e dicionário mínimo

| Variável original | Tipo esperado | Papel | Descrição | Problemas / tratamento inicial |
|---|---|---|---|---|
| `DATE` | data (`YYYY-MM-DD`) | Índice temporal | Dia da observação | Converter para `datetime`, ordenar crescente, verificar duplicidade e continuidade entre dias úteis. |
| `VALUE` | numérico contínuo | Série-alvo bruta | Cotação/valor diário do ouro | Converter `.` para ausente (`NaN`) antes de transformar o tipo. Confirmar unidade e moeda antes de rotular a variável. |

O arquivo é exibido no GitHub como texto com campos separados por espaços, ainda que tenha extensão `.csv`. A leitura deve aceitar separador por espaços em branco, por exemplo com `sep=r'\s+'`, e preservar `.` como valor ausente. Não assumir vírgula como delimitador.

## 4. Qual pergunta o modelo deve responder?

Antes de modelar, escolher **uma** definição de previsão. Recomenda-se começar pela primeira.

| Opção | Alvo no instante `t` | Uso | Observação |
|---|---|---|---|
| Preço do próximo pregão | `VALUE(t+1)` | Previsão direta de nível | Fácil de comunicar, mas sofre com não estacionaridade. |
| Retorno simples | `VALUE(t+1) / VALUE(t) - 1` | Decisão/direção e análise financeira | Escala comparável no tempo; exige preços válidos consecutivos. |
| Retorno logarítmico | `ln(VALUE(t+1)) - ln(VALUE(t))` | Modelagem estatística | Alternativa preferida se `VALUE > 0`; soma ao longo do tempo. |
| Direção do movimento | `1[VALUE(t+1) > VALUE(t)]` | Classificação | Complementar, não substitui uma métrica de erro do retorno. |

**Recomendação inicial:** usar `retorno_log_1d` como alvo principal de modelagem e manter `VALUE(t+1)` como saída de negócio derivada. A série em nível possui tendência e mudanças de patamar que tornam a avaliação de um modelo aparentemente boa, mas pouco informativa, quando comparada apenas pelo erro absoluto.

## 5. Preparação dos dados

### 5.1 Leitura e validações

1. Carregar o arquivo com separador por espaços e declarar `.` como nulo.
2. Converter `DATE` para data e `VALUE` para número.
3. Ordenar por `DATE` e garantir que cada data apareça no máximo uma vez.
4. Criar um relatório com: primeira/última data, linhas, nulos em `VALUE`, datas repetidas e intervalos entre observações.
5. Não preencher automaticamente fins de semana, feriados ou dias de cotação ausente. Eles não equivalem a preço zero e podem não ser dias de pregão.
6. Para criar retornos, usar somente pares consecutivos com valores observados; documentar a regra adotada para lacunas internas.

### 5.2 Transformações recomendadas

| Campo derivado | Fórmula / regra | Finalidade |
|---|---|---|
| `log_price_t` | `ln(VALUE_t)` | Reduz escala e ajuda a interpretar variações relativas. |
| `return_1d_t` | `ln(VALUE_t) - ln(VALUE_{t-1})` | Alvo ou atributo de curto prazo. |
| `lag_return_k` | `return_1d_(t-k)` | Captura dependência temporal sem vazamento. |
| `ma_k` | média móvel de `VALUE` até `t-1` | Tendência local; nunca incluir `t+1`. |
| `vol_k` | desvio-padrão móvel de retornos até `t-1` | Regime de volatilidade. |
| `dow` / `month` | dia da semana / mês da data | Calendário; usar codificação cíclica quando apropriado. |
| `gap_days` | diferença em dias desde a última observação | Distingue uma lacuna normal de pregão de outra ausência. |

Todos os cálculos móveis e defasagens devem ser obtidos apenas a partir de informações disponíveis em ou antes de `t`. A maneira segura de implementar médias móveis e volatilidade é aplicar `shift(1)` antes da janela móvel.

## 6. Separação temporal e validação

O corte de 80%/20% deve ocorrer **após** a limpeza e a ordenação, sem `shuffle`:

```text
1968-04-01 ──────────────── 80% treino ────────────────|──── 20% teste ──── 2014-04-10
                                                      corte
```

- O período de teste deve ser o trecho final, preservando uma situação de previsão futura.
- Dentro do treino, usar validação expansiva (*walk-forward*): treinar até uma data, validar no bloco seguinte, avançar a janela e repetir.
- Ajustar imputadores, escaladores, seleção de atributos e hiperparâmetros somente no treino de cada dobra.
- `random_state = 42` é pertinente para modelos aleatórios, como *Random Forest* ou *XGBoost*, e para otimização estocástica. Não é pertinente à escolha do corte temporal.

## 7. Modelos e baselines

O valor de um modelo só pode ser demonstrado contra baselines temporais simples.

| Categoria | Sugestão | Papel |
|---|---|---|
| Baseline 1 | Persistência: `previsão(t+1) = VALUE(t)` | Referência obrigatória para previsão de preço. |
| Baseline 2 | Retorno nulo: `previsão do retorno = 0` | Referência obrigatória para retorno. |
| Estatístico | Naïve com *drift*, ARIMA/SARIMAX | Capta autocorrelação e tendência de forma interpretável. |
| Volatilidade | GARCH sobre retornos | Indicado para prever variância/risco, não necessariamente a média do retorno. |
| Machine learning | Regressão regularizada, árvore *boosted* com lags | Usar apenas atributos passados e validação temporal. |
| Multivariado | SARIMAX, regressão ou *boosting* com variáveis externas | Só após montar o dicionário e garantir disponibilidade temporal das fontes. |

## 8. Métricas e critérios de avaliação

| Alvo | Métricas recomendadas | Interpretação |
|---|---|---|
| Preço em nível | MAE, RMSE, MAPE/sMAPE com cautela | Erro na unidade do preço; comparar diretamente ao baseline de persistência. |
| Retorno | MAE, RMSE, correlação de Pearson/Spearman | Mede proximidade das variações; retornos próximos de zero tornam MAPE inadequado. |
| Direção | Acurácia, *balanced accuracy*, matriz de confusão | Usar em conjunto com retorno; uma alta acurácia pode não representar valor econômico. |
| Risco | Erro da volatilidade prevista, cobertura de intervalos | Avalia incerteza e não apenas previsão pontual. |

Além das métricas agregadas, apresentar erros por janelas temporais, especialmente em períodos de forte variação. Reportar intervalo de confiança ou distribuição dos erros quando possível.

## 9. Riscos metodológicos e limitações

- **Proveniência incompleta:** o repositório hospeda o arquivo, mas o próprio arquivo não declara fornecedor, unidade, moeda ou método de formação da cotação. Confirmar esses itens ou registrar formalmente a limitação.
- **Dados antigos:** a série termina em 2014 na versão referenciada, portanto não representa condições recentes do mercado. Não é apropriada para inferir desempenho atual sem uma atualização de fonte.
- **Ausências codificadas como `.`:** não tratá-las como zero; avaliar se são feriados, fins de semana ou falhas de registro.
- **Não estacionaridade e quebras estruturais:** décadas de dados incluem mudanças de regime. Um único modelo global pode ter desempenho desigual entre subperíodos.
- **Risco de vazamento:** a normalização global, a interpolação usando valores futuros e janelas móveis não defasadas tornam a avaliação inválida.
- **Uso financeiro:** desempenho preditivo histórico não é recomendação de investimento. Um experimento que inclua regra de negociação deve considerar custos, *slippage*, liquidez e risco.

## 10. Produtos esperados da análise

1. Arquivo tratado com `DATE`, `VALUE`, marcação de ausência e atributos derivados.
2. Relatório de qualidade e proveniência, incluindo a unidade confirmada ou a limitação correspondente.
3. Visualizações: preço, log-preço, retornos, volatilidade móvel, nulos/lacunas e cortes temporais.
4. Tabela de comparação entre baselines e modelos, avaliada exclusivamente no período de teste final.
5. Conclusão com escopo claro: o que o modelo prevê, para qual horizonte e sob quais limitações.
