# Base 2 — Metro Interstate Traffic Volume

## Identificação

| Item | Registro |
|---|---|
| Responsável | P1 — Matheus Bastos Castilho |
| Fonte | [UCI Machine Learning Repository — Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) |
| Autoria/citação | Hogue, J. (2019), DOI: 10.24432/C5X60B |
| Licença | CC BY 4.0 |
| Data desta auditoria | 2026-09-21 |
| Arquivo congelado | `data/base_02/raw.csv` |
| SHA-256 | `749c90d720360a4215bb15345526073c079ba4cc95e3fa558796d083f85fce9e` |
| Cobertura no arquivo | 2012-10-02 09:00 a 2018-09-30 23:00 |
| Observações | 48.204 |
| Granularidade pretendida | Horária (1 hora) |
| Coluna temporal | `date_time` |
| Variável-alvo | `traffic_volume` |
| Unidade do alvo | Contagem de veículos no sentido oeste da I-94, estação ATR 301 |
| Divisão solicitada | 80% treino / 20% teste, preservando a ordem temporal |
| `random_state` | 42, semente comum do projeto; não embaralhar a série |

O conjunto descreve o tráfego horário na I-94, entre Minneapolis e Saint Paul (Minnesota, EUA), acrescido de condições meteorológicas e feriados. A UCI o classifica como série temporal multivariada e informa horário local CST.

## Dicionário das variáveis da base

| Coluna | Tipo | Unidade | Descrição | Disponibilidade para prever `traffic_volume` |
|---|---|---|---|---|
| `holiday` | categórica | — | Feriado nacional dos EUA ou `State Fair`. O texto `None` significa ausência de feriado, não valor faltante. | Conhecido antecipadamente por calendário. |
| `temp` | numérica contínua | Kelvin | Temperatura média da hora. | Observada durante/após a hora; usar lag ou previsão meteorológica disponível na origem. |
| `rain_1h` | numérica contínua | mm | Chuva ocorrida na hora. | Observada após a hora; usar lag ou previsão meteorológica. |
| `snow_1h` | numérica contínua | mm | Neve ocorrida na hora. | Observada após a hora; usar lag ou previsão meteorológica. |
| `clouds_all` | inteiro | % | Cobertura de nuvens. | Observada durante/após a hora; usar lag ou previsão meteorológica. |
| `weather_main` | categórica | — | Descrição curta do clima. | Observada durante/após a hora; usar lag ou previsão meteorológica. |
| `weather_description` | categórica | — | Descrição detalhada do clima. | Observada durante/após a hora; usar lag ou previsão meteorológica. |
| `date_time` | data/hora | CST local segundo UCI | Hora da observação. | Chave temporal; permite atributos de calendário conhecidos antecipadamente. |
| `traffic_volume` | inteiro | veículos/hora | Volume reportado pela estação ATR 301 no sentido oeste. | **Alvo** da previsão. |

## Qualidade e preparação

| Verificação | Resultado | Decisão proposta para a base processada |
|---|---|---|
| Valores ausentes | Nenhum nas colunas numéricas e de clima. Ao ler CSV com a configuração padrão, 48.143 valores textuais `None` em `holiday` podem ser convertidos indevidamente em nulos. | Ler com `keep_default_na=False` ou preencher nulos dessa coluna com `None` após validar o significado. |
| Linhas idênticas | 17. | Preservar no CSV bruto; a consolidação por timestamp absorve essas repetições sem alterar o arquivo congelado. |
| Horários repetidos | 5.445 horários possuem mais de um registro (máximo de 6); há 40.575 horários únicos. | Consolidar por `date_time`: média para as colunas numéricas e moda determinística com desempate lexicográfico para as categóricas. |
| Regularidade | 10.217 intervalos consecutivos não são de 1 hora na sequência ordenada; a grade completa contém 52.551 horas e 11.976 lacunas de alvo. | Construir a grade horária após a consolidação; manter `traffic_volume` ausente e excluir somente as linhas sem alvo dos recortes de modelagem. |
| Ordenação | Crescente. | Preservar a ordenação temporal. |
| Atípicos do alvo | 0 observações fora de 1,5 IQR (`-4.417` a `10.543` veículos/hora); mínimo 0, máximo 7.280. | Não remover automaticamente; zero pode representar condição real ou requerer investigação contextual. |

## Disponibilidade temporal e prevenção de vazamento

Feriados e atributos derivados de `date_time` (hora, dia da semana, mês) são conhecidos antes da previsão. As variáveis meteorológicas observadas e categorias de tempo não podem ser usadas no mesmo horário do alvo sem uma previsão meteorológica emitida antes da origem. No cenário sem fonte de previsão, usar apenas lags delas. Ajustar fuso horário e horário de verão antes de combinar dados externos; a descrição da UCI chama o horário de CST local.

## Horizonte e sazonalidade

- Horizonte definido: uma hora à frente (`t+1`), conforme `projeto.yaml` e `metadata.yaml`.
- STL reexecutado em 2026-10-03: força sazonal diária (24 horas) `0,8080` e semanal (168 horas) `0,9717`; forças de tendência `0,1037` e `0,0386`, respectivamente. As duas sazonalidades são relevantes, com predominância do ciclo semanal.
- A divisão cronológica é 80% treino e 20% teste sobre as 40.575 horas observadas, sem embaralhamento.
- A semente comum do projeto é 42.

O dicionário de covariáveis e sua disponibilidade temporal está em `data/base_02/dicionario_variaveis_externas_base2.md`.

## Referências

- Hogue, J. (2019). *Metro Interstate Traffic Volume* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5X60B
- UCI Machine Learning Repository. Licença CC BY 4.0. Consulta em 2026-09-21.
