"""Auditoria reproduzível das cinco bases do trabalho.

As funções deste módulo somente leem as bases de origem. Nenhum arquivo de
origem é alterado e as regras de limpeza ficam separadas das decisões ainda
pendentes do grupo.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _base_record(base: str, path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    return {
        "base": base,
        "arquivo": str(path),
        "sha256": sha256(path),
        "linhas": int(len(frame)),
        "colunas": int(frame.shape[1]),
        "nulos_por_coluna": {str(k): int(v) for k, v in frame.isna().sum().items()},
        "colunas_observadas": [str(c) for c in frame.columns],
    }


def auditar_base1(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    result = _base_record("base_01", path, frame)
    date = pd.to_datetime(frame["Date"], errors="coerce")
    ordered = date.sort_values()
    expected = pd.date_range(date.min(), date.max(), freq="D")
    result.update(
        inicio=str(date.min().date()),
        fim=str(date.max().date()),
        datas_invalidas=int(date.isna().sum()),
        datas_duplicadas=int(date.duplicated().sum()),
        linhas_duplicadas=int(frame.duplicated().sum()),
        ordenada_original=bool(date.is_monotonic_increasing),
        lacunas_diarias=int(len(expected.difference(pd.DatetimeIndex(ordered)))),
        nulos_alvo=int(frame["Close"].isna().sum()),
        valores_nao_numericos={
            c: int(pd.to_numeric(frame[c], errors="coerce").isna().sum())
            for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        },
        adj_close_igual_close=bool(frame["Close"].eq(frame["Adj Close"]).all()),
        valores_nao_positivos={
            c: int((pd.to_numeric(frame[c], errors="coerce") <= 0).sum())
            for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        },
    )
    return result


def auditar_base2(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path, keep_default_na=False)
    result = _base_record("base_02", path, frame)
    date = pd.to_datetime(frame["date_time"], errors="coerce")
    sorted_date = date.sort_values()
    expected = pd.date_range(date.min(), date.max(), freq="h")
    numeric = ["temp", "rain_1h", "snow_1h", "clouds_all", "traffic_volume"]
    duplicate_mask = date.duplicated(keep=False)
    result.update(
        inicio=str(date.min()),
        fim=str(date.max()),
        datas_invalidas=int(date.isna().sum()),
        timestamps_duplicados=int(date.duplicated().sum()),
        grupos_com_duplicidade=int(date[duplicate_mask].nunique()),
        linhas_duplicadas=int(frame.duplicated().sum()),
        ordenada_original=bool(date.is_monotonic_increasing),
        lacunas_horarias=int(len(expected.difference(pd.DatetimeIndex(sorted_date.unique())))),
        nulos_alvo=int(pd.to_numeric(frame["traffic_volume"], errors="coerce").isna().sum()),
        valores_nao_numericos={
            c: int(pd.to_numeric(frame[c], errors="coerce").isna().sum()) for c in numeric
        },
        alvo_min=float(pd.to_numeric(frame["traffic_volume"], errors="coerce").min()),
        alvo_max=float(pd.to_numeric(frame["traffic_volume"], errors="coerce").max()),
        categorias_holiday=sorted(frame["holiday"].astype(str).unique().tolist()),
        possiveis_conflitos_nas_duplicidades={
            c: int(frame.loc[duplicate_mask].groupby("date_time")[c].nunique().gt(1).sum())
            for c in ["traffic_volume", "holiday", "weather_main", "weather_description"]
        },
    )
    return result


def auditar_base3(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    result = _base_record("base_03", path, frame)
    date = pd.to_datetime(frame[["year", "month", "day", "hour"]], errors="coerce")
    expected = pd.date_range(date.min(), date.max(), freq="h")
    numeric = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    result.update(
        inicio=str(date.min()),
        fim=str(date.max()),
        datas_invalidas=int(date.isna().sum()),
        timestamps_duplicados=int(date.duplicated().sum()),
        linhas_duplicadas=int(frame.duplicated().sum()),
        ordenada_original=bool(date.is_monotonic_increasing),
        lacunas_horarias=int(len(expected.difference(pd.DatetimeIndex(date.unique())))),
        no_unicos=int(frame["No"].nunique()),
        no_sequencial=bool(frame["No"].equals(pd.Series(range(1, len(frame) + 1), name="No"))),
        nulos_numericos={c: int(pd.to_numeric(frame[c], errors="coerce").isna().sum()) for c in numeric},
        nulos_categoricos={"wd": int(frame["wd"].isna().sum()), "station": int(frame["station"].isna().sum())},
        alvo_nao_negativo=bool((pd.to_numeric(frame["PM2.5"], errors="coerce").dropna() >= 0).all()),
        estacoes=sorted(frame["station"].dropna().astype(str).unique().tolist()),
    )
    return result


def auditar_base4(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    result = _base_record("base_04", path, frame)
    date = pd.to_datetime(frame["Date Time"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    sorted_date = date.sort_values()
    expected = pd.date_range(date.min(), date.max(), freq="10min")
    numeric = [c for c in frame.columns if c != "Date Time"]
    invalid = frame[numeric].eq(-9999).sum()
    result.update(
        inicio=str(date.min()),
        fim=str(date.max()),
        datas_invalidas=int(date.isna().sum()),
        timestamps_duplicados=int(date.duplicated().sum()),
        linhas_duplicadas=int(frame.duplicated().sum()),
        ordenada_original=bool(date.is_monotonic_increasing),
        linhas_grade_10min=int(len(expected)),
        timestamps_ausentes_na_grade=int(len(expected.difference(pd.DatetimeIndex(sorted_date.unique())))),
        codigos_menos_9999={str(k): int(v) for k, v in invalid[invalid > 0].items()},
        total_codigos_menos_9999=int(invalid.sum()),
        nulos_alvo=int(frame["T (degC)"].isna().sum()),
    )
    return result


def auditar_base5(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    if len(frame.columns) == 1:
        frame = pd.read_csv(path, sep=";")
    result = _base_record("base_05", path, frame)
    date = pd.to_datetime(frame["DATE"], errors="coerce")
    if "GOLD_PRICE" in frame:
        value = pd.to_numeric(frame["GOLD_PRICE"], errors="coerce")
        target = pd.to_numeric(frame["TARGET"], errors="coerce")
        lag_1 = pd.to_numeric(frame["GOLD_LAG_1"], errors="coerce")
        result.update(
            esquema="ouro_com_taxas",
            nulos_preco=int(value.isna().sum()),
            colunas_primitivas=["DATE", "GOLD_PRICE", "TREASURY_10Y", "FED_FUNDS_RATE"],
            target_entregue_igual_proxima_linha_fracao=float(
                np.isclose(target.iloc[:-1], value.shift(-1).iloc[:-1], equal_nan=False).mean()
            ),
            lag_1_entregue_igual_shift_fracao=float(
                np.isclose(lag_1.iloc[1:], value.shift(1).iloc[1:], equal_nan=False).mean()
            ),
        )
    else:
        value = pd.to_numeric(frame["VALUE"], errors="coerce")
        expected_target = value.shift(-1).gt(value).fillna(False).astype(int)
        result.update(
            esquema="valor_com_alvo_binario",
            nulos_value=int(value.isna().sum()),
            dominios_invalidos={
                c: sorted(set(frame[c].dropna().unique()) - {0, 1})
                for c in ["IS_HOLIDAY", "TARGET_UP"]
            },
            is_holiday_counts={
                str(k): int(v)
                for k, v in frame["IS_HOLIDAY"].value_counts(dropna=False).items()
            },
            target_up_counts={
                str(k): int(v)
                for k, v in frame["TARGET_UP"].value_counts(dropna=False).items()
            },
            target_up_reproduz_proxima_linha=bool(
                frame["TARGET_UP"].eq(expected_target).all()
            ),
            target_up_com_par_preco_valido=int(
                (
                    frame["TARGET_UP"].eq(1)
                    & value.notna()
                    & value.shift(-1).notna()
                ).sum()
            ),
        )
    result.update(
        inicio=str(date.min().date()),
        fim=str(date.max().date()),
        datas_invalidas=int(date.isna().sum()),
        datas_duplicadas=int(date.duplicated().sum()),
        linhas_duplicadas=int(frame.duplicated().sum()),
        ordenada_original=bool(date.is_monotonic_increasing),
        valores_nao_positivos=int((value.dropna() <= 0).sum()),
    )
    return result


def auditar_todas(paths: dict[str, Path]) -> dict[str, dict[str, Any]]:
    """Executa a auditoria sem tocar nos arquivos de origem."""
    functions = {
        "base_01": auditar_base1,
        "base_02": auditar_base2,
        "base_03": auditar_base3,
        "base_04": auditar_base4,
        "base_05": auditar_base5,
    }
    return {key: functions[key](paths[key]) for key in functions}
