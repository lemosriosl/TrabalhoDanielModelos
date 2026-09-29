# Base 3 — Qualidade do ar em Pequim (estação Aotizhongxin)

## Identificação

| Item | Registro |
|---|---|
| Responsável | P2 — Pedro Henrique Gomes Frossard |
| Fonte | [UCI Machine Learning Repository — Beijing Multi-Site Air-Quality Data](https://archive.ics.uci.edu/dataset/501/beijingmultisiteairqualitydata) |
| Autoria/citação | Chen, S. (2017), DOI: 10.24432/C5RK5G |
| Licença | CC BY 4.0 |
| Data desta auditoria | 2026-09-22 |
| Arquivo | `PRSA_Data_Aotizhongxin_20130301-20170228.csv` |
| SHA-256 | `a94fbcfc71708b6ffdc033360163d91efb7f675e496f6b5860929aa96b96351b` |
| Cobertura no arquivo | 2013-03-01 00:00 a 2017-02-28 23:00 |
| Observações | 35.064 |
| Granularidade | Horária |
| Colunas temporais | `year`, `month`, `day`, `hour` (compor `datetime`) |
| Variável-alvo | `PM2.5` |
| Unidade do alvo | µg/m³ |
| Estação | Aotizhongxin (uma das 12 estações do conjunto completo, que soma 420.768 linhas) |
| Divisão solicitada | A definir pelo grupo, preservando a ordem temporal |
| `random_state` solicitado | A definir pelo grupo (aplicável somente a componentes estocásticos; não embaralhar a série) |

Este é o dataset originalmente referenciado no dicionário mestre do projeto para o Grupo 3 (qualidade do ar em Pequim), substituindo o par `data.csv`/`test.csv` de séries financeiras usado anteriormente por engano. O arquivo traz dados horários de poluentes atmosféricos e variáveis meteorológicas da estação Aotizhongxin, com dados meteorológicos casados com a estação do China Meteorological Administration mais próxima.

## Dicionário das variáveis da base

| Coluna | Tipo no arquivo | Unidade | Descrição | Papel e uso temporal |
|---|---|---|---|---|
| `No` | inteiro | — | Índice sequencial da linha (1 a 35.064). | Não usar como feature; serve só de conferência de ordenação. |
| `year`, `month`, `day`, `hour` | inteiros | — | Componentes da data/hora da medição. | Combinar em `datetime`; chave temporal. |
| `PM2.5` | numérico contínuo | µg/m³ | Concentração de material particulado fino. | **Alvo** da previsão. |
| `PM10` | numérico contínuo | µg/m³ | Concentração de material particulado grosso. | Covariável de poluição, medida no mesmo instante do alvo — ver dicionário de variáveis externas. |
| `SO2` | numérico contínuo | µg/m³ | Concentração de dióxido de enxofre. | Idem. |
| `NO2` | numérico contínuo | µg/m³ | Concentração de dióxido de nitrogênio. | Idem. |
| `CO` | numérico contínuo | µg/m³ | Concentração de monóxido de carbono. | Idem. |
| `O3` | numérico contínuo | µg/m³ | Concentração de ozônio. | Idem. |
| `TEMP` | numérico contínuo | °C | Temperatura do ar. | Covariável meteorológica, medida no mesmo instante do alvo. |
| `PRES` | numérico contínuo | hPa | Pressão atmosférica. | Idem. |
| `DEWP` | numérico contínuo | °C | Temperatura do ponto de orvalho. | Idem. |
| `RAIN` | numérico contínuo | mm | Precipitação na hora. | Idem; zero é valor válido (sem chuva). |
| `wd` | categórica | — | Direção do vento (16 pontos cardeais, ex. `NNW`). | Idem; variável circular. |
| `WSPM` | numérico contínuo | m/s | Velocidade do vento. | Idem. |
| `station` | categórica | — | Nome da estação de monitoramento. | Constante (`Aotizhongxin`); não é feature útil neste arquivo — só relevante se outras estações forem combinadas. |

## Qualidade e preparação

| Verificação | Resultado | Decisão |
|---|---|---|
| Valores ausentes | `PM2.5`: 925; `PM10`: 718; `SO2`: 935; `NO2`: 1.023; `CO`: 1.776; `O3`: 1.719; `TEMP`/`PRES`/`DEWP`/`RAIN`: 20 cada; `wd`: 81; `WSPM`: 14. Nenhum ausente em `year`/`month`/`day`/`hour`. | Definir e documentar estratégia de imputação/remoção por coluna antes da modelagem; não preencher `PM2.5` (alvo) com valor futuro. |
| Linhas duplicadas | 0 linhas exatamente duplicadas. | — |
| Cobertura horária | Grade completa: 35.064 horas esperadas entre o início e o fim, 35.064 linhas presentes, nenhuma hora faltando na grade (as ausências são de valores nas colunas, não de linhas). | Não é necessário reindexar para preencher lacunas de calendário; tratar apenas os `NaN` internos. |
| Ordenação | Crescente por `year`/`month`/`day`/`hour`. | Preservar a ordenação; converter para `datetime` único. |
| Atípicos do alvo | 1.624 observações de `PM2.5` fora de 1,5 IQR (limite inferior negativo, superior 252,0 µg/m³), de 34.139 valores não nulos. | Não remover automaticamente: picos de poluição são o próprio fenômeno de interesse; investigar antes de qualquer corte. |

## Disponibilidade temporal e prevenção de vazamento

`PM10`, `SO2`, `NO2`, `CO`, `O3`, `TEMP`, `PRES`, `DEWP`, `RAIN`, `wd` e `WSPM` são medidos no mesmo instante que `PM2.5`; nenhuma pode ser usada contemporânea ao próprio `t` que está sendo previsto — apenas defasadas, ou substituídas por previsão/observação disponível na origem quando `t+h` for o horizonte. Os componentes `year`/`month`/`day`/`hour` e atributos de calendário derivados são conhecidos antecipadamente. Ver o dicionário de variáveis externas atualizado para o detalhamento por variável.

## Horizonte e sazonalidade

- Horizonte ainda não definido pelo grupo; registrar em `config/projeto.yaml` antes da modelagem.
- Sazonalidades candidatas: diária (24 horas) e anual (poluição varia por estação do ano, com invernos historicamente mais poluídos em Pequim); confirmar força por STL e validação temporal, não assumir a priori.

## Referências

- Chen, S. (2017). *Beijing Multi-Site Air Quality* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5RK5G
- Zhang, S., Guo, B., Dong, A., He, J., Xu, Z., Chen, S. X. (2017). Cautionary Tales on Air-Quality Improvement in Beijing. *Proceedings of the Royal Society A*, 473(2205).
- UCI Machine Learning Repository. Licença CC BY 4.0. Consulta em 2026-09-22.