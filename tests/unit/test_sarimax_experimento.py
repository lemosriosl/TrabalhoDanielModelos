import numpy as np
import pandas as pd

from series_temporais.models.sarimax import SarimaxConfig
from series_temporais.models.sarimax_experimento import walk_forward_horario


def test_walk_forward_preserva_lacunas_sem_pontuar_ou_vazar():
    indice = pd.date_range("2024-01-01", periods=36, freq="h")
    y = pd.Series(np.arange(36, dtype=float), index=indice)
    y.iloc[[4, 19, 27]] = np.nan

    previsoes, registro = walk_forward_horario(
        y, indice[18], SarimaxConfig(order=(1, 1, 0))
    )

    assert len(previsoes) == y.iloc[18:].notna().sum()
    assert registro["lacunas_na_avaliacao"] == 2
    assert (previsoes["training_target_cutoff"] < previsoes["target_time"]).all()
