# Dicionário de variáveis externas — estrutura do projeto

## O que é este documento

Este Markdown é o **catálogo de variáveis exógenas** do projeto. Ele registra todo dado que não pertence à série-alvo original, mas que pode ajudar a explicar ou prever seu comportamento. Para cada variável, o dicionário deve indicar origem, definição, unidade, frequência, disponibilidade temporal, regra de transformação e riscos de uso.

O objetivo é tornar os experimentos reproduzíveis e evitar *data leakage*: uma variável externa só pode entrar na previsão de `t+h` se seu valor for conhecido — ou puder ser previsto separadamente — no instante `t`.

## Regras de preenchimento

- Criar uma entrada por variável, e não apenas por fonte.
- Registrar URL, licença/termos de uso, data de extração, período coberto e fuso horário.
- Definir a chave de junção temporal e espacial: por exemplo, `data`, `data_hora` ou `timestamp + estação`.
- Informar se o valor é **observado no passado**, **conhecido antecipadamente** (calendário/feriado) ou **previsão disponível antecipadamente** (previsão meteorológica).
- Ajustar frequência e fuso antes da junção; descrever regra de agregação ou preenchimento.
- Versionar uma cópia local dos dados externos ou registrar hash/versão da consulta.

## Campos padronizados

| Campo | Como preencher |
|---|---|
| ID | Identificador estável, como `G5_USD_BRL` |
| Grupo / base-alvo | Grupo que usará a variável e série-alvo correspondente |
| Variável externa | Nome de negócio e nome técnico da coluna |
| Hipótese | Relação esperada com o alvo, sem afirmar causalidade sem evidência |
| Fonte e licença | Organização, URL, licença/termos e data de consulta |
| Cobertura | Início/fim, geografia e população/mercado abrangidos |
| Unidade e tipo | Unidade, tipo numérico/categórico e faixa esperada |
| Frequência e fuso | Frequência original, fuso e regra de alinhamento |
| Disponibilidade em `t` | Quando a informação é conhecida em relação ao instante previsto |
| Chave de junção | Campos e regra de agregação para a base-alvo |
| Tratamento | Nulos, *outliers*, transformação, defasagem e normalização |
| Risco / limitação | Revisões, atraso de publicação, acesso restrito, quebras históricas e viés |
| Status | Proposto, em validação, aprovado ou descartado |

## Grupo 1 — Bitcoin (a preencher)

**Base-alvo:** histórico de preços do Bitcoin.

| ID | Variável externa | Fonte | Frequência / disponibilidade | Chave de junção | Hipótese | Status |
|---|---|---|---|---|---|---|
| G1_001 |  |  |  |  |  | Proposto |
| G1_002 |  |  |  |  |  | Proposto |

## Grupo 2 — Tráfego na I-94 (a preencher)

**Base-alvo:** volume horário de tráfego.

| ID | Variável externa | Fonte | Frequência / disponibilidade | Chave de junção | Hipótese | Status |
|---|---|---|---|---|---|---|
| G2_001 |  |  |  |  |  | Proposto |
| G2_002 |  |  |  |  |  | Proposto |

## Grupo 3 — Qualidade do ar em Pequim (a preencher)

**Base-alvo:** concentração horária de poluentes por estação.

| ID | Variável externa | Fonte | Frequência / disponibilidade | Chave de junção | Hipótese | Status |
|---|---|---|---|---|---|---|
| G3_001 |  |  |  |  |  | Proposto |
| G3_002 |  |  |  |  |  | Proposto |

## Grupo 4 — Clima em Jena (a preencher)

**Base-alvo:** temperatura ou outra variável meteorológica em frequência horária.

| ID | Variável externa | Fonte | Frequência / disponibilidade | Chave de junção | Hipótese | Status |
|---|---|---|---|---|---|---|
| G4_001 |  |  |  |  |  | Proposto |
| G4_002 |  |  |  |  |  | Proposto |

## Grupo 5 — Preços diários do ouro

**Base-alvo:** `VALUE` da série diária de ouro. Como o arquivo termina em 2014-04-10 e não documenta a unidade no próprio conteúdo, todas as fontes externas precisam ser recortadas ao mesmo período e ter unidade/fuso explicitamente harmonizados antes da junção.

### Variáveis candidatas

| ID | Variável externa | Hipótese e uso | Frequência / disponibilidade em `t` | Chave de junção e transformação | Status |
|---|---|---|---|---|---|
| G5_USD_INDEX | Índice do dólar americano (DXY ou proxy documentada) | Ouro cotado em USD frequentemente apresenta relação inversa com a força do dólar; usar retorno/variação, não apenas nível. | Diária de mercado; valor de fechamento só é conhecido após o pregão. Para prever o mesmo fechamento, não usar; para `t+1`, usar valor até `t`. | Junção por data de pregão; retorno logarítmico defasado em 1 dia. | Proposto |
| G5_USD_BRL | Taxa de câmbio USD/BRL | Útil se o objetivo de negócio for interpretar valor em reais ou exposição cambial; não é necessária para prever uma série estritamente em USD. | Diária; verificar horário de referência e dias sem cotação. | Junção por data; retorno logarítmico e `lag(1)`. | Proposto |
| G5_REAL_RATE | Taxa de juros real / rendimento de título indexado à inflação | Taxas reais afetam o custo de oportunidade de manter ouro, que não paga cupom. | Diária quando a fonte permitir; séries de títulos podem ter dias sem negociação. Conhecida após a divulgação/fechamento. | Junção por último valor disponível até `t`; usar variação e defasagens. | Proposto |
| G5_NOMINAL_RATE | Taxa de juros nominal (ex.: Treasury) | Captura condições de juros e risco; deve especificar vencimento e fonte. | Diária; valor de fechamento conhecido após o mercado. | Junção por data; nível, diferença e `lag(1)`. | Proposto |
| G5_INFLATION | Inflação (CPI) | Pode refletir demanda por proteção inflacionária, mas é divulgada com atraso e revisões. | Mensal; **não** está disponível contemporaneamente ao mês de referência. | *Forward fill* somente a partir da data oficial de divulgação; usar `release_date`, não o mês de competência. | Proposto |
| G5_VIX | Índice de volatilidade/aversão a risco | Pode captar busca por ativos defensivos durante maior incerteza. | Diária de mercado; conhecido após fechamento. | Junção por data; variação percentual / `lag(1)`. | Proposto |
| G5_SP500 | Retorno de índice acionário amplo | Representa apetite a risco; relação potencialmente variável por regime. | Diária de mercado; usar somente valores até `t`. | Junção por data; retorno logarítmico defasado. | Proposto |
| G5_OIL | Preço do petróleo | Proxy de inflação/atividade e de choques de commodities; relação empírica, não causal por definição. | Diária de mercado. | Junção por data; retorno logarítmico, possíveis lags de 1, 5 e 21 pregões. | Proposto |
| G5_CENTRAL_BANK | Compras líquidas de ouro por bancos centrais | Pode representar demanda estrutural, mas tem baixa frequência, revisão e possível defasagem de publicação. | Mensal/trimestral; normalmente conhecida após o período de referência. | Usar data de publicação e manter valor anterior até nova divulgação; não usar o dado revisado retroativamente sem controle. | Proposto |
| G5_CALENDAR | Calendário de pregão e feriados | Distingue lacunas normais de ausência de dados e pode apoiar atributos de calendário. | Conhecido antecipadamente. | Junção por data; `is_trading_day`, dias desde último pregão e mês. | Aprovado para qualidade |

### Especificação detalhada das entradas do Grupo 5

#### G5_USD_INDEX — força do dólar

| Campo | Preenchimento |
|---|---|
| Variável | Retorno diário de um índice de dólar especificado e rastreável (ex.: DXY ou proxy). |
| Justificativa | A cotação internacional do ouro costuma ser analisada em conjunto com a força do dólar. A relação pode mudar de sinal/intensidade por período, portanto deve ser validada fora da amostra. |
| Fonte a definir | Selecionar uma fonte com série histórica, licença e horário de fechamento documentados. Registrar o identificador exato do índice. |
| Disponibilidade | Usar a observação conhecida no fim de `t` para prever `t+1`. Não usar o fechamento de `t+1` para prever o próprio `t+1`. |
| Transformação | Retorno logarítmico, `lag(1)`, `lag(5)` e, se justificado na validação, média móvel defasada. |
| Riscos | Fuso/horário de fechamento diferente do ouro, composição do índice, lacunas por feriado e correlação instável. |

#### G5_REAL_RATE — juros reais

| Campo | Preenchimento |
|---|---|
| Variável | Taxa real de juros com vencimento e definição fixados previamente. |
| Justificativa | Mede parte do custo de oportunidade de carregar um ativo sem fluxo de caixa. |
| Fonte a definir | Preferir série oficial ou fornecedor que informe metodologia, observações faltantes e revisões. |
| Disponibilidade | Usar somente a última observação publicada até o instante de previsão. |
| Transformação | Nível, variação diária/semanal e defasagens; padronizar dentro do treino de cada dobra. |
| Riscos | Série pode não ter cotação diária, pode sofrer alteração de metodologia e não implica causalidade. |

#### G5_INFLATION — inflação divulgada

| Campo | Preenchimento |
|---|---|
| Variável | Inflação mensal (índice e país devem ser especificados). |
| Justificativa | Hipótese de proteção inflacionária, tratada como relação a validar. |
| Fonte a definir | Fonte oficial com calendário de divulgação e política de revisão. |
| Disponibilidade | A referência de um mês só pode entrar após sua divulgação oficial. Criar `available_from = release_date`. |
| Transformação | Taxa mensal/12 meses; manter o último valor divulgado até a próxima publicação. |
| Riscos | Vazamento por uso do mês de competência, revisões retroativas e frequência diferente da série-alvo. |

#### G5_CENTRAL_BANK — demanda institucional

| Campo | Preenchimento |
|---|---|
| Variável | Compras líquidas de ouro por bancos centrais, com definição geográfica e unidade confirmadas. |
| Justificativa | Variável de demanda potencialmente relevante em horizontes médios, não para resposta imediata diária. |
| Fonte a definir | Organismo setorial ou fonte oficial que registre revisão e data de publicação. |
| Disponibilidade | Considerar apenas o valor disponível na data de publicação; nunca preencher o passado com dado revisado sem sinalização. |
| Transformação | Variação no período, média móvel defasada ou *feature* de regime em baixa frequência. |
| Riscos | Defasagem longa, revisões, baixa frequência e perda de granularidade diária. |

## Checklist antes de aprovar uma variável externa

- [ ] A fonte, licença/termos e data de extração estão registrados.
- [ ] A unidade, moeda, frequência e fuso horário foram identificados.
- [ ] O período cobre o treino e o teste sem buscar valores futuros.
- [ ] A data de disponibilidade foi distinguida da data de referência econômica.
- [ ] A junção foi feita sem duplicar linhas nem criar preenchimento indevido.
- [ ] Transformações, imputação e escalonamento foram ajustados somente no treino.
- [ ] O ganho sobre os baselines foi confirmado em validação temporal e no teste final.
