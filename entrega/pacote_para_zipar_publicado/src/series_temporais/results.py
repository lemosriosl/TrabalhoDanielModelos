"""Contrato compartilhado para o consolidado de métricas dos modelos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd


METRICS_COLUMNS = (
    "base_id",
    "modelo",
    "alvo",
    "frequencia",
    "horizonte_passos",
    "origens_avaliadas",
    "mae",
    "mape",
    "posicao_base",
    "vencedor",
    "tempo_execucao_segundos",
    "hiperparametros",
    "features_exogenas",
    "notebook",
    "commit",
    "gerado_em",
)


def metrics_frame(rows: Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    """Normaliza registros de métricas e rejeita linhas incompletas."""

    frame = pd.DataFrame(rows)
    missing = sorted(set(METRICS_COLUMNS).difference(frame.columns))
    if missing and not frame.empty:
        raise KeyError(f"Métricas sem colunas obrigatórias: {missing}")
    if frame.empty:
        return pd.DataFrame(columns=METRICS_COLUMNS)

    frame = frame.loc[:, METRICS_COLUMNS].copy()
    for column in ("hiperparametros", "features_exogenas"):
        frame[column] = frame[column].map(
            lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True)
            if isinstance(value, (dict, list, tuple))
            else value
        )
    return frame.sort_values(["base_id", "posicao_base", "modelo"], kind="stable")


def write_metrics(rows: Iterable[Mapping[str, Any]], path: Path) -> pd.DataFrame:
    """Grava o consolidado canônico; o CSV nunca deve ser editado à mão."""

    frame = metrics_frame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    return frame
