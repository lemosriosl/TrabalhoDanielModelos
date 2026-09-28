"""Avaliação walk-forward usando o ajuste e os registros da pipeline de aula."""

from __future__ import annotations

from time import perf_counter

import pandas as pd

from .pipeline_sarimax import ajustar_referencia, escalar_exogenas


def prever_walk_forward_referencia(
    serie: pd.Series,
    inicio_teste: pd.Timestamp,
    *,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int],
    exogenas: pd.DataFrame | None = None,
    trend: str = "n",
    maxiter: int = 100,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Prevê um passo, revela o alvo e atualiza o estado sem reestimar parâmetros."""
    inicio_teste = pd.Timestamp(inicio_teste)
    treino_y = serie.loc[serie.index < inicio_teste]
    teste_y = serie.loc[serie.index >= inicio_teste]
    treino_x = teste_x = None
    if exogenas is not None:
        treino_x = exogenas.loc[treino_y.index]
        teste_x = exogenas.loc[teste_y.index]
        treino_x, teste_x, _ = escalar_exogenas(treino_x, teste_x)
    ajuste = ajustar_referencia(
        treino_y,
        treino_x,
        order=order,
        seasonal_order=seasonal_order,
        trend=trend,
        maxiter=maxiter,
    )
    resultado = ajuste.resultado
    linhas: list[dict[str, object]] = []
    inicio_walk = perf_counter()
    ultimo_observado = treino_y.dropna().index.max()
    for instante, real in teste_y.items():
        x_instante = None if teste_x is None else teste_x.loc[[instante]]
        previsto = float(resultado.get_forecast(steps=1, exog=x_instante).predicted_mean.iloc[0])
        if pd.notna(real):
            linhas.append({
                "target_time": instante,
                "y_true": float(real),
                "y_pred_sarimax": previsto,
                "residuo_sarimax": float(real - previsto),
                "training_target_cutoff": ultimo_observado,
            })
            ultimo_observado = instante
        novo_y = pd.Series([real], index=pd.DatetimeIndex([instante]), name=serie.name)
        resultado = resultado.extend(novo_y, exog=x_instante)
    previsoes = pd.DataFrame(linhas).set_index("target_time")
    previsoes["erro_absoluto_sarimax"] = previsoes.residuo_sarimax.abs()
    if not (previsoes.training_target_cutoff < previsoes.index).all():
        raise AssertionError("Vazamento temporal detectado no walk-forward.")
    return previsoes, {
        "BIC": float(ajuste.resultado.bic),
        "convergiu": ajuste.convergiu,
        "segundos_ajuste": ajuste.segundos,
        "segundos_walk_forward": perf_counter() - inicio_walk,
        "avisos": ajuste.avisos,
        "MAE": float(previsoes.erro_absoluto_sarimax.mean()),
    }
