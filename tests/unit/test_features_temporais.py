import numpy as np
import pandas as pd
import pytest

from series_temporais.features.regras_bases import (
    BASE_1,
    BASE_2,
    catalogo_base5,
    preparar_entrada_base2,
    validar_proibidas,
)
from series_temporais.features.temporal import (
    CovariavelTemporal,
    Disponibilidade,
    build_one_step_frame,
    catalogo_features,
    choque_futuro_nao_altera_features,
    chronological_train_test,
    longest_observed_run,
)


def _dados_regulares(n=20):
    return pd.DataFrame(
        {
            "data": pd.date_range("2025-01-01", periods=n, freq="h"),
            "alvo": np.arange(n, dtype=float),
            "externa": np.arange(100, 100 + n, dtype=float),
            "feriado": [1 if i % 5 == 0 else 0 for i in range(n)],
        }
    )


def test_features_usam_apenas_origem_e_passado():
    dados = _dados_regulares()
    quadro, features = build_one_step_frame(
        dados,
        time_col="data",
        target_col="alvo",
        external_cols=["externa"],
        expected_step="1h",
        lags=[1, 2],
        windows=[2],
    )

    linha = quadro.loc[quadro.origin_time.eq(dados.loc[8, "data"])].iloc[0]
    assert linha.level_t == 8
    assert linha.y_true == 9
    assert linha.externa_t == 108
    assert linha.target_lag_1 == 7
    assert linha.target_lag_2 == 6
    assert linha.target_mean_2 == pytest.approx(6.5)
    assert {"y_true", "target_delta", "target_time"}.isdisjoint(features)


def test_conhecido_antecipadamente_usa_valor_da_data_alvo():
    dados = _dados_regulares()
    quadro, features = build_one_step_frame(
        dados,
        time_col="data",
        target_col="alvo",
        external_cols=["feriado"],
        expected_step="1h",
        availability={
            "feriado": CovariavelTemporal(Disponibilidade.CONHECIDO_ANTECIPADAMENTE)
        },
    )
    assert "feriado_alvo" in features
    linha = quadro.loc[quadro.origin_time.eq(dados.loc[8, "data"])].iloc[0]
    assert linha.feriado_alvo == dados.loc[9, "feriado"]


def test_alterar_futuro_nao_altera_features_de_origens_anteriores():
    dados = _dados_regulares()
    original, features = build_one_step_frame(
        dados,
        time_col="data",
        target_col="alvo",
        external_cols=["externa"],
        expected_step="1h",
        lags=[1],
        windows=[2],
    )
    alterado = dados.copy()
    alterado.loc[10:, ["alvo", "externa"]] = 999_999
    reconstruido, _ = build_one_step_frame(
        alterado,
        time_col="data",
        target_col="alvo",
        external_cols=["externa"],
        expected_step="1h",
        lags=[1],
        windows=[2],
    )

    limite = dados.loc[9, "data"]
    cols = ["origin_time", *features]
    pd.testing.assert_frame_equal(
        original.loc[original.origin_time.le(limite), cols].reset_index(drop=True),
        reconstruido.loc[reconstruido.origin_time.le(limite), cols].reset_index(drop=True),
    )


def test_disponibilidade_atrasada_e_proibida_sao_aplicadas():
    dados = _dados_regulares()
    quadro, features = build_one_step_frame(
        dados,
        time_col="data",
        target_col="alvo",
        external_cols=["externa"],
        expected_step="1h",
        availability={
            "externa": CovariavelTemporal(Disponibilidade.COM_ATRASO, atraso=2)
        },
    )
    assert "externa_lag_2" in features
    primeira = quadro.iloc[0]
    indice_origem = dados.index[dados.data.eq(primeira.origin_time)][0]
    assert primeira.externa_lag_2 == dados.loc[indice_origem - 2, "externa"]

    with pytest.raises(ValueError, match="proibida"):
        build_one_step_frame(
            dados,
            time_col="data",
            target_col="alvo",
            external_cols=["externa"],
            expected_step="1h",
            availability={
                "externa": CovariavelTemporal(Disponibilidade.PROIBIDA)
            },
        )


def test_grade_irregular_duplicada_ou_desordenada_e_rejeitada():
    dados = _dados_regulares()
    for invalido in (
        dados.drop(index=5).reset_index(drop=True),
        pd.concat([dados, dados.iloc[[5]]], ignore_index=True).sort_values("data"),
        dados.sort_values("data", ascending=False),
    ):
        with pytest.raises(ValueError):
            build_one_step_frame(
                invalido,
                time_col="data",
                target_col="alvo",
                expected_step="1h",
            )


def test_corte_cronologico_purga_alvo_na_fronteira():
    quadro, _ = build_one_step_frame(
        _dados_regulares(),
        time_col="data",
        target_col="alvo",
        expected_step="1h",
    )
    treino, teste = chronological_train_test(quadro, 0.7)
    assert treino.target_time.max() < teste.origin_time.min()
    assert treino.origin_time.max() < teste.origin_time.min()


def test_catalogo_nao_deixa_feature_sem_classificacao():
    _, features = build_one_step_frame(
        _dados_regulares(),
        time_col="data",
        target_col="alvo",
        external_cols=["externa", "feriado"],
        expected_step="1h",
        lags=[1],
        windows=[2],
        availability={
            "externa": CovariavelTemporal(),
            "feriado": CovariavelTemporal(Disponibilidade.CONHECIDO_ANTECIPADAMENTE),
        },
    )
    catalogo = catalogo_features(
        features,
        status_por_feature={"externa_t": "em_validacao", "feriado_alvo": "aprovado"},
    )
    assert catalogo.feature.tolist() == features
    assert not catalogo.grupo.eq("revisar").any()
    assert catalogo.set_index("feature").loc["externa_t", "disponibilidade"] == "conhecido em t"
    assert catalogo.set_index("feature").loc["target_mean_2", "disponibilidade"] == "termina em t-1"
    assert catalogo.set_index("feature").loc["feriado_alvo", "grupo"] == "conhecido_antecipadamente"
    assert catalogo.set_index("feature").loc["feriado_alvo", "status"] == "aprovado"


def test_choque_futuro_preserva_features_anteriores():
    dados = _dados_regulares()
    resultado = choque_futuro_nao_altera_features(
        dados,
        time_col="data",
        indice_inicial_do_choque=12,
        colunas=["alvo", "externa"],
        target_col="alvo",
        external_cols=["externa"],
        expected_step="1h",
        lags=[1, 2],
        windows=[3],
    )
    assert resultado["iguais"] is True
    assert resultado["diferenca_maxima"] == 0
    assert resultado["origens_comparadas"] > 0


def test_maior_trecho_observado_nao_interpola():
    serie = pd.Series([1.0, 2.0, np.nan, 3.0, 4.0, 5.0, np.nan])
    trecho = longest_observed_run(serie, minimum_length=3)
    assert trecho.tolist() == [3.0, 4.0, 5.0]
    with pytest.raises(ValueError, match="necessárias 4"):
        longest_observed_run(serie, minimum_length=4)


def test_regras_das_bases_1_e_2_sao_consistentes():
    validar_proibidas(BASE_1.external_cols(), BASE_1)
    validar_proibidas(BASE_2.external_cols(), BASE_2)
    assert "Adj Close" in BASE_1.proibidas
    assert "is_holiday" in BASE_2.external_cols()
    assert BASE_2.availability()["is_holiday"].disponibilidade == (
        Disponibilidade.CONHECIDO_ANTECIPADAMENTE
    )
    with pytest.raises(ValueError, match="proibidas"):
        validar_proibidas(["Adj Close", "Open"], BASE_1)


def test_preparar_base2_e_conhecido_antecipadamente():
    bruto = pd.DataFrame(
        {
            "date_time": pd.date_range("2020-01-01", periods=10, freq="h"),
            "traffic_volume": np.arange(10, dtype=float),
            "temp": np.arange(10, dtype=float),
            "rain_1h": 0.0,
            "snow_1h": 0.0,
            "clouds_all": 10.0,
            "holiday": [None, "X", None, None, None, None, None, None, None, None],
        }
    )
    dados = preparar_entrada_base2(bruto)
    assert dados["is_holiday"].tolist() == [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    quadro, features = build_one_step_frame(
        dados,
        time_col=BASE_2.time_col,
        target_col=BASE_2.target_col,
        external_cols=BASE_2.external_cols(),
        expected_step=BASE_2.expected_step,
        lags=[1],
        windows=[2],
        availability=BASE_2.availability(),
    )
    assert "is_holiday_alvo" in features
    # Origem no índice 2: histórico suficiente; alvo = índice 3 (sem feriado).
    linha = quadro.loc[quadro.origin_time.eq(dados.loc[2, "date_time"])].iloc[0]
    assert linha.is_holiday_alvo == dados.loc[3, "is_holiday"] == 0
    # A origem imediatamente anterior ao feriado (índice 0) aponta para o alvo 1.
    # Com window=2 ela é removida; a regra shift(-1) é validada no teste unitário
    # test_conhecido_antecipadamente_usa_valor_da_data_alvo.
    assert dados.loc[1, "is_holiday"] == 1


def test_catalogo_base5_marca_taxas_como_provisorias():
    catalogo = catalogo_base5(
        ["price_t", "treasury_10y_t", "fed_funds_rate_t", "target_week_sin"]
    )
    idx = catalogo.set_index("feature")
    assert idx.loc["price_t", "status"] == "aprovado"
    assert idx.loc["treasury_10y_t", "status"] == "provisorio"
    assert idx.loc["fed_funds_rate_t", "status"] == "provisorio"
