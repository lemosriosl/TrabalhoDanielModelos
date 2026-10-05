"""Executa apenas o teste final SARIMAX com a configuração salva no notebook.

Não refaz a busca de hiperparâmetros. A configuração é lida do ranking HTML já
executado no notebook, preservando a decisão registrada no remoto.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def notebook_path(base: int) -> Path:
    suffix = f"base_{base:02d}-grupo{base}_SARIMAX.ipynb"
    return ROOT / "notebooks" / suffix


def frozen_sarimax_config(notebook: dict[str, Any]) -> dict[str, Any]:
    """Retorna o primeiro colocado SARIMAX do ranking persistido no notebook."""

    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            html = output.get("data", {}).get("text/html")
            if not html:
                continue
            if isinstance(html, list):
                html = "".join(html)
            for table in pd.read_html(StringIO(html)):
                if "candidate_key" not in table.columns or "family" not in table.columns:
                    continue
                rows = table.loc[table["family"].eq("SARIMAX")]
                if rows.empty:
                    continue
                winner = rows.iloc[0]
                # A visualização do pandas pode abreviar candidate_key com
                # reticências. As colunas individuais continuam completas.
                required = {"order", "seasonal_order", "trend", "exog_cols"}
                if required.issubset(table.columns):
                    exog_text = str(winner["exog_cols"])
                    try:
                        exog_cols = ast.literal_eval(exog_text)
                    except (SyntaxError, ValueError):
                        exog_cols = [
                            value.strip()
                            for value in exog_text.strip("[]").split(",")
                            if value.strip()
                        ]
                    return {
                        "order": ast.literal_eval(str(winner["order"])),
                        "seasonal_order": ast.literal_eval(
                            str(winner["seasonal_order"])
                        ),
                        "trend": str(winner["trend"]),
                        "exog_cols": exog_cols,
                    }
                return json.loads(winner["candidate_key"])
    raise ValueError("Ranking SARIMAX persistido não encontrado no notebook.")


def cell_source(notebook: dict[str, Any], marker: str) -> str:
    for cell in notebook["cells"]:
        source = "".join(cell.get("source", []))
        if marker in source:
            return source
    raise ValueError(f"Célula com marcador {marker!r} não encontrada.")


def final_frame_setup_source(notebook: dict[str, Any], base: int) -> str:
    """Seleciona a preparação de treino/teste correspondente à base."""

    marker = "if df_train.empty or df_test.empty" if base == 5 else "df_train = df.iloc"
    return cell_source(notebook, marker)


def run_final_evaluation(base: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Reexecuta o trecho final causal usando o vencedor persistido."""

    path = notebook_path(base)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    winner = frozen_sarimax_config(notebook)

    # O carregamento é o do próprio notebook; somente a busca é deliberadamente
    # omitida. SMOKE_TEST=False restaura a partição completa treino/teste.
    os.environ["SARIMAX_SMOKE_TEST"] = "0"
    os.environ["MPLBACKEND"] = "Agg"
    namespace: dict[str, Any] = {"display": lambda *_args, **_kwargs: None}
    exec(cell_source(notebook, "BASE_NUMBER ="), namespace)
    namespace["plt"].show = lambda *_args, **_kwargs: None
    exec(cell_source(notebook, "DATA_PATH = ROOT"), namespace)
    exec(final_frame_setup_source(notebook, base), namespace)

    final_cell = cell_source(notebook, "TESTE FINAL CORRIGIDO")
    function_definitions = final_cell.split("base_predictions =", maxsplit=1)[0]
    function_definitions = function_definitions.replace(
        "for target_time, row in df_test.iterrows():",
        "for step, (target_time, row) in enumerate(df_test.iterrows(), start=1):\n"
        "        if step == 1 or step % 25 == 0 or step == len(df_test):\n"
        "            print(f'Base {BASE_NUMBER}: origem {step}/{len(df_test)}')",
    )
    function_definitions = function_definitions.replace(
        "for origin_time, row in df_test.iterrows():",
        "for step, (origin_time, row) in enumerate(df_test.iterrows(), start=1):\n"
        "        if step == 1 or step % 25 == 0 or step == len(df_test):\n"
        "            print(f'Base {BASE_NUMBER}: origem {step}/{len(df_test)}')",
    )
    exec(function_definitions, namespace)

    predictions, converged, warnings_seen, exog_cols = namespace[
        "walk_forward_sarimax_model"
    ](winner)
    namespace["validate_prediction_frame"](predictions)
    predictions.insert(0, "base_id", f"base_{base:02d}")
    predictions.insert(1, "modelo", "sarimax")
    predictions["residual"] = predictions["y_true"] - predictions["y_pred"]

    evidence = {
        "base_id": f"base_{base:02d}",
        "notebook": str(path.relative_to(ROOT)).replace("\\", "/"),
        "frozen_config": winner,
        "exog_used": exog_cols,
        "origins": len(predictions),
        "converged_all": bool(converged),
        "warnings": warnings_seen,
    }
    return predictions, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=int, choices=range(1, 6), required=True)
    args = parser.parse_args()

    predictions, evidence = run_final_evaluation(args.base)
    output_dir = ROOT / "results" / "predictions"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"base_{args.base:02d}__sarimax.csv"
    predictions.to_csv(output, index=False)

    audit_dir = ROOT / "results" / "extraidos_do_remoto"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit = audit_dir / f"base_{args.base:02d}__sarimax_final_audit.json"
    audit.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    mae = (predictions["y_true"] - predictions["y_pred"]).abs().mean()
    print(f"Concluído: {output}")
    print(f"Origens: {len(predictions)} | MAE: {mae:.12g} | Convergiu: {evidence['converged_all']}")


if __name__ == "__main__":
    main()
