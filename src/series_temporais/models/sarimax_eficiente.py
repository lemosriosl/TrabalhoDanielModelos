"""Walk-forward SARIMAX incremental para séries longas."""

from __future__ import annotations

from time import perf_counter

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .sarimax import SarimaxConfig, metricas_previsao


def avaliar_incremental(
    serie: pd.Series, inicio_avaliacao: pd.Timestamp, config: SarimaxConfig
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Prevê um passo, revela o alvo e atualiza apenas o estado do filtro.

    ``extend`` conserva o estado filtrado sem reconstruir todo o histórico a
    cada hora. Ausências no alvo entram como ausências reais, nunca imputadas.
    """
    y = pd.Series(serie, copy=True).astype(float)
    if not isinstance(y.index, pd.DatetimeIndex) or y.index.has_duplicates or not y.index.is_monotonic_increasing:
        raise ValueError("A série requer DatetimeIndex crescente e sem duplicidades.")
    inicio = pd.Timestamp(inicio_avaliacao)
    primeira = int(y.index.searchsorted(inicio))
    if primeira <= 0 or primeira >= len(y):
        raise ValueError("Avaliação sem treino ou sem período posterior.")
    treino = y.iloc[:primeira]
    inicio_ajuste = perf_counter()
    resultado = SARIMAX(
        treino,
        order=config.order,
        seasonal_order=config.seasonal_order,
        trend=config.trend,
        enforce_stationarity=config.enforce_stationarity,
        enforce_invertibility=config.enforce_invertibility,
    ).fit(disp=False)
    segundos_ajuste = perf_counter() - inicio_ajuste
    ultimo_observado = treino.dropna().index.max()
    linhas: list[dict[str, object]] = []
    inicio_walk = perf_counter()
    passo = y.index[1] - y.index[0]
    for posicao in range(primeira, len(y)):
        alvo_tempo = y.index[posicao]
        previsao = float(resultado.get_forecast(steps=1).predicted_mean.iloc[0])
        real = y.iloc[posicao]
        if pd.notna(real):
            linhas.append({
                "origin_time": alvo_tempo - passo,
                "target_time": alvo_tempo,
                "y_true": float(real),
                "y_pred_sarimax": previsao,
                "residuo_sarimax": float(real - previsao),
                "training_target_cutoff": ultimo_observado,
            })
            ultimo_observado = alvo_tempo
        novo = pd.Series([real], index=pd.DatetimeIndex([alvo_tempo]), name=y.name)
        resultado = resultado.extend(novo)
    previsoes = pd.DataFrame(linhas)
    if previsoes.empty or not (previsoes.training_target_cutoff < previsoes.target_time).all():
        raise AssertionError("Previsões inválidas ou com vazamento temporal.")
    previsoes["erro_absoluto_sarimax"] = previsoes.residuo_sarimax.abs()
    previsoes["erro_quadratico_sarimax"] = previsoes.residuo_sarimax.pow(2)
    registro: dict[str, object] = {
        "ordem": str(config.order), "ordem_sazonal": str(config.seasonal_order),
        "observacoes_treino_grade": len(treino), "observacoes_treino_observadas": int(treino.notna().sum()),
        "observacoes_avaliadas": len(previsoes), "lacunas_na_avaliacao": int(y.iloc[primeira:].isna().sum()),
        "segundos_ajuste_inicial": segundos_ajuste, "segundos_walk_forward": perf_counter() - inicio_walk,
    }
    registro.update(metricas_previsao(previsoes))
    return previsoes, registro
