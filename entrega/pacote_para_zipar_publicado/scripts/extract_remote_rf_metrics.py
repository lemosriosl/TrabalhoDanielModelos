"""Extrai, de origin/main, as métricas RF já registradas em notebooks executados."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd

from series_temporais.notebook_metrics import find_metric_table


ROOT = Path(__file__).resolve().parents[1]
COMMIT = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True).strip()
SPECS = {
    "base_01": ("base_01-grupo1_RF.ipynb", "MAE", "Random Forest"),
    "base_02": ("base_02-grupo2_RF.ipynb", "MAE", "Random Forest"),
    "base_03": ("base_03-grupo3_RF.ipynb", "MAE", "Random Forest"),
    "base_04": ("base_04-grupo4_RF.ipynb", "MAE", "Random Forest"),
    "base_05": ("base_05-grupo5_RF_retorno.ipynb", "MAE_retorno", "Random Forest"),
}

rows = []
for base_id, (filename, metric_column, model_name) in SPECS.items():
    raw = subprocess.check_output(
        ["git", "show", f"origin/main:notebooks/{filename}"], cwd=ROOT
    )
    notebook = json.loads(raw.decode("utf-8"))
    table = find_metric_table(notebook, metric_column)
    selected = table.loc[table["modelo"].astype(str).str.startswith(model_name)].copy()
    if base_id == "base_05":
        selected = selected.loc[selected["modelo"].astype(str).str.contains("todas \(principal\)")]
    else:
        selected = selected.loc[selected["modelo"].eq(model_name)]
    if len(selected) != 1:
        raise ValueError(f"Não foi possível identificar uma linha principal para {base_id}.")
    row = selected.iloc[0]
    rows.append(
        {
            "base_id": base_id,
            "modelo": "random_forest",
            "mae": float(row[metric_column]),
            "origens_avaliadas": int(row.get("observacoes", 0)) or pd.NA,
            "notebook_remoto": f"notebooks/{filename}",
            "commit_remoto": COMMIT,
        }
    )

output = ROOT / "results" / "extraidos_do_remoto" / "random_forest_metrics.csv"
output.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8", lineterminator="\n")
print(output)
