# Dicionário de variáveis externas — Base 2 (tráfego I-94)

## Escopo

O alvo é `traffic_volume` em frequência horária e o horizonte é `t+1`. Clima e feriados vêm no mesmo arquivo da série e são covariáveis internas; atributos de calendário são derivados. Sem uma previsão meteorológica externa emitida antes da origem, o estado climático da própria hora só pode representar `t`, nunca `t+1`.

| ID | Variável | Origem e unidade | Disponibilidade na origem `t` | Uso permitido | Tratamento | Status e risco |
|---|---|---|---|---|---|---|
| G2_HOLIDAY | `holiday` / `is_holiday` | UCI; categoria | Calendário da hora-alvo conhecido antecipadamente | Indicador `is_holiday_alvo` | Preservar `None` como “sem feriado”; não interpretar como ausente | Aprovada |
| G2_TEMP | `temp` | UCI; Kelvin | Observada na hora `t` | `temp_t` ou lags; previsão de `t+1` somente com fonte meteorológica própria | Escalonar apenas no treino | Em validação |
| G2_RAIN | `rain_1h` | UCI; mm | Acumulado observado na hora `t` | `rain_1h_t` ou lags | Zero é válido; considerar `log1p` | Em validação |
| G2_SNOW | `snow_1h` | UCI; mm | Acumulado observado na hora `t` | `snow_1h_t` ou lags | Zero é válido; considerar indicador e lags | Em validação |
| G2_CLOUDS | `clouds_all` | UCI; percentual | Observada na hora `t` | `clouds_all_t` ou lags | Validar faixa de 0 a 100 | Em validação |
| G2_WEATHER_MAIN | `weather_main` | UCI; categoria | Observada durante/após a hora `t` | Somente com lag ou previsão externa | Moda determinística na consolidação; codificação ajustada no treino | Excluída do quadro atual para reduzir risco temporal |
| G2_WEATHER_DESC | `weather_description` | UCI; categoria | Observada durante/após a hora `t` | Somente com lag ou previsão externa | Moda determinística; avaliar cardinalidade | Excluída do quadro atual |
| G2_CALENDAR | Hora, dia da semana e mês | Derivada de `date_time` | Conhecida antecipadamente | Codificação cíclica da hora-alvo | Seno/cosseno sem ajuste com o teste | Aprovada |

## Consolidação dos timestamps repetidos

Antes de criar a grade horária, os registros com o mesmo `date_time` são consolidados de forma determinística:

- média para `temp`, `rain_1h`, `snow_1h`, `clouds_all` e `traffic_volume`;
- moda para `holiday`, `weather_main` e `weather_description`;
- em empate de moda, escolha lexicográfica para tornar a execução reproduzível;
- criação posterior da grade horária completa;
- manutenção de `traffic_volume` ausente nas 11.976 horas sem observação, sem imputação;
- divisão 80%/20% somente sobre as 40.575 horas com alvo observado.

## Regras temporais

- A semente comum do projeto é 42 e a série nunca é embaralhada.
- Lags e janelas móveis terminam antes da hora-alvo.
- Transformações são ajustadas exclusivamente no treino de cada dobra.
- Horário local e transições de horário de verão continuam sendo uma limitação documentada.

## Rastreabilidade

- Fonte: https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume
- Licença: CC BY 4.0; DOI 10.24432/C5X60B.
- Arquivo congelado: `data/base_02/raw.csv`
- SHA-256: `749c90d720360a4215bb15345526073c079ba4cc95e3fa558796d083f85fce9e`
- Arquivos relacionados: `documentacao.md`, `disponibilidade_covariaveis_base2.csv` e `catalogo_features_base2.csv`.
