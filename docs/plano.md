# Plano de execucao

Cada etapa deve terminar com uma evidencia reproduzivel e uma atualizacao em `collaboration/demandas.csv`.

## Etapa 0 - Alinhamento do grupo

- Definir grupo, integrantes e modelo de especializacao.
- Confirmar as cinco bases congeladas, fontes, alvo e variaveis externas.
- Definir frequencia, horizonte, origens e janela inicial do walk-forward.
- Preencher `config/projeto.yaml` e resolver `docs/decisoes_pendentes.md`.

## Etapa 1 - Auditoria e documentacao das bases

- Registrar fonte, periodo, frequencia, unidade, alvo e dicionario de variaveis.
- Verificar ausencias, duplicidades, irregularidade temporal e valores atipicos.
- Classificar a disponibilidade real de cada variavel externa.
- Produzir graficos exploratorios sem alterar os dados brutos.

## Etapa 2 - STL e preparacao

- Regularizar cada serie quando necessario e documentar a decisao.
- Executar STL e interpretar tendencia, sazonalidade e residuo.
- Calcular a forca da sazonalidade pelo metodo definido em sala.
- Implementar transformacoes reproduziveis em `src/series_temporais/data/`.

## Etapa 3 - Features e validacao

- Criar lags, janelas, calendario, encoding ciclico e variaveis externas validas.
- Tratar valores ausentes gerados pelas features.
- Implementar e testar o divisor walk-forward comum aos quatro modelos.
- Demonstrar por teste que nenhuma feature acessa o futuro.

## Etapa 4 - Otimizacao

- Definir os espacos de busca dos quatro modelos em cada base.
- Otimizar apenas dentro do periodo de desenvolvimento.
- Salvar configuracoes escolhidas em `results/hyperparameters/`.
- Congelar os hiperparametros antes do teste final.

## Etapa 5 - Avaliacao final

- Executar 20 combinacoes: cinco bases por quatro modelos.
- Salvar previsoes, residuos, parametros e tempos de execucao.
- Consolidar MAE por base, ranking interno, vitorias e posicao media.
- Nao fazer media direta de MAE entre bases.

## Etapa 6 - Diagnostico e interpretacao

- Gerar residuos no tempo, ACF e teste de Ljung-Box para cada combinacao.
- Interpretar vies, variabilidade e autocorrelacao.
- Analisar coeficientes/efeitos do SARIMAX, componentes do Holt-Winters e importancia de features nos modelos tabulares.
- Produzir o estudo aprofundado do modelo de especializacao.

## Etapa 7 - Relatorio e entrega

- Construir o relatorio fonte em `notebooks/relatorio/`.
- Gerar HTML paginado autocontido e PDF com o mesmo conteudo.
- Revisar narrativa, citacoes, figuras, tabelas e participacao dos integrantes.
- Copiar apenas artefatos finais para `entrega/` e gerar o ZIP solicitado.

