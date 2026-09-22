# Dicionário de variáveis externas — Base 3 (Qualidade do ar em Pequim, estação Aotizhongxin)

Responsável: P2 — Pedro Henrique Gomes Frossard. Data da auditoria: 2026-09-22.

**Alvo:** `PM2.5` horário (µg/m³), estação Aotizhongxin. Fonte: [UCI — Beijing Multi-Site Air-Quality Data](https://archive.ics.uci.edu/dataset/501/beijingmultisiteairqualitydata), Chen (2017), DOI 10.24432/C5RK5G, CC BY 4.0. Chave: `year`/`month`/`day`/`hour` combinados em `datetime`.

Esta versão substitui o dicionário anterior da Base 3, que havia sido feito sobre um par de arquivos financeiros (`data.csv`/`test.csv`) por engano de proveniência; o grupo confirmou que a base correta é esta, de qualidade do ar.

Uma variável só pode prever `t+h` se estiver disponível na origem `t`; valor observado no futuro é vazamento. Todas as variáveis abaixo são medidas no mesmo instante que `PM2.5`, então nenhuma pode ser usada contemporânea ao próprio `t` que está sendo previsto — apenas defasadas, ou substituídas por previsão meteorológica disponível na origem.

| ID | Variável | Disponibilidade em `t` | Chave/tratamento | Hipótese e risco | Status |
|---|---|---|---|---|---|
| G3_PM10 | `PM10` (µg/m³) | Simultânea a `PM2.5`; só serve como preditora se defasada. | `datetime`; imputar/tratar os 718 nulos; `lag(1)` ou anterior. | Partícula grossa fortemente correlacionada com PM2.5 (mesma origem de poluição); alto risco de quase-duplicação/vazamento se usada contemporânea. | Em validação |
| G3_SO2 | `SO2` (µg/m³) | Simultânea a `PM2.5`. | `datetime`; tratar os 935 nulos; lag. | Poluente de origem industrial/combustão; pode ajudar a explicar picos, mas covaria com outros poluentes. | Em validação |
| G3_NO2 | `NO2` (µg/m³) | Simultânea a `PM2.5`. | `datetime`; tratar os 1.023 nulos; lag. | Associado a tráfego/combustão; covaria com PM2.5 e CO. | Em validação |
| G3_CO | `CO` (µg/m³) | Simultânea a `PM2.5`. | `datetime`; tratar os 1.776 nulos; lag; avaliar escala (valores até 10.000). | Indicador de combustão incompleta; forte colinearidade esperada com outros poluentes. | Em validação |
| G3_O3 | `O3` (µg/m³) | Simultânea a `PM2.5`. | `datetime`; tratar os 1.719 nulos; lag. | Ozônio tem dinâmica distinta (formação fotoquímica), pode se comportar de forma inversa aos demais poluentes em alguns períodos. | Em validação |
| G3_TEMP | `TEMP` (°C) | Simultânea a `PM2.5`. | `datetime`; tratar os 20 nulos; lag ou previsão meteorológica disponível na origem. | Temperatura afeta dispersão/formação de poluentes e demanda por aquecimento; risco de vazamento se contemporânea. | Em validação |
| G3_PRES | `PRES` (hPa) | Simultânea a `PM2.5`. | `datetime`; tratar os 20 nulos; lag. | Pressão associada a estagnação atmosférica, que favorece acúmulo de poluição. | Em validação |
| G3_DEWP | `DEWP` (°C) | Simultânea a `PM2.5`. | `datetime`; tratar os 20 nulos; lag. | Ponto de orvalho covaria com temperatura e umidade; redundância a controlar com `TEMP`. | Em validação |
| G3_RAIN | `RAIN` (mm) | Simultânea a `PM2.5`. | `datetime`; manter zero como valor válido; tratar os 20 nulos; lag. | Chuva tende a reduzir concentração de particulados (efeito de lavagem atmosférica); risco de vazamento contemporâneo. | Em validação |
| G3_WSPM | `WSPM` (m/s) | Simultânea a `PM2.5`. | `datetime`; tratar os 14 nulos; lag. | Vento mais forte dispersa poluentes; hipótese de relação inversa com PM2.5. | Em validação |
| G3_WD | `wd` (direção do vento, 16 pontos) | Simultânea a `PM2.5`. | `datetime`; tratar os 81 nulos; codificar como variável circular (seno/cosseno) ou one-hot, não como categoria ordinal. | Direção do vento pode indicar transporte de poluição de regiões industriais vizinhas; tratamento incorreto como escala linear distorce a variável. | Proposto |
| G3_CALENDAR | Hora, dia da semana, mês e estação do ano | Conhecidos antecipadamente. | Derivados de `datetime`; codificação cíclica. | Pode capturar o ciclo diário de tráfego/aquecimento e a sazonalidade anual (invernos mais poluídos); ganho deve ser validado fora da amostra. | Proposto |

`station` não entra como variável externa: é constante (`Aotizhongxin`) neste arquivo e só teria variação se outras estações do conjunto completo (420.768 linhas, 12 estações) fossem combinadas — o que está fora do escopo desta base conforme definido pelo grupo.