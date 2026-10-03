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
