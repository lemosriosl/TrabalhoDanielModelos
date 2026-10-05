"""Variante rápida e explicitamente provisória das cinco pipelines SARIMAX.

O protocolo oficial reestima o modelo em cada origem. Esta variante ajusta os
coeficientes uma única vez na partição inicial e apenas atualiza o estado do
filtro depois que cada alvo é revelado. Assim, ela preserva causalidade,
horizonte e origens do recorte SARIMAX, mas não substitui o resultado oficial.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX

from series_temporais.data.preparacao_base5 import ALVO_CANONICO, preparar_modelagem_ouro
from series_temporais.paths import project_root as find_project_root


@dataclass(frozen=True)
class FastConfig:
    base_id: str
    time_col: str
    target_col: str
    primary_col: str
    frequency: str
    train_ratio: float
    seasonal_lag: int
    tuning_rows: int
    differencing: int


CONFIGS = {
    1: FastConfig("base_01", "Date", "Close", "Open", "D", 0.70, 7, 730, 1),
    2: FastConfig("base_02", "date_time", "traffic_volume", "temp", "h", 0.80, 24, 336, 1),
    3: FastConfig("base_03", "datetime", "PM2.5", "TEMP", "h", 0.80, 24, 336, 1),
    4: FastConfig("base_04", "Date Time", "T (degC)", "Tpot (K)", "10min", 0.80, 144, 288, 1),
    5: FastConfig("base_05", "DATE", ALVO_CANONICO, "treasury_10y_t", "W-FRI", 0.75, 52, 104, 0),
}

FAST_PROTOCOL = "fast_state_update"
FAST_WARNING = (
    "provisorio: ajuste unico no treino inicial e atualizacao de estado sem "
    "reestimacao por origem; nao entra no ranking oficial"
)


def _calendar_features(index: pd.DatetimeIndex, frequency: str) -> pd.DataFrame:
    if frequency in {"h", "10min"}:
        position = index.hour + index.minute / 60
        period = 24.0
    elif frequency == "D":
        position = index.dayofweek
        period = 7.0
    else:
        position = index.isocalendar().week.to_numpy(dtype=float) - 1
        period = 52.0
    return pd.DataFrame(
        {
            "calendar_sin": np.sin(2 * np.pi * position / period),
            "calendar_cos": np.cos(2 * np.pi * position / period),
            "dezembro": (index.month == 12).astype(float),
        },
        index=index,
    )


def _prepare_standard_base(
    config: FastConfig,
    root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(root / "data" / config.base_id / "prepared.csv")
    required = [config.time_col, config.target_col, config.primary_col]
    missing = sorted(set(required).difference(raw.columns))
    if missing:
        raise KeyError(f"{config.base_id}: colunas ausentes: {missing}")
    raw[config.time_col] = pd.to_datetime(raw[config.time_col], errors="raise")
    raw[config.target_col] = pd.to_numeric(raw[config.target_col], errors="coerce")
    raw[config.primary_col] = pd.to_numeric(raw[config.primary_col], errors="coerce")
    aggregated = (
        raw.groupby(config.time_col, sort=True)[[config.target_col, config.primary_col]]
        .mean()
        .sort_index()
    )
    frame = pd.DataFrame(index=pd.DatetimeIndex(aggregated.index))
    frame.index.name = "target_time"
    frame["y"] = aggregated[config.target_col]
    frame["primary_lag_1"] = aggregated[config.primary_col].shift(1)
    frame = frame.join(_calendar_features(frame.index, config.frequency))
    frame = frame.dropna(subset=["y", "primary_lag_1"])
    frame["seasonal_lag"] = frame["y"].shift(config.seasonal_lag)
    frame["origin_time"] = frame.index.to_series().shift(1)
    frame = frame.dropna(subset=["origin_time"])

    cut = int(len(frame) * config.train_ratio)
    train = frame.iloc[:cut].copy()
    test = frame.iloc[cut:].copy()
    train = train.dropna(subset=["seasonal_lag"])
    if test["seasonal_lag"].isna().any():
        raise ValueError(f"{config.base_id}: histórico insuficiente para a sazonalidade.")
    return train, test


def _prepare_base5(
    config: FastConfig,
    root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(root / "data" / config.base_id / "raw.csv")
    _, _, _, canonical_train, canonical_test = preparar_modelagem_ouro(raw)

    def convert(frame: pd.DataFrame) -> pd.DataFrame:
        index = pd.DatetimeIndex(pd.to_datetime(frame["DATE"], errors="raise"))
        converted = pd.DataFrame(index=index)
        converted.index.name = "origin_time"
        converted["target_time"] = pd.to_datetime(frame["target_date"], errors="raise").to_numpy()
        converted["y"] = frame[ALVO_CANONICO].to_numpy(dtype=float)
        converted["primary_lag_1"] = frame[config.primary_col].to_numpy(dtype=float)
        converted = converted.join(_calendar_features(index, config.frequency))
        return converted

    full = convert(pd.concat([canonical_train, canonical_test], ignore_index=True))
    full["seasonal_lag"] = full["y"].shift(config.seasonal_lag)
    train = full.iloc[: len(canonical_train)].dropna(subset=["seasonal_lag"]).copy()
    test = full.iloc[len(canonical_train) :].copy()
    if test["seasonal_lag"].isna().any():
        raise ValueError("base_05: histórico insuficiente para a sazonalidade.")
    return train, test


def prepare_fast_frame(
    base_number: int,
    root: str | Path | None = None,
) -> tuple[FastConfig, pd.DataFrame, pd.DataFrame]:
    """Prepara treino e teste sem consultar alvos futuros como features."""

    if base_number not in CONFIGS:
        raise ValueError("base_number deve estar entre 1 e 5.")
    project_root = Path(root) if root is not None else find_project_root()
    config = CONFIGS[base_number]
    if base_number == 5:
        train, test = _prepare_base5(config, project_root)
    else:
        train, test = _prepare_standard_base(config, project_root)
    if train.empty or test.empty:
        raise ValueError(f"{config.base_id}: treino ou teste vazio.")
    return config, train, test


def _orders(config: FastConfig) -> list[tuple[int, int, int]]:
    d = config.differencing
    return [(0, d, 0), (1, d, 0), (0, d, 1), (1, d, 1)]


EXOG_SETS = {
    "primary": ["primary_lag_1"],
    "calendar": ["calendar_sin", "calendar_cos", "dezembro"],
    "primary_calendar": ["primary_lag_1", "calendar_sin", "calendar_cos", "dezembro"],
    "seasonal_lag": ["seasonal_lag"],
    "all": ["primary_lag_1", "calendar_sin", "calendar_cos", "dezembro", "seasonal_lag"],
}


def _fit(
    y: np.ndarray,
    exog: np.ndarray | None,
    order: tuple[int, int, int],
    maxiter: int,
):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return SARIMAX(
            y,
            exog=exog,
            order=order,
            seasonal_order=(0, 0, 0, 0),
            trend="n",
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False, maxiter=maxiter)


def _folds(length: int, seasonal_lag: int) -> list[tuple[slice, slice]]:
    horizon = max(4, min(24, seasonal_lag))
    first_validation = length - 3 * horizon
    if first_validation < 40:
        horizon = max(2, (length - 40) // 3)
        first_validation = length - 3 * horizon
    return [
        (slice(0, first_validation + fold * horizon), slice(first_validation + fold * horizon, first_validation + (fold + 1) * horizon))
        for fold in range(3)
    ]


def _score_candidates(
    train: pd.DataFrame,
    config: FastConfig,
    exog_options: dict[str, list[str]],
    verbose: bool,
) -> pd.DataFrame:
    tuning = train.tail(max(config.tuning_rows, config.seasonal_lag + 80)).copy()
    rows: list[dict[str, Any]] = []
    for exog_name, exog_cols in exog_options.items():
        for order in _orders(config):
            started = perf_counter()
            fold_maes: list[float] = []
            converged = True
            try:
                for fit_slice, validation_slice in _folds(len(tuning), config.seasonal_lag):
                    fit_frame = tuning.iloc[fit_slice]
                    validation = tuning.iloc[validation_slice]
                    x_fit = x_validation = None
                    if exog_cols:
                        scaler = StandardScaler()
                        x_fit = scaler.fit_transform(fit_frame[exog_cols])
                        x_validation = scaler.transform(validation[exog_cols])
                    fitted = _fit(fit_frame["y"].to_numpy(dtype=float), x_fit, order, maxiter=35)
                    converged = converged and bool(fitted.mle_retvals.get("converged", True))
                    predicted = np.asarray(
                        fitted.get_forecast(len(validation), exog=x_validation).predicted_mean,
                        dtype=float,
                    )
                    fold_maes.append(float(np.mean(np.abs(validation["y"].to_numpy(dtype=float) - predicted))))
            except (ValueError, np.linalg.LinAlgError) as exc:
                fold_maes = [float("inf")]
                converged = False
                error = type(exc).__name__
            else:
                error = ""
            row = {
                "order": order,
                "exog_name": exog_name,
                "exog_cols": exog_cols,
                "validation_mae": float(np.mean(fold_maes)),
                "converged": converged,
                "elapsed_seconds": perf_counter() - started,
                "error": error,
            }
            rows.append(row)
            if verbose:
                print(f"{config.base_id} | {exog_name:16s} | {order} | MAE={row['validation_mae']:.6f} | {row['elapsed_seconds']:.2f}s")
    ranking = pd.DataFrame(rows).sort_values(["validation_mae", "elapsed_seconds"], kind="stable")
    if not np.isfinite(ranking["validation_mae"]).any():
        raise RuntimeError(f"{config.base_id}: nenhum candidato rápido foi ajustado.")
    return ranking.reset_index(drop=True)


def _walk_forward_fixed_parameters(
    train: pd.DataFrame,
    test: pd.DataFrame,
    order: tuple[int, int, int],
    exog_cols: list[str],
) -> tuple[pd.DataFrame, bool, float]:
    started = perf_counter()
    x_train = x_test = None
    if exog_cols:
        scaler = StandardScaler()
        x_train = scaler.fit_transform(train[exog_cols])
        x_test = scaler.transform(test[exog_cols])
    fitted = _fit(train["y"].to_numpy(dtype=float), x_train, order, maxiter=60)
    converged = bool(fitted.mle_retvals.get("converged", True))
    predictions: list[float] = []
    for position, y_true in enumerate(test["y"].to_numpy(dtype=float)):
        next_exog = None if x_test is None else x_test[position : position + 1]
        y_pred = float(np.asarray(fitted.get_forecast(1, exog=next_exog).predicted_mean)[0])
        if not np.isfinite(y_pred):
            raise ValueError("A previsão rápida deve ser finita.")
        predictions.append(y_pred)
        fitted = fitted.extend([y_true], exog=next_exog)

    prediction_frame = pd.DataFrame(
        {
            "origin_time": pd.to_datetime(test.index if test.index.name == "origin_time" else test["origin_time"]),
            "target_time": pd.to_datetime(test["target_time"] if "target_time" in test else test.index),
            "y_true": test["y"].to_numpy(dtype=float),
            "y_pred": predictions,
        }
    )
    return prediction_frame, converged, perf_counter() - started


def _metric_values(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float]:
    mae = float(np.mean(np.abs(y_true - y_pred)))
    nonzero = np.abs(y_true) > np.finfo(float).eps
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100) if nonzero.any() else float("nan")
    return mae, mape


def _metric_row(
    config: FastConfig,
    model: str,
    predictions: pd.DataFrame,
    train_rows: int,
    order: tuple[int, int, int] | None,
    exog_cols: list[str],
    candidates: int,
    converged: bool,
    elapsed_seconds: float,
) -> dict[str, Any]:
    mae, mape = _metric_values(predictions["y_true"].to_numpy(dtype=float), predictions["y_pred"].to_numpy(dtype=float))
    return {
        "base_id": config.base_id,
        "modelo": model,
        "protocolo": FAST_PROTOCOL,
        "alvo": config.target_col,
        "frequencia": config.frequency,
        "treino_inicial": train_rows,
        "origens_avaliadas": len(predictions),
        "horizonte_passos": 1,
        "mae": mae,
        "mape": mape,
        "order": "" if order is None else str(order),
        "features_exogenas": ";".join(exog_cols),
        "candidatos_tuning": candidates,
        "convergiu": converged,
        "tempo_segundos": elapsed_seconds,
        "comparabilidade": FAST_WARNING,
    }


def run_fast_pipeline(
    base_number: int,
    root: str | Path | None = None,
    verbose: bool = True,
) -> dict[str, pd.DataFrame]:
    """Executa baseline, SARIMA e SARIMAX rápidos para uma base."""

    config, train, test = prepare_fast_frame(base_number, root=root)
    if verbose:
        print(f"{config.base_id}: treino={len(train):,}; teste={len(test):,}; sazonalidade causal={config.seasonal_lag}")

    sarima_ranking = _score_candidates(train, config, {"none": []}, verbose)
    sarimax_ranking = _score_candidates(train, config, EXOG_SETS, verbose)
    best_sarima = sarima_ranking.iloc[0]
    best_sarimax = sarimax_ranking.iloc[0]

    sarima_predictions, sarima_converged, sarima_seconds = _walk_forward_fixed_parameters(train, test, tuple(best_sarima["order"]), [])
    sarimax_features = list(best_sarimax["exog_cols"])
    sarimax_predictions, sarimax_converged, sarimax_seconds = _walk_forward_fixed_parameters(train, test, tuple(best_sarimax["order"]), sarimax_features)

    y_true = test["y"].to_numpy(dtype=float)
    baseline_pred = np.zeros(len(test), dtype=float) if config.differencing == 0 else np.r_[train["y"].iloc[-1], y_true[:-1]]
    baseline_predictions = sarima_predictions.copy()
    baseline_predictions["y_pred"] = baseline_pred
    baseline_name = "Baseline_retorno_zero" if config.differencing == 0 else "Baseline_persistencia"

    comparison = pd.DataFrame(
        [
            _metric_row(config, baseline_name, baseline_predictions, len(train), None, [], 0, True, 0.0),
            _metric_row(config, "SARIMA_fast", sarima_predictions, len(train), tuple(best_sarima["order"]), [], len(sarima_ranking), sarima_converged, sarima_seconds),
            _metric_row(config, "SARIMAX_fast", sarimax_predictions, len(train), tuple(best_sarimax["order"]), sarimax_features, len(sarimax_ranking), sarimax_converged, sarimax_seconds),
        ]
    ).sort_values("mae", kind="stable")
    comparison["ranking_na_base"] = np.arange(1, len(comparison) + 1)
    comparison = comparison.reset_index(drop=True)
    predictions = pd.concat(
        [
            baseline_predictions.assign(modelo=baseline_name),
            sarima_predictions.assign(modelo="SARIMA_fast"),
            sarimax_predictions.assign(modelo="SARIMAX_fast"),
        ],
        ignore_index=True,
    )
    if verbose:
        print("\nResultado provisório — não substitui o walk-forward oficial:")
        print(comparison[["modelo", "mae", "mape", "order", "features_exogenas"]].to_string(index=False))
    return {
        "comparison": comparison,
        "predictions": predictions,
        "sarima_ranking": sarima_ranking,
        "sarimax_ranking": sarimax_ranking,
    }


def upsert_fast_metrics(
    comparison: pd.DataFrame,
    root: str | Path | None = None,
) -> Path:
    """Atualiza o único consolidado provisório gerado pelas execuções rápidas."""

    project_root = Path(root) if root is not None else find_project_root()
    destination = project_root / "results" / "sarimax_fast_metrics.csv"
    current = pd.read_csv(destination) if destination.exists() else pd.DataFrame()
    base_id = str(comparison["base_id"].iloc[0])
    if not current.empty:
        current = current.loc[current["base_id"].astype(str) != base_id]
    merged = pd.concat([current, comparison], ignore_index=True)
    merged = merged.sort_values(["base_id", "ranking_na_base"], kind="stable")
    merged.to_csv(destination, index=False)
    return destination
