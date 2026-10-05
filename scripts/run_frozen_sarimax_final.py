"""Executa apenas o teste final SARIMAX com a configuração salva no notebook.

Não refaz a busca de hiperparâmetros. A configuração é lida do ranking HTML já
executado no notebook, preservando a decisão registrada no remoto.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import time
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np


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


def validate_base4_checkpoint_prefix(
    predictions: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame
) -> None:
    """Recusa uma retomada que não coincide com o começo do teste canônico."""

    from series_temporais.validation import validate_prediction_frame

    validate_prediction_frame(predictions)
    count = len(predictions)
    if count > len(test):
        raise ValueError("Checkpoint contém mais previsões que o teste.")
    expected_targets = pd.DatetimeIndex(test.index[:count])
    expected_origins = pd.DatetimeIndex(
        [train.index[-1], *test.index[: count - 1]]
    )
    targets = pd.DatetimeIndex(pd.to_datetime(predictions["target_time"]))
    origins = pd.DatetimeIndex(pd.to_datetime(predictions["origin_time"]))
    cutoffs = pd.DatetimeIndex(
        pd.to_datetime(predictions["training_target_cutoff"])
    )
    if not targets.equals(expected_targets) or not origins.equals(expected_origins):
        raise ValueError("Checkpoint não corresponde às origens canônicas da Base 4.")
    if not cutoffs.equals(expected_origins):
        raise ValueError("Checkpoint contém corte de treino incorreto.")
    if not np.allclose(
        predictions["y_true"].to_numpy(dtype=float),
        test["vendas"].iloc[:count].to_numpy(dtype=float),
    ):
        raise ValueError("Checkpoint contém valores reais divergentes.")
    if not np.allclose(
        predictions["residual"].to_numpy(dtype=float),
        predictions["y_true"].to_numpy(dtype=float)
        - predictions["y_pred"].to_numpy(dtype=float),
    ):
        raise ValueError("Checkpoint contém resíduos divergentes.")
    if not predictions["base_id"].eq("base_04").all() or not predictions[
        "modelo"
    ].eq("sarimax").all():
        raise ValueError("Checkpoint pertence a outra base ou modelo.")


def checkpoint_base4(
    namespace: dict[str, Any], winner: dict[str, Any], every: int
) -> tuple[pd.DataFrame, bool, str, list[str]]:
    """Avalia blocos consecutivos com o mesmo histórico causal do loop integral."""

    if every < 1:
        raise ValueError("checkpoint_every deve ser positivo.")
    train = namespace["df_train"].copy()
    test = namespace["df_test"].copy()
    output = ROOT / "results" / "predictions" / "base_04__sarimax.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        completed = pd.read_csv(output)
        validate_base4_checkpoint_prefix(completed, train, test)
        if "converged" not in completed.columns:
            raise ValueError("Checkpoint sem registro de convergência.")
    else:
        completed = pd.DataFrame()
    convergence = bool(completed["converged"].all()) if len(completed) else True
    warnings_seen: list[str] = []
    exog_cols = list(winner["exog_cols"])

    for start in range(len(completed), len(test), every):
        end = min(start + every, len(test))
        namespace["df_train"] = pd.concat([train, test.iloc[:start]])
        namespace["df_test"] = test.iloc[start:end].copy()
        part, converged, warning_text, exog_cols = namespace[
            "walk_forward_sarimax_model"
        ](winner)
        part.insert(0, "base_id", "base_04")
        part.insert(1, "modelo", "sarimax")
        part["residual"] = part["y_true"] - part["y_pred"]
        part["converged"] = bool(converged)
        completed = pd.concat([completed, part], ignore_index=True)
        validate_base4_checkpoint_prefix(completed, train, test)
        convergence = convergence and bool(converged)
        if warning_text:
            warnings_seen.append(warning_text)
        temporary = output.with_suffix(".csv.tmp")
        completed.to_csv(temporary, index=False)
        os.replace(temporary, output)
        print(f"CHECKPOINT_BASE04={end}/{len(test)}", flush=True)

    namespace["df_train"] = train
    namespace["df_test"] = test
    return completed, convergence, " | ".join(warnings_seen[:3]), exog_cols


def run_final_evaluation(
    base: int, *, benchmark_origins: int | None = None,
    checkpoint_every: int | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
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
    if benchmark_origins is not None:
        if benchmark_origins < 1:
            raise ValueError("benchmark_origins deve ser positivo.")
        namespace["df_test"] = namespace["df_test"].iloc[:benchmark_origins].copy()

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

    if checkpoint_every is not None:
        if base != 4 or benchmark_origins is not None:
            raise ValueError("Checkpoint é exclusivo do teste final da Base 4.")
        predictions, converged, warnings_seen, exog_cols = checkpoint_base4(
            namespace, winner, checkpoint_every
        )
    else:
        predictions, converged, warnings_seen, exog_cols = namespace[
            "walk_forward_sarimax_model"
        ](winner)
    namespace["validate_prediction_frame"](predictions)
    if "base_id" not in predictions.columns:
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
    parser.add_argument("--benchmark-origins", type=int)
    parser.add_argument("--checkpoint-every", type=int)
    args = parser.parse_args()

    started = time.perf_counter()
    predictions, evidence = run_final_evaluation(
        args.base, benchmark_origins=args.benchmark_origins,
        checkpoint_every=args.checkpoint_every,
    )
    if args.benchmark_origins is not None:
        elapsed = time.perf_counter() - started
        print(
            f"Benchmark Base {args.base}: {len(predictions)} origens em "
            f"{elapsed:.2f}s; nenhum resultado final foi gravado."
        )
        return
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
