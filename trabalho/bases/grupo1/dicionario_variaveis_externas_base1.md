# Dicionário de variáveis externas — Base 1 (Bitcoin)

Responsável: P1 — Matheus Bastos Castilho. Data da auditoria: 2026-09-21.

**Alvo:** `Close` diário, em USD/BTC. Fonte indicada: [Bitget](https://www.bitget.com/price/bitcoin/historical-data), cuja página declara frequência diária e fuso GMT+0. O CSV congelado não traz metadados de extração e inclui `Adj Close`; a proveniência direta pela Bitget deve ser confirmada antes da aprovação final.

Uma variável só pode prever `t+h` se estiver disponível na origem `t`; valor observado no futuro é vazamento.

| ID | Variável | Disponibilidade em `t` | Chave/tratamento | Hipótese e risco | Status |
|---|---|---|---|---|---|
| G1_OPEN | `Open` | Abertura de `t`; confirmar horário exato da fonte. | `Date`; usar apenas se conhecido na origem, ou em lag. | Resume informação pré-abertura; não assumir que prevê o próprio fechamento sem validar o instante. | Em validação |
| G1_HIGH | `High` | Somente após o dia `t`. | `Date`; `lag(1)` ou anterior; amplitude/retorno defasado. | Pode refletir volatilidade; uso no próprio `t` causa vazamento. | Em validação |
| G1_LOW | `Low` | Somente após o dia `t`. | `Date`; `lag(1)` ou anterior; amplitude/retorno defasado. | Pode refletir pressão vendedora; uso no próprio `t` causa vazamento. | Em validação |
| G1_VOLUME | `Volume` | Fim de `t`. | `Date`; `log1p` e lags; escalar somente no treino. | Pode sinalizar liquidez/intensidade; unidade/metodologia do CSV precisam ser confirmadas. | Em validação |
| G1_CALENDAR | Dia da semana e mês | Conhecido antecipadamente. | Derivado de `Date`; codificação cíclica, alinhada a GMT+0 se a fonte Bitget for confirmada. | Pode representar padrões de negociação; ganho deve ser validado fora da amostra. | Proposto |

`Adj Close` não entra como externa: é igual a `Close` nas 2.836 linhas do arquivo e duplicaria o alvo.
