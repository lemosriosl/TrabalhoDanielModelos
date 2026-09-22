# Base 5 — preços diários do ouro

## 1. Identificação da base

| Campo | Descrição |
|---|---|
| Nome no projeto | Base 5 — preços diários do ouro |
| Arquivo auditado | `trabalho/bases/grupo5/grupo5_new.csv` |
| Versão anterior | `grupo5_old.csv`; mesmas datas e preços, sem as duas colunas adicionais |
| Fonte histórica indicada na documentação anterior | [gold.daily.prices.csv](https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv); confirmar proveniência primária e licença |
| Tipo de dado | Série temporal de preço com indicador de feriado e rótulo de direção fornecidos |
| Frequência do arquivo | Uma linha por dia de segunda a sexta; cotações observadas são irregulares por ausências |
| Período observado | 1968-04-01 a 2014-04-10 |
| Quantidade | 12.009 linhas e 4 colunas |
| Delimitador | Ponto e vírgula (`;`) |
| SHA-256 | `8446b3f07b6834625e9e82b58955ea8ef906d67c23d34ee05440602349e02947` |

O CSV não informa moeda, unidade do preço, fornecedor, calendário usado em `IS_HOLIDAY` nem processo de criação de `TARGET_UP`. A data de obtenção original desses dados também não está registrada no arquivo. Esses itens precisam de confirmação antes da entrega final. Os números abaixo são da auditoria local do arquivo fornecido.

## 2. Dicionário das variáveis

| Variável | Tipo | Unidade / significado verificável | Papel e cuidado |
|---|---|---|---|
| `DATE` | Data `YYYY-MM-DD` | Dia da linha | Chave temporal; validar ordem e unicidade. |
| `VALUE` | Número decimal ou vazio | Valor de preço na unidade de origem, ainda não confirmada | Série de interesse; vazio é cotação ausente, não zero. |
| `IS_HOLIDAY` | 0/1 | Marcador de feriado segundo calendário não documentado | Variável fornecida para auditoria; disponibilidade e calendário precisam de confirmação antes de entrar no modelo. |
| `TARGET_UP` | 0/1 | `1` se `VALUE` da próxima **linha** é maior que `VALUE` atual; `0` nos demais casos, inclusive pares com nulo | Rótulo futuro, nunca feature. Não corresponde necessariamente à direção até a próxima cotação observada. |

Para a comparação de modelos do trabalho, o alvo definitivo ainda depende de decisão registrada em `config/projeto.yaml`. O notebook atual usa **retorno logarítmico até a próxima cotação observada** como alvo exploratório e também prepara preço futuro; isso não aprova, por si só, o horizonte do experimento final.

## 3. Qualidade dos dados

| Verificação | Resultado |
|---|---:|
| Datas nulas / duplicadas | 0 / 0 |
| Datas fora de ordem | 0 |
| Valores de `VALUE` ausentes | 368 de 12.009 (3,06%) |
| Cotações observadas | 11.641 |
| Preços observados não positivos | 0 |
| `IS_HOLIDAY = 1` | 297 |
| `IS_HOLIDAY = 1` com preço observado | 180 |
| `IS_HOLIDAY = 0` com preço ausente | 251 |
| `TARGET_UP = 1` | 5.629 |

O calendário de linhas é regular de segunda a sexta: 9.607 intervalos de 1 dia e 2.401 de 3 dias entre linhas consecutivas. Entre **preços observados**, a distância chega a 6 dias, por causa de cotações ausentes. O indicador `IS_HOLIDAY` não é uma máscara de valores ausentes.

Estatísticas de `VALUE`, excluindo os 368 nulos:

| Medida | Valor |
|---|---:|
| Média | 446,1900 |
| Mediana | 363,7500 |
| Desvio padrão | 382,4057 |
| Mínimo | 34,7750 |
| Máximo | 1.896,5000 |

A regra observada de `TARGET_UP` foi conferida nas 12.009 linhas: `VALUE.shift(-1) > VALUE` reproduz todos os rótulos. Isso descreve o arquivo, sem confirmar por que a coluna foi criada. Um `0` com preço ausente não deve ser interpretado como queda.

## 4. Preparação recomendada

1. Ler `grupo5_new.csv` com `sep=';'`; registrar caminho relativo, hash e versão. Não substituir automaticamente pelo CSV antigo ou por download remoto.
2. Converter `DATE` para data e `VALUE` para número; validar ordenação, duplicidade, valores inválidos e domínio 0/1 dos indicadores.
3. Preservar as linhas com `VALUE` ausente para auditoria. Não preencher com zero, interpolação que use o futuro ou calendário presumido.
4. Para a preparação exploratória do notebook, manter só preços observados e registrar `target_date` e `target_gap_days`, pois o próximo preço observado pode não estar na linha seguinte.
5. Derivar preço e retorno futuros apenas para `y`; retirar `TARGET_UP`, `target_date`, `target_gap_days` e qualquer outro alvo de `X`. Não usar `IS_HOLIDAY` como feature enquanto sua proveniência e disponibilidade forem desconhecidas.
6. Calcular lags e janelas móveis apenas com o histórico disponível na origem. Ajustar imputação, escala e seleção de features somente no trecho de treino de cada dobra.
7. Definir horizonte, origens, período de teste e frequência comparáveis para SARIMAX, Holt-Winters, Random Forest e modelo de especialização antes da avaliação final. Registrar essa decisão em `config/projeto.yaml` e, se estrutural, em `docs/adr/`.

## 5. Análise exploratória esperada

- Série de preços e distribuição dos valores observados.
- Retornos logarítmicos entre cotações e sua distribuição.
- Volatilidade móvel calculada sobre retornos, com janela e defasagem explícitas.
- Contagem de ausências por período, lacunas entre cotações e cruzamento de `IS_HOLIDAY` com `VALUE` ausente.
- Resumo anual e inspeção de períodos extremos sem inferir causalidade.
- ACF e STL somente depois de decidir como representar a frequência e as ausências; o período sazonal não pode ser presumido do calendário de linhas.

O notebook `eda_preparacao_base_5_ouro.ipynb` cobre a auditoria, os gráficos iniciais e a preparação exploratória. Seu corte cronológico 80%/20% **não é o protocolo final** enquanto os campos correspondentes do projeto estiverem pendentes.

## 6. Implicações para Holt-Winters

Holt-Winters usa a série-alvo univariada; `IS_HOLIDAY` e outras exógenas não entram diretamente nesse modelo. Antes de ajustar o modelo, é preciso definir a série temporal efetivamente usada, a regra de tratamento das 368 ausências e um período sazonal coerente com a frequência aprovada. Tendência e sazonalidade aditiva podem ser avaliadas por walk-forward; uma componente multiplicativa só deve ser considerada se fizer sentido empírico e técnico para o alvo positivo escolhido. Os quatro modelos devem compartilhar origens, horizonte e teste.

## 7. Riscos e limitações

- A unidade, moeda, fornecedor e fonte primária do preço não estão comprovados no CSV.
- O calendário de `IS_HOLIDAY` é desconhecido; há preços em dias marcados e ausências em dias não marcados.
- `TARGET_UP` consulta a próxima linha e transforma pares com preço ausente em `0`. Usá-lo como feature causa vazamento; usá-lo como rótulo sem filtrar pares válidos mistura ausência com movimento de preço.
- O alvo de próxima cotação observada tem intervalo variável de 1 a 6 dias neste arquivo; não equivale automaticamente a horizonte de um dia civil.
- O arquivo termina em 2014 e não representa condições atuais de mercado.
- Escala global, interpolação futura e ajuste de hiperparâmetros sobre o teste invalidam a avaliação.

## 8. Checklist antes da entrega

- [ ] Confirmar proveniência primária, licença, data de acesso, unidade e moeda de `VALUE`.
- [ ] Confirmar calendário e disponibilidade temporal de `IS_HOLIDAY`.
- [ ] Decidir se `TARGET_UP` tem algum uso válido; documentar a regra para pares ausentes.
- [ ] Aprovar alvo, frequência, horizonte, origens, teste final e período sazonal no projeto.
- [ ] Selecionar e obter ao menos duas variáveis externas com fontes e datas de disponibilidade verificáveis, se exigidas no experimento.
- [ ] Produzir ACF/STL com tratamento de ausências documentado.
- [ ] Avaliar os quatro modelos em walk-forward e registrar parâmetros, previsões, resíduos, MAE e tempo.
