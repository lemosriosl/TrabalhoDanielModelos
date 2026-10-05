# Relatório de revisão dos modelos e da pipeline

## 1) Como a pipeline está organizada e se ela é consistente

A arquitetura do projeto está bem padronizada no nível metodológico e no contrato causal.

- O arquivo [projeto.yaml](../projeto.yaml) fixa a estratégia de validação: walk-forward, horizonte de 1 passo, janela expansiva, MAE como métrica principal.
- O módulo [src/series_temporais/validation/walk_forward.py](../src/series_temporais/validation/walk_forward.py) exige que a previsão use apenas histórico reve-lado até a origem, com alvo posterior à origem e sem vazamento temporal.
- O módulo [src/series_temporais/features/regras_bases.py](../src/series_temporais/features/regras_bases.py) define um contrato por base: alvo canônico, frequência, lags e janelas, além de regras de disponibilidade da feature.
- O módulo [src/series_temporais/results.py](../src/series_temporais/results.py) padroniza o CSV consolidado de métricas, com colunas fixas para base, modelo, alvo, frequência, horizonte, MAE e hiperparâmetros.

Em termos práticos, a pipeline está consistente no desenho:

1. dado bruto; 2. preparação e feature engineering; 3. split causal; 4. walk-forward; 5. métricas fora da amostra; 6. consolidação em `results/metrics.csv`.

O ponto de atenção é que a padronização da arquitetura não significa que todas as execuções modelares foram igualmente concluídas e comparáveis entre si. A documentação do projeto deixa claro que:

- o XGBoost está consolidado em `results/metrics.csv` para as cinco bases;
- o Random Forest foi extraído como evidência parcial do remoto e não é considerado ranking homologado;
- SARIMAX final foi validado/commitado apenas para Bases 1 e 2 na documentação [docs/sarimax_bases_1_2.md](../docs/sarimax_bases_1_2.md);
- Holt-Winters e o restante das comparações ainda dependem de uma consolidação homogênea por base e por modelo.

Ou seja: a estrutura da pipeline está coerente; a competição final ainda não está completamente homogenizada em todos os modelos e bases.

## 2) Teoria dos quatro modelos

### 2.1 SARIMAX

SARIMAX combina:

- componente AR (auto-regressivo): dependência linear do passado;
- componente I (integração): diferenciação para estabilizar séries não estacionárias;
- componente MA (média móvel): dependência em erros recentes;
- componente sazonal (S): ciclos regulares em nível de período conhecido;
- regressões exógenas (X): covariáveis observadas fora do alvo.

É um modelo muito forte quando a série apresenta sazonalidade aparente, tendência linear e dependência temporal clara. É mais rígido em relação a não-linearidades e interações entre variáveis, e em geral exige que a série seja bem compreendida em termos de estacionariedade, diferenciação e período sazonal.

### 2.2 Holt-Winters

Holt-Winters é um modelo de suavização exponencial que separa:

- nível;
- tendência;
- sazonalidade.

Ele é muito eficiente para séries com estrutura repetitiva e mudança gradual de nível, especialmente quando a sazonalidade é estável e a série não exige muitas interações complexas entre covariáveis. Funciona melhor quando o componente dominante é a persistência de padrão sazonal ou tendência, e piora quando a série tem regime não linear, ruído alto ou múltiplas variáveis explicativas relevantes.

### 2.3 Random Forest

Random Forest é um conjunto de árvores de regressão. Ele aprende relações não lineares por cortes em diferentes variáveis e combina várias árvores para reduzir variância.

Ele é adequado para problemas com:

- interações entre features;
- limiares e efeitos não lineares;
- ganho com lags, médias móveis e variáveis exógenas.

Mas, como árvore de decisão, ele não “sabe” por si só que a série é temporal; a ordem temporal precisa entrar por meio de lags, rolling stats, hora do dia, dia da semana, janelas e variáveis de calendário. Em séries financeiras ou de tráfego, isso costuma funcionar bem quando há dependência local forte e padrões repetitivos, mas pode perder em séries com estrutura linear mais clara ou com comportamento de mudança brusca sem boa representação por features.

### 2.4 XGBoost

XGBoost é uma técnica de boosting de árvores: cada nova árvore corrige o erro da árvore anterior. O modelo aprende interações complexas, efeitos não lineares e regras condicionais com alta capacidade preditiva.

Ele é especialmente forte quando:

- a relação entre passado e futuro é mais de “regra de decisão” do que de linearidade pura;
- há variáveis exógenas relevantes;
- a base possui sazonalidade intrínseca que pode ser capturada por lags, estatísticas móveis e variáveis de calendário;
- a previsão deve ser feita em múltiplas janelas com re-treinamento periódico.

O projeto define que o XGBoost use treino causal e refit periódico, seguindo o contrato formal em [src/series_temporais/validation/walk_forward.py](../src/series_temporais/validation/walk_forward.py). O documento [docs/modelo_xgboost.md](../docs/modelo_xgboost.md) também deixa explícito que o objetivo é prever 1 passo à frente com features conhecidas na origem e com rejeição de dados futuros.

## 3) Funcionamento por base

### Base 1 — Bitcoin / preço diário

- Freq: diária (D)
- Alvo: `Close`
- Estrutura típica: tendência, volatilidade, ciclos de curto/médio prazo e forte dependência autoregressiva.

Teoricamente:

- SARIMAX pode ser útil se a série tiver componente sazonal e tendência mais estável.
- Holt-Winters também faz sentido para nível e tendência, mas não captura bem mudanças bruscas de regime e volatilidade.
- Random Forest e XGBoost tendem a funcionar bem com lags e janelas porque conseguem aprender relações não lineares entre preços recentes e volatilidade/nível.

Resumo: a Base 1 é uma base em que a combinação de dependência temporal e não-linearidade favorece árvores, especialmente XGBoost, mas onde a interpretação causal de séries financeiras continua delicada.

### Base 2 — tráfego por hora

- Freq: horária (h)
- Alvo: `traffic_volume`
- Estrutura típica: forte ciclo diário e semanal, e forte efeito de feriado/horário.

Teoricamente:

- Holt-Winters é muito adequado para padrões sazonais repetitivos de alta regularidade.
- SARIMAX também é forte, principalmente com sazonalidade intradiária e exógenas como feriado e meteorologia.
- Random Forest e XGBoost são excelentes em capturar interações entre hora do dia, dia da semana, feriado e valores recentes, especialmente quando as features incluem `lag`, `rolling`, e variáveis climáticas.

Resumo: é uma base que em teoria favorece modelos de sazonalidade e também modelos de árvore com features temporais bem construídas. A documentação do XGBoost aponta que o tráfego tem padrão intradiário forte, que é justamente onde árvores de boosting se destacam.

### Base 3 — qualidade do ar / PM2.5 por hora

- Freq: horária (h)
- Alvo: `PM2.5`
- Estrutura típica: dependência temporal + múltiplas variáveis exógenas (PM10, SO2, NO2, O3, vento, temperatura etc.).

Teoricamente:

- SARIMAX pode ser útil como benchmark linear, mas tende a ficar limitado frente a interações complexas entre poluentes e condições meteorológicas.
- Holt-Winters tem pouca vantagem em séries dominadas por variáveis exógenas e interações não lineares.
- Random Forest e XGBoost são bem posicionados para explorar relações não lineares entre poluentes e o clima, especialmente quando o alvo depende simultaneamente de múltiplos estados ambientais.

Resumo: a Base 3 é um caso típico em que a flexibilidade do XGBoost ou do Random Forest tem mais potencial do que um modelo puramente linear ou de suavização.

### Base 4 — temperatura a cada 10 minutos

- Freq: 10 minutos
- Alvo: `T (degC)`
- Estrutura típica: alta frequência, ciclos diários e algumas interações meteorológicas.

Teoricamente:

- Holt-Winters pode ser competitivo em ciclos muito regulares, mas perde quando há variações meteorológicas e interações múltiplas.
- SARIMAX pode funcionar em escala com sazonalidade bem definida, mas em alta frequência com múltiplas covariáveis e ritmos curtos pode ficar mais instável do que modelos de árvore.
- Random Forest e XGBoost são bons para lidar com interações entre temperatura, umidade, pressão, vento e variáveis derivadas de ciclo horário.

Resumo: a Base 4 é uma base muito adequada para modelos que aprendem interações  e variáveis contextuais, como árvores e boosting. A natureza de alta frequência também exige atenção ao corte causal e ao refit periódico, que aparece no contrato do XGBoost.

### Base 5 — retorno logarítmico semanal de ativo financeiro

- Freq: semanal (W-FRI)
- Alvo: `target_log_return_t_plus_1`
- Estrutura típica: retorno, pouca persistência linear, ruído financeiro, regime de mercado ou mudança de tendência.

Teoricamente:

- SARIMAX e Holt-Winters podem funcionar como baseline de tendência, mas retornos geralmente são mais difíceis de modelar com dependência linear estruturada.
- Random Forest e XGBoost têm melhor chance porque aprendem padrões condicionais em um espaço de features mais amplo, especialmente quando usam indicadores macroeconômicos e valores de mercado recentes.
- A forma de previsão do projeto é especial: o modelo aprende retorno e depois reconverte para preço por `price_t * exp(retorno_previsto)`, conforme documentado em [docs/modelo_xgboost.md](../docs/modelo_xgboost.md).

Resumo: a Base 5 é a mais exigente em termos de eficiência estatística e causalidade. Mesmo sem um ranking final totalmente homologado, ela é a base em que a especialização do XGBoost é mais plausivelmente alinhada com a teoria de modelos de árvore em dados financeiros.

## 4) Comparação geral dos modelos na prática do repositório

Em termos de teoria, os quatro modelos têm papel diferente:

- SARIMAX: melhor quando a série tem estrutura linear bem definida, sazonalidade e exógenas claras;
- Holt-Winters: melhor para séries com nível/tendência/sazonalidade muito estáveis;
- Random Forest: forte em interações e não-linearidades com features temporais bem construídas;
- XGBoost: geralmente o mais flexível e poderoso para séries com múltiplas interações e features de contexto.

No repositório, a parte de padronização metodológica foi bem executada:

- contratos causais;
- split temporal fixo;
- horizonte único;
- MAE fora da amostra;
- metodologia de refit e expansão de janela;
- consolidação de resultados em esquemas padronizados.

Mas a parte de comparação final entre modelos ainda não está totalmente uniforme. A documentação disponível indica que a consolidação final e a homologação do ranking global ainda estão pendentes para alguns modelos/bases. A revisão indica que a pipeline está sólida, mas a comparação final não está totalmente fechada em todos os cenários.

## 5) Conclusão

A pipeline está bem organizada e majoritariamente coerente com a teoria de previsão em séries temporais. O maior problema não é a modelagem em si, e sim a materialização final dos resultados: não houve consolidação completa e simultânea dos quatro modelos para todas as bases sob o mesmo critério de avaliação e exportação.

A leitura mais segura do projeto é:

- a estrutura da experimentação está padronizada;
- os contratos de causalidade e de métricas estão consistentes;
- a teoria dos modelos está alinhada com as bases;
- a comparação final ainda está incompleta para alguns modelos e bases, principalmente em SARIMAX, Random Forest e Holt-Winters, embora o XGBoost tenha a base de execução e consolidação mais madura.

Em síntese, a pipeline é metodologicamente consistente, mas a homologação comparativa final ainda não está totalmente fechada em todas as combinações base/modelo.
