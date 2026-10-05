import numpy as np
import pandas as pd
import pytest

from series_temporais.reporting.residuos import salvar_residuos_base5, salvar_residuos_nivel


def sample(rows=12):
    origins = pd.date_range("2020-01-03", periods=rows, freq="W-FRI")
    actual = np.arange(100.0, 100.0 + rows)
    forecast = actual - 1
    previous = actual - 2
    return pd.DataFrame({
        "DATE": origins, "target_date": origins + pd.Timedelta(days=7),
        "price_t": previous, "target_price_t_plus_1": actual,
        "y_true_return": np.log(actual / previous),
        "y_pred_return_xgb": np.log(forecast / previous),
        "y_pred_return_zero": 0.,
        "residual_return_xgb": np.log(actual / previous) - np.log(forecast / previous),
        "y_true_price": actual, "price_pred_xgb": forecast,
        "price_pred_persistencia": previous, "residual_price_xgb": 1.0,
        "absolute_error_price_xgb": 1.0, "squared_error_price_xgb": 1.0,
        "target_has_new_quote": 1, "price_was_carried": 0,
        "model_refit_origin": origins, "training_target_cutoff": origins,
    })


def test_export_preserves_all_rows_without_overwriting_full_run(tmp_path):
    frame = sample()
    directory = tmp_path / "results" / "residuals"
    directory.mkdir(parents=True)
    full = directory / "base_05_XGBoost.csv"
    full.write_text("resultado completo", encoding="utf-8")
    original = frame.copy(deep=True)
    path = salvar_residuos_base5(frame, tmp_path, smoke=True, expected_rows=12)
    saved = pd.read_csv(path)
    assert len(saved) == len(frame)
    np.testing.assert_allclose(saved.residual_return_xgb, frame.residual_return_xgb)
    assert set(frame.columns).issubset(saved.columns)
    np.testing.assert_allclose(saved.absolute_error_return_xgb, saved.residual_return_xgb.abs())
    np.testing.assert_allclose(saved.squared_error_return_xgb, saved.residual_return_xgb ** 2)
    pd.testing.assert_frame_equal(frame, original)
    assert full.read_text(encoding="utf-8") == "resultado completo"


def test_export_rejects_future_training_cutoff(tmp_path):
    frame = sample()
    frame.loc[0, "training_target_cutoff"] = frame.loc[0, "target_date"]
    with pytest.raises(ValueError, match="causalidade"):
        salvar_residuos_base5(frame, tmp_path, smoke=True, expected_rows=12)


def test_export_rejects_inconsistent_residuals(tmp_path):
    frame = sample()
    frame.loc[0, "residual_price_xgb"] = 100
    with pytest.raises(ValueError, match="inconsistentes"):
        salvar_residuos_base5(frame, tmp_path, smoke=True, expected_rows=12)


def test_return_export_full_run_and_price_conversion(tmp_path):
    frame = sample(586)
    path = salvar_residuos_base5(frame, tmp_path)
    saved = pd.read_csv(path)
    assert path.name == "base_05_XGBoost.csv" and len(saved) == 586
    np.testing.assert_allclose(saved.price_pred_xgb, saved.price_t * np.exp(saved.y_pred_return_xgb))


@pytest.mark.parametrize("column,value,message", [
    ("price_pred_xgb", 200., "Conversão"),
    ("residual_return_xgb", 99., "retorno inconsistentes"),
    ("y_pred_return_zero", 1., "Persistência"),
    ("model_refit_origin", pd.Timestamp("2030-01-01"), "causalidade"),
    ("target_has_new_quote", 2, "cobertura"),
    ("y_pred_return_xgb", np.nan, "não finitos"),
])
def test_return_export_rejects_invalid_contract(tmp_path, column, value, message):
    frame = sample()
    frame.loc[0, column] = value
    with pytest.raises(ValueError, match=message):
        salvar_residuos_base5(frame, tmp_path, smoke=True, expected_rows=12)


def test_return_export_rejects_incomplete_full_run(tmp_path):
    with pytest.raises(ValueError, match="586"):
        salvar_residuos_base5(sample(), tmp_path)


def test_base5_notebook_exports_canonical_return():
    import json
    from pathlib import Path
    nb = json.loads((Path(__file__).resolve().parents[1] / "notebooks" /
                     "base_05-grupo5_XGBoost.ipynb").read_text(encoding="utf-8"))
    code = "\n".join("".join(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == "code")
    assert "from series_temporais.reporting.residuos import salvar_residuos_base5" in code
    assert "salvar_residuos_base5(predictions, ROOT, smoke=SMOKE_TEST, expected_rows=len(test_df))" in code


def level_sample():
    source = sample()
    return pd.DataFrame({
        "origin_time": source.DATE, "target_time": source.target_date,
        "y_true": source.y_true_price, "y_pred_xgb": source.price_pred_xgb,
        "y_pred_persistencia": source.price_pred_persistencia,
        "residuo_xgb": source.residual_price_xgb,
        "model_refit_origin": source.model_refit_origin,
        "training_target_cutoff": source.training_target_cutoff,
        "level_t": source.price_pred_persistencia,
    })


@pytest.mark.parametrize("base", [1, 2, 3, 4])
def test_level_export_preserves_rows_columns_and_error_identity(tmp_path, base):
    frame = level_sample()
    original = frame.copy()
    path = salvar_residuos_nivel(frame, tmp_path, base, expected_rows=len(frame))
    saved = pd.read_csv(path, parse_dates=["origin_time", "target_time"])
    assert path.name == f"base_{base:02d}_XGBoost.csv"
    assert len(saved) == len(frame)
    assert saved.origin_time.tolist() == frame.origin_time.tolist()
    np.testing.assert_allclose(saved.residuo_xgb, saved.y_true - saved.y_pred_xgb)
    np.testing.assert_allclose(saved.erro_absoluto_xgb, saved.residuo_xgb.abs())
    np.testing.assert_allclose(saved.erro_quadratico_xgb, saved.residuo_xgb ** 2)
    pd.testing.assert_frame_equal(frame, original)


def test_level_export_rejects_future_cutoff_and_incomplete_run(tmp_path):
    frame = level_sample()
    with pytest.raises(ValueError, match="Quantidade"):
        salvar_residuos_nivel(frame, tmp_path, 1, expected_rows=len(frame) + 1)
    frame.loc[0, "training_target_cutoff"] = frame.loc[0, "target_time"]
    with pytest.raises(ValueError, match="causalidade"):
        salvar_residuos_nivel(frame, tmp_path, 1, expected_rows=len(frame))


@pytest.mark.parametrize("base", [1, 2, 3, 4, 5])
def test_temporal_residual_plot_preserves_all_values_and_input(base):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from series_temporais.reporting.residuos import plotar_residuos_temporais_xgboost
    frame = sample() if base == 5 else level_sample()
    original = frame.copy(deep=True)
    column = "residual_return_xgb" if base == 5 else "residuo_xgb"
    fig, audit = plotar_residuos_temporais_xgboost(
        frame, base, frequency="W-FRI", expected_rows=12,
        expected_mae=frame[column].abs().mean())
    np.testing.assert_allclose(fig.axes[0].lines[0].get_ydata(), frame[column])
    np.testing.assert_allclose(fig.axes[0].lines[1].get_ydata(), [0, 0])
    assert audit["origens_avaliadas"] == 12 and audit["lacunas_no_tracado"] == 0
    assert ("Retorno logarítmico" in fig.axes[0].get_ylabel()) == (base == 5)
    pd.testing.assert_frame_equal(frame, original)
    plt.close(fig)


def test_temporal_residual_plot_does_not_interpolate_calendar_gaps():
    import matplotlib.pyplot as plt
    from series_temporais.reporting.residuos import plotar_residuos_temporais_xgboost
    frame = sample().drop(index=[3, 4])
    fig, audit = plotar_residuos_temporais_xgboost(frame, 5, frequency="W-FRI")
    plotted = fig.axes[0].lines[0].get_ydata()
    assert len(plotted) == 12 and np.isnan(plotted[3:5]).all()
    assert audit["origens_avaliadas"] == 10 and audit["lacunas_no_tracado"] == 2
    plt.close(fig)


@pytest.mark.parametrize("problem", ["count", "mae", "infinity", "identity", "future", "horizon", "order"])
def test_temporal_residual_plot_rejects_invalid_execution(problem):
    from series_temporais.reporting.residuos import plotar_residuos_temporais_xgboost
    frame = sample()
    kwargs = {"expected_rows": 12, "expected_mae": frame.residual_return_xgb.abs().mean()}
    if problem == "count": kwargs["expected_rows"] = 13
    if problem == "mae": kwargs["expected_mae"] = 999
    if problem == "infinity": frame.loc[0, "residual_return_xgb"] = np.inf
    if problem == "identity": frame.loc[0, "residual_return_xgb"] = 999
    if problem == "future": frame.loc[0, "training_target_cutoff"] = frame.loc[0, "target_date"]
    if problem == "horizon": frame.loc[0, "target_date"] += pd.Timedelta(days=7)
    if problem == "order": frame = frame.iloc[::-1]
    with pytest.raises(ValueError):
        plotar_residuos_temporais_xgboost(frame, 5, frequency="W-FRI", **kwargs)


def test_csv_residual_plot_checks_consolidated_metrics(tmp_path):
    import matplotlib.pyplot as plt
    from series_temporais.reporting.residuos import grafico_residuos_xgboost
    directory = tmp_path / "results/residuals"
    directory.mkdir(parents=True)
    data = tmp_path / "data/base_05"
    data.mkdir(parents=True)
    (data / "metadata.yaml").write_text("target: target_log_return_t_plus_1\nfrequency: W-FRI\n", encoding="utf-8")
    frame = sample()
    frame.to_csv(directory / "base_05_XGBoost.csv", index=False)
    metric = pd.DataFrame([{"base_id": "base_05", "modelo": "XGBoost",
                           "alvo": "target_log_return_t_plus_1", "frequencia": "W-FRI",
                           "origens_avaliadas": 12, "mae": frame.residual_return_xgb.abs().mean()}])
    metric.to_csv(tmp_path / "results/metrics.csv", index=False)
    fig, audit = grafico_residuos_xgboost(tmp_path, 5)
    assert len(audit["csv_sha256"]) == 64 and audit["modo"] == "full"
    plt.close(fig)
    metric.loc[0, "mae"] = 123
    metric.to_csv(tmp_path / "results/metrics.csv", index=False)
    with pytest.raises(ValueError, match="MAE"):
        grafico_residuos_xgboost(tmp_path, 5)


def test_five_notebooks_have_standalone_residual_plot_cells():
    import ast
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for base in range(1, 6):
        notebook = json.loads((root / f"notebooks/base_{base:02d}-grupo{base}_XGBoost.ipynb").read_text(encoding="utf-8"))
        cells = [cell for cell in notebook["cells"] if cell.get("id") == f"xgb-residuos-temporais-{base}"]
        assert len(cells) == 1
        cell = cells[0]
        assert "residuos-temporais-xgboost" in cell["metadata"]["tags"]
        calls = [node.func.id for node in ast.walk(ast.parse("".join(cell["source"])))
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        assert "grafico_residuos_xgboost" in calls
        assert not {"XGBRegressor", "temporal_random_search", "walk_forward"}.intersection(calls)
