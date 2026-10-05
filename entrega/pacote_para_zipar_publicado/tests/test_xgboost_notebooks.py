import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _notebook(number: int) -> dict:
    path = ROOT / "notebooks" / f"base_{number:02d}-grupo{number}_XGBoost.ipynb"
    return json.loads(path.read_text(encoding="utf-8"))


def _source(notebook: dict, cell_type: str | None = None) -> str:
    return "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell_type is None or cell["cell_type"] == cell_type
    )


def test_five_xgboost_notebooks_use_canonical_data_paths():
    for number in range(1, 6):
        notebook = _notebook(number)
        code = _source(notebook, "code")
        filename = "raw.csv" if number == 5 else "prepared.csv"
        assert f'data/base_{number:02d}/{filename}' in code
        assert "trabalho/bases" not in code
        assert f"grupo{number}.csv" not in code


def test_xgboost_protocol_is_temporal_and_freezes_parameters():
    required = (
        "purged_time_series_splits",
        "training_target_cutoff",
        "FROZEN_PARAMS",
        "assert json.dumps(best_params",
        "permutation_importance",
        "acorr_ljungbox",
        "N_ITER_AMPLA = 2 if SMOKE_TEST else 120",
        "N_ITER_REFINADA = 1 if SMOKE_TEST else 30",
    )
    for number in range(1, 6):
        code = _source(_notebook(number), "code")
        for marker in required:
            assert marker in code, (number, marker)


def test_saved_xgboost_runs_finished_without_notebook_errors():
    for number in range(1, 6):
        notebook = _notebook(number)
        errors = [
            output
            for cell in notebook["cells"]
            for output in cell.get("outputs", [])
            if output.get("output_type") == "error"
        ]
        assert not errors, number
        serialized = json.dumps(notebook, ensure_ascii=False)
        assert "BUSCA COMPLETA (150 candidatos)" in serialized
        assert '"search_candidates"' in serialized or "search_candidates" in serialized


def test_xgboost_study_covers_assignment_topics():
    study = (ROOT / "docs" / "modelo_xgboost.md").read_text(encoding="utf-8").lower()
    required_topics = (
        "funcionamento e intuição",
        "hipóteses, preparação e limitações",
        "hiperparâmetros e seus efeitos",
        "importância das features",
        "desempenho nas cinco bases",
        "pontos de atenção",
        "gain",
        "permutation importance",
    )
    for topic in required_topics:
        assert topic in study
