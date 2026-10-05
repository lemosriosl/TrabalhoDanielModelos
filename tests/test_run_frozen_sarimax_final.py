import json

import pandas as pd
import pytest

import scripts.run_frozen_sarimax_final as runner
from scripts.run_frozen_sarimax_final import (
    checkpoint_base4,
    final_frame_setup_source,
    frozen_sarimax_config,
    notebook_path,
    validate_base4_checkpoint_prefix,
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


def test_base4_checkpoint_must_match_canonical_prefix():
    train = pd.DataFrame(
        {"vendas": [1.0, 2.0]}, index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    test = pd.DataFrame(
        {"vendas": [3.0, 4.0]}, index=pd.to_datetime(["2020-01-03", "2020-01-04"])
    )
    predictions = pd.DataFrame(
        {
            "base_id": ["base_04"],
            "modelo": ["sarimax"],
            "origin_time": ["2020-01-02"],
            "target_time": ["2020-01-03"],
            "y_true": [3.0],
            "y_pred": [2.5],
            "training_target_cutoff": ["2020-01-02"],
            "residual": [0.5],
        }
    )

    validate_base4_checkpoint_prefix(predictions, train, test)
    predictions.loc[0, "target_time"] = "2020-01-04"
    with pytest.raises(ValueError, match="origens canônicas"):
        validate_base4_checkpoint_prefix(predictions, train, test)


def test_base4_checkpoint_resumes_without_repeating_origins(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    train = pd.DataFrame(
        {"vendas": [1.0, 2.0]}, index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    test = pd.DataFrame(
        {"vendas": [3.0, 4.0, 5.0]},
        index=pd.to_datetime(["2020-01-03", "2020-01-04", "2020-01-05"]),
    )
    namespace = {"df_train": train, "df_test": test}
    calls = []

    def predict_one_block(_winner):
        calls.append(len(namespace["df_test"]))
        history = namespace["df_train"].copy()
        rows = []
        for target_time, row in namespace["df_test"].iterrows():
            cutoff = history.index[-1]
            rows.append(
                {
                    "origin_time": cutoff,
                    "target_time": target_time,
                    "y_true": row["vendas"],
                    "y_pred": history["vendas"].iloc[-1],
                    "training_target_cutoff": cutoff,
                }
            )
            history = pd.concat([history, row.to_frame().T.set_axis([target_time])])
        return pd.DataFrame(rows), True, "", []

    namespace["walk_forward_sarimax_model"] = predict_one_block
    winner = {"exog_cols": []}

    first, _, _, _ = checkpoint_base4(namespace, winner, 2)
    second, _, _, _ = checkpoint_base4(namespace, winner, 2)

    assert len(first) == len(second) == 3
    assert calls == [2, 1]
    assert first["y_pred"].tolist() == [2.0, 3.0, 4.0]
