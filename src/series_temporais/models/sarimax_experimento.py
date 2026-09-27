"""Rotinas reutilizáveis de seleção e avaliação causal de SARIMAX.

Aceita lacunas no alvo: elas são assimiladas como observações ausentes no
estado do modelo e jamais recebem imputação. Apenas alvos efetivamente
observados compõem previsões avaliadas, métricas e diagnósticos.
"""

from __future__ import annotations

from time import perf_counter

import pandas as pd

from .sarimax import SarimaxConfig, ajustar_sarimax, metricas_previsao


def walk_forward_horario(
    serie: pd.Series,
    inicio_avaliacao: pd.Timestamp,
    config: SarimaxConfig,
) -> tuple[pd.DataFrame, dict[str, float | int | str | None]]:
    """Avalia um passo à frente sem revelar alvos futuros ao modelo.

    A série deve possuir índice temporal regular e ordenado. Valores ausentes
    no alvo são permitidos para representar lacunas reais; não são pontuados.
    """
    y = pd.Series(serie, copy=True).astype(float)
    if not isinstance(y.index, pd.DatetimeIndex):
        raise TypeError("A série deve possuir DatetimeIndex.")
    if y.index.has_duplicates or not y.index.is_monotonic_increasing:
        raise ValueError("A série precisa estar ordenada e sem timestamps duplicados.")
    inicio = pd.Timestamp(inicio_avaliacao)
    primeira_posicao = int(y.index.searchsorted(inicio))
    if primeira_posicao <= 0 or primeira_posicao >= len(y):
        raise ValueError("A avaliação precisa preservar treino e período posterior.")
    treino = y.iloc[:primeira_posicao]
    if treino.notna().sum() == 0:
        raise ValueError("O treino não possui alvo observado.")

    inicio_tempo = perf_counter()
    resultado = ajustar_sarimax_sem_exogenas(treino, config)
    segundos_ajuste = perf_counter() - inicio_tempo
    linhas: list[dict[str, object]] = []
    ultimo_alvo_observado = treino.dropna().index.max()
    inicio_walk = perf_counter()

    for posicao in range(primeira_posicao, len(y)):
        target_time = y.index[posicao]
        previsao = float(resultado.get_forecast(steps=1).predicted_mean.iloc[0])
        real = y.iloc[posicao]
        if pd.notna(real):
            linhas.append(
                {
                    "origin_time": target_time - (y.index[1] - y.index[0]),
                    "target_time": target_time,
                    "y_true": float(real),
                    "y_pred_sarimax": previsao,
                    "residuo_sarimax": float(real - previsao),
                    "training_target_cutoff": ultimo_alvo_observado,
                }
            )
            ultimo_alvo_observado = target_time
        novo = pd.Series([real], index=pd.DatetimeIndex([target_time]), name=y.name)
        resultado = resultado.append(novo, refit=False)

    previsoes = pd.DataFrame(linhas)
    if previsoes.empty:
        raise ValueError("Não há alvo observado no período de avaliação.")
    previsoes["erro_absoluto_sarimax"] = previsoes["residuo_sarimax"].abs()
    previsoes["erro_quadratico_sarimax"] = previsoes["residuo_sarimax"].pow(2)
    if not (previsoes["training_target_cutoff"] < previsoes["target_time"]).all():
        raise AssertionError("A previsão consultou o alvo da própria data.")
    registro: dict[str, float | int | str | None] = {
        "ordem": str(config.order),
        "ordem_sazonal": str(config.seasonal_order),
        "tendencia": config.trend,
        "observacoes_treino_grade": int(len(treino)),
        "observacoes_treino_observadas": int(treino.notna().sum()),
        "observacoes_avaliadas": int(len(previsoes)),
        "lacunas_na_avaliacao": int(y.iloc[primeira_posicao:].isna().sum()),
        "segundos_ajuste_inicial": segundos_ajuste,
        "segundos_walk_forward": perf_counter() - inicio_walk,
    }
    registro.update(metricas_previsao(previsoes))
    return previsoes, registro


def ajustar_sarimax_sem_exogenas(serie: pd.Series, config: SarimaxConfig):
    """Ajusta SARIMAX univariado, permitindo alvo ausente no filtro de estado."""
    if serie.dropna().empty:
        raise ValueError("Não há observações para ajustar o SARIMAX.")
    # ``ajustar_sarimax`` protege a versão sem lacunas; aqui a lacuna é uma
    # informação explícita de ausência, suportada pelo filtro de Kalman.
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    modelo = SARIMAX(
        serie,
        order=config.order,
        seasonal_order=config.seasonal_order,
        trend=config.trend,
        enforce_stationarity=config.enforce_stationarity,
        enforce_invertibility=config.enforce_invertibility,
    )
    return modelo.fit(disp=False)


def selecionar_ordem(
    serie_treino: pd.Series,
    inicio_validacao: pd.Timestamp,
    candidatas: list[SarimaxConfig],
) -> tuple[SarimaxConfig, pd.DataFrame]:
    """Compara configurações só na validação interna temporal por MAE."""
    linhas: list[dict[str, object]] = []
    for numero, config in enumerate(candidatas, start=1):
        previsoes, registro = walk_forward_horario(serie_treino, inicio_validacao, config)
        linhas.append(
            {
                "candidato": numero,
                "ordem": registro["ordem"],
                "ordem_sazonal": registro["ordem_sazonal"],
                "MAE_validacao": registro["MAE"],
                "RMSE_validacao": registro["RMSE"],
                "observacoes_avaliadas": registro["observacoes_avaliadas"],
                "segundos_total": registro["segundos_ajuste_inicial"] + registro["segundos_walk_forward"],
            }
        )
    tabela = pd.DataFrame(linhas).sort_values(["MAE_validacao", "candidato"]).reset_index(drop=True)
    escolhida = candidatas[int(tabela.loc[0, "candidato"]) - 1]
    return escolhida, tabela
