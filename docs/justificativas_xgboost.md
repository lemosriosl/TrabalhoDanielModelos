# Justificativas das escolhas do XGBoost

Atualizado em 05/10/2026. Este texto se refere somente ao XGBoost. Explica razões técnicas e operacionais; não demonstra que as escolhas são ótimas nem substitui a correção das amostras de teste dos demais modelos.

## Features e informações disponíveis

XGBoost não possui um relógio temporal interno: recebe uma tabela. Lags, estatísticas móveis e calendário tornam explícitas a dependência recente, a volatilidade e os ciclos. Covariáveis entram somente quando conhecidas na origem; medições futuras observadas não são features. Reutilizar o quadro do RF evita criar uma vantagem artificial por seleção diferente de features entre esses dois modelos. Nas execuções atuais há 23/22/29/33/49 features nas Bases 1–5.

Um modelo univariado e um multivariado não precisam ter entradas idênticas para representar soluções de previsão distintas. Entretanto, a comparação de desempenho requer mesmo alvo, horizonte, observações avaliadas e ausência de leakage. Usar mais informações não garante menor erro; comparações não isolam apenas o algoritmo quando os pipelines diferem. Nas Bases 1–4, as origens das quatro famílias continuam diferentes: essa pendência não foi corrigida nem justificada como aceitável por este texto.

## Variação do nível e retorno

Nas Bases 1–4, o estimador aprende a mudança do nível e a previsão final é o nível observado na origem mais a mudança prevista. Isso coloca a persistência como referência explícita (mudança zero) e permite aprender correções locais, sem depender de extrapolação direta de níveis nunca vistos pelas folhas das árvores. Não é garantia de estacionariedade nem de melhora; alvo interno e escala de avaliação devem ser distinguidos. MAE principal permanece na unidade original.

Na Base 5, o alvo oficial atual é o retorno logarítmico semanal `target_log_return_t_plus_1`, não preço ou log-preço. Preço é reconstruído por `price_t * exp(retorno_previsto)`. Zero retorno corresponde à persistência do preço. A avaliação principal inclui as 586 semanas; o recorte de novas cotações é complementar e não substitui o resultado principal.

## Otimização temporal e regularização

São 150 candidatos reproduzíveis (120 amplos e 30 refinados) em três dobras expansivas purgadas, somente dentro do treino. Uma busca aleatória limitada permite explorar interações entre profundidade, número de árvores, taxa de aprendizado, amostragem e regularização com custo viável. Não equivale a testar todas as combinações nem a provar um ótimo global. As dobras respeitam a ordem temporal; a purga impede incorporar alvos ainda não revelados na primeira origem de validação.

A configuração de cada base é selecionada pelo menor MAE médio de validação e congelada antes do teste. Os valores particulares são uma consequência da seleção, não uma explicação causal inventada depois de ver o teste. Semente, versões, quadro utilizado e parâmetros são registrados para rastreabilidade.

## Retreino periódico sem previsão em bloco

Cada origem recebe previsão de um passo com as features disponíveis naquele momento. O que permanece fixo entre reajustes são as árvores, não os dados de entrada da previsão. As cadências 7/24/24/144/4 contam origens avaliáveis nas Bases 1–5; exclusões podem tornar a duração em calendário diferente.

Retreinar o conjunto completo de árvores em todas as 82.830 origens da Base 4 tinha custo elevado. Reajustar a cada 144 origens reduz para 576 ajustes, tornando a avaliação operacionalmente viável. Em cada reajuste o histórico é expansivo e contém somente alvos já revelados. Não há aprendizagem online das árvores antigas nem consulta a alvos futuros entre reajustes.

A cadência é uma escolha operacional, não comprovadamente a melhor para acurácia. Pode reduzir adaptação a mudanças rápidas. As diferenças de atualização em relação às outras famílias precisam ser declaradas: compara-se o pipeline com essa política, não exclusivamente o algoritmo sob políticas idênticas. Essa justificativa não resolve origens de teste diferentes.

## Baseline, importância e leitura dos resultados

Persistência é uma referência exigente para séries com dependência recente. Perder para ela em Bitcoin/ouro não autoriza escolher outra configuração pelo teste ou trocar a amostra para obter vitória. Tráfego, poluição e temperatura oferecem padrões de calendário/histórico que o XGBoost pode aproveitar; essa hipótese é compatível com as execuções, não uma prova causal. Não afirmar superioridade sobre outras famílias usando MAEs de amostras distintas.

Gain descreve contribuição às divisões das árvores; Permutation Importance verifica sensibilidade do erro ao embaralhamento. São complementares, afetadas por correlação e por janelas curtas, e não demonstram causalidade. A análise sem taxas externas na Base 5 é sensibilidade, não instrumento para substituir retroativamente a avaliação oficial.

## Roteiro curto para apresentação

1. Transformamos a série em features temporais causais porque o XGBoost opera sobre uma tabela.
2. Espelhamos as features e origens do RF; outras famílias ainda precisam de alinhamento para ranking final.
3. Prevemos mudança do nível nas Bases 1–4 e retorno semanal na Base 5, mantendo a unidade correta na avaliação.
4. Escolhemos parâmetros em validação temporal purgada e os congelamos antes do teste.
5. Produzimos uma previsão de um passo em cada origem, com retreino periódico para viabilizar o custo; não alegamos cadência ótima.
6. Reportamos persistência e limitações, inclusive derrotas e amostras diferentes. Justificativa não substitui validação.

## Referências

- Chen, T.; Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. DOI: 10.1145/2939672.2939785.
- [Documentação oficial de parâmetros do XGBoost](https://xgboost.readthedocs.io/en/stable/parameter.html).
- Hyndman, R. J.; Athanasopoulos, G. *Forecasting: Principles and Practice*, 3ª ed., [avaliação](https://otexts.com/fpp3/accuracy.html) e [validação temporal](https://otexts.com/fpp3/tscv.html).
