"""Comparação exploratória entre HW e SARIMAX nas observações idênticas.

Não produz ranking dos quatro modelos nem substitui o teste canônico.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from series_temporais.reporting.evidencias_relatorio import HORIZON


def _read_predictions(path: Path, base: int) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["origin_time", "target_time", "y_true", "y_pred"])
    frame["origin_time"] = pd.to_datetime(frame.origin_time)
    frame["target_time"] = pd.to_datetime(frame.target_time)
    if frame.origin_time.duplicated().any():
        raise ValueError(f"Origens duplicadas: {path}")
    if not np.isfinite(frame[["y_true", "y_pred"]].to_numpy()).all():
        raise ValueError(f"Valores não finitos: {path}")
    frame = frame.loc[frame.target_time.sub(frame.origin_time).eq(HORIZON[base])].copy()
    return frame


def gerar_comparacao_pareada(predictions_dir: Path, bases=(1, 2, 3, 5)) -> pd.DataFrame:
    """Compara somente pares com origem, alvo e valor real coincidentes."""
    rows = []
    for base in bases:
        stem = f"base_{base:02d}"
        hw = _read_predictions(predictions_dir / f"{stem}__holt_winters.csv", base)
        sar = _read_predictions(predictions_dir / f"{stem}__sarimax.csv", base)
        paired = hw.merge(sar, on=["origin_time", "target_time"], suffixes=("_hw", "_sar"), validate="one_to_one")
        same_actual = np.isclose(paired.y_true_hw, paired.y_true_sar, rtol=0, atol=1e-8)
        if not same_actual.all():
            raise ValueError(f"Valor real divergente nas origens pareadas: {stem}")
        if paired.empty:
            raise ValueError(f"Sem observações pareadas: {stem}")
        rows.append({
            "base_id": stem,
            "origens_pareadas": len(paired),
            "mae_hw_pareado": float((paired.y_true_hw - paired.y_pred_hw).abs().mean()),
            "mae_sarimax_pareado": float((paired.y_true_sar - paired.y_pred_sar).abs().mean()),
            "origens_hw_horizonte_1": len(hw),
            "origens_sarimax_horizonte_1": len(sar),
            "escopo": "exploratorio_dois_modelos_sem_ranking_final",
        })
    return pd.DataFrame(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions-dir", type=Path, default=root / "results" / "predictions")
    parser.add_argument("--output", type=Path, default=root / "results" / "comparacao_pareada_hw_sarimax.csv")
    args = parser.parse_args()
    result = gerar_comparacao_pareada(args.predictions_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
