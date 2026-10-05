"""Contratos da execução rápida, que não substitui o protocolo oficial."""

from pathlib import Path

import numpy as np

from series_temporais.models.sarimax_fast import CONFIGS, prepare_fast_frame


ROOT = Path(__file__).resolve().parents[1]


def test_fast_frames_are_causal_and_keep_one_step_origins():
    for base_number in CONFIGS:
        _, train, test = prepare_fast_frame(base_number, root=ROOT)
        assert not train.empty
        assert not test.empty
        origins = test.index if base_number == 5 else test["origin_time"]
        targets = test["target_time"] if base_number == 5 else test.index
        assert (targets.to_numpy() > origins.to_numpy()).all()
        assert np.isfinite(test[["y", "seasonal_lag"]].to_numpy(dtype=float)).all()


def test_fast_seasonal_lag_is_always_from_the_past():
    for base_number, config in CONFIGS.items():
        _, train, test = prepare_fast_frame(base_number, root=ROOT)
        combined = np.r_[train["y"].to_numpy(), test["y"].to_numpy()]
        seasonal = np.r_[
            train["seasonal_lag"].to_numpy(), test["seasonal_lag"].to_numpy()
        ]
        assert config.seasonal_lag >= 1
        assert len(train) > config.seasonal_lag
        assert test["seasonal_lag"].notna().all()
        np.testing.assert_allclose(
            seasonal[config.seasonal_lag :],
            combined[: -config.seasonal_lag],
        )


def test_fast_results_are_explicitly_separate_from_official_metrics():
    source = (ROOT / "src" / "series_temporais" / "models" / "sarimax_fast.py").read_text(encoding="utf-8")
    assert '"results" / "sarimax_fast_metrics.csv"' in source
    assert '"results" / "metrics.csv"' not in source
    assert "nao entra no ranking oficial" in source
