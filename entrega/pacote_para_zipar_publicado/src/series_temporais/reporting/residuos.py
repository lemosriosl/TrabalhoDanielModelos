"""Exportação reproduzível das previsões individuais do XGBoost."""

from pathlib import Path

import numpy as np
import pandas as pd


def salvar_residuos_nivel(predictions: pd.DataFrame, root: Path, base: int,
                         *, expected_rows: int, smoke: bool = False) -> Path:
    """Salva todas as previsões das Bases 1–4 sem modificar o quadro recebido."""
    if base not in (1, 2, 3, 4):
        raise ValueError("Use o exportador específico para a Base 5.")
    required = ["origin_time", "target_time", "y_true", "y_pred_xgb",
                "y_pred_persistencia", "residuo_xgb", "model_refit_origin",
                "training_target_cutoff"]
    missing = set(required).difference(predictions.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    frame = predictions.copy()
    if len(frame) != expected_rows or expected_rows <= 0:
        raise ValueError("Quantidade de previsões incompatível com o teste.")
    origins = pd.to_datetime(frame.origin_time)
    targets = pd.to_datetime(frame.target_time)
    cutoffs = pd.to_datetime(frame.training_target_cutoff)
    refits = pd.to_datetime(frame.model_refit_origin)
    if any(values.isna().any() for values in (origins, targets, cutoffs, refits)):
        raise ValueError("Datas ausentes.")
    if not origins.is_monotonic_increasing or origins.duplicated().any():
        raise ValueError("Origens fora de ordem ou duplicadas.")
    if not ((targets > origins) & (cutoffs <= refits) & (refits <= origins)).all():
        raise ValueError("Previsões sem causalidade temporal.")
    if not np.isfinite(frame[required[2:6]].to_numpy(dtype=float)).all():
        raise ValueError("Valores não finitos.")
    if not np.allclose(frame.residuo_xgb, frame.y_true - frame.y_pred_xgb):
        raise ValueError("Resíduos inconsistentes.")
    frame["erro_absoluto_xgb"] = frame.residuo_xgb.abs()
    frame["erro_quadratico_xgb"] = frame.residuo_xgb.pow(2)
    directory = Path(root) / "results" / "residuals"
    directory.mkdir(parents=True, exist_ok=True)
    suffix = "_smoke" if smoke else ""
    path = directory / f"base_{base:02d}_XGBoost{suffix}.csv"
    frame.to_csv(path, index=False, encoding="utf-8")
    return path


def salvar_residuos_base5(predictions: pd.DataFrame, root: Path, *,
                         smoke: bool = False, expected_rows: int = 586) -> Path:
    """Exporta o alvo canônico em retorno e sua conversão para preço."""
    required = ["DATE", "target_date", "price_t", "target_price_t_plus_1",
                "y_true_return", "y_pred_return_xgb", "y_pred_return_zero",
                "residual_return_xgb", "price_pred_xgb",
                "price_pred_persistencia", "residual_price_xgb",
                "target_has_new_quote", "price_was_carried",
                "model_refit_origin", "training_target_cutoff"]
    missing = set(required).difference(predictions.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    frame = predictions.copy()
    origins = pd.to_datetime(frame.DATE)
    targets = pd.to_datetime(frame.target_date)
    cutoffs = pd.to_datetime(frame.training_target_cutoff)
    refits = pd.to_datetime(frame.model_refit_origin)
    if any(values.isna().any() for values in (origins, targets, cutoffs, refits)):
        raise ValueError("Datas ausentes.")
    if not origins.is_monotonic_increasing or origins.duplicated().any():
        raise ValueError("Origens fora de ordem ou duplicadas.")
    if not ((targets > origins) & (cutoffs <= refits) & (refits <= origins)).all():
        raise ValueError("Previsões sem causalidade temporal.")
    numeric = required[2:13]
    if not np.isfinite(frame[numeric].to_numpy(dtype=float)).all():
        raise ValueError("Valores não finitos.")
    if not frame[["price_t", "target_price_t_plus_1", "price_pred_xgb", "price_pred_persistencia"]].gt(0).all().all():
        raise ValueError("Preços devem ser positivos.")
    if not frame[["target_has_new_quote", "price_was_carried"]].isin([0, 1]).all().all():
        raise ValueError("Indicadores de cobertura inválidos.")
    if not np.allclose(frame.price_pred_xgb, frame.price_t * np.exp(frame.y_pred_return_xgb)):
        raise ValueError("Conversão retorno–preço inconsistente.")
    if not np.allclose(frame.y_true_return, np.log(frame.target_price_t_plus_1 / frame.price_t)):
        raise ValueError("Retorno real inconsistente com os preços.")
    if not np.allclose(frame.y_pred_return_zero, 0) or not np.allclose(frame.price_pred_persistencia, frame.price_t):
        raise ValueError("Persistência inconsistente.")
    if not np.allclose(frame.residual_price_xgb, frame.target_price_t_plus_1 - frame.price_pred_xgb):
        raise ValueError("Resíduos inconsistentes.")
    if not np.allclose(frame.residual_return_xgb, frame.y_true_return - frame.y_pred_return_xgb):
        raise ValueError("Resíduos em retorno inconsistentes.")
    if expected_rows <= 0 or len(frame) != expected_rows:
        raise ValueError(f"Esperadas {expected_rows} linhas; obtidas {len(frame)}.")
    for scale in ("return", "price"):
        frame[f"absolute_error_{scale}_xgb"] = frame[f"residual_{scale}_xgb"].abs()
        frame[f"squared_error_{scale}_xgb"] = frame[f"residual_{scale}_xgb"].pow(2)
    directory = Path(root) / "results" / "residuals"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("base_05_XGBoost_smoke.csv" if smoke else "base_05_XGBoost.csv")
    frame.to_csv(path, index=False, encoding="utf-8")
    return path
