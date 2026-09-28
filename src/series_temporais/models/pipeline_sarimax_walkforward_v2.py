"""Walk-forward da pipeline com atualização posicional do estado."""

from __future__ import annotations

from time import perf_counter
import pandas as pd

from .pipeline_sarimax import ajustar_referencia, escalar_exogenas


def prever_walk_forward_referencia_v2(serie, inicio_teste, *, order, seasonal_order, exogenas=None, trend="n", maxiter=100):
    inicio_teste = pd.Timestamp(inicio_teste)
    treino_y = serie.loc[serie.index < inicio_teste]
    teste_y = serie.loc[serie.index >= inicio_teste]
    treino_x = teste_x = None
    if exogenas is not None:
        treino_x = exogenas.loc[treino_y.index]
        teste_x = exogenas.loc[teste_y.index]
        treino_x, teste_x, _ = escalar_exogenas(treino_x, teste_x)
    ajuste = ajustar_referencia(treino_y, treino_x, order=order, seasonal_order=seasonal_order, trend=trend, maxiter=maxiter)
    resultado = ajuste.resultado
    ultimo_observado = treino_y.dropna().index.max()
    linhas = []
    inicio_walk = perf_counter()
    for instante, real in teste_y.items():
        x_linha = None if teste_x is None else teste_x.loc[[instante]]
        previsto = float(resultado.get_forecast(steps=1, exog=x_linha).predicted_mean.iloc[0])
        if pd.notna(real):
            linhas.append({"target_time": instante, "y_true": float(real), "y_pred_sarimax": previsto, "residuo_sarimax": float(real - previsto), "training_target_cutoff": ultimo_observado})
            ultimo_observado = instante
        resultado = resultado.extend([real], exog=None if x_linha is None else x_linha.to_numpy())
    previsoes = pd.DataFrame(linhas).set_index("target_time")
    previsoes["erro_absoluto_sarimax"] = previsoes.residuo_sarimax.abs()
    if not (previsoes.training_target_cutoff < previsoes.index).all():
        raise AssertionError("Vazamento temporal detectado no walk-forward.")
    return previsoes, {"BIC": float(ajuste.resultado.bic), "convergiu": ajuste.convergiu, "segundos_ajuste": ajuste.segundos, "segundos_walk_forward": perf_counter() - inicio_walk, "avisos": ajuste.avisos, "MAE": float(previsoes.erro_absoluto_sarimax.mean())}
