# XGBoost — estudo do modelo de especialização

## Escopo e protocolo

Atualização de 04/10/2026: os cinco XGBoosts foram executados com reajustes a cada 7/24/24/144/4 origens nas Bases 1–5. Todas as origens continuam recebendo uma previsão de um passo com features atuais e treino causal. A cadência é operacional, não escolhida pelo teste nem comprovadamente ótima. Os números abaixo substituem resultados históricos. O alvo canônico da Base 5 é retorno logarítmico semanal.

O XGBoost é o modelo de especialização aplicado às cinco bases. Para que a comparação seja válida, cada notebook reutiliza as features, a origem da previsão, o horizonte e o corte de teste definidos pelo Random Forest da respectiva base. A importância das features do Random Forest pertence ao pacote da Pessoa 3; este documento cobre o XGBoost e sua comparação nas cinco bases.

O protocolo separa seleção e avaliação. Os hiperparâmetros são escolhidos somente no treino por uma busca aleatória reproduzível de 150 configurações: 120 combinações amplas e 30 combinações refinadas ao redor da melhor região. Cada candidato é avaliado em três dobras temporais expansivas e purgadas. A purga exclui alvos posteriores à primeira origem da validação; alvos revelados exatamente na origem são permitidos no cenário pós-observação. Depois da escolha por MAE médio de validação, os hiperparâmetros são congelados e usados no teste walk-forward final. Nas Bases 1–4, o estimador aprende a variação do nível e a previsão é somada ao nível atual; as métricas principais são calculadas no nível. Na Base 5, aprende o retorno e converte para preço por `price_t * exp(retorno_previsto)`.

A persistência — repetir o último nível observado — é o baseline. O MAE é calculado apenas sobre previsões fora da amostra. MAEs brutos de bases com escalas diferentes não são promediados; a comparação global usa vitórias e skill relativo à persistência:

`skill = 1 - MAE_XGBoost / MAE_persistência`.

## Funcionamento e intuição

As razões técnicas de escolha das features, previsão de variação/retorno, busca temporal e cadência operacional estão em [Justificativas do XGBoost](justificativas_xgboost.md), com um roteiro de apresentação. Elas não demonstram superioridade nem corrigem a pendência das origens distintas entre famílias. As justificativas acrescentadas nesta revisão referem-se somente ao XGBoost.

O XGBoost constrói árvores de decisão em sequência. A primeira árvore produz uma aproximação inicial; cada árvore seguinte tenta reduzir os erros que permaneceram. Tecnicamente, a nova árvore aproxima o gradiente da função de perda, e a previsão final é a soma das contribuições das árvores multiplicadas pela taxa de aprendizado.

Árvores são adequadas para relações não lineares, limiares e interações. Por exemplo, o efeito da hora sobre o tráfego pode mudar conforme o dia da semana, e o efeito da umidade sobre a temperatura pode depender do vento. O XGBoost pode aprender essas combinações sem que todas sejam especificadas manualmente.

O algoritmo, porém, não entende a ordem temporal por conta própria. A série precisa ser convertida em uma tabela causal contendo estados disponíveis na origem, defasagens, estatísticas móveis e variáveis de calendário. O modelo nunca deve receber uma medição que só se tornaria conhecida depois da origem prevista.

## Hipóteses, preparação e limitações

As principais hipóteses práticas são:

- os padrões históricos ainda têm alguma utilidade no período previsto;
- as features usadas estariam disponíveis no instante real da previsão;
- treino e teste respeitam a ordem do tempo;
- a grade temporal e o significado das variáveis permanecem consistentes;
- mudanças de regime não tornam todo o histórico irrelevante.

O XGBoost não exige normalização e suporta relações não lineares, mas não elimina a necessidade de preparação. Datas, duplicidades, intervalos irregulares, valores ausentes e disponibilidade das covariáveis precisam ser tratados antes do ajuste. Lags e janelas móveis são calculados somente com o passado.

Entre as vantagens estão flexibilidade, capacidade de representar interações e regularização incorporada. Entre as limitações estão menor transparência que modelos lineares, sensibilidade ao protocolo de tuning, custo computacional e dificuldade para extrapolar tendências além dos valores vistos. Um bom desempenho de teste não prova estabilidade futura nem causalidade.

## Hiperparâmetros e seus efeitos

- `n_estimators`: número de árvores. Mais árvores aumentam capacidade e custo; em excesso podem sobreajustar.
- `learning_rate`: contribuição de cada árvore. Valores menores produzem passos conservadores e normalmente exigem mais árvores.
- `max_depth`: profundidade máxima. Profundidades maiores representam interações mais complexas, com maior risco de sobreajuste.
- `min_child_weight`: evidência mínima para criar folhas. Valores maiores tornam a árvore mais conservadora.
- `subsample`: fração das linhas usada por árvore. Valores abaixo de 1 adicionam aleatoriedade e regularização.
- `colsample_bytree`: fração das features considerada por árvore. Reduz dependência de poucas variáveis e pode melhorar generalização.
- `reg_alpha`: penalização L1, que favorece estruturas mais esparsas.
- `reg_lambda`: penalização L2, que reduz contribuições extremas das folhas.

Configurações selecionadas antes do teste final:

| Base | `n_estimators` | `learning_rate` | `max_depth` | `min_child_weight` | `subsample` | `colsample_bytree` | `reg_alpha` | `reg_lambda` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | 0,01 | 9 | 2 | 0,765 | 0,85 | 0,1 | 10 |
| 2 | 900 | 0,01 | 9 | 7 | 0,765 | 1 | 0 | 1 |
| 3 | 100 | 0,02 | 8 | 3 | 0,70 | 0,69 | 0,05 | 10 |
| 4 | 100 | 0,02 | 8 | 3 | 0,70 | 0,69 | 0,05 | 10 |
| 5 | 50 | 0,01 | 4 | 5 | 0,70 | 0,60 | 0,1 | 0,5 |

As diferenças são coerentes com a heterogeneidade das bases: a Base 2 selecionou muitas árvores com taxa pequena, enquanto a Base 5 preferiu um conjunto curto, mais raso e regularizado. Isso não significa que uma configuração seja universalmente superior; ela foi escolhida dentro do treino de cada série.

## Importância das features

Foram calculadas duas medidas complementares em janelas fora da amostra, com o modelo congelado na origem do diagnóstico:

- **Gain:** redução de perda atribuída às divisões que usam cada feature. É rápido, mas pode favorecer variáveis usadas repetidamente pelas árvores.
- **Permutation Importance:** aumento do MAE quando os valores de uma feature são embaralhados no conjunto fora da amostra. Está mais ligada ao desempenho preditivo observado, mas features correlacionadas podem substituir umas às outras e reduzir a importância aparente.

Nas Bases 1–4, os diagnósticos são amostrados: Base 1 a cada 28 origens em janela de 26; Bases 2–3 a cada 168 em janela de 168; Base 4 a cada 1.440 em janela de 144. Na Base 5, usam o bloco de cada reajuste, normalmente quatro origens (duas no último). Permutar uma única observação seria inválido; as janelas têm pelo menos duas linhas. Janelas curtas, especialmente na Base 5, tornam a importância ruidosa.

As duas medidas são agregadas entre janelas por média e desvio-padrão. Nas Bases 1–4, a permutação mede aumento do MAE da variação prevista, não diretamente do preço/nível; na Base 5 mede retorno. Não comparar suas magnitudes brutas entre bases. Valores negativos significam que embaralhar a variável não piorou o modelo naquela janela; sugerem instabilidade ou redundância, não efeito protetor. Os diagnósticos não selecionam hiperparâmetros nem substituem as previsões principais e não têm interpretação causal.

### Leitura por base

**Base 1 — Bitcoin.** Os maiores Gains aparecem em `target_std_7`, `target_lag_30`, `target_mean_30` e `target_mean_14`. A permutação é instável: para `target_std_7`, a média é 0,64 e o desvio entre janelas 11,36. Isso é compatível com pouco ganho marginal fora da amostra e com a pequena derrota para a persistência.

**Base 2 — tráfego.** `target_lag_3`, hora do dia, `target_lag_1` e o nível atual dominam as duas medidas. O resultado mostra uma rotina intradiária forte, combinada com dependência recente. Essa estrutura repetitiva explica por que o XGBoost supera amplamente a persistência.

**Base 3 — PM2.5.** Os maiores Gains são `target_lag_1`, `WSPM_t`, `target_lag_2`, `RAIN_t` e `level_t`. A permutação de `target_lag_1` aumenta o MAE em média 1,27, com desvio 1,13 entre janelas. O modelo aproveita dependência recente e covariáveis ambientais, mas a dispersão exige cautela ao ordenar variáveis correlacionadas.

**Base 4 — temperatura.** Hora do dia é dominante, seguida pela volatilidade recente, déficit/pressão de vapor, nível atual e lags. O padrão diário forte e regular oferece ao modelo uma vantagem clara sobre repetir a última temperatura.

**Base 5 — ouro.** Os maiores Gains aparecem em `price_mean_4`, `price_lag_13`, `fed_funds_lag_4`, `source_observations` e `return_mean_52`. A permutação fica próxima de zero e muda de sinal em várias features. O Gain das taxas não comprova contribuição incremental; por exemplo, `fed_funds_lag_4` tem permutação média zero. A derrota marginal no conjunto completo e as janelas curtas recomendam interpretação cautelosa, sem concluir causalidade.

## Desempenho nas cinco bases

Resultados da execução completa com 150 candidatos por base:

| Base | Série | MAE XGBoost | MAE persistência | Skill | Resultado |
|---|---|---:|---:|---:|---|
| 1 | Bitcoin diário — preço | 694,1673 | 693,4339 | −0,11% | derrota marginal |
| 2 | Tráfego horário — volume | 127,8916 | 584,0842 | 78,10% | vitória forte |
| 3 | PM2.5 horário — concentração | 9,5287 | 10,2058 | 6,64% | vitória |
| 4 | Temperatura a cada 10 min — °C | 0,136486 | 0,166198 | 17,88% | vitória |
| 5 | Ouro semanal — retorno logarítmico | 0,02013327 | 0,02010082 | −0,16% | derrota marginal |

O XGBoost venceu a persistência em três das cinco bases segundo o MAE do teste. As diferenças pequenas nas Bases 1 e 5 não demonstram, por si sós, significância estatística. A diferença de desempenho pode estar associada à previsibilidade disponível:

- tráfego e temperatura possuem ciclos recorrentes fortes, representados por calendário e lags;
- PM2.5 combina persistência com covariáveis ambientais informativas;
- Bitcoin apresenta mudanças de regime e alta volatilidade, deixando pouco ganho além do último valor;
- retornos semanais do ouro são mais próximos de um sinal fraco e ruidoso, no qual uma previsão zero — equivalente à persistência do preço — é difícil de superar.

As explicações são compatíveis com as evidências, mas não constituem prova causal. Para isolar o papel de uma família de features seria necessária uma ablação temporal específica.

### Robustez da Base 5

A avaliação principal inclui todas as 586 semanas. No recorte de 523 semanas com nova cotação, MAE de retorno é 0,02239585 contra 0,02252215 da persistência, ganho de aproximadamente 0,56%. Na escala auxiliar de preço, o MAE completo é 19,0009 contra 18,9520; com nova cotação, 21,1239 contra 21,2349. O pequeno ganho no recorte não substitui a derrota na avaliação principal. Semanas carregadas têm retorno real zero e favorecem a persistência; cobertura e origem são preservadas no CSV.

### Resíduos, ACF e Ljung–Box

Resíduos são `real - previsto`: positivos indicam subestimação. Os CSVs preservam todos os erros, não somente uma amostra. Os cinco notebooks incluem agora uma célula autônoma **Resíduos XGBoost ao longo do tempo**, separada da ACF, com data do alvo no eixo horizontal e referência em zero. Na Base 5 o gráfico principal usa retorno, incluindo todas as 586 semanas; preço continua auxiliar. Lacunas de calendário interrompem a linha, sem interpolação dos erros.

A célula foi executada isoladamente a partir dos CSVs completos existentes e as figuras ficaram incorporadas às saídas dos notebooks, sem novo ajuste ou mudança de métricas. Em um kernel novo, pode-se executar somente essa célula para reproduzir o gráfico: ela lê o CSV local, valida as datas, os resíduos, a contagem e o MAE de `results/metrics.csv`. Os CSVs continuam ignorados pelo Git; para regenerar a figura após clonar, é preciso recuperar esses vetores completos. Em execução integral do notebook, a célula usa o quadro `predictions` em memória.

| Base | Defasagens com rejeição de ausência de autocorrelação (5%) | Sem rejeição |
|---|---|---|
| 1 | 1, 14, 30 | 7 |
| 2 | 1, 24, 48, 168 | nenhuma das testadas |
| 3 | 1, 24, 48, 168 | nenhuma das testadas |
| 4 | 1, 6, 144, 288 | nenhuma das testadas |
| 5 | 4, 13, 26, 52 | 1 |

Há dependência residual em todas as bases, mesmo onde o MAE supera a persistência. Não rejeitar numa defasagem não prova ruído branco; Ljung–Box avalia autocorrelação conjunta até cada lag, não normalidade. Os p-valores impressos como zero na Base 4 representam valores numericamente muito pequenos. As várias verificações são diagnósticas, sem correção de múltiplos testes.

### Execução e custo

| Base | Features | Previsões | Cadência (origens) | Reajustes | Ajustes do tuning (s) | Avaliação (s) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 23 | 842 | 7 | 121 | 394,6581 | 56,4237 |
| 2 | 22 | 3.372 | 24 | 141 | 766,1005 | 1.228,4855 |
| 3 | 29 | 2.847 | 24 | 119 | 480,1676 | 111,2921 |
| 4 | 33 | 82.830 | 144 | 576 | 940,8669 | 3.833,9213 |
| 5 | 49 | 586 | 4 | 147 | 502,9252 | 207,8157 |

O tempo do tuning é a soma dos ajustes registrados para os candidatos, incluindo buscas reaproveitadas dos checkpoints; não é o tempo de parede desta última chamada. A avaliação inclui treino, previsão e diagnósticos executados dentro do intervalo cronometrado. O consolidado registra a soma dessas duas colunas. A Base 4 passou de 82.830 reajustes potenciais para 576, mantendo 82.830 previsões; a avaliação final levou cerca de 64 minutos. Cadência mede origens avaliáveis, não necessariamente intervalos de calendário quando há exclusões.

## Pontos de atenção antes da entrega definitiva

- A auditoria local identifica Treasury como DGS10 e Fed Funds como DFF e comprova o preenchimento causal seguido de atraso de uma observação no calendário original. A disponibilidade histórica exata e as versões em tempo real ainda não foram homologadas; ver `data/base_05/auditoria_taxas_base5.md`. Não confundir DFF com meta da taxa básica.
- A Base 5 deve manter também o recorte de semanas com nova cotação, porque semanas carregadas favorecem mecanicamente a persistência.
- Horizonte, origens e cortes foram espelhados do Random Forest e devem permanecer iguais nos quatro modelos.
- Se o catálogo de features for alterado, o tuning e o teste precisam ser executados novamente; não se deve reutilizar os parâmetros atuais.
- A interpretação final deve considerar resíduos, ACF e Ljung–Box exibidos em cada notebook. Rejeição de ruído branco indica estrutura temporal ainda não capturada.
- Os notebooks e resultados RF permanecem como no remoto. A cadência 7/24/24/144/4 é exclusiva do XGBoost e não impõe reexecução dos outros modelos. Na comparação final, declarar a diferença de cadência de reajuste e homologar alvo, horizonte e origens; três vitórias aqui significam somente comparação com persistência. O CSV `results/random_forest_metrics.csv` preserva as métricas RF extraídas pelo grupo, separadas do consolidado canônico.

## Reprodutibilidade

Os notebooks registram semente 42, versões das bibliotecas, hash do dado, lista de features, parâmetros, tempos e origens de reajuste. As execuções atuais usam Python 3.13.7 e XGBoost 3.4.1. Checkpoints temporários permitem retomar a busca, não o walk-forward interrompido; o arquivo de progresso não é um checkpoint de retomada.

Após a revisão, os checkpoints passam ao esquema v2: a identificação inclui os valores e tipos do quadro de tuning, alvo, origens, protocolo, sementes, versões e código metodológico. Mudanças apenas em Markdown ou outputs não invalidam a busca. Checkpoints antigos não são migrados automaticamente, portanto a próxima execução poderá refazer o tuning; esta proteção não modifica as previsões e métricas já salvas nem exige reexecutar o teste XGBoost nesta demanda.

Resíduos são gerados em `results/residuals/base_NN_XGBoost.csv` (ignorados pelo Git); métricas consolidadas em `results/metrics.csv` são geradas por código e mantêm posição/vencedor ausentes até o ranking comum. MAPE é ausente para retorno ou presença de zeros no alvo. O sufixo `+dirty` identifica alterações locais não commitadas.

A tabela global da Base 5 foi reconsolidada depois da reexecução das Bases 1–3, sem refazer o treino. Resumos temporários são convenientes, mas não são evidência permanente; os notebooks e o consolidado preservam os resultados. Para repetir a geração do CSV sem ajustar modelos, use o comando documentado em `results/README.md`, com os CSVs e resumos disponíveis.
