# Triagem para entrega sem reexecutar modelos

Atualizada em 2026-10-05. Escopo: examinar saídas já salvas e preparar uma apresentação honesta dos resultados. Esta triagem não altera dados brutos, previsões originais ou hiperparâmetros e não equivale à homologação do protocolo do enunciado.

## O que não coincide

| Item | Evidência observada | Tratamento possível agora | Limite que permanece |
|---|---|---|---|
| Origens de teste | Base 1: 851 HW/SARIMAX versus 842 RF/XGBoost. Base 2: 8.115 HW, 7.598 SARIMAX e 3.372 RF/XGBoost. Base 3: 6.828 HW, 6.824 SARIMAX e 2.847 RF/XGBoost. Base 4: 84.045 HW versus 82.830 RF/XGBoost. | Informar `n` junto a cada MAE; não calcular ranking, vitórias ou posição média. | O enunciado exige as mesmas origens e observações de teste nos quatro modelos. |
| Horizonte SARIMAX | Bases 2 e 3 contêm 14/7.598 e 53/6.824 linhas, respectivamente, cujo alvo está mais de uma hora após a origem. Na Base 3, seis origens compartilhadas com HW têm instante-alvo diferente. | Mostrar o MAE de uma hora já filtrado: 574,086284 (7.584 linhas) e 10,369544 (6.771 linhas). Preservar MAEs brutos apenas como histórico de auditoria. | Filtrar não corrige a execução completa nem iguala as origens às dos outros modelos. |
| RF das Bases 1 e 2 | Notebook versus CSV local: MAE 764,717551 versus 738,894178 (Base 1) e 129,760961 versus 127,346397 (Base 2). A primeira previsão e o primeiro corte de treino já diferem, não sendo simples arredondamento. | Manter o valor do notebook identificado como tal; registrar o CSV como execução conflitante e solicitar o histórico/arquivo correto ao responsável. | Não escolher uma versão como definitiva sem reconciliar parâmetros, dados e momento de execução. |
| Previsões completas | Os MAEs de RF/XGBoost estão salvos em notebooks/consolidado, mas os CSVs integrais por origem não foram localizados para todas as bases. O Git ignora `results/predictions/` e `results/residuals/`. | Solicitar exportações originais; manter tabelas individuais com proveniência. | Contagens iguais, inclusive as 586 da Base 5, não comprovam identidade das datas e alvos. |
| SARIMAX da Base 4 | Apenas resultado parcial local; sem MAE final de referência. | Marcar explicitamente como não concluído e fora desta avaliação. | Fica ausente uma das 20 combinações obrigatórias. |
| Relatório e gestão | O relatório agora incorpora cinco STL, painéis de resíduos/ACF de HW e RF, painéis XGBoost e importância RF dos notebooks. O registro diário real está fora do repositório. | Manter legenda e proveniência de cada figura; solicitar o registro diário ao grupo. | Ainda faltam figuras residuais finais equivalentes do SARIMAX e séries temporais residuais completas do XGBoost. Na Base 5, os gráficos HW/RF são do subconjunto de robustez com 523 cotações novas, não das 586 origens do MAE principal. Não inventar autores, datas, carga ou complexidade. |
| Texto teórico novo no remoto | `entrega/relatorio_modelos_por_base.md` foi acrescentado após o início desta atualização. Ele descreve potencial teórico dos modelos, mas também sugere vantagens entre famílias sem teste em origens comuns e afirma que a avaliação SARIMAX final estaria documentada somente para Bases 1 e 2, enquanto a auditoria local dispõe de CSVs finais das Bases 1, 2, 3 e 5. | Preservar como material suplementar de autoria do grupo, fora do pacote final preparado; usar a matriz auditada do v2 para resultados empíricos. | Revisar o texto com o responsável antes de eventualmente incluí-lo na entrega; não usar suas inferências como ranking. |

## Comparação pareada possível sem novo treino

`results/comparacao_pareada_hw_sarimax.csv` é gerado por `series_temporais.reporting.comparacao_pareada` a partir dos CSVs completos. Exige origem, instante-alvo e valor real coincidentes, além de horizonte de um passo. São 851 pares na Base 1, 7.584 na Base 2, 6.758 na Base 3 e 586 na Base 5. Essa é **uma análise exploratória de dois modelos**, não a classificação dos quatro exigida pelo enunciado. Na Base 3, 13 previsões SARIMAX de uma hora não possuem par HW exato; seis origens compartilhadas divergiam no horário-alvo.

## Como apresentar no relatório

1. Separar “resultados individuais” de “comparação homologada”. Na segunda categoria, registrar explicitamente que ainda não há ranking dos quatro modelos.
2. Exibir unidade, MAE, quantidade de origens, fonte e ressalva de horizonte em cada célula. Para SARIMAX 2/3, usar no texto principal somente o MAE filtrado de uma hora.
3. Apresentar a tabela pareada HW/SARIMAX como verificação complementar, sem extrapolar para RF/XGBoost ou escolher vencedor geral.
4. Explicar que restrição de tempo impediu nova avaliação final. Isso é uma limitação de execução, **não prova de equivalência entre amostras** nem cumprimento substitutivo do protocolo.
5. Solicitar ao professor orientação/autorização para a entrega parcial, pois o enunciado exige mesmas origens, ranking por base, vitórias, posição média, vinte combinações e registro diário.

## Arquivos ainda necessários antes do ZIP final

- Registro diário real de cada integrante, com data, demanda, evidência, carga, complexidade e status.
- Previsões integrais originais de RF/XGBoost, se ainda estiverem com os responsáveis, e explicação da divergência dos RF 1/2.
- Figuras finais residuais/ACF do SARIMAX e séries residuais completas XGBoost, se disponíveis em outros artefatos; os painéis recuperáveis dos notebooks já foram incorporados ao relatório.
- Revisão humana do PDF/HTML e decisão do professor sobre a comparação parcial e o SARIMAX da Base 4.

Fontes de auditoria: `results/metricas_individuais_auditadas.csv`, `results/ljung_box_auditado.csv`, `results/achados_auditoria.json`, `results/comparacao_pareada_hw_sarimax.csv`, notebooks executados, `projeto.yaml` e `docs/atividade/n2_series_temporais.pdf` (seções 5.4-7, 10 e 12-13).
