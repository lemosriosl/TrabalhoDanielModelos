"""Diagnóstico de importância em janelas fora da amostra, separado do ajuste."""

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


def importancia_temporal(model, window, features, target_col, *, origin_col,
                         training_cutoff, refit_origin, n_repeats=3, seed=42):
    """Retorna importância para um modelo fixo; não treina nem altera parâmetros."""
    if len(window) < 2:
        return []
    origins = pd.to_datetime(window[origin_col])
    cutoff, refit = pd.Timestamp(training_cutoff), pd.Timestamp(refit_origin)
    if origins.isna().any() or not origins.is_monotonic_increasing:
        raise ValueError("Janela diagnóstica fora de ordem ou com datas ausentes.")
    if cutoff > refit or origins.min() < refit:
        raise ValueError("Janela de importância não está fora da amostra.")
    perm = permutation_importance(
        model, window[features], window[target_col], scoring="neg_mean_absolute_error",
        n_repeats=n_repeats, random_state=seed, n_jobs=1,
    )
    gain = np.asarray(model.feature_importances_, dtype=float)
    return [{
        "model_refit_origin": refit, "feature": feature,
        "gain": float(gain[pos]),
        "permutation_mean": float(perm.importances_mean[pos]),
        "permutation_std": float(perm.importances_std[pos]),
        "diagnostic_rows": len(window),
        "diagnostic_last_origin": origins.max(),
    } for pos, feature in enumerate(features)]
