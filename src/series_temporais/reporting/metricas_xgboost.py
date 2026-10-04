"""Consolidação dos XGBoosts executados; não importa nem ajusta estimadores."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from series_temporais.paths import project_root
from series_temporais.results import METRICS_COLUMNS, write_metrics
from series_temporais.validation import validate_prediction_frame


def registro_xgboost(predictions, summary, metadata, *, interval, exogenous,
                     commit, generated_at):
    """Recalcula MAE e verifica a evidência antes de construir uma linha."""
    base = int(summary["base"])
    if base not in range(1, 6):
        raise ValueError("Base inválida.")
    if base == 5:
        actual, forecast = "y_true_return", "y_pred_return_xgb"
        origin, target = "DATE", "target_date"
    else:
        actual, forecast = "y_true", "y_pred_xgb"
        origin, target = "origin_time", "target_time"
    contract = predictions.rename(columns={origin: "origin_time", target: "target_time",
                                           actual: "y_true", forecast: "y_pred"})
    validate_prediction_frame(contract)
    refits = pd.to_datetime(predictions.model_refit_origin)
    origins = pd.to_datetime(predictions[origin])
    cutoffs = pd.to_datetime(predictions.training_target_cutoff)
    if refits.isna().any() or not ((cutoffs <= refits) & (refits <= origins)).all():
        raise ValueError("Origem de reajuste não causal.")
    if not isinstance(interval, int) or isinstance(interval, bool) or interval < 1:
        raise ValueError("Intervalo de retreino inválido.")
    expected_refits = (len(predictions) + interval - 1) // interval
    if len(predictions) != summary["observacoes_teste"]:
        raise ValueError("Quantidade de origens divergente.")
    if refits.nunique() != expected_refits or summary["refits"] != expected_refits:
        raise ValueError("Cadência divergente da execução.")
    # Além da quantidade, confira a sequência exata das origens de reajuste.
    expected = pd.Series(origins.iloc[::interval].repeat(interval).to_numpy()[:len(origins)])
    if not refits.reset_index(drop=True).equals(expected):
        raise ValueError("Cadência divergente da execução.")
    real = predictions[actual].to_numpy(dtype=float)
    pred = predictions[forecast].to_numpy(dtype=float)
    mae = float(np.mean(np.abs(real - pred)))
    if not np.isclose(mae, summary["mae_xgboost"], rtol=1e-9, atol=1e-10):
        raise ValueError("MAE divergente do resumo executado.")
    if summary["search_candidates"] != 150 or summary["alvo"] != metadata["target"]:
        raise ValueError("Resumo incompatível com busca completa ou alvo.")
    if summary["frequencia"] != metadata["frequency"]:
        raise ValueError("Frequência divergente.")
    times = [float(summary[key]) for key in ("search_seconds_recorded", "evaluation_seconds")]
    if not np.isfinite(times).all() or min(times) < 0:
        raise ValueError("Tempo registrado inválido.")
    mape = None if base == 5 or np.any(real == 0) else float(np.mean(np.abs((real - pred) / real)) * 100)
    return {
        "base_id": f"base_{base:02d}", "modelo": "XGBoost",
        "alvo": metadata["target"], "frequencia": metadata["frequency"],
        "horizonte_passos": metadata["horizon_steps"], "origens_avaliadas": len(real),
        "mae": mae, "mape": mape, "posicao_base": None, "vencedor": None,
        "tempo_execucao_segundos": sum(times),
        "hiperparametros": {"estimador": summary["best_params"], "refit_every": interval,
                            "search_candidates": summary["search_candidates"]},
        "features_exogenas": list(exogenous),
        "notebook": f"notebooks/base_{base:02d}-grupo{base}_XGBoost.ipynb",
        "commit": commit, "gerado_em": generated_at,
    }


def atualizar_metricas_xgboost(root, summaries):
    """Valida todas as entradas antes de substituir suas linhas no consolidado."""
    root = Path(root)
    config = yaml.safe_load((root / "projeto.yaml").read_text(encoding="utf-8"))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        commit += "+dirty"
    generated_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for summary in summaries:
        base = int(summary["base"])
        directory = root / "data" / f"base_{base:02d}"
        metadata = yaml.safe_load((directory / "metadata.yaml").read_text(encoding="utf-8"))
        data = directory / ("raw.csv" if base == 5 else "prepared.csv")
        if hashlib.sha256(data.read_bytes()).hexdigest() != summary["data_sha256"]:
            raise ValueError(f"Dado mudou desde a execução da Base {base}.")
        predictions = pd.read_csv(root / "results" / "residuals" / f"base_{base:02d}_XGBoost.csv")
        availability = pd.read_csv(directory / metadata["external_availability"])
        exogenous = availability.loc[availability.feature.notna() &
                                    availability.disponibilidade.ne("proibida"), "feature"].tolist()
        interval = config["validacao"]["intervalo_retreino_xgboost_por_base"][f"base_{base:02d}"]
        rows.append(registro_xgboost(predictions, summary, metadata, interval=interval,
                                    exogenous=exogenous, commit=commit, generated_at=generated_at))
    keys = [(row["base_id"], row["modelo"]) for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("Bases duplicadas na consolidação.")
    path = root / "results" / "metrics.csv"
    previous = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=METRICS_COLUMNS)
    keep = [row for row in previous.to_dict("records")
            if (row["base_id"], row["modelo"]) not in keys]
    return write_metrics([*keep, *rows], path)


def comparacao_xgboost(root):
    """Compara os registros atuais com persistência; nenhuma média de MAEs."""
    root = Path(root)
    path = root / "results" / "metrics.csv"
    columns = ["base_id", "alvo", "frequencia", "origens_avaliadas", "mae_xgboost",
               "mae_persistencia", "skill_vs_persistencia", "vence_persistencia"]
    if not path.exists():
        return pd.DataFrame(columns=columns)
    metrics = pd.read_csv(path)
    records = []
    xgb = metrics.loc[metrics.modelo.eq("XGBoost")]
    if xgb.base_id.duplicated().any():
        raise ValueError("Registros XGBoost duplicados.")
    for row in xgb.to_dict("records"):
        path = root / "results" / "residuals" / f"{row['base_id']}_XGBoost.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if row["base_id"] == "base_05":
            actual, forecast, baseline = "y_true_return", "y_pred_return_xgb", "y_pred_return_zero"
        else:
            actual, forecast, baseline = "y_true", "y_pred_xgb", "y_pred_persistencia"
        values = frame[[actual, forecast, baseline]].to_numpy(dtype=float)
        if not np.isfinite(values).all() or len(frame) != row["origens_avaliadas"]:
            raise ValueError("CSV incompatível com o consolidado.")
        mae = float(np.mean(np.abs(values[:, 0] - values[:, 1])))
        persistence = float(np.mean(np.abs(values[:, 0] - values[:, 2])))
        if not np.isclose(mae, row["mae"], rtol=1e-9, atol=1e-10):
            raise ValueError("MAE divergente entre CSV e consolidado.")
        records.append({
            **{key: row[key] for key in columns[:4]},
            "mae_xgboost": mae, "mae_persistencia": persistence,
            "skill_vs_persistencia": 1 - mae / persistence if persistence else None,
            "vence_persistencia": mae < persistence,
        })
    return pd.DataFrame(records, columns=columns).sort_values("base_id").reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--summary-dir", type=Path, default=Path(tempfile.gettempdir()) /
                        "trabalho_daniel_xgboost" / "summary")
    args = parser.parse_args()
    root = args.root or project_root()
    summaries = [json.loads((args.summary_dir / f"base{n}.json").read_text(encoding="utf-8"))
                 for n in range(1, 6)]
    result = atualizar_metricas_xgboost(root, summaries)
    print(result[["base_id", "modelo", "alvo", "origens_avaliadas", "mae"]].to_string(index=False))
    print(f"Consolidado salvo: {root / 'results' / 'metrics.csv'}")


if __name__ == "__main__":
    main()
