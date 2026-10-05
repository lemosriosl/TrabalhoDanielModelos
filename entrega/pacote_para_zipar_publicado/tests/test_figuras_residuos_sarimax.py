from pathlib import Path

import pandas as pd
import pytest

from series_temporais.reporting.figuras_residuos_sarimax import residuos_um_passo


def test_filtra_horizonte_e_calcula_residuo(tmp_path: Path):
    path = tmp_path / "sarimax.csv"
    pd.DataFrame([
        {"origin_time": "2020-01-01 00:00", "target_time": "2020-01-01 01:00",
         "training_target_cutoff": "2020-01-01 00:00", "y_true": 10, "y_pred": 8},
        {"origin_time": "2020-01-01 01:00", "target_time": "2020-01-01 03:00",
         "training_target_cutoff": "2020-01-01 01:00", "y_true": 12, "y_pred": 9},
    ]).to_csv(path, index=False)
    frame, excluded = residuos_um_passo(path, 2)
    assert excluded == 1
    assert len(frame) == 1
    assert frame.residuo.iloc[0] == 2


def test_rejeita_treino_posterior_a_origem(tmp_path: Path):
    path = tmp_path / "sarimax.csv"
    pd.DataFrame([{
        "origin_time": "2020-01-01 00:00", "target_time": "2020-01-01 01:00",
        "training_target_cutoff": "2020-01-01 01:00", "y_true": 10, "y_pred": 8,
    }]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Treino após a origem"):
        residuos_um_passo(path, 2)
