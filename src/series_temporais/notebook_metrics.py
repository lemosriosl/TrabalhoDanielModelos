"""Leitura de tabelas de métricas registradas em notebooks executados."""

from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd


def find_metric_table(notebook: dict[str, Any], required_column: str) -> pd.DataFrame:
    """Retorna a primeira tabela HTML de saída que contém a coluna requerida."""

    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            html = output.get("data", {}).get("text/html")
            if not html:
                continue
            if isinstance(html, list):
                html = "".join(html)
            for table in pd.read_html(StringIO(html)):
                if required_column in table.columns:
                    return table
    raise ValueError(f"Notebook não contém tabela com a coluna {required_column!r}.")
