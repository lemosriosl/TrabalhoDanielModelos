import csv
from pathlib import Path

import pytest

from series_temporais.results import METRICS_COLUMNS, metrics_frame, write_metrics


ROOT = Path(__file__).resolve().parents[1]


def test_metrics_csv_uses_the_canonical_header():
    with (ROOT / "results" / "metrics.csv").open(encoding="utf-8", newline="") as file:
        assert tuple(next(csv.reader(file))) == METRICS_COLUMNS


def test_empty_metrics_file_can_be_regenerated(tmp_path):
    output = tmp_path / "metrics.csv"
    frame = write_metrics([], output)
    assert frame.empty
    assert output.read_text(encoding="utf-8").splitlines()[0] == ",".join(METRICS_COLUMNS)


def test_incomplete_metric_row_is_rejected():
    with pytest.raises(KeyError, match="colunas obrigatórias"):
        metrics_frame([{"base_id": "base_01", "modelo": "SARIMAX"}])
