import pandas as pd
import pytest

from series_temporais.reporting.comparacao_pareada import gerar_comparacao_pareada


def _write(path, rows):
    pd.DataFrame(rows).to_csv(path, index=False)


def test_comparison_keeps_only_identical_one_step_observations(tmp_path):
    _write(tmp_path / "base_02__holt_winters.csv", [
        {"origin_time": "2020-01-01 00:00", "target_time": "2020-01-01 01:00", "y_true": 10, "y_pred": 8},
        {"origin_time": "2020-01-01 01:00", "target_time": "2020-01-01 02:00", "y_true": 12, "y_pred": 10},
    ])
    _write(tmp_path / "base_02__sarimax.csv", [
        {"origin_time": "2020-01-01 00:00", "target_time": "2020-01-01 01:00", "y_true": 10, "y_pred": 9},
        {"origin_time": "2020-01-01 01:00", "target_time": "2020-01-01 03:00", "y_true": 15, "y_pred": 14},
    ])
    row = gerar_comparacao_pareada(tmp_path, bases=(2,)).iloc[0]
    assert row.origens_pareadas == 1
    assert row.mae_hw_pareado == 2
    assert row.mae_sarimax_pareado == 1
    assert row.origens_sarimax_horizonte_1 == 1


def test_comparison_rejects_disagreement_in_observed_target(tmp_path):
    for stem, actual in (("holt_winters", 10), ("sarimax", 11)):
        _write(tmp_path / f"base_02__{stem}.csv", [{
            "origin_time": "2020-01-01 00:00", "target_time": "2020-01-01 01:00",
            "y_true": actual, "y_pred": 9,
        }])
    with pytest.raises(ValueError, match="Valor real divergente"):
        gerar_comparacao_pareada(tmp_path, bases=(2,))
