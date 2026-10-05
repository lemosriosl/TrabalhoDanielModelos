"""Evita divergências entre estudo, consolidado e tabela salva da Base 5."""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def table(section):
    return {int(parts[1].strip()): [value.strip() for value in parts[2:-1]]
            for line in section.splitlines() if re.match(r"\| [1-5] \|", line)
            for parts in [line.split("|")]}


def test_study_metrics_and_parameters_match_consolidated_results():
    doc = (ROOT / "docs" / "modelo_xgboost.md").read_text(encoding="utf-8")
    performance = table(doc.split("## Desempenho nas cinco bases")[1]
                        .split("O XGBoost venceu")[0])
    parameters = table(doc.split("Configurações selecionadas antes do teste final:")[1]
                        .split("## Importância das features")[0])
    metrics = pd.read_csv(ROOT / "results" / "metrics.csv")
    for row in metrics.loc[metrics.modelo.eq("XGBoost")].to_dict("records"):
        base = int(row["base_id"][-2:])
        published = float(performance[base][1].replace(",", "."))
        assert np.isclose(published, row["mae"], rtol=1e-5, atol=5e-7)
        params = json.loads(row["hiperparametros"])["estimador"]
        names = ["n_estimators", "learning_rate", "max_depth", "min_child_weight",
                 "subsample", "colsample_bytree", "reg_alpha", "reg_lambda"]
        np.testing.assert_allclose([float(v.replace(",", ".")) for v in parameters[base]],
                                   [params[name] for name in names])
    assert "três das cinco bases" in doc
    assert "## Desempenho nas cinco bases" in doc and "### Resíduos, ACF e Ljung–Box" in doc


def test_base5_saved_comparison_matches_current_consolidated_metrics():
    nb = json.loads((ROOT / "notebooks" / "base_05-grupo5_XGBoost.ipynb").read_text(encoding="utf-8"))
    cell = next(c for c in nb["cells"] if "comparacao_xgboost(ROOT)" in "".join(c["source"]))
    assert "sem reexecutar treinamento" in cell["metadata"]["consolidacao_atualizada_em"]
    output = next(o for o in cell["outputs"]
                  if "<th>vence_persistencia</th>" in "".join(o.get("data", {}).get("text/html", [])))
    html = "".join(output["data"]["text/html"])
    rows = [re.findall(r"<td>(.*?)</td>", tr) for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S)]
    values = {row[0]: float(row[4]) for row in rows if row}
    metrics = pd.read_csv(ROOT / "results" / "metrics.csv")
    assert len(values) == 5
    for row in metrics.loc[metrics.modelo.eq("XGBoost")].to_dict("records"):
        assert np.isclose(values[row["base_id"]], row["mae"], rtol=0, atol=5.1e-7)
