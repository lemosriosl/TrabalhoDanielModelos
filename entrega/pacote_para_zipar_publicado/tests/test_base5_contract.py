import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from series_temporais.data import ALVO_CANONICO, preparar_modelagem_ouro
from series_temporais.validation import validate_prediction_contract


ROOT = Path(__file__).resolve().parents[1]


def _notebook_source(name: str) -> str:
    notebook = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )


def test_base5_shared_weekly_target_and_origins():
    raw = pd.read_csv(ROOT / "data" / "base_05" / "raw.csv")
    weekly, frame, features, train, test = preparar_modelagem_ouro(raw)

    assert len(weekly) == 2398
    assert len(frame) == 2344
    assert len(train) == 1758
    assert len(test) == 586
    assert len(features) == 49
    assert test.DATE.iloc[0] == pd.Timestamp("2003-01-17")
    assert test.DATE.iloc[-1] == pd.Timestamp("2014-04-04")
    assert test.target_date.iloc[-1] == pd.Timestamp("2014-04-11")
    assert train.target_date.max() == test.DATE.min()
    assert test.target_date.sub(test.DATE).eq(pd.Timedelta(days=7)).all()
    esperado = np.log(frame.target_price_t_plus_1 / frame.price_t)
    assert np.allclose(frame[ALVO_CANONICO], esperado)


def test_base5_canonical_notebooks_use_shared_return_contract():
    canonical = {
        "base_05-grupo5_SARIMAX.ipynb",
        "base_05-grupo5_HW.ipynb",
        "base_05-grupo5_RF_retorno.ipynb",
        "base_05-grupo5_XGBoost.ipynb",
    }
    for name in canonical:
        source = _notebook_source(name)
        assert "preparar_modelagem_ouro" in source, name
        assert "ALVO_CANONICO" in source, name
        assert "validate_prediction_contract" in source, name
        assert "586" in source, name
        assert "len(test_df)" in source or "len(df_test)" in source, name


def test_base5_price_random_forest_is_explicitly_auxiliary():
    path = ROOT / "notebooks" / "base_05-grupo5_RF_preco.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    markdown = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "markdown"
    ).lower()
    assert "auxiliar" in markdown
    assert "não participa" in markdown or "nao participa" in markdown


def test_prediction_contract_rejects_different_origins_or_targets():
    expected = pd.DataFrame(
        {
            "DATE": pd.to_datetime(["2024-01-05", "2024-01-12"]),
            "target_date": pd.to_datetime(["2024-01-12", "2024-01-19"]),
            ALVO_CANONICO: [0.01, -0.02],
        }
    )
    predictions = pd.DataFrame(
        {
            "origin_time": expected.DATE,
            "target_time": expected.target_date,
            "y_true": expected[ALVO_CANONICO],
            "y_pred": [0.0, 0.0],
            "training_target_cutoff": expected.DATE,
        }
    )
    validate_prediction_contract(
        predictions, expected, expected_target_col=ALVO_CANONICO,
    )

    wrong = predictions.copy()
    wrong.loc[1, "y_true"] = 0.5
    with pytest.raises(ValueError, match="valores reais"):
        validate_prediction_contract(
            wrong, expected, expected_target_col=ALVO_CANONICO,
        )
