"""Contratos estáticos do protocolo walk-forward nos notebooks de modelo."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def _source(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )


def test_all_model_notebooks_are_valid_json():
    for notebook in NOTEBOOKS.glob("*grupo*_*.*ipynb"):
        json.loads(notebook.read_text(encoding="utf-8"))


def test_random_forest_and_xgboost_refit_at_every_origin():
    names = [
        *(f"base_{number:02d}-grupo{number}_RF.ipynb" for number in range(1, 5)),
        "base_05-grupo5_RF_preco.ipynb",
        "base_05-grupo5_RF_retorno.ipynb",
        *(f"base_{number:02d}-grupo{number}_XGBoost.ipynb" for number in range(1, 6)),
    ]
    for name in names:
        source = _source(NOTEBOOKS / name)
        assert "refit_every = 1" in source or "REFIT_EVERY = 1" in source, name
        assert "training_target_cutoff" in source, name
        assert (
            "training_target_cutoff <=" in source or "cutoff <= refit_origin" in source
        ), name


def test_base5_return_random_forest_uses_complete_canonical_grid():
    source = _source(NOTEBOOKS / "base_05-grupo5_RF_retorno.ipynb")
    assert "training_df = train_df.copy()" in source
    assert "history = history_all" in source
    assert "assert 'target_has_new_quote' not in feature_columns" in source
    assert "todas (principal)" in source


def test_base5_price_random_forest_keeps_observed_target_filter_as_auxiliary():
    source = _source(NOTEBOOKS / "base_05-grupo5_RF_preco.ipynb")
    assert "training_df = selecionar_alvos_observados(train_df)" in source
    assert "history = selecionar_alvos_observados(history_all)" in source


def test_sarimax_final_section_refits_at_every_origin():
    for number in range(1, 6):
        notebook = json.loads(
            (NOTEBOOKS / f"base_{number:02d}-grupo{number}_SARIMAX.ipynb").read_text(
                encoding="utf-8"
            )
        )
        final_source = "".join(notebook["cells"][-1]["source"])
        assert "TESTE FINAL CORRIGIDO" in final_source
        assert "get_forecast(steps=1" in final_source
        assert (
            "for origin_time, row in df_test.iterrows()" in final_source
            or "for target_time, row in df_test.iterrows()" in final_source
        )
        assert "fit_sarimax_model(" in final_source
        assert "history = pd.concat(" in final_source
        assert "refit=False" not in final_source
        if number == 5:
            assert "validate_prediction_contract" in final_source
        assert "KNOWN_AT_ORIGIN_EXOG" in final_source
        assert "validate_prediction_frame" in final_source


def test_sarimax_full_search_is_default_and_smoke_mode_is_explicit():
    for number in range(1, 6):
        source = _source(NOTEBOOKS / f"base_{number:02d}-grupo{number}_SARIMAX.ipynb")
        assert "os.getenv('SARIMAX_SMOKE_TEST', '0') == '1'" in source
        assert "S_VALUES = list(range(0, 101))" in source
        assert "SMOKE_ORIGINS" in source
        assert "SMOKE_TRAIN_ROWS" in source


def test_holt_winters_keeps_one_step_state_updates():
    for number in range(1, 6):
        source = _source(NOTEBOOKS / f"base_{number:02d}-grupo{number}_HW.ipynb")
        assert "prever_um_passo" in source
        assert "atualizar_estado" in source
        assert "caminho_um_passo" in source


def test_base5_holt_winters_predicts_canonical_return_directly():
    source = _source(NOTEBOOKS / "base_05-grupo5_HW.ipynb")
    assert "TARGET = ALVO_CANONICO" in source
    assert "y_series = weekly.set_index('DATE').log_return_t" in source
    assert "predictions['y_pred_return_hw'] = predictions.pred_hw_escala_modelo" in source
    assert "training_df = train_df.copy()" in source
    assert "Holt-Winters — todas (principal)" in source


def test_base5_sarimax_benchmark_does_not_touch_final_test():
    notebook = json.loads(
        (NOTEBOOKS / "base_05-grupo5_SARIMAX.ipynb").read_text(encoding="utf-8")
    )
    benchmark_source = "".join(notebook["cells"][10]["source"])
    assert "benchmark_validation = df_train" in benchmark_source
    assert "fit_and_forecast(df_train, df_test" not in benchmark_source


def test_all_sarimax_benchmarks_use_only_internal_training_validation():
    for number in range(1, 6):
        notebook = json.loads(
            (NOTEBOOKS / f"base_{number:02d}-grupo{number}_SARIMAX.ipynb").read_text(
                encoding="utf-8"
            )
        )
        benchmark_source = "".join(notebook["cells"][10]["source"])
        assert "benchmark_train = df_train" in benchmark_source
        assert "benchmark_validation = df_train" in benchmark_source
        assert "fit_and_forecast(df_train, df_test" not in benchmark_source
