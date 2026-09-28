import numpy as np
import pandas as pd

from series_temporais.models.pipeline_sarimax_walkforward import prever_walk_forward_referencia


def test_walk_forward_da_pipeline_nao_vaza_alvo():
    indice = pd.date_range("2024-01-01", periods=30, freq="D")
    serie = pd.Series(np.arange(30, dtype=float), index=indice, name="y")
    previsoes, registro = prever_walk_forward_referencia(
        serie, indice[20], order=(1, 1, 0), seasonal_order=(0, 0, 0, 0), maxiter=10
    )
    assert len(previsoes) == 10
    assert (previsoes.training_target_cutoff < previsoes.index).all()
    assert "BIC" in registro and "convergiu" in registro
