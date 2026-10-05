"""Executa os loops reais dos notebooks com um estimador leve e determinístico."""

import ast
import json
import re
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("number", range(1, 6))
def test_notebook_periodic_loop_preserves_origins_and_causality(number, tmp_path):
    notebook = json.loads((ROOT / "notebooks" / f"base_{number:02d}-grupo{number}_XGBoost.ipynb").read_text(encoding="utf-8"))
    code = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
    function = next(n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef) and n.name == "walk_forward")
    params = {"frozen": 42}
    seen = []

    class Model:
        feature_importances_ = np.array([1.0])

        def fit(self, x, y):
            seen.append((len(y), y.tolist()))
            self.last = float(y.iloc[-1])

        def predict(self, x):
            return x["x"].to_numpy(dtype=float) + self.last

    def factory(received):
        assert received == params
        return Model()

    namespace = {
        "np": np, "pd": pd, "time": time, "json": json,
        "CHECKPOINT_DIR": tmp_path, "ORIGIN_COL": "origin",
        "TARGET_TIME_COL": "target_time", "MODEL_TARGET": "y", "FEATURES": ["x"],
        "estimator_factory": factory, "IMPORTANCE_EVERY": 2, "IMPORTANCE_WINDOW": 2,
        "PROGRESS_EVERY": 1, "PERMUTATION_REPEATS": 1,
        "PERMUTATION_MAX_ROWS": 10, "RANDOM_STATE": 42,
        "importancia_temporal": lambda *args, **kwargs: [],
        "permutation_importance": lambda *args, **kwargs: SimpleNamespace(
            importances_mean=np.array([1.0]), importances_std=np.array([0.0])
        ),
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), "notebook", "exec"), namespace)
    dates = pd.date_range("2024-01-01", periods=9, freq="D")
    frame = pd.DataFrame({"origin": dates[:-1], "target_time": dates[1:],
                          "x": np.arange(10., 18.), "y": np.arange(1., 9.)})
    predictions, fits, _ = namespace["walk_forward"](frame.iloc[:3], frame.iloc[3:], params, 2)
    assert len(predictions) == 5 and len(fits) == 3
    assert predictions.origin.tolist() == frame.origin.iloc[3:].tolist()
    assert predictions.target_time.tolist() == frame.target_time.iloc[3:].tolist()
    assert predictions.y_pred.tolist() == [16., 17., 20., 21., 24.]
    assert [size for size, _ in seen] == [3, 5, 7]
    assert (predictions.training_target_cutoff <= predictions.model_refit_origin).all()
    assert (predictions.model_refit_origin <= predictions.origin).all()
    assert params == {"frozen": 42}


def test_project_refit_intervals_match_notebooks():
    config = (ROOT / "projeto.yaml").read_text(encoding="utf-8")
    section = config.split("intervalo_retreino_xgboost_por_base:", 1)[1].split("metrica_principal:", 1)[0]
    intervals = {int(number): int(value) for number, value in re.findall(r"base_(\d+): (\d+)", section)}
    assert intervals == {1: 7, 2: 24, 3: 24, 4: 144, 5: 4}
    for number, interval in intervals.items():
        nb = json.loads((ROOT / "notebooks" / f"base_{number:02d}-grupo{number}_XGBoost.ipynb").read_text(encoding="utf-8"))
        code = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
        assert re.search(rf"(?im)^refit_every = {interval}$", code)
