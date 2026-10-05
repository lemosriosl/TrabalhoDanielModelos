import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, RegressorMixin

from series_temporais.reporting.importancias import importancia_temporal


class FixedLinearModel(RegressorMixin, BaseEstimator):
    feature_importances_ = np.array([1.0, 0.0])

    def fit(self, X, y):
        raise AssertionError("Diagnóstico não deve reajustar modelo.")

    def predict(self, X):
        return X["signal"].to_numpy()


def window():
    return pd.DataFrame({"DATE": pd.date_range("2024-01-05", periods=20, freq="D"),
                         "signal": np.arange(20.0), "noise": 1.0, "target": np.arange(20.0)})


def measure(frame, cutoff="2024-01-05"):
    return importancia_temporal(FixedLinearModel(), frame, ["signal", "noise"], "target",
        origin_col="DATE", training_cutoff=cutoff, refit_origin="2024-01-05",
        n_repeats=2, seed=42)


def test_multiline_permutation_detects_signal_and_preserves_input():
    frame = window()
    original = frame.copy()
    rows = measure(frame)
    assert rows[0]["permutation_mean"] > 0
    assert rows[1]["permutation_mean"] == 0
    assert rows[0]["diagnostic_rows"] == 20
    pd.testing.assert_frame_equal(frame, original)
    assert rows == measure(frame)


def test_singleton_is_skipped_instead_of_reported_as_zero():
    assert measure(window().head(1)) == []


def test_future_training_cutoff_is_rejected():
    with pytest.raises(ValueError, match="fora da amostra"):
        measure(window(), cutoff="2024-01-06")
