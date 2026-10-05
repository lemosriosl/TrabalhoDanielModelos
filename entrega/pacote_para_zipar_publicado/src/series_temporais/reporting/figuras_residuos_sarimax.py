"""Gera diagnósticos gráficos do teste SARIMAX salvo, sem ajustar modelos."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf

from series_temporais.reporting.evidencias_relatorio import HORIZON


BASES = (1, 2, 3, 5)


def residuos_um_passo(path: Path, base: int) -> tuple[pd.DataFrame, int]:
    """Retém somente previsões causais com alvo no passo da frequência da base."""
    frame = pd.read_csv(path, usecols=[
        "origin_time", "target_time", "training_target_cutoff", "y_true", "y_pred"
    ])
    for column in ("origin_time", "target_time", "training_target_cutoff"):
        frame[column] = pd.to_datetime(frame[column], errors="raise")
    if frame.origin_time.duplicated().any():
        raise ValueError(f"Origens duplicadas: {path}")
    if not np.isfinite(frame[["y_true", "y_pred"]].to_numpy(dtype=float)).all():
        raise ValueError(f"Valor não finito: {path}")
    if frame.training_target_cutoff.gt(frame.origin_time).any():
        raise ValueError(f"Treino após a origem: {path}")
    mask = frame.target_time.sub(frame.origin_time).eq(HORIZON[base])
    excluded = int((~mask).sum())
    valid = frame.loc[mask].sort_values("target_time").copy()
    if valid.empty:
        raise ValueError(f"Sem previsões de um passo: {path}")
    valid["residuo"] = valid.y_true - valid.y_pred
    return valid, excluded


def gerar_figuras(predictions_dir: Path, output_dir: Path) -> list[dict[str, str | int]]:
    """Usa apenas os CSVs já calculados das Bases 1, 2, 3 e 5."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str | int]] = []
    for base in BASES:
        stem = f"base_{base:02d}"
        source = predictions_dir / f"{stem}__sarimax.csv"
        frame, excluded = residuos_um_passo(source, base)
        series = frame.residuo.to_numpy(dtype=float)
        residual_path = output_dir / f"{stem}__residuos.png"
        acf_path = output_dir / f"{stem}__acf.png"

        fig, ax = plt.subplots(figsize=(10, 3.2), constrained_layout=True)
        ax.plot(frame.target_time, series, color="#1769aa", linewidth=0.65)
        ax.axhline(0, color="#4b5563", linewidth=0.8)
        ax.set(title=f"Base {base}: resíduos SARIMAX fora da amostra",
               xlabel="Instante-alvo", ylabel="Real - previsto")
        fig.savefig(residual_path, dpi=150)
        plt.close(fig)

        max_lag = min(30, len(series) - 1)
        corr = acf(series, nlags=max_lag, fft=True)
        fig, ax = plt.subplots(figsize=(8, 3.2), constrained_layout=True)
        ax.vlines(range(1, max_lag + 1), 0, corr[1:], color="#1769aa", linewidth=1.2)
        ax.axhline(0, color="#4b5563", linewidth=0.8)
        bound = 1.96 / np.sqrt(len(series))
        ax.axhspan(-bound, bound, color="#a7cdea", alpha=0.42,
                   label="Referência aproximada de 95%")
        ax.set(title=f"Base {base}: ACF residual SARIMAX ({len(series)} origens)",
               xlabel="Defasagem", ylabel="ACF", xlim=(0, max_lag + 1), ylim=(-1, 1))
        ax.legend(loc="upper right", fontsize=8)
        fig.savefig(acf_path, dpi=150)
        plt.close(fig)

        rows.append({
            "base_id": stem, "origens_horizonte_1": len(frame),
            "horizontes_excluidos": excluded,
            "sha256_csv_fonte": hashlib.sha256(source.read_bytes()).hexdigest(),
            "figura_residuos": residual_path.name, "figura_acf": acf_path.name,
        })
    with (output_dir / "manifesto.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions-dir", type=Path,
                        default=root / "results" / "predictions")
    parser.add_argument("--output-dir", type=Path,
                        default=root / "results" / "figuras_sarimax")
    args = parser.parse_args()
    for row in gerar_figuras(args.predictions_dir, args.output_dir):
        print(row["base_id"], row["origens_horizonte_1"], row["horizontes_excluidos"])


if __name__ == "__main__":
    main()
