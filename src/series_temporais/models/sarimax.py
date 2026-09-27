"""SARIMAX causal para séries temporais com avaliação passo a passo.

O módulo não define horizonte, recorte de teste ou candidatos de tuning: essas
decisões pertencem ao protocolo comum do grupo. Ele recebe tais decisões de
quem orquestra o experimento e impede que a previsão consulte o alvo futuro.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX


@dataclass(frozen=True)
class SarimaxConfig:
    """Configuração congelável de um SARIMAX."""

    order: tuple[int, int, int]
    seasonal_order: tuple[int, int, int, int] = (0, 0, 0, 0)
    trend: str | None = None
    enforce_stationarity: bool = False
    enforce_invertibility: bool = False


def exogenas_defasadas(exogenas: pd.DataFrame, passos: int = 1) -> pd.DataFrame:
    """Alinha medições observadas no passado ao alvo futuro.

    A linha em ``t`` da saída carrega o valor observado em ``t-passos``. Assim,
    ao prever ``y_t`` a previsão não recebe uma medição observada em ``t``.
    Calendário conhecido antecipadamente pode ser mantido fora desta função.
    """
    if passos < 1:
        raise ValueError("A defasagem deve ser positiva para variáveis observadas.")
    return exogenas.shift(passos)


def _validar_serie(serie: pd.Series) -> pd.Series:
    y = pd.Series(serie, copy=True).astype(float)
    if not isinstance(y.index, pd.DatetimeIndex):
        raise TypeError("A série deve possuir DatetimeIndex.")
    if y.index.has_duplicates or not y.index.is_monotonic_increasing:
        raise ValueError("A série deve estar ordenada e sem timestamps duplicados.")
    if y.isna().any():
        raise ValueError("SARIMAX exige série sem valores ausentes no recorte recebido.")
    return y


def _validar_exogenas(exogenas: pd.DataFrame | None, indice: pd.DatetimeIndex) -> pd.DataFrame | None:
    if exogenas is None:
        return None
    x = exogenas.copy()
    if not x.index.equals(indice):
        raise ValueError("As exógenas devem compartilhar exatamente o índice da série.")
    if x.isna().any().any():
        raise ValueError("Exógenas ausentes precisam ser tratadas causalmente antes do SARIMAX.")
    return x.astype(float)


def ajustar_sarimax(
    serie: pd.Series,
    config: SarimaxConfig,
    exogenas: pd.DataFrame | None = None,
):
    """Ajusta SARIMAX somente nas observações entregues pela origem."""
    y = _validar_serie(serie)
    x = _validar_exogenas(exogenas, y.index)
    model = SARIMAX(
        y,
        exog=x,
        order=config.order,
        seasonal_order=config.seasonal_order,
        trend=config.trend,
        enforce_stationarity=config.enforce_stationarity,
        enforce_invertibility=config.enforce_invertibility,
    )
    return model.fit(disp=False)


def walk_forward_um_passo(
    serie: pd.Series,
    inicio_teste: pd.Timestamp,
    config: SarimaxConfig,
    exogenas: pd.DataFrame | None = None,
    intervalo_refit: int | None = None,
) -> tuple[pd.DataFrame, dict[str, float | int | str | None]]:
    """Gera previsões de um passo com atualização apenas após observar o alvo.

    ``inicio_teste`` é a primeira data cujo alvo será previsto. Um refit, quando
    escolhido pelo protocolo, ocorre antes da previsão e usa somente alvos já
    conhecidos. Entre refits, o filtro de estado recebe o alvo realizado após a
    previsão, preservando a natureza expansiva do walk-forward.
    """
    y = _validar_serie(serie)
    x = _validar_exogenas(exogenas, y.index)
    inicio_teste = pd.Timestamp(inicio_teste)
    first_test = int(y.index.searchsorted(inicio_teste))
    if first_test <= 0 or first_test >= len(y):
        raise ValueError("inicio_teste precisa deixar treino e teste não vazios.")
    if intervalo_refit is not None and intervalo_refit < 1:
        raise ValueError("intervalo_refit deve ser positivo ou None.")

    historico_y = y.iloc[:first_test].copy()
    historico_x = None if x is None else x.iloc[:first_test].copy()
    inicio = perf_counter()
    resultado = ajustar_sarimax(historico_y, config, historico_x)
    segundos_ajuste_inicial = perf_counter() - inicio
    linhas: list[dict[str, object]] = []
    n_refits = 1
    inicio_walk = perf_counter()

    for offset, posicao in enumerate(range(first_test, len(y))):
        target_time = y.index[posicao]
        origin_time = y.index[posicao - 1]
        if intervalo_refit is not None and offset and offset % intervalo_refit == 0:
            resultado = ajustar_sarimax(historico_y, config, historico_x)
            n_refits += 1

        x_target = None if x is None else x.iloc[[posicao]]
        previsao = float(resultado.get_forecast(steps=1, exog=x_target).predicted_mean.iloc[0])
        real = float(y.iloc[posicao])
        linhas.append(
            {
                "origin_time": origin_time,
                "target_time": target_time,
                "y_true": real,
                "y_pred_sarimax": previsao,
                "residuo_sarimax": real - previsao,
                "training_target_cutoff": historico_y.index.max(),
                "model_refit_origin": historico_y.index.max(),
            }
        )
        # A observação entra no estado apenas depois que a previsão foi salva.
        novo_y = pd.Series([real], index=pd.DatetimeIndex([target_time]), name=historico_y.name)
        historico_y = pd.concat([historico_y, novo_y])
        if historico_x is not None:
            historico_x = pd.concat([historico_x, x_target])
        resultado = resultado.append(novo_y, exog=x_target, refit=False)

    previsoes = pd.DataFrame(linhas)
    if not previsoes.empty:
        if not (previsoes["training_target_cutoff"] < previsoes["target_time"]).all():
            raise AssertionError("Foi detectado acesso ao alvo da data prevista.")
        previsoes["erro_absoluto_sarimax"] = previsoes["residuo_sarimax"].abs()
        previsoes["erro_quadratico_sarimax"] = previsoes["residuo_sarimax"].pow(2)

    registro = {
        "ordem": str(config.order),
        "ordem_sazonal": str(config.seasonal_order),
        "tendencia": config.trend,
        "observacoes_treino_inicial": first_test,
        "observacoes_teste": len(previsoes),
        "numero_refits": n_refits,
        "segundos_ajuste_inicial": segundos_ajuste_inicial,
        "segundos_walk_forward": perf_counter() - inicio_walk,
    }
    return previsoes, registro


def metricas_previsao(previsoes: pd.DataFrame) -> dict[str, float]:
    """Calcula métricas somente nas previsões fora da amostra."""
    residuos = previsoes["residuo_sarimax"].astype(float)
    y_true = previsoes["y_true"].astype(float)
    ss_total = float(((y_true - y_true.mean()) ** 2).sum())
    return {
        "MAE": float(residuos.abs().mean()),
        "RMSE": float(np.sqrt((residuos**2).mean())),
        "MedAE": float(residuos.abs().median()),
        "R2": float("nan") if ss_total == 0 else float(1 - (residuos**2).sum() / ss_total),
        "vies_medio": float(residuos.mean()),
    }


def diagnostico_ljung_box(previsoes: pd.DataFrame, lags: Iterable[int]) -> pd.DataFrame:
    """Executa Ljung-Box apenas nos resíduos fora da amostra."""
    residuos = previsoes["residuo_sarimax"].dropna()
    lags_validos = sorted({int(lag) for lag in lags if 0 < int(lag) < len(residuos)})
    if not lags_validos:
        raise ValueError("Não há lags válidos para Ljung-Box.")
    resultado = acorr_ljungbox(residuos, lags=lags_validos, return_df=True)
    resultado["rejeita_ruido_branco_5pct"] = resultado.lb_pvalue < 0.05
    return resultado
