"""Núcleo reutilizável inspirado na pipeline SARIMAX de referência do curso.

Mantém os elementos da referência: ajuste com captura de convergência e
avisos, escala ajustada só no treino, BIC e previsão fora da amostra.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
import warnings

import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX


@dataclass(frozen=True)
class AjusteSarimax:
    resultado: object
    convergiu: bool
    segundos: float
    avisos: str


def escalar_exogenas(
    treino: pd.DataFrame, futuro: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Ajusta escala exclusivamente no treino e a aplica ao período futuro."""
    if list(treino.columns) != list(futuro.columns):
        raise ValueError("Treino e futuro precisam ter as mesmas exógenas.")
    scaler = StandardScaler()
    treino_saida = pd.DataFrame(
        scaler.fit_transform(treino.astype(float)), index=treino.index, columns=treino.columns
    )
    futuro_saida = pd.DataFrame(
        scaler.transform(futuro.astype(float)), index=futuro.index, columns=futuro.columns
    )
    return treino_saida, futuro_saida, scaler


def ajustar_referencia(
    y: pd.Series,
    exogenas: pd.DataFrame | None,
    *,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int],
    trend: str = "n",
    maxiter: int = 100,
) -> AjusteSarimax:
    """Ajusta como a referência, registrando BIC e convergência."""
    inicio = perf_counter()
    with warnings.catch_warnings(record=True) as capturados:
        warnings.simplefilter("always")
        modelo = SARIMAX(
            endog=y,
            exog=exogenas,
            order=order,
            seasonal_order=seasonal_order,
            trend=trend,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        resultado = modelo.fit(disp=False, maxiter=maxiter)
    return AjusteSarimax(
        resultado=resultado,
        convergiu=bool(resultado.mle_retvals.get("converged", True)),
        segundos=perf_counter() - inicio,
        avisos=" | ".join(str(item.message) for item in capturados[:3]),
    )


def prever_referencia(
    treino_y: pd.Series,
    futuro_y: pd.Series,
    *,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int],
    treino_x: pd.DataFrame | None = None,
    futuro_x: pd.DataFrame | None = None,
    trend: str = "n",
    maxiter: int = 100,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Ajusta no treino, prevê o futuro e registra diagnóstico do candidato."""
    if (treino_x is None) != (futuro_x is None):
        raise ValueError("Exógenas devem ser fornecidas para treino e futuro juntos.")
    if treino_x is not None:
        treino_x, futuro_x, _ = escalar_exogenas(treino_x, futuro_x)
    ajuste = ajustar_referencia(
        treino_y, treino_x, order=order, seasonal_order=seasonal_order, trend=trend, maxiter=maxiter
    )
    pred = ajuste.resultado.get_forecast(steps=len(futuro_y), exog=futuro_x).predicted_mean
    pred.index = futuro_y.index
    previsoes = pd.DataFrame({"y_true": futuro_y, "y_pred_sarimax": pred})
    previsoes["residuo_sarimax"] = previsoes.y_true - previsoes.y_pred_sarimax
    previsoes["erro_absoluto_sarimax"] = previsoes.residuo_sarimax.abs()
    return previsoes, {
        "BIC": float(ajuste.resultado.bic),
        "convergiu": ajuste.convergiu,
        "segundos_ajuste": ajuste.segundos,
        "avisos": ajuste.avisos,
        "MAE": float(previsoes.erro_absoluto_sarimax.mean()),
    }
