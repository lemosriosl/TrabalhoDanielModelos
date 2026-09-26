from pathlib import Path

import pandas as pd

from series_temporais.data.preparacao_base5 import (
    construir_quadro_ouro,
    preparar_ouro_semanal,
)

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "trabalho/bases/grupo5/grupo5.csv"


def test_preparacao_semanal_da_base5_e_causal():
    bruto = pd.read_csv(CSV)
    semanal = preparar_ouro_semanal(bruto)

    assert len(semanal) == 2398
    assert semanal.DATE.diff().dropna().dt.days.eq(7).all()
    assert semanal.price_was_carried.sum() == 254
    assert semanal.quote_age_days.max() == 17
    assert semanal[["price_t", "treasury_10y_t", "fed_funds_rate_t"]].notna().all().all()


def test_feature_engineering_da_base5_exclui_derivacoes_entregues_e_futuro():
    bruto = pd.read_csv(CSV)
    semanal = preparar_ouro_semanal(bruto)
    modelavel, features = construir_quadro_ouro(semanal)

    derivadas_origem = set(bruto.columns[4:])
    assert len(modelavel) == 2344
    assert len(features) == 49
    assert derivadas_origem.isdisjoint(features)
    assert {
        "target_date",
        "target_price_t_plus_1",
        "target_log_return_t_plus_1",
        "target_has_new_quote",
    }.isdisjoint(features)
    assert modelavel.target_date.gt(modelavel.DATE).all()
    esperado = semanal.set_index("DATE").source_observations.gt(0)
    observado = modelavel.set_index("target_date").target_has_new_quote.astype(bool)
    assert observado.eq(esperado.reindex(observado.index)).all()


def test_mudar_semana_futura_nao_altera_features_anteriores():
    bruto = pd.read_csv(CSV)
    semanal = preparar_ouro_semanal(bruto)
    original, features = construir_quadro_ouro(semanal)
    alterado = semanal.copy()
    corte = 1800
    alterado.loc[corte:, ["price_t", "log_price_t", "log_return_t"]] = 999_999
    reconstruido, _ = construir_quadro_ouro(alterado)
    limite = semanal.loc[corte - 1, "DATE"]

    pd.testing.assert_frame_equal(
        original.loc[original.DATE.le(limite), ["DATE", *features]].reset_index(drop=True),
        reconstruido.loc[
            reconstruido.DATE.le(limite), ["DATE", *features]
        ].reset_index(drop=True),
    )
