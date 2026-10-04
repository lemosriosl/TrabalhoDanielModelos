import json
import ast
from pathlib import Path

import pandas as pd
import pytest

from series_temporais.validation.checkpoints import assinatura_busca_temporal, codigo_metodologico


def frame():
    dates = pd.date_range("2020-01-01", periods=5)
    return pd.DataFrame({"origin": dates[:-1], "target_time": dates[1:],
                         "y": [1., 2., 3., 4.], "x": [5., 6., 7., 8.]})


def signature(data=None, **kwargs):
    arguments = dict(features=["x"], alvo="y", origem="origin", instante_alvo="target_time",
                     protocolo={"seed": 42, "folds": 3, "version": "1"}, codigo="v1")
    arguments.update(kwargs)
    return assinatura_busca_temporal(frame() if data is None else data, **arguments)


def test_signature_reproducible_and_ignores_dataframe_index():
    data = frame()
    data.index = range(10, 14)
    assert signature() == signature(data)


@pytest.mark.parametrize("column", ["x", "y", "origin", "target_time"])
def test_changed_tuning_values_invalidate_cache(column):
    data = frame()
    data.loc[0, column] += pd.Timedelta(hours=1) if column in ("origin", "target_time") else 1.
    assert signature(data) != signature()


def test_target_dtype_protocol_and_code_invalidate_cache():
    data = frame().rename(columns={"y": "other_target"})
    assert signature(data, alvo="other_target") != signature()
    assert signature(frame().astype({"x": "float32"})) != signature()
    assert signature(protocolo={"seed": 43, "folds": 3, "version": "1"}) != signature()
    assert signature(protocolo={"seed": 42, "folds": 4, "version": "1"}) != signature()
    assert signature(protocolo={"seed": 42, "folds": 3, "version": "2"}) != signature()
    assert signature(codigo="v2") != signature()


def test_unrelated_columns_do_not_read_test_or_invalidate_tuning():
    data = frame().assign(unused_future=999.)
    assert signature(data) == signature()


def test_method_code_ignores_notebook_outputs_but_not_logic(tmp_path):
    path = tmp_path / "model.ipynb"
    notebook = {"cells": [{"cell_type": "markdown", "source": ["Study"]},
                           {"cell_type": "code", "source": ["def prepare(x):\n    return x + 1\n"],
                            "outputs": []}]}
    path.write_text(json.dumps(notebook), encoding="utf-8")
    initial = codigo_metodologico(path, funcoes=["prepare"])
    notebook["cells"][0]["source"] = ["New study"]
    notebook["cells"][1]["outputs"] = [{"text": "New output"}]
    path.write_text(json.dumps(notebook), encoding="utf-8")
    assert codigo_metodologico(path, funcoes=["prepare"]) == initial
    notebook["cells"][1]["source"] = ["def prepare(x):\n    return x + 2\n"]
    path.write_text(json.dumps(notebook), encoding="utf-8")
    assert codigo_metodologico(path, funcoes=["prepare"]) != initial
    shared = tmp_path / "prepare.py"
    shared.write_text("version1", encoding="utf-8")
    first = codigo_metodologico(path, funcoes=["prepare"], arquivos=[shared])
    shared.write_text("version2", encoding="utf-8")
    assert codigo_metodologico(path, funcoes=["prepare"], arquivos=[shared]) != first


def test_missing_method_fails_closed(tmp_path):
    path = tmp_path / "model.ipynb"
    path.write_text(json.dumps({"cells": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="não encontradas"):
        codigo_metodologico(path, funcoes=["prepare"])


@pytest.mark.parametrize("base", range(1, 6))
def test_notebooks_use_signed_tuning_and_existing_method_functions(base):
    root = Path(__file__).resolve().parents[1]
    path = root / "notebooks" / f"base_{base:02d}-grupo{base}_XGBoost.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code = "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code")
    tree = ast.parse(code)
    signature = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == "RUN_SIGNATURE" for t in node.targets))
    assert signature.func.id == "assinatura_busca_temporal"
    assert signature.args[0].id == "tuning_df"
    method = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "CODIGO_METODOLOGICO" for t in node.targets))
    functions = ast.literal_eval(next(k.value for k in method.keywords if k.arg == "funcoes"))
    files = [root / "src/series_temporais/data/preparacao_base5.py"] if base == 5 else []
    assert len(codigo_metodologico(path, funcoes=functions, arquivos=files)) == 64
