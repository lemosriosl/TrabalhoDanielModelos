# XGBoost — estudo do modelo de especialização

## Escopo e protocolo

O XGBoost é o modelo de especialização aplicado às cinco bases. Para que a comparação seja válida, cada notebook reutiliza as features, a origem da previsão, o horizonte e o corte de teste definidos pelo Random Forest da respectiva base. A importância das features do Random Forest pertence ao pacote da Pessoa 3; este documento cobre o XGBoost e sua comparação nas cinco bases.

O protocolo separa seleção e avaliação. Os hiperparâmetros são escolhidos somente no treino por uma busca aleatória reproduzível de 150 configurações: 120 combinações amplas e 30 combinações refinadas ao redor da melhor região. Cada candidato é avaliado em três dobras temporais expansivas e purgadas. A purga exclui do treino qualquer observação cujo alvo alcance a origem da validação. Depois da escolha por MAE médio de validação, os parâmetros são congelados e usados no teste walk-forward final.

A persistência — repetir o último nível observado — é o baseline. O MAE é calculado apenas sobre previsões fora da amostra. MAEs brutos de bases com escalas diferentes não são promediados; a comparação global usa vitórias e skill relativo à persistência:

`skill = 1 - MAE_XGBoost / MAE_persistência`.

## Funcionamento e intuição

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
| 1 | 50 | 0,01 | 7 | 1 | 0,595 | 0,51 | 0 | 2,5 |
| 2 | 900 | 0,01 | 9 | 12 | 0,765 | 0,92 | 0,05 | 5 |
| 3 | 100 | 0,02 | 8 | 3 | 0,70 | 0,69 | 0,05 | 10 |
| 4 | 200 | 0,01 | 7 | 2 | 0,805 | 0,69 | 0,05 | 10 |
| 5 | 50 | 0,02 | 4 | 6 | 0,805 | 0,60 | 0,25 | 1,5 |

As diferenças são coerentes com a heterogeneidade das bases: a Base 2 selecionou muitas árvores com taxa pequena, enquanto a Base 5 preferiu um conjunto curto, mais raso e regularizado. Isso não significa que uma configuração seja universalmente superior; ela foi escolhida dentro do treino de cada série.

## Importância das features

Foram calculadas duas medidas complementares em cada reajuste do walk-forward:

- **Gain:** redução de perda atribuída às divisões que usam cada feature. É rápido, mas pode favorecer variáveis usadas repetidamente pelas árvores.
- **Permutation Importance:** aumento do MAE quando os valores de uma feature são embaralhados no conjunto fora da amostra. Está mais ligada ao desempenho preditivo observado, mas features correlacionadas podem substituir umas às outras e reduzir a importância aparente.

As duas medidas são agregadas entre reajustes por média e desvio-padrão. Valores negativos de permutação significam que, naquela amostra, embaralhar a variável não piorou o modelo; isso é sinal de instabilidade ou redundância, não de efeito protetor. Nenhuma medida deve ser interpretada como causal.

### Leitura por base

**Base 1 — Bitcoin.** O Gain se concentra em volatilidade, médias e defasagens do preço, como `target_std_30`, `target_std_7`, `target_lag_30` e `target_mean_14`. A Permutation Importance é pequena e instável para várias delas. Isso combina com o ganho quase nulo sobre a persistência: há estrutura histórica reconhecida pelas árvores, mas pouca contribuição marginal robusta fora da amostra.

**Base 2 — tráfego.** `target_lag_3`, hora do dia, `target_lag_1` e o nível atual dominam as duas medidas. O resultado mostra uma rotina intradiária forte, combinada com dependência recente. Essa estrutura repetitiva explica por que o XGBoost supera amplamente a persistência.

**Base 3 — PM2.5.** A principal feature é `target_lag_1`, acompanhada por velocidade do vento, PM10, nível atual e outros poluentes. O modelo aproveita tanto persistência de curto prazo quanto condições atmosféricas. A dispersão entre importâncias recomenda cautela ao ordenar poluentes correlacionados.

**Base 4 — temperatura.** Hora do dia é dominante, seguida pela volatilidade recente, déficit/pressão de vapor, nível atual e lags. O padrão diário forte e regular oferece ao modelo uma vantagem clara sobre repetir a última temperatura.

**Base 5 — ouro.** Gain distribui-se por médias e dispersões de preço/retorno e por taxas externas defasadas. Já a Permutation Importance fica muito próxima de zero e muda de sinal em várias features. Esse desacordo, somado à derrota para a persistência, indica que as divisões encontradas no treino não produziram ganho fora da amostra suficientemente estável.

## Desempenho nas cinco bases

Resultados da execução completa com 150 candidatos por base:

| Base | Série | MAE XGBoost | MAE persistência | Skill | Resultado |
|---|---|---:|---:|---:|---|
| 1 | Bitcoin diário | 692,4661 | 693,4339 | 0,14% | vitória marginal |
| 2 | Tráfego horário | 129,8732 | 584,0842 | 77,76% | vitória forte |
| 3 | PM2.5 horário | 9,5849 | 10,2058 | 6,08% | vitória |
| 4 | Temperatura a cada 10 min | 0,1370 | 0,1662 | 17,56% | vitória |
| 5 | Ouro semanal | 19,1032 | 18,9520 | −0,80% | derrota marginal |

O XGBoost venceu a persistência em quatro das cinco bases. A diferença de desempenho pode ser explicada principalmente pela previsibilidade disponível:

- tráfego e temperatura possuem ciclos recorrentes fortes, representados por calendário e lags;
- PM2.5 combina persistência com covariáveis ambientais informativas;
- Bitcoin apresenta mudanças de regime e alta volatilidade, deixando pouco ganho além do último valor;
- retornos semanais do ouro são mais próximos de um sinal fraco e ruidoso, no qual uma previsão zero — equivalente à persistência do preço — é difícil de superar.

As explicações são compatíveis com as evidências, mas não constituem prova causal. Para isolar o papel de uma família de features seria necessária uma ablação temporal específica.

## Pontos de atenção antes da entrega definitiva

- Na Base 5, as séries de Treasury de 10 anos e Fed Funds ainda precisam de homologação de fonte, unidade e disponibilidade histórica.
- A Base 5 deve manter também o recorte de semanas com nova cotação, porque semanas carregadas favorecem mecanicamente a persistência.
- Horizonte, origens e cortes foram espelhados do Random Forest e devem permanecer iguais nos quatro modelos.
- Se o catálogo de features for alterado, o tuning e o teste precisam ser executados novamente; não se deve reutilizar os parâmetros atuais.
- A interpretação final deve considerar resíduos, ACF e Ljung–Box exibidos em cada notebook. Rejeição de ruído branco indica estrutura temporal ainda não capturada.

## Reprodutibilidade

Os notebooks registram semente, versões das bibliotecas, hash do dado, lista de features, parâmetros, tempo de busca, tempo de avaliação e origens de reajuste. Checkpoints ficam em uma pasta temporária e permitem retomar a busca. A ordem recomendada de execução é das bases 1 a 5, pois a Base 5 lê os resumos temporários anteriores e apresenta a consolidação.
