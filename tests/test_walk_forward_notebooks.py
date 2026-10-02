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


def test_base5_random_forests_fit_only_observed_targets_without_feature_leakage():
    for name in (
        "base_05-grupo5_RF_preco.ipynb",
        "base_05-grupo5_RF_retorno.ipynb",
    ):
        source = _source(NOTEBOOKS / name)
        assert "training_df = selecionar_alvos_observados(train_df)" in source, name
        assert "history = selecionar_alvos_observados(history_all)" in source, name
        assert "assert 'target_has_new_quote' not in feature_columns" in source, name
        assert "assert history.target_has_new_quote.eq(1).all()" in source, name


def test_sarimax_final_section_is_one_step_and_updates_state():
    for number in range(1, 6):
        notebook = json.loads(
            (NOTEBOOKS / f"base_{number:02d}-grupo{number}_SARIMAX.ipynb").read_text(
                encoding="utf-8"
            )
        )
        final_source = "".join(notebook["cells"][-1]["source"])
        assert "TESTE FINAL CORRIGIDO" in final_source
        assert "get_forecast(steps=1" in final_source
        assert "result.append(" in final_source
        assert "KNOWN_AT_ORIGIN_EXOG" in final_source
        assert "validate_prediction_frame" in final_source


def test_holt_winters_keeps_one_step_state_updates():
    for number in range(1, 6):
        source = _source(NOTEBOOKS / f"base_{number:02d}-grupo{number}_HW.ipynb")
        assert "prever_um_passo" in source
        assert "atualizar_estado" in source
        assert "caminho_um_passo" in source
