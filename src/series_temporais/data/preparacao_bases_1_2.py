"""Preparação reproduzível das Bases 1 (Bitcoin) e 2 (tráfego I-94)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _moda_deterministica(values: pd.Series) -> object:
    """Retorna a moda, desempatada alfabeticamente."""
    values = values.dropna()
    if values.empty:
        return pd.NA
    counts = values.astype(str).value_counts()
    return sorted(counts[counts == counts.max()].index)[0]


def dividir_cronologicamente(
    dataframe: pd.DataFrame, coluna_tempo: str, proporcao_treino: float
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide uma tabela já ordenada sem embaralhamento."""
    if not 0 < proporcao_treino < 1:
        raise ValueError("A proporção de treino deve estar entre 0 e 1.")
    ordered = dataframe.sort_values(coluna_tempo).reset_index(drop=True)
    split = int(len(ordered) * proporcao_treino)
    train, test = ordered.iloc[:split].copy(), ordered.iloc[split:].copy()
    if train.empty or test.empty or train[coluna_tempo].max() >= test[coluna_tempo].min():
        raise ValueError("A divisão cronológica não gerou treino e teste válidos.")
    return train, test


def preparar_base1(caminho_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Audita e separa a série diária de Bitcoin em 70%/30%."""
    raw = pd.read_csv(caminho_csv)
    clean = raw.copy()
    clean["Date"] = pd.to_datetime(clean["Date"], errors="raise")
    clean = clean.sort_values("Date").reset_index(drop=True)
    if clean["Date"].duplicated().any() or clean.duplicated().any():
        raise ValueError("A Base 1 possui duplicidades inesperadas.")
    if clean["Date"].isna().any() or clean["Close"].isna().any():
        raise ValueError("A Base 1 possui data ou alvo ausente.")
    expected = pd.date_range(clean["Date"].min(), clean["Date"].max(), freq="D")
    observed = pd.DatetimeIndex(clean["Date"])
    if not expected.equals(observed):
        raise ValueError("A Base 1 não possui grade diária completa.")
    if not clean["Close"].equals(clean["Adj Close"]):
        raise ValueError("`Adj Close` deixou de ser idêntica a `Close`; revise a documentação.")
    train, test = dividir_cronologicamente(clean, "Date", 0.70)
    audit = {"linhas_origem": len(raw), "linhas_preparadas": len(clean), "datas_duplicadas": int(clean["Date"].duplicated().sum()), "lacunas_diarias": int(len(expected.difference(observed))), "nulos_alvo": int(clean["Close"].isna().sum()), "proporcao_treino": len(train) / len(clean)}
    return clean, train, test, audit


def preparar_base2(caminho_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Regulariza Base 2 sem imputar alvo e separa-a em 80%/20%."""
    raw = pd.read_csv(caminho_csv, keep_default_na=False)
    raw["date_time"] = pd.to_datetime(raw["date_time"], errors="raise")
    raw = raw.sort_values("date_time").reset_index(drop=True)
    numeric_cols = ["temp", "rain_1h", "snow_1h", "clouds_all", "traffic_volume"]
    categorical_cols = ["holiday", "weather_main", "weather_description"]
    grouped_numeric = raw.groupby("date_time", as_index=False)[numeric_cols].mean()
    grouped_categorical = raw.groupby("date_time", as_index=False)[categorical_cols].agg(_moda_deterministica)
    consolidated = grouped_numeric.merge(grouped_categorical, on="date_time", how="inner")
    consolidated = consolidated[["holiday", "temp", "rain_1h", "snow_1h", "clouds_all", "weather_main", "weather_description", "date_time", "traffic_volume"]].sort_values("date_time").reset_index(drop=True)
    expected = pd.date_range(consolidated["date_time"].min(), consolidated["date_time"].max(), freq="h")
    clean = consolidated.set_index("date_time").reindex(expected).rename_axis("date_time").reset_index()
    clean = clean[["holiday", "temp", "rain_1h", "snow_1h", "clouds_all", "weather_main", "weather_description", "date_time", "traffic_volume"]]
    model_rows = clean.dropna(subset=["traffic_volume"]).copy()
    train, test = dividir_cronologicamente(model_rows, "date_time", 0.80)
    audit = {"linhas_origem": len(raw), "timestamps_unicos": len(consolidated), "timestamps_repetidos_origem": int(raw["date_time"].duplicated().sum()), "linhas_grade_horaria": len(clean), "lacunas_horarias": int(clean["traffic_volume"].isna().sum()), "nulos_alvo_apos_preparacao": int(clean["traffic_volume"].isna().sum()), "proporcao_treino": len(train) / len(model_rows)}
    return clean, train, test, audit


def salvar_preparacao(pasta: Path, prefixo: str, clean: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> None:
    """Salva artefatos derivados de forma padronizada na pasta da base."""
    pasta.mkdir(parents=True, exist_ok=True)
    clean.to_csv(pasta / f"{prefixo}_limpa_preparada.csv", index=False)
    train.to_csv(pasta / f"{prefixo}_treino_preparada.csv", index=False)
    test.to_csv(pasta / f"{prefixo}_teste_preparada.csv", index=False)
