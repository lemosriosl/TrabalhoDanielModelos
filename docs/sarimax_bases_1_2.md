# SARIMAX — execuções finais das Bases 1 e 2

Registro de 04/10/2026. Commit solicitado pelo grupo, restrito às Bases 1 e 2.

## Procedimento registrado

O executor `scripts/run_frozen_sarimax_final.py` reutiliza a configuração SARIMAX do ranking salvo no notebook, sem refazer tuning. Desativa o modo reduzido e executa o walk-forward final. Não altera notebooks nem dados brutos. Esta execução não comprova que a busca original foi integral; os outputs remotos de seleção foram produzidos em modo reduzido.

| Base | Origens | MAE calculado nas previsões | Unidade |
|---|---:|---:|---|
| 1 | 851 | 698,560125825 | USD/BTC |
| 2 | 7.598 | 574,980677093 | veículos/hora |

Configurações congeladas e convergência informada estão em `results/extraidos_do_remoto/base_01__sarimax_final_audit.json` e `base_02__sarimax_final_audit.json`. As previsões estão em `results/predictions/base_01__sarimax.csv` e `base_02__sarimax.csv`.

## Verificações deste commit

- Contagens das previsões coincidem com as auditorias.
- Origens são únicas; o corte de treino não ultrapassa a origem e o alvo é posterior à origem.
- Valores reais, previstos e resíduos são finitos; resíduo é real menos previsto.
- Os dois testes de `tests/test_run_frozen_sarimax_final.py` foram executados diretamente e aprovados. O ambiente não possui pytest; não houve execução da suíte completa.

## Limites de interpretação

As origens não coincidem em quantidade com as do XGBoost (842 e 3.372). Estes MAEs não são um ranking homologado. Antes de comparar modelos, conferir alvos, grades, origens e horizonte. `results/metrics.csv` não foi modificado nesta tarefa.

Por solicitação explícita de commit das execuções, os dois CSVs de previsões são incluídos como exceção pontual ao padrão de ignorar arquivos gerados. `.gitignore` permanece inalterado. Alterações dos relatórios e artefatos das demais bases não integram este commit.
