# Auditoria das taxas externas — 2026-10-03

## Resultado comprovado

O script de preparação da origem documentada identifica `TREASURY_10Y` como
FRED **DGS10** e `FED_FUNDS_RATE` como FRED **DFF**. Antes de remover linhas
incompletas, ele junta as séries ao calendário original do ouro, aplica
`ffill()` e depois `shift(1)` nas duas taxas.

Referência fixada: commit `885edaab761981eae97f5224dc1740d2310c0214` de
`TheoMGtech/pls-regration-comparation`:

- [Configuração da origem](https://github.com/TheoMGtech/pls-regration-comparation/blob/885edaab761981eae97f5224dc1740d2310c0214/bases/grupo5-tratamento/DATASET_CONFIG.md).
- [Script de preparação](https://github.com/TheoMGtech/pls-regration-comparation/blob/885edaab761981eae97f5224dc1740d2310c0214/bases/grupo5-tratamento/prepare_gold_dataset.py).

Reproduzi essa transformação em memória e comparei, por `DATE`, com o
`data/base_05/raw.csv` congelado:

| Coluna | Linhas comparadas | Coincidências (tolerância 1e-8) | Maior diferença absoluta |
|---|---:|---:|---:|
| TREASURY_10Y | 9.864 | 9.864 | 0 |
| FED_FUNDS_RATE | 9.864 | 9.864 | 0 |

Isso comprova a correspondência dos valores locais com os arquivos versionados
na origem e sua defasagem. Não comprova a data em que alguém baixou os arquivos
do FRED nem a disponibilidade de cada vintage em tempo real.

Hashes SHA-256 dos arquivos de origem usados:

| Arquivo em `bases/grupo5-tratamento/` | SHA-256 |
|---|---|
| gold_daily_prices.csv | 8446b3f07b6834625e9e82b58955ea8ef906d67c23d34ee05440602349e02947 |
| dgs10.csv | 6465b567d87d8fb97ba5ac8d3768c708b159308ffdf689dba5ae5bcd18c68a8a |
| dff.csv | 04a7489a0bf7aed26f63625a5f8eb4be5c635a92b35ac37019ba5b5ea390370c |

Para reproduzir: ler ouro com delimitador detectado; normalizar
`observation_date` das taxas para `DATE`; fazer junções à esquerda pelo
calendário completo do ouro; aplicar `ffill().shift(1)` às taxas; só depois
selecionar as datas presentes no arquivo local e comparar os valores.
Aplicar a defasagem diretamente nas 9.864 linhas filtradas não reproduz a
transformação original.

O download direto dos CSVs do FRED nesta auditoria falhou por conexão encerrada
pelo servidor. A comparação numérica foi com os arquivos versionados da origem,
não com uma nova extração do FRED.

## Definições econômicas verificadas

- [DGS10 no FRED](https://fred.stlouisfed.org/series/DGS10): rendimento de mercado
  do Treasury americano de vencimento constante de dez anos, cotado em base de
  investimento; frequência diária, percentual, sem ajuste sazonal. Fonte
  declarada: Federal Reserve Board, release H.15.
- [DFF no FRED](https://fred.stlouisfed.org/series/DFF): taxa efetiva de federal
  funds, frequência diária (sete dias), percentual, sem ajuste sazonal; fonte
  declarada: Federal Reserve Board, H.15. Não confundir com taxa-alvo do FOMC
  ou média mensal FEDFUNDS.

Percentual significa, por exemplo, 5,71% armazenado como `5.71`, não `0.0571`.

## Disponibilidade temporal: o que permanece pendente

As colunas locais já representam a observação anterior no calendário original
do ouro. Na agregação semanal, usar o último valor datado até a origem e
preencher semanas vazias não remove essa defasagem existente. Não acrescentamos
uma segunda defasagem nem alteramos features ou previsões nesta investigação.

O [New York Fed](https://www.newyorkfed.org/markets/reference-rates/effr)
publica atualmente a taxa efetiva do dia útil anterior por volta das 9h.
Essa regra atual não deve ser aplicada automaticamente a 1968–2014: o
[comunicado de 2016](https://www.newyorkfed.org/markets/opolicy/operating_policy_160106)
documenta mudança de fonte, de média ponderada para mediana ponderada e do
protocolo de publicação a partir de março de 2016, posterior à nossa amostra.

Para homologação completa ainda faltam horários históricos de publicação,
fuso/horário da origem semanal e avaliação de revisões/vintages. O calendário
inclui feriados: uma observação anterior do ouro não é uma garantia universal
de um intervalo de publicação suficiente. Usar somente a data da observação
não comprova disponibilidade em tempo real.

**Conclusão:** fonte, identificação e defasagem estão verificadas; o atraso
intradiário/histórico continua parcialmente documentado. Não há justificativa
para declarar atraso zero nem para afirmar que a auditoria eliminou todo risco
de disponibilidade. A análise sem taxas permanece uma demanda separada.
