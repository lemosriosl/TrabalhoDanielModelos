import numpy as np
import pandas as pd

from series_temporais.models.sarimax import SarimaxConfig
from series_temporais.models.sarimax_eficiente import avaliar_incremental


def test_avaliacao_incremental_e_causal_com_lacuna():
    indice = pd.date_range("2024-01-01", periods=48, freq="h")
    serie = pd.Series(np.arange(48, dtype=float), index=indice)
    serie.iloc[30] = np.nan
    previsoes, registro = avaliar_incremental(serie, indice[24], SarimaxConfig((1, 1, 0)))
    assert registro["observacoes_avaliadas"] == 23
    assert (previsoes.training_target_cutoff < previsoes.target_time).all()
