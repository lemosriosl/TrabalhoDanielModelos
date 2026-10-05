from series_temporais.notebook_metrics import find_metric_table


def test_find_metric_table_reads_html_notebook_output():
    notebook = {
        "cells": [
            {"outputs": [{"data": {"text/html": "<table><tr><th>modelo</th><th>MAE</th></tr><tr><td>RF</td><td>1.2</td></tr></table>"}}]}
        ]
    }

    table = find_metric_table(notebook, "MAE")

    assert table.to_dict("records") == [{"modelo": "RF", "MAE": 1.2}]
