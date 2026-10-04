import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from series_temporais.reporting.metricas_xgboost import atualizar_metricas_xgboost, comparacao_xgboost, registro_xgboost
from series_temporais.results import write_metrics


def inputs(base=1):
    origins = pd.date_range("2024-01-01", periods=3, freq="D")
    frame = pd.DataFrame({
        "origin_time": origins, "target_time": origins + pd.Timedelta(days=1),
        "y_true": [1., 2., 3.], "y_pred_xgb": [0., 1., 2.],
        "training_target_cutoff": [origins[0], origins[0], origins[2]],
        "model_refit_origin": [origins[0], origins[0], origins[2]],
    })
    metadata = {"target": "Close", "frequency": "D", "horizon_steps": 1}
    if base == 5:
        frame = frame.rename(columns={"origin_time": "DATE", "target_time": "target_date",
                                      "y_true": "y_true_return", "y_pred_xgb": "y_pred_return_xgb"})
        metadata["target"] = "target_log_return_t_plus_1"
    summary = {"base": base, "observacoes_teste": 3, "refits": 2, "mae_xgboost": 1.,
               "search_candidates": 150, "alvo": metadata["target"], "frequencia": "D",
               "best_params": {"max_depth": 2}, "search_seconds_recorded": 5.,
               "evaluation_seconds": 10.}
    return frame, summary, metadata


def record(frame, summary, metadata, interval=2):
    return registro_xgboost(frame, summary, metadata, interval=interval,
                            exogenous=["Open_t"], commit="abc+dirty", generated_at="2026-10-04")


def test_metric_record_preserves_evidence_and_no_invented_rank():
    frame, summary, metadata = inputs()
    row = record(frame, summary, metadata)
    assert row["mae"] == 1.
    assert row["mape"] == pytest.approx(100 * (1 + .5 + 1/3) / 3)
    assert row["tempo_execucao_segundos"] == 15.
    assert row["posicao_base"] is None and row["vencedor"] is None
    assert row["hiperparametros"] == {"estimador": {"max_depth": 2}, "refit_every": 2,
                                      "search_candidates": 150}
    assert row["features_exogenas"] == ["Open_t"]


def test_return_record_does_not_calculate_mape():
    assert record(*inputs(5))["mape"] is None


def test_zero_target_does_not_calculate_mape():
    frame, summary, metadata = inputs()
    frame.loc[0, "y_true"] = 0.
    summary["mae_xgboost"] = 2/3
    assert record(frame, summary, metadata)["mape"] is None


@pytest.mark.parametrize("field,value,message", [
    ("mae_xgboost", 99., "MAE"),
    ("search_candidates", 3, "busca completa"),
    ("refits", 3, "Cadência"),
    ("observacoes_teste", 4, "origens"),
    ("alvo", "outro", "alvo"),
    ("evaluation_seconds", np.nan, "Tempo"),
])
def test_record_rejects_stale_or_incomplete_summary(field, value, message):
    frame, summary, metadata = inputs()
    summary[field] = value
    with pytest.raises(ValueError, match=message):
        record(frame, summary, metadata)


def test_record_rejects_cadence_with_correct_count_but_wrong_positions():
    frame, summary, metadata = inputs()
    frame.loc[1, "model_refit_origin"] = frame.loc[1, "origin_time"]
    frame.loc[2, "model_refit_origin"] = frame.loc[1, "origin_time"]
    frame.loc[2, "training_target_cutoff"] = frame.loc[1, "origin_time"]
    with pytest.raises(ValueError, match="Cadência"):
        record(frame, summary, metadata)


def test_notebooks_export_metrics_without_smoke_overwriting_full_runs():
    root = Path(__file__).resolve().parents[1]
    for base in range(1, 6):
        nb = json.loads((root / "notebooks" / f"base_{base:02d}-grupo{base}_XGBoost.ipynb").read_text(encoding="utf-8"))
        code = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
        assert "if not SMOKE_TEST:" in code
        assert "atualizar_metricas_xgboost(ROOT, [summary])" in code


def setup_export(tmp_path, monkeypatch):
    frame, summary, metadata = inputs()
    directory = tmp_path / "data" / "base_01"
    directory.mkdir(parents=True)
    (directory / "prepared.csv").write_text("dado congelado", encoding="utf-8")
    summary["data_sha256"] = hashlib.sha256((directory / "prepared.csv").read_bytes()).hexdigest()
    import yaml
    metadata["external_availability"] = "availability.csv"
    (directory / "metadata.yaml").write_text(yaml.safe_dump(metadata), encoding="utf-8")
    (directory / "availability.csv").write_text(
        "feature,disponibilidade\nOpen_t,na_origem\n,proibida\n", encoding="utf-8")
    (tmp_path / "projeto.yaml").write_text(
        "validacao:\n  intervalo_retreino_xgboost_por_base:\n    base_01: 2\n", encoding="utf-8")
    residuals = tmp_path / "results" / "residuals"
    residuals.mkdir(parents=True)
    frame.to_csv(residuals / "base_01_XGBoost.csv", index=False)
    monkeypatch.setattr(
        "series_temporais.reporting.metricas_xgboost.subprocess.check_output",
        lambda args, **kwargs: "abcdef\n" if args[1] == "rev-parse" else " M notebook",
    )
    other = record(frame, summary, metadata)
    other["modelo"] = "SARIMAX"
    write_metrics([other], tmp_path / "results" / "metrics.csv")
    return summary


def test_export_preserves_other_models_and_is_idempotent(tmp_path, monkeypatch):
    summary = setup_export(tmp_path, monkeypatch)
    atualizar_metricas_xgboost(tmp_path, [summary])
    result = atualizar_metricas_xgboost(tmp_path, [summary])
    assert result.modelo.tolist() == ["SARIMAX", "XGBoost"]
    assert len(result) == 2
    assert result.loc[result.modelo.eq("XGBoost"), "commit"].iloc[0] == "abcdef+dirty"


def test_failed_validation_does_not_change_existing_metrics(tmp_path, monkeypatch):
    summary = setup_export(tmp_path, monkeypatch)
    path = tmp_path / "results" / "metrics.csv"
    original = path.read_bytes()
    summary["data_sha256"] = "hash antigo"
    with pytest.raises(ValueError, match="Dado mudou"):
        atualizar_metricas_xgboost(tmp_path, [summary])
    assert path.read_bytes() == original


def test_comparison_uses_current_metrics_and_csv_not_temporary_summaries(tmp_path, monkeypatch):
    summary = setup_export(tmp_path, monkeypatch)
    path = tmp_path / "results" / "residuals" / "base_01_XGBoost.csv"
    frame = pd.read_csv(path)
    frame["y_pred_persistencia"] = frame.y_true - 2.
    frame.to_csv(path, index=False)
    atualizar_metricas_xgboost(tmp_path, [summary])
    result = comparacao_xgboost(tmp_path)
    assert len(result) == 1
    assert result.mae_xgboost.iloc[0] == 1.
    assert result.mae_persistencia.iloc[0] == 2.
    assert result.skill_vs_persistencia.iloc[0] == .5
    assert result.vence_persistencia.iloc[0]
    frame.loc[0, "y_pred_xgb"] = 99.
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="MAE divergente"):
        comparacao_xgboost(tmp_path)


def test_comparison_without_metrics_is_partial_not_invented(tmp_path):
    assert comparacao_xgboost(tmp_path).empty
