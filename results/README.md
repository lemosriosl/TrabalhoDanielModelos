# Métricas consolidadas

`metrics.csv` é o consolidado reproduzível da comparação final. Ele começa apenas
com o cabeçalho e recebe linhas somente depois que cada notebook termina o teste
walk-forward canônico.

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
