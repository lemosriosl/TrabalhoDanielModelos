from pathlib import Path

import pandas as pd
import pytest

from series_temporais.reporting.evidencias_relatorio import _prediction_metric, gerar_evidencias


ROOT = Path(__file__).resolve().parents[1]


def test_metric_uses_only_valid_out_of_sample_forecasts(tmp_path):
    path = tmp_path / "forecasts.csv"
    pd.DataFrame({
        "origin_time": ["2020-01-01", "2020-01-02"],
        "target_time": ["2020-01-02", "2020-01-03"],
        "training_target_cutoff": ["2020-01-01", "2020-01-02"],
        "y_true": [2.0, 4.0], "y_pred": [1.0, 2.0],
        "residuo": [1.0, 2.0],
    }).to_csv(path, index=False)
    mae, count, residuals = _prediction_metric(path)
    assert (mae, count, residuals.tolist()) == (1.5, 2, [1.0, 2.0])


@pytest.mark.parametrize("column,value", [
    ("target_time", "2019-12-31"),
    ("training_target_cutoff", "2020-01-03"),
    ("residuo", 99.0),
])
def test_metric_rejects_leakage_and_inconsistent_residuals(tmp_path, column, value):
    path = tmp_path / "forecasts.csv"
    row = {"origin_time": "2020-01-02", "target_time": "2020-01-03",
           "training_target_cutoff": "2020-01-02", "y_true": 2.0,
           "y_pred": 1.0, "residuo": 1.0}
    row[column] = value
    pd.DataFrame([row]).to_csv(path, index=False)
    with pytest.raises(ValueError):
        _prediction_metric(path)


def test_audit_recovers_rf_counts_and_flags_non_comparable_origins():
    metrics, diagnostics, findings = gerar_evidencias(ROOT)
    assert len(metrics) == 19  # SARIMAX 4 deliberately excluded
    assert set(metrics.loc[metrics.modelo.eq("Random Forest"), "origens"]) == {842, 3372, 2847, 82830, 586}
    assert len(diagnostics.query("base_id == 'base_01' and modelo == 'SARIMAX'")) == 4
    sarimax = metrics.loc[metrics.modelo.eq("SARIMAX")].set_index("base_id")
    assert int(sarimax.loc["base_02", "origens"] - sarimax.loc["base_02", "origens_horizonte_1"]) == 14
    assert int(sarimax.loc["base_03", "origens"] - sarimax.loc["base_03", "origens_horizonte_1"]) == 53
    assert int(sarimax.loc["base_05", "origens_horizonte_1"]) == 586
    assert any("base_02: contagens de origens distintas" in item for item in findings)
    assert any("base_02: Holt-Winters e SARIMAX compartilham" in item for item in findings)
    assert not any("base_05: Holt-Winters e SARIMAX" in item for item in findings)
    assert any("CSV local de RF" in item for item in findings)
