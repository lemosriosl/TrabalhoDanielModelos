import numpy as np
import pandas as pd
import pytest

from series_temporais.validation import (
    purged_time_series_splits,
    validate_prediction_frame,
    walk_forward_callback,
    walk_forward_refit,
)


class LastValueRegressor:
    def fit(self, x, y):
        self.last_target = float(y.iloc[-1])
        return self

    def predict(self, x):
        return np.repeat(self.last_target, len(x))


def _frames():
    dates = pd.date_range("2024-01-01", periods=7, freq="D")
    frame = pd.DataFrame(
        {
            "origin": dates[:-1],
            "target_time": dates[1:],
            "y": np.arange(1.0, 7.0),
            "x": np.arange(10.0, 16.0),
        }
    )
    return frame.iloc[:3].copy(), frame.iloc[3:].copy()


def test_refit_walk_forward_uses_only_revealed_targets():
    train, test = _frames()
    predictions, fits = walk_forward_refit(
        train,
        test,
        origin_col="origin",
        target_time_col="target_time",
        target_col="y",
        feature_cols=["x"],
        estimator_factory=LastValueRegressor,
    )
    assert len(predictions) == len(test) == len(fits)
    assert (predictions.training_target_cutoff <= predictions.origin_time).all()
    assert fits.training_rows.tolist() == [3, 4, 5]
    assert predictions.y_pred.tolist() == [3.0, 4.0, 5.0]


def test_callback_walk_forward_receives_only_past_history():
    train, test = _frames()
    sizes = []

    def predict_one(history, row):
        sizes.append(len(history))
        return history.y.iloc[-1]

    predictions = walk_forward_callback(
        train,
        test,
        origin_col="origin",
        target_time_col="target_time",
        target_col="y",
        predict_one=predict_one,
    )
    assert sizes == [3, 4, 5]
    assert predictions.y_pred.tolist() == [3.0, 4.0, 5.0]


@pytest.mark.parametrize("interval,expected_fits", [(1, 3), (2, 2), (10, 1)])
def test_periodic_refit_preserves_all_origins(interval, expected_fits):
    train, test = _frames()
    predictions, fits = walk_forward_refit(
        train, test, origin_col="origin", target_time_col="target_time",
        target_col="y", feature_cols=["x"], estimator_factory=LastValueRegressor,
        refit_every=interval,
    )
    assert len(predictions) == len(test)
    assert len(fits) == expected_fits
    assert predictions.origin_time.tolist() == test.origin.tolist()
    assert predictions.target_time.tolist() == test.target_time.tolist()
    assert (predictions.training_target_cutoff <= predictions.model_refit_origin).all()
    assert (predictions.model_refit_origin <= predictions.origin_time).all()
    if interval == 2:
        assert predictions.y_pred.tolist() == [3.0, 3.0, 5.0]
        assert fits.training_rows.tolist() == [3, 5]


@pytest.mark.parametrize("interval", [0, -1, 1.5, True])
def test_periodic_refit_rejects_invalid_interval(interval):
    train, test = _frames()
    with pytest.raises(ValueError, match="inteiro positivo"):
        walk_forward_refit(
            train, test, origin_col="origin", target_time_col="target_time",
            target_col="y", feature_cols=["x"], estimator_factory=LastValueRegressor,
            refit_every=interval,
        )


def test_periodic_refit_uses_current_features_not_recursive_predictions():
    class FeatureRegressor(LastValueRegressor):
        def predict(self, x):
            return np.asarray(x["x"], dtype=float) + self.last_target
    train, test = _frames()
    predictions, fits = walk_forward_refit(
        train, test, origin_col="origin", target_time_col="target_time",
        target_col="y", feature_cols=["x"], estimator_factory=FeatureRegressor,
        refit_every=2,
    )
    assert predictions.y_pred.tolist() == [16.0, 17.0, 20.0]
    assert len(fits) == 2


def test_walk_forward_rejects_training_target_at_test_origin():
    train, test = _frames()
    train.loc[train.index[-1], "target_time"] = test.origin.iloc[0] + pd.Timedelta(days=1)
    with pytest.raises(ValueError, match="alcança"):
        walk_forward_refit(
            train,
            test,
            origin_col="origin",
            target_time_col="target_time",
            target_col="y",
            feature_cols=["x"],
            estimator_factory=LastValueRegressor,
        )


def test_prediction_contract_rejects_noncausal_cutoff():
    bad = pd.DataFrame(
        {
            "origin_time": ["2024-01-02"],
            "target_time": ["2024-01-03"],
            "training_target_cutoff": ["2024-01-03"],
            "y_true": [1.0],
            "y_pred": [1.0],
        }
    )
    with pytest.raises(ValueError, match="informação futura"):
        validate_prediction_frame(bad)


def test_temporal_purge_keeps_target_revealed_at_validation_origin():
    origins = pd.date_range("2024-01-01", periods=8, freq="D")
    targets = origins + pd.Timedelta(days=1)
    train_idx, validation_idx = purged_time_series_splits(origins, targets, n_splits=2)[0]
    first_validation_origin = origins[validation_idx[0]]
    assert targets[train_idx].max() == first_validation_origin
