# Base 1 — Bitcoin (BTC)

## Identificação

| Item | Registro |
|---|---|
| Responsável | P1 — Matheus Bastos Castilho |
| Fonte indicada para a base | [Bitget — Bitcoin historical data](https://www.bitget.com/price/bitcoin/historical-data) |
| Data desta auditoria | 2026-09-21 |
| Arquivo congelado | `trabalho/bases/base_grupo1/grupo1.csv` |
| SHA-256 | `dcb86b9461168a1cc3f122a40d7aa6b53ac773a5703423320a2a90c3823c38f7` |
| Cobertura no arquivo | 2017-01-01 a 2024-10-06 |
| Observações | 2.836 |
| Granularidade | Diária |
| Coluna temporal | `Date` |
| Variável-alvo | `Close` |
| Unidade do alvo | USD por BTC |
| Divisão solicitada | 70% treino / 30% teste, preservando a ordem temporal |
| `random_state` solicitado | 42 (aplicável somente a componentes estocásticos; não embaralhar a série) |

### Nota de rastreabilidade da fonte

A página Bitget informa dados históricos diários de OHLCV em USD, atualizados diariamente e exibidos em GMT+0. O arquivo congelado possui o mesmo conceito de mercado, mas inclui a coluna `Adj Close` e não contém metadados de extração; portanto, sua proveniência direta pela Bitget não pode ser comprovada somente pelo CSV. Antes da entrega final, registrar a data de download e a origem exata do arquivo — ou congelar um CSV exportado da Bitget — sem sobrescrever este artefato.

## Dicionário das variáveis da base

| Coluna | Tipo no arquivo | Unidade | Descrição | Papel e uso temporal |
|---|---|---|---|---|
| `Date` | data | dia | Data de referência do candle diário. | Chave temporal; converter para `datetime` e ordenar em ordem crescente. |
| `Open` | numérico contínuo | USD/BTC | Primeiro preço do dia. | Informação observada no próprio dia; para prever `Close_t`, usar apenas `Open` conhecido no instante de origem ou suas defasagens. |
| `High` | numérico contínuo | USD/BTC | Maior preço negociado no dia. | Observado após o decorrer do dia; usar somente com defasagem para evitar vazamento. |
| `Low` | numérico contínuo | USD/BTC | Menor preço negociado no dia. | Observado após o decorrer do dia; usar somente com defasagem. |
| `Close` | numérico contínuo | USD/BTC | Preço de fechamento diário. | **Alvo** da previsão. |
| `Adj Close` | numérico contínuo | USD/BTC | Fechamento ajustado informado pelo arquivo. | Na versão congelada é idêntico a `Close` em todas as linhas; excluir de features, pois é redundante e equivaleria ao alvo. |
| `Volume` | inteiro | unidade monetária/volume conforme a origem do CSV | Volume diário negociado. | Observado ao fim do dia; para previsão de `t+1`, usar `Volume_t` ou lags, nunca `Volume_{t+1}`. |

## Qualidade e preparação

| Verificação | Resultado | Decisão |
|---|---|---|
| Valores ausentes | Nenhum nas 7 colunas. | Não imputar. |
| Linhas e datas duplicadas | 0. | Manter verificação no pipeline. |
| Ordenação | Crescente. | Preservar a ordenação. |
| Frequência | Todos os intervalos entre datas são de 1 dia. | Definir frequência diária. |
| Atípicos do alvo | 0 pontos fora dos limites de 1,5 IQR (`-38.045,77` a `82.817,06` USD). | Não remover valores por regra estatística; oscilações de preço são parte do fenômeno. |
| Coerência `Close`/`Adj Close` | Iguais em 2.836 de 2.836 linhas. | Remover `Adj Close` somente na base processada/modelagem, não no CSV congelado. |

## Disponibilidade temporal e prevenção de vazamento

O candle de um dia só fica completo após o fechamento. Consequentemente, `High`, `Low`, `Close` e `Volume` de `t` não podem prever `Close_t`; eles podem entrar como valores de `t` para prever `t+1`, ou em lags. A data e atributos de calendário derivados dela são conhecidos antecipadamente. A página Bitget informa GMT+0; caso o CSV seja substituído por uma exportação dessa fonte, padronizar a coluna temporal nesse fuso antes de qualquer junção.

## Horizonte e sazonalidade

- Horizonte ainda não definido pelo grupo; registrar em `config/projeto.yaml` antes da modelagem.
- Sazonalidades candidatas para investigação: semanal (7 dias) e anual aproximada (365 dias). A existência e a força devem ser confirmadas por STL e validação temporal; não assumir sazonalidade apenas pela frequência diária.

## Referências

- Bitget. *Bitcoin historical data*. Consulta em 2026-09-21. https://www.bitget.com/price/bitcoin/historical-data
