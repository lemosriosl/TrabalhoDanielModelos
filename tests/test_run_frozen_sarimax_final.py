import json

from scripts.run_frozen_sarimax_final import (
    final_frame_setup_source,
    frozen_sarimax_config,
    notebook_path,
)


def test_frozen_sarimax_config_reads_first_ranked_sarimax_candidate():
    notebook = {
        "cells": [
            {
                "outputs": [
                    {
                        "data": {
                            "text/html": (
                                "<table><tr><th>candidate_key</th><th>family</th></tr>"
                                '<tr><td>{"order": [1, 1, 1], "exog_cols": []}</td>'
                                "<td>SARIMAX</td></tr></table>"
                            )
                        }
                    }
                ]
            }
        ]
    }

    assert frozen_sarimax_config(notebook) == {"order": [1, 1, 1], "exog_cols": []}


def test_base5_uses_its_weekly_canonical_test_setup():
    notebook = json.loads(notebook_path(5).read_text(encoding="utf-8"))

    setup = final_frame_setup_source(notebook, 5)

    assert "def fit_sarimax_model" in setup
    assert "if df_train.empty or df_test.empty" in setup
    assert "df_train = df.iloc" not in setup
