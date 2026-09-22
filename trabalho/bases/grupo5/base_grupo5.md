# Base 5 — preços diários do ouro (`grupo5_new.csv`)

## Identificação e proveniência

Esta ficha descreve **`trabalho/bases/grupo5/grupo5_new.csv`**, a versão usada no EDA. O arquivo anterior, `grupo5_old.csv`, permanece apenas para comparação. Ambos têm as mesmas 12.009 datas e os mesmos valores de `VALUE`; o novo arquivo troca o separador por `;` e acrescenta duas colunas. SHA-256 do novo arquivo: `8446b3f07b6834625e9e82b58955ea8ef906d67c23d34ee05440602349e02947`.

O histórico de `DATE` e `VALUE` corresponde ao arquivo [gold.daily.prices.csv](https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv) citado na versão anterior desta ficha. A origem, regra de construção e data de geração de `IS_HOLIDAY` e `TARGET_UP` **não estão documentadas no CSV**. A unidade, moeda e fornecedor da cotação também não constam do arquivo. Até confirmação, `VALUE` significa valor de preço na unidade de origem, sem afirmar USD/onça troy.

| Propriedade observada | Valor |
|---|---:|
| Separador e cabeçalho | `;` e `DATE;VALUE;IS_HOLIDAY;TARGET_UP` |
| Período | 1968-04-01 a 2014-04-10 |
| Linhas / datas únicas | 12.009 / 12.009 |
| Frequência de linhas | Segunda a sexta, com algumas cotações ausentes |
| `VALUE` ausente | 368 (3,06%) |
| `VALUE` observado | 11.641 |
| `IS_HOLIDAY = 1` | 297 (inclui 180 linhas com preço observado) |
| `TARGET_UP = 1` | 5.629 |

## Dicionário das colunas

| Coluna | Tipo no arquivo | Interpretação verificada e uso |
|---|---|---|
| `DATE` | `YYYY-MM-DD` | Data da linha. Converter para data, ordenar e verificar duplicatas. |
| `VALUE` | número ou vazio | Preço observado; vazio significa cotação ausente, nunca zero. É a única série numérica de preço. |
| `IS_HOLIDAY` | 0/1 | Indicador de feriado fornecido. Não equivale a ausência de cotação: há linhas marcadas como feriado com preço e linhas sem preço não marcadas. Calendário e momento de disponibilidade precisam ser confirmados antes de seu uso como feature. |
| `TARGET_UP` | 0/1 | Rótulo já calculado no arquivo. A auditoria mostra que equivale a `1` quando `VALUE` da **próxima linha do CSV** é maior que o da linha atual; caso contrário, inclusive quando um dos preços está ausente, vale `0`. É informação futura e nunca deve entrar em `X`. |

## Regra de preparação

1. Ler exclusivamente `grupo5_new.csv` com `sep=';'`, sem baixar outra versão por fallback. Registrar o SHA-256 e verificar esquema, ordem, datas, duplicatas, valores não positivos, nulos e contagens dos indicadores.
2. Manter `IS_HOLIDAY` e `TARGET_UP` na auditoria da fonte. Não imputar `VALUE` e não criar cotações em fins de semana ou feriados. Remover linhas sem preço apenas da tabela de modelagem.
3. A preparação exploratória atual preserva a previsão do **próximo preço observado**, que já era a definição no notebook antigo. Isso pode pular uma ou mais linhas sem cotação. Registrar a data prevista e o intervalo em dias. O horizonte comum do experimento ainda depende da decisão do grupo.
4. Criar os alvos `target_price_t_plus_1` e `target_log_return_t_plus_1` a partir dos preços observados. Se houver estudo de direção, derivar `target_up_next_observed` desses mesmos pares válidos. Não usar `TARGET_UP` da fonte como rótulo equivalente: a regra dele é a próxima **linha**, mesmo se estiver sem cotação.
5. Usar apenas informações disponíveis na origem `t` nas features: preço atual, retornos passados, lags, médias e volatilidades móveis defasadas, calendário conhecido e intervalo desde a última cotação. `IS_HOLIDAY` fica fora de `X` enquanto sua definição e disponibilidade não forem confirmadas. `TARGET_UP` também fica fora de `X`.

## EDA e validação

O notebook `eda_preparacao_base_5_ouro.ipynb` mostra qualidade da fonte, série de preços, retornos, distribuição, volatilidade móvel dos **retornos** e resumo anual. O corte cronológico 80%/20% que ele apresenta é **exploratório**; não fixa as origens, o horizonte nem o teste final comum aos quatro modelos. Não há embaralhamento nem ajuste de imputação ou escala em toda a série. O walk-forward final, seleção de hiperparâmetros e MAE fora da amostra seguem `config/projeto.yaml` quando esses campos forem aprovados e preenchidos.

Para preço, persistência (`previsão = preço em t`) é um baseline. Para retorno, retorno zero é outro. SARIMAX, Holt-Winters, Random Forest e o modelo de especialização devem ser avaliados nas mesmas origens e observações de teste; seus hiperparâmetros devem ficar fixos durante o teste final. A comparação entre bases de escalas diferentes usa vitórias e posição média, não a média bruta dos MAEs.

## Pendências

- Confirmar a fonte, o calendário e a data de disponibilidade de `IS_HOLIDAY`.
- Confirmar a origem e o propósito de `TARGET_UP`; a regra observada não equivale ao alvo de próximo preço **observado** quando há lacuna.
- Confirmar unidade, moeda e fornecedor de `VALUE`.
- Aprovar alvo, variáveis externas, horizonte, origens e teste final em `config/projeto.yaml` antes da comparação de modelos.
