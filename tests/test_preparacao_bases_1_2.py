from pathlib import Path

import pandas as pd

from series_temporais.data.preparacao_bases_1_2 import preparar_base1, preparar_base2


def test_base1_remove_adj_close_apenas_dos_derivados(tmp_path: Path):
    raw = pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Open": [10.0, 11.0, 12.0],
            "High": [12.0, 13.0, 14.0],
            "Low": [9.0, 10.0, 11.0],
            "Close": [11.0, 12.0, 13.0],
            "Adj Close": [11.0, 12.0, 13.0],
            "Volume": [100, 110, 120],
        }
    )
    path = tmp_path / "base1.csv"
    raw.to_csv(path, index=False)

    prepared, train, test, _ = preparar_base1(path)

    assert "Adj Close" in raw.columns
    assert "Adj Close" not in prepared.columns
    assert "Adj Close" not in train.columns
    assert "Adj Close" not in test.columns


def test_base2_consolida_repeticoes_e_nao_imputa_alvo(tmp_path: Path):
    raw = pd.DataFrame(
        {
            "holiday": ["None", "None", "None"],
            "temp": [280.0, 282.0, 284.0],
            "rain_1h": [0.0, 2.0, 0.0],
            "snow_1h": [0.0, 0.0, 0.0],
            "clouds_all": [10, 30, 20],
            "weather_main": ["Clear", "Clouds", "Clear"],
            "weather_description": ["clear sky", "few clouds", "clear sky"],
            "date_time": ["2024-01-01 00:00:00", "2024-01-01 00:00:00", "2024-01-01 02:00:00"],
            "traffic_volume": [100, 200, 300],
        }
    )
    path = tmp_path / "base2.csv"
    raw.to_csv(path, index=False)

    prepared, train, test, audit = preparar_base2(path)

    assert len(prepared) == 3
    assert prepared.loc[0, "traffic_volume"] == 150
    assert prepared.loc[0, "temp"] == 281
    assert pd.isna(prepared.loc[1, "traffic_volume"])
    assert audit["lacunas_horarias"] == 1
    assert len(train) + len(test) == 2