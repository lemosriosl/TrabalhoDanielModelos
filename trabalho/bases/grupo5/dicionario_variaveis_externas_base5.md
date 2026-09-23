# Dicionário de variáveis externas — Base 5 (preços diários do ouro)

**Responsável pela auditoria documental:** Codex (agente). **Data:** 2026-09-22. **Arquivo-alvo:** `trabalho/bases/grupo5/grupo5_new.csv`, SHA-256 `8446b3f07b6834625e9e82b58955ea8ef906d67c23d34ee05440602349e02947`.

**Série de interesse:** `VALUE`, valor de preço na unidade de origem ainda não confirmada. O notebook usa o retorno até a próxima cotação observada apenas para exploração; alvo e horizonte finais dependem de aprovação no projeto. Chave de junção: `DATE` (`YYYY-MM-DD`), com uma linha por dia de segunda a sexta entre 1968-04-01 e 2014-04-10. Há 368 preços ausentes.

Uma exógena só pode prever o alvo em `t+h` se o valor usado já era conhecido **na origem `t`**. Datas de referência e datas de publicação são diferentes; para séries publicadas depois do período de referência, a junção deve respeitar a publicação real. Fuso e horário de fechamento precisam ser confrontados antes de tratar dois registros com a mesma data como simultaneamente disponíveis. Fonte, identificador, unidade, licença, cobertura histórica, revisão e data de acesso de cada série candidata ainda precisam ser registrados. Nenhuma das séries propostas abaixo está dentro de `grupo5_new.csv`.

## Colunas relacionadas já presentes no arquivo

| ID | Variável | Disponibilidade em `t` | Tratamento e risco | Status |
|---|---|---|---|---|
| G5_HOLIDAY_FLAG | `IS_HOLIDAY` | Não comprovada: o calendário e a regra de marcação não constam do CSV. | Não é proxy de cotação ausente: 180 linhas marcadas têm preço e 251 não marcadas não têm. Manter na auditoria; só usar após identificar calendário e demonstrar que seria conhecido na origem. | Pendente; fora de `X` |
| G5_TARGET_LABEL | `TARGET_UP` | Depende do `VALUE` da próxima linha; indisponível na origem. | Rótulo futuro, **nunca exógena nem feature**. `0` inclui pares com preço ausente; não equivale à direção até a próxima cotação observada. | Excluído de `X` |
| G5_CALENDAR | Dia da semana e mês derivados de `DATE` | Conhecidos antecipadamente. | Podem ser criados sem fonte adicional. A data prevista só deve ser usada se a origem já conhece o calendário e o horizonte; o notebook usa calendário da origem. Não substituem as duas exógenas externas pendentes. | Disponível como derivação |

## Fontes externas candidatas, ainda não incorporadas

As hipóteses abaixo adaptam as propostas já registradas em `trabalho/bases/dicionario_variaveis_externas.md`. Os identificadores representam **candidatos**, não séries obtidas nem variáveis aprovadas. Sem fonte escolhida e checagem de cobertura para 1968–2014, nenhum deles entra na matriz de modelagem.

| ID | Variável candidata | Disponibilidade na origem `t` | Chave e tratamento proposto | Hipótese e risco | Status |
|---|---|---|---|---|---|
| G5_USD_INDEX | Índice amplo do dólar, com identificação exata a definir | Fechamento de `t` somente se publicado antes da origem; caso contrário, usar último fechamento anterior disponível. | Junção temporal por data/hora de publicação; retorno ou variação calculado apenas até `t`. | Relação com a cotação do ouro pode variar por período; diferenças de fuso e horário podem causar vazamento. | Proposto; fonte pendente |
| G5_REAL_RATE | Rendimento real de título com país e vencimento definidos | Última observação publicada até `t`; não presumir observação em todos os dias da série-alvo. | Junção pelo último valor efetivamente disponível; nível, variação e lags avaliados no treino. | Pode representar custo de oportunidade; cobertura, revisão e definição do título precisam ser verificadas. | Proposto; fonte pendente |
| G5_NOMINAL_RATE | Rendimento nominal de título especificado | Mesmo critério de publicação e fechamento da taxa escolhida. | Chave temporal e identificação de vencimento; usar valor conhecido ou defasado. | Pode capturar ambiente de juros; diferenças de mercado e horário importam. | Proposto; fonte pendente |
| G5_INFLATION | Índice de inflação mensal com país definido | Só após divulgação oficial de cada referência, nunca desde o primeiro dia do mês de competência. | Junção `as of` pela data/hora de divulgação; manter o último dado publicado e controlar revisões. | Frequência mensal e revisões podem gerar vazamento retrospectivo. | Proposto; fonte pendente |
| G5_VIX | Índice de volatilidade com definição e cobertura verificadas | Fechamento apenas após publicação; usar observação anterior se necessário. | Junção temporal e variação defasada. | Proxy de risco; verificar início da série e cobertura para o período-alvo. | Proposto; fonte pendente |
| G5_SP500 | Índice acionário amplo ou retorno associado | Fechamento conhecido até a origem; horários de negociação podem diferir. | Retorno calculado só com preços já publicados; junção pela disponibilidade. | Hipótese de apetite a risco, sem relação estável garantida. | Proposto; fonte pendente |
| G5_OIL | Preço ou contrato de petróleo identificado | Cotação e horário de referência precisam anteceder a origem. | Definir contrato, rolagem e unidade; usar retorno ou variação histórica. | Proxy de commodities/atividade; mudanças de contrato e fuso exigem cuidado. | Proposto; fonte pendente |
| G5_CENTRAL_BANK | Compras líquidas de ouro por bancos centrais | Valor conhecido apenas após divulgação do período, possivelmente com revisão. | Junção pela data de publicação e versão disponível naquela data; sem preencher retroativamente com revisão. | Baixa frequência e defasagem longa podem limitar utilidade para previsão diária. | Proposto; fonte pendente |

## Critérios de aprovação de uma exógena

1. Registrar fonte primária, identificador exato, licença/termos, data de acesso, unidade, moeda, país, fuso e cobertura histórica. Registrar checksum da extração usada.
2. Definir a origem da previsão e a data/hora de disponibilidade de cada observação. Se houver revisões, guardar ou reconstruir a versão conhecida à época; sem isso, restringir o uso.
3. Demonstrar a junção sem acesso a valores posteriores à origem. Ausências e *forward fill* só podem usar a última observação já publicada.
4. Avaliar cobertura e lacunas no trecho comum antes de escolher as pelo menos duas exógenas exigidas. Uma candidata com cobertura parcial não deve reduzir silenciosamente o teste ou mudar as origens de apenas um modelo.
5. Ajustar escala, seleção, imputação e hiperparâmetros somente no passado de cada origem. Random Forest e modelo de especialização devem compartilhar as features compatíveis; SARIMAX usa exógenas somente quando disponíveis para a previsão. Holt-Winters permanece univariado.

**Pendência central:** nenhuma série externa foi fornecida com `grupo5_new.csv`. As variáveis acima são propostas documentais; a escolha final e sua inclusão no experimento dependem de fonte, disponibilidade temporal e protocolo comum aprovados em `config/projeto.yaml`.
