# Métricas consolidadas

`metrics.csv` é o consolidado canônico. Nesta auditoria contém cinco linhas
XGBoost, sem posições ou vencedor; os demais modelos ainda não foram integrados
ao mesmo protocolo de origens. Não interpretar esse arquivo como ranking final.

O arquivo deve ser gerado com `series_temporais.results.write_metrics`; não deve
ser preenchido manualmente. Cada linha identifica a base, o alvo, a frequência,
o horizonte, o número de origens, as métricas, a posição no ranking, os parâmetros,
as exógenas, o notebook de origem, o commit e o instante de geração.

Para comparações válidas, modelos da mesma base precisam usar exatamente o mesmo
alvo, as mesmas origens e o mesmo horizonte.

### XGBoost

Os cinco notebooks atualizam sua própria linha ao finalizar. Para consolidar
execuções anteriores sem novo treino, na raiz do projeto:

```powershell
python -c "import sys; sys.path.insert(0, 'src'); from series_temporais.reporting.metricas_xgboost import main; main()"
```

Esse comando usa os CSVs de resíduos locais e os resumos completos em
`%TEMP%/trabalho_daniel_xgboost/summary` (ou `--summary-dir`). Valida hash do dado,
MAE, origens e cadência e preserva os registros dos outros modelos. Esses insumos
locais precisam existir; apenas clonar o Git não recupera os checkpoints.

As linhas XGBoost não têm posição nem vencedor até a consolidação dos quatro
modelos. MAPE é percentual e fica vazio para retorno ou séries com zero.
O tempo é a soma do tempo registrado dos ajustes de tuning e avaliação, não
o tempo de parede da chamada com cache. As exógenas listadas são as covariáveis
diretas do contrato de disponibilidade, não a lista completa de features derivadas.
O sufixo `+dirty` no commit indica execução/consolidação com alterações locais.

Os checkpoints de tuning XGBoost usam uma assinatura v2 do quadro de treino,
alvo, origens, protocolo, versões e implementação metodológica. Checkpoints
anteriores não são migrados automaticamente: a próxima execução pode repetir
a busca completa. Essa atualização não altera os resultados já consolidados.
Os CSVs individuais de resíduos continuam ignorados pelo Git.

Os gráficos temporais de resíduos XGBoost ficam incorporados às saídas dos cinco
notebooks, além da ACF já existente. A célula **Resíduos XGBoost ao longo do tempo**
pode ser executada sozinha, em kernel novo, usando o CSV completo local e verificando
sua contagem e MAE contra o consolidado. Não dispara tuning/retreino nem reescreve
CSV ou métricas. Na Base 5, a escala principal é retorno logarítmico.

### Evidências individuais para o relatório v2

`metricas_individuais_auditadas.csv`, `ljung_box_auditado.csv` e
`achados_auditoria.json` são gerados por
`python src/series_temporais/reporting/evidencias_relatorio.py`.
Cada linha informa a fonte: CSV completo local de previsões de Holt-Winters
ou SARIMAX, saída executada de notebook de Random Forest ou XGBoost, ou
o consolidado XGBoost. O SARIMAX da Base 4 não entra nesses arquivos por
solicitação do grupo. Os CSVs de RF das Bases 1 e 2 divergem de seus notebooks;
o JSON registra essa inconsistência. Como as origens dos quatro modelos não
coincidem nas Bases 1–4, estas tabelas são descritivas, não um ranking.

As colunas `origens_horizonte_1` e `mae_horizonte_1` valem para os modelos com
CSV completo. Nas Bases 2 e 3, o SARIMAX possui respectivamente 14 e 53
linhas cujo alvo fica mais de uma hora após a origem; por isso, seu MAE bruto
mistura horizontes. O relatório usa somente as linhas de uma hora para esses
dois MAEs e para o Ljung–Box, sem alterar os CSVs originais.
### SARIMAX rápido provisório

`sarimax_fast_metrics.csv` é um consolidado provisório separado. Ele usa busca
curta, ajuste único no treino inicial e atualização de estado sem reestimar os
coeficientes em cada origem. Serve para obter uma referência rápida e plausível,
mas não deve ser misturado ao ranking oficial de `metrics.csv`.

### Ranking descritivo

`ranking_descritivo_modelos.csv` ordena os MAEs apenas dentro de cada base,
marca o vencedor descritivo por base e resume vitórias e posição média. Quando
disponível, usa o MAE filtrado para horizonte de um passo. O arquivo não calcula
média de MAEs entre bases e mantém `comparacao_homologada=false`, pois as origens
dos quatro modelos ainda não são equivalentes. Na Base 4, o SARIMAX oficial
permanece ausente; o resultado rápido não é usado para preencher essa lacuna.
