import numpy as np
import pandas as pd

from series_temporais.models.pipeline_sarimax import escalar_exogenas, prever_referencia


def test_escala_usa_somente_parametros_do_treino():
    indice = pd.date_range("2024-01-01", periods=6, freq="D")
    treino = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]}, index=indice[:4])
    futuro = pd.DataFrame({"x": [100.0, 101.0]}, index=indice[4:])
    treino_escalado, futuro_escalado, _ = escalar_exogenas(treino, futuro)
    assert abs(treino_escalado.x.mean()) < 1e-12
    assert futuro_escalado.x.iloc[0] > 50


def test_previsao_referencia_registra_bic_e_mae():
    indice = pd.date_range("2024-01-01", periods=24, freq="D")
    y = pd.Series(np.arange(24, dtype=float), index=indice)
    previsoes, registro = prever_referencia(
        y.iloc[:18], y.iloc[18:], order=(1, 1, 0), seasonal_order=(0, 0, 0, 0), maxiter=10
    )
    assert len(previsoes) == 6
    assert "BIC" in registro and "MAE" in registro and "convergiu" in registro
