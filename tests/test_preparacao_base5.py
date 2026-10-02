import pandas as pd
import pytest

import numpy as np

from series_temporais.data.preparacao_base5 import (
    construir_quadro_ouro,
    selecionar_alvos_observados,
)


def test_selecionar_alvos_observados_exclui_preco_carregado_sem_reordenar():
    quadro = pd.DataFrame(
        {
            "DATE": pd.to_datetime(["2024-01-05", "2024-01-12", "2024-01-19"]),
            "target_has_new_quote": [1, 0, 1],
            "target_price_t_plus_1": [100.0, 100.0, 104.0],
        }
    )

    observado = selecionar_alvos_observados(quadro)

    assert observado["DATE"].tolist() == [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-19")]
    assert observado["target_price_t_plus_1"].tolist() == [100.0, 104.0]
    assert observado.index.tolist() == [0, 1]


@pytest.mark.parametrize("valores", [[1, None], [1, 2]])
def test_selecionar_alvos_observados_rejeita_indicador_invalido(valores):
    quadro = pd.DataFrame({"target_has_new_quote": valores})

    with pytest.raises(ValueError, match="binário"):
        selecionar_alvos_observados(quadro)


def test_selecionar_alvos_observados_exige_indicador():
    with pytest.raises(KeyError, match="target_has_new_quote"):
        selecionar_alvos_observados(pd.DataFrame({"alvo": [1.0]}))


def test_quadro_marca_semana_alvo_sem_cotacao_sem_usar_indicador_como_feature():
    datas = pd.date_range("2023-01-06", periods=60, freq="W-FRI")
    precos = pd.Series(np.arange(100.0, 160.0))
    precos.iloc[56] = precos.iloc[55]
    observacoes = pd.Series(1, index=range(60))
    observacoes.iloc[56] = 0
    semanal = pd.DataFrame(
        {
            "DATE": datas,
            "price_t": precos,
            "treasury_10y_t": np.linspace(3.0, 4.0, 60),
            "fed_funds_rate_t": np.linspace(4.0, 5.0, 60),
            "source_observations": observacoes,
            "price_was_carried": observacoes.eq(0),
            "quote_age_days": np.where(observacoes.eq(0), 7, 0),
            "log_price_t": np.log(precos),
            "log_return_t": np.log(precos).diff(),
        }
    )

    quadro, features = construir_quadro_ouro(semanal)
    origem_antes_da_lacuna = quadro.loc[quadro["DATE"].eq(datas[55])].iloc[0]

    assert origem_antes_da_lacuna["target_has_new_quote"] == 0
    assert "target_has_new_quote" not in features
    assert datas[55] not in selecionar_alvos_observados(quadro)["DATE"].tolist()
