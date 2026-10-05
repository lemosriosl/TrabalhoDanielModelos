"""Extrai métricas e diagnósticos das execuções salvas, sem refazer o tuning."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox


LAGS = {
    1: [1, 7, 14, 30],
    2: [1, 24, 48, 168],
    3: [1, 24, 48, 168],
    4: [1, 6, 144, 288],
    5: [1, 4, 13, 26, 52],
}
HORIZON = {1: pd.Timedelta(days=1), 2: pd.Timedelta(hours=1),
           3: pd.Timedelta(hours=1), 4: pd.Timedelta(minutes=10),
           5: pd.Timedelta(days=7)}


def _notebook(root: Path, base: int, model: str) -> tuple[Path, dict]:
    name = f"base_{base:02d}-grupo{base}_{model}.ipynb"
    if base == 5 and model == "RF":
        name = "base_05-grupo5_RF_retorno.ipynb"
    path = root / "notebooks" / name
    return path, json.loads(path.read_text(encoding="utf-8"))


def _tables(notebook: dict):
    for cell_index, cell in enumerate(notebook["cells"]):
        for output in cell.get("outputs", []):
            raw = output.get("data", {}).get("text/html")
            if not raw:
                continue
            html = "".join(raw) if isinstance(raw, list) else raw
            try:
                tables = pd.read_html(StringIO(html))
            except ValueError:
                continue
            for frame in tables:
                yield cell_index, frame


def _metric_from_notebook(root: Path, base: int, model: str) -> tuple[float, int, str]:
    path, notebook = _notebook(root, base, model)
    count = None
    mae = None
    for _, frame in _tables(notebook):
        columns = set(frame.columns)
        if {"recorte", "linhas"}.issubset(columns):
            test = frame.loc[frame.recorte.astype(str).str.startswith("teste")]
            if len(test):
                count = int(test.iloc[0].linhas)
        if base == 5 and model == "RF" and {"modelo", "MAE_retorno"}.issubset(columns):
            selected = frame.loc[frame.modelo.astype(str).str.startswith("Random Forest — todas")]
            if len(selected):
                mae = float(selected.iloc[0].MAE_retorno)
                count = int(selected.iloc[0].observacoes)
        elif base < 5 and {"modelo", "MAE"}.issubset(columns):
            selected = frame.loc[frame.modelo.eq("Random Forest")]
            if len(selected):
                mae = float(selected.iloc[0].MAE)
    if count is None or mae is None:
        raise ValueError(f"RF sem métrica ou contagem salva: {path}")
    return mae, count, str(path.relative_to(root)).replace("\\", "/")


def _prediction_metric(path: Path) -> tuple[float, int, pd.Series]:
    frame = pd.read_csv(path)
    required = {"origin_time", "target_time", "training_target_cutoff", "y_true", "y_pred"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Previsões sem contrato: {path}")
    if frame.origin_time.duplicated().any():
        raise ValueError(f"Origens duplicadas: {path}")
    origin = pd.to_datetime(frame.origin_time)
    target = pd.to_datetime(frame.target_time)
    cutoff = pd.to_datetime(frame.training_target_cutoff)
    if not (origin.lt(target).all() and cutoff.le(origin).all()):
        raise ValueError(f"Contrato temporal inválido: {path}")
    residual = frame.y_true.astype(float) - frame.y_pred.astype(float)
    if not np.isfinite(residual).all():
        raise ValueError(f"Resíduos não finitos: {path}")
    for name in ("residuo", "residual"):
        if name in frame and not np.allclose(frame[name], residual, rtol=1e-7, atol=1e-8):
            raise ValueError(f"Resíduos inconsistentes: {path}")
    return float(residual.abs().mean()), len(frame), residual


def _ljung_from_notebook(root: Path, base: int, model: str) -> list[dict]:
    path, notebook = _notebook(root, base, model)
    candidate = None
    for cell_index, frame in _tables(notebook):
        if "lb_pvalue" in frame.columns and "lb_stat" in frame.columns:
            candidate = (cell_index, frame)
    if candidate is None:
        raise ValueError(f"Ljung-Box ausente: {path}")
    cell_index, frame = candidate
    lag_column = "lag" if "lag" in frame else frame.columns[0]
    return [
        {
            "base_id": f"base_{base:02d}", "modelo": "Random Forest" if model == "RF" else model,
            "lag": int(row[lag_column]), "lb_stat": float(row.lb_stat),
            "p_valor": float(row.lb_pvalue), "fonte": f"{path.relative_to(root).as_posix()}#cell-{cell_index}",
        }
        for _, row in frame.iterrows()
    ]


def gerar_evidencias(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Produz tabelas rastreáveis; jamais calcula ranking com amostras distintas."""
    root = root.resolve()
    xgb = pd.read_csv(root / "results" / "metrics.csv").set_index("base_id")
    metrics: list[dict] = []
    diagnostics: list[dict] = []
    findings: list[str] = []
    for base in range(1, 6):
        base_id = f"base_{base:02d}"
        saved_predictions = {}
        for model, stem in (("Holt-Winters", "holt_winters"), ("SARIMAX", "sarimax")):
            if base == 4 and model == "SARIMAX":
                findings.append("Base 4: SARIMAX final excluído por solicitação do grupo.")
                continue
            path = root / "results" / "predictions" / f"{base_id}__{stem}.csv"
            mae, count, residual = _prediction_metric(path)
            observed = pd.read_csv(path, usecols=["origin_time", "target_time", "y_true", "y_pred"])
            saved_predictions[model] = observed.drop(columns="y_pred")
            one_step = pd.to_datetime(observed.target_time).sub(pd.to_datetime(observed.origin_time)).eq(HORIZON[base])
            valid_count = int(one_step.sum())
            valid_mae = float((observed.loc[one_step, "y_true"] - observed.loc[one_step, "y_pred"]).abs().mean())
            if valid_count != count:
                findings.append(f"{base_id}: {model} possui {count-valid_count} de {count} previsões com horizonte diferente de um passo; MAE global não é homologável como teste de um passo.")
            metrics.append({"base_id": base_id, "modelo": model, "mae": mae, "origens": count,
                            "origens_horizonte_1": valid_count, "mae_horizonte_1": valid_mae,
                            "fonte": path.relative_to(root).as_posix(), "tipo_fonte": "csv_final"})
            lb = acorr_ljungbox(residual.loc[one_step.to_numpy()].reset_index(drop=True),
                                lags=LAGS[base], return_df=True)
            diagnostics.extend({"base_id": base_id, "modelo": model, "lag": int(lag),
                                "lb_stat": float(row.lb_stat), "p_valor": float(row.lb_pvalue),
                                "fonte": path.relative_to(root).as_posix()}
                               for lag, row in lb.iterrows())
        if len(saved_predictions) == 2:
            common = saved_predictions["Holt-Winters"].merge(saved_predictions["SARIMAX"],
                on="origin_time", how="inner", suffixes=("_hw", "_sarimax"))
            if not common.target_time_hw.eq(common.target_time_sarimax).all() or not np.allclose(
                    common.y_true_hw, common.y_true_sarimax, equal_nan=True):
                findings.append(f"{base_id}: Holt-Winters e SARIMAX discordam em alvo/instante nas origens comuns.")
            elif len(common) != len(saved_predictions["Holt-Winters"]) or len(common) != len(saved_predictions["SARIMAX"]):
                findings.append(f"{base_id}: Holt-Winters e SARIMAX compartilham {len(common)} origens, de {len(saved_predictions['Holt-Winters'])} e {len(saved_predictions['SARIMAX'])} respectivamente.")
        rf_mae, rf_count, rf_source = _metric_from_notebook(root, base, "RF")
        metrics.append({"base_id": base_id, "modelo": "Random Forest", "mae": rf_mae,
                        "origens": rf_count, "fonte": rf_source, "tipo_fonte": "notebook_executado"})
        diagnostics.extend(_ljung_from_notebook(root, base, "RF"))
        rf_csv = root / "results" / "predictions" / f"{base_id}__random_forest.csv"
        if rf_csv.exists():
            csv_mae, csv_count, _ = _prediction_metric(rf_csv)
            if csv_count != rf_count or not np.isclose(csv_mae, rf_mae, rtol=1e-5):
                findings.append(f"{base_id}: CSV local de RF ({csv_mae:.6f}; {csv_count} origens) diverge do notebook ({rf_mae:.6f}; {rf_count} origens).")
        xrow = xgb.loc[base_id]
        metrics.append({"base_id": base_id, "modelo": "XGBoost", "mae": float(xrow.mae),
                        "origens": int(xrow.origens_avaliadas), "fonte": "results/metrics.csv",
                        "tipo_fonte": "consolidado_xgboost"})
        diagnostics.extend(_ljung_from_notebook(root, base, "XGBoost"))
        counts = {r["modelo"]: r["origens"] for r in metrics if r["base_id"] == base_id}
        if len(set(counts.values())) > 1:
            findings.append(f"{base_id}: contagens de origens distintas: {counts}.")
    metrics_frame = pd.DataFrame(metrics)
    metrics_frame["origens_horizonte_1"] = metrics_frame["origens_horizonte_1"].astype("Int64")
    return metrics_frame, pd.DataFrame(diagnostics), findings


def salvar_evidencias(root: Path) -> tuple[Path, Path, Path]:
    metrics, diagnostics, findings = gerar_evidencias(root)
    target = root / "results"
    target.mkdir(parents=True, exist_ok=True)
    metrics_path = target / "metricas_individuais_auditadas.csv"
    diagnostics_path = target / "ljung_box_auditado.csv"
    findings_path = target / "achados_auditoria.json"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8")
    diagnostics.to_csv(diagnostics_path, index=False, encoding="utf-8")
    findings_path.write_text(json.dumps(findings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metrics_path, diagnostics_path, findings_path


if __name__ == "__main__":
    for result in salvar_evidencias(Path(__file__).resolve().parents[3]):
        print(result)
