from pathlib import Path

from series_temporais.data.preparacao_bases_1_2 import preparar_base1, preparar_base2


ROOT = Path(__file__).resolve().parents[2]


def test_base1_regular_e_dividida_cronologicamente():
    clean, train, test, audit = preparar_base1(ROOT / "trabalho/bases/grupo1/grupo1.csv")

    assert len(clean) == 2836
    assert audit["lacunas_diarias"] == 0
    assert audit["datas_duplicadas"] == 0
    assert len(train) == 1985
    assert len(test) == 851
    assert train.Date.max() < test.Date.min()
    assert clean.Close.equals(clean["Adj Close"])


def test_base2_regularizada_sem_imputar_alvo_e_dividida_cronologicamente():
    clean, train, test, audit = preparar_base2(ROOT / "trabalho/bases/grupo2/grupo2.csv")

    assert audit["timestamps_repetidos_origem"] > 0
    assert audit["lacunas_horarias"] > 0
    assert clean.date_time.is_monotonic_increasing
    assert not clean.date_time.duplicated().any()
    assert clean.traffic_volume.isna().sum() == audit["nulos_alvo_apos_preparacao"]
    assert train.date_time.max() < test.date_time.min()
