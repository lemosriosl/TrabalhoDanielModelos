# Dicionário de variáveis externas — Base 2 (Tráfego na I-94)

Responsável: P1 — Matheus Bastos Castilho. Data da auditoria: 2026-09-21.

**Alvo:** `traffic_volume`, veículos/hora no sentido oeste da I-94, estação ATR 301. Fonte: [UCI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume), John Hogue (2019), CC BY 4.0. Chave: `date_time`, horário local CST segundo a UCI.

Uma variável só pode prever `t+h` se estiver disponível na origem `t`; valor observado no futuro é vazamento.

| ID | Variável | Disponibilidade em `t` | Chave/tratamento | Hipótese e risco | Status |
|---|---|---|---|---|---|
| G2_HOLIDAY | `holiday` | Conhecido antecipadamente. | `date_time`; preservar `None` como não-feriado; one-hot ajustado no treino. | Feriados e State Fair podem mudar a demanda. | Aprovado para qualidade |
| G2_TEMP | `temp` (K) | Observada durante/após a hora; usar previsão meteorológica ou lag. | `date_time`; padronizar somente no treino. | Temperatura pode alterar deslocamentos; valor contemporâneo observado causa vazamento. | Em validação |
| G2_RAIN | `rain_1h` (mm) | Observada após a hora; usar previsão ou lag. | `date_time`; manter zero válido; `log1p`/lags se justificado. | Precipitação pode reduzir/deslocar fluxo; risco de vazamento contemporâneo. | Em validação |
| G2_SNOW | `snow_1h` (mm) | Observada após a hora; usar previsão ou lag. | `date_time`; manter zero válido; indicador de ocorrência e lags. | Neve pode impactar mobilidade; risco de vazamento contemporâneo. | Em validação |
| G2_CLOUDS | `clouds_all` (%) | Observada durante/após a hora; usar previsão ou lag. | `date_time`; limitar a 0–100. | Proxy de condições meteorológicas. | Proposto |
| G2_WEATHER_MAIN | `weather_main` | Observada durante/após a hora; usar previsão ou lag. | `date_time`; one-hot ajustado no treino. | Tipo de clima pode diferenciar condições de tráfego. | Proposto |
| G2_WEATHER_DESC | `weather_description` | Observada durante/após a hora; usar previsão ou lag. | `date_time`; avaliar alta cardinalidade e redundância com `weather_main`. | Pode captar severidade, mas traz risco de sobreajuste. | Proposto |
| G2_CALENDAR | Hora, dia da semana e mês | Conhecidos antecipadamente. | Derivados de `date_time`; codificação cíclica e ajuste de fuso/DST. | Capturam ciclos diário e semanal. | Aprovado para qualidade |

Os 5.445 horários repetidos do CSV devem ser resolvidos em uma base processada, com regra versionada, antes de junções e modelagem. Sem uma previsão meteorológica disponível na origem, as covariáveis de clima só podem ser usadas defasadas.
