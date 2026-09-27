import numpy as np
import pandas as pd

from series_temporais.models.sarimax import (
    SarimaxConfig,
    diagnostico_ljung_box,
    exogenas_defasadas,
    metricas_previsao,
    walk_forward_um_passo,
)


def test_exogenas_observadas_sao_defasadas():
    indice = pd.date_range("2024-01-01", periods=4, freq="D")
    original = pd.DataFrame({"chuva": [1, 2, 3, 4]}, index=indice)

    resultado = exogenas_defasadas(original)

    assert pd.isna(resultado.iloc[0, 0])
    assert resultado.iloc[2, 0] == 2


def test_walk_forward_registra_apenas_alvos_futuros():
    indice = pd.date_range("2024-01-01", periods=32, freq="D")
    serie = pd.Series(np.linspace(1, 32, 32) + np.sin(np.arange(32)), index=indice)
    previsoes, registro = walk_forward_um_passo(
        serie,
        inicio_teste=indice[24],
        config=SarimaxConfig(order=(1, 0, 0)),
    )

    assert len(previsoes) == 8
    assert (previsoes.training_target_cutoff < previsoes.target_time).all()
    assert previsoes.origin_time.iloc[0] == indice[23]
    assert registro["observacoes_teste"] == 8
    assert metricas_previsao(previsoes)["MAE"] >= 0
    assert not diagnostico_ljung_box(previsoes, [1, 2]).empty
