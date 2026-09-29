"""Preparação causal da série semanal de ouro da Base 5."""

from __future__ import annotations

import numpy as np
import pandas as pd


PRIMITIVAS = ["DATE", "GOLD_PRICE", "TREASURY_10Y", "FED_FUNDS_RATE"]


def preparar_ouro_semanal(
    dados: pd.DataFrame,
    regra_semanal: str = "W-FRI",
) -> pd.DataFrame:
    """Agrega a última observação semanal e carrega só o estado passado."""

    ausentes = sorted(set(PRIMITIVAS).difference(dados.columns))
    if ausentes:
        raise KeyError(f"Colunas primitivas ausentes: {ausentes}")

    diario = dados[PRIMITIVAS].copy()
    diario["DATE"] = pd.to_datetime(diario["DATE"], errors="raise")
    if diario["DATE"].isna().any() or diario["DATE"].duplicated().any():
        raise ValueError("DATE deve ser completa e única.")
    diario = diario.sort_values("DATE", kind="stable")
    for coluna in PRIMITIVAS[1:]:
        diario[coluna] = pd.to_numeric(diario[coluna], errors="coerce")
    if diario["GOLD_PRICE"].isna().any() or diario["GOLD_PRICE"].le(0).any():
        raise ValueError("GOLD_PRICE deve ser positivo e não ausente.")

    diario["semana"] = diario["DATE"].dt.to_period(regra_semanal).dt.end_time.dt.normalize()
    agrupado = diario.groupby("semana", sort=True)
    semanal = agrupado.agg(
        price_t=("GOLD_PRICE", "last"),
        treasury_10y_t=("TREASURY_10Y", "last"),
        fed_funds_rate_t=("FED_FUNDS_RATE", "last"),
        source_observations=("DATE", "size"),
        last_quote_date=("DATE", "max"),
    )
    grade = pd.date_range(semanal.index.min(), semanal.index.max(), freq=regra_semanal)
    semanal = semanal.reindex(grade)
    semanal.index.name = "DATE"
    semanal["source_observations"] = semanal["source_observations"].fillna(0).astype(int)
    semanal["price_was_carried"] = semanal["source_observations"].eq(0)

    # ffill é causal: em cada semana só propaga o último estado já observado.
    estado = ["price_t", "treasury_10y_t", "fed_funds_rate_t", "last_quote_date"]
    semanal[estado] = semanal[estado].ffill()
    if semanal[estado].isna().any().any():
        raise ValueError("A primeira semana não possui estado conhecido para propagação.")
    semanal["quote_age_days"] = (
        semanal.index.to_series().sub(semanal["last_quote_date"]).dt.days.to_numpy()
    )
    semanal["log_price_t"] = np.log(semanal["price_t"])
    semanal["log_return_t"] = semanal["log_price_t"].diff()
    return semanal.reset_index()


def construir_quadro_ouro(
    semanal: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Cria as 49 features semanais já adotadas pela Base 5."""

    requeridas = {
        "DATE",
        "price_t",
        "treasury_10y_t",
        "fed_funds_rate_t",
        "source_observations",
        "price_was_carried",
        "quote_age_days",
        "log_price_t",
        "log_return_t",
    }
    ausentes = sorted(requeridas.difference(semanal.columns))
    if ausentes:
        raise KeyError(f"Colunas semanais ausentes: {ausentes}")
    quadro = semanal.copy()
    quadro["DATE"] = pd.to_datetime(quadro["DATE"], errors="raise")
    if not quadro["DATE"].is_monotonic_increasing:
        raise ValueError("A série semanal deve estar em ordem crescente.")
    if not quadro["DATE"].diff().dropna().eq(pd.Timedelta(days=7)).all():
        raise ValueError("A série semanal deve possuir grade regular de sete dias.")

    quadro["target_date"] = quadro["DATE"].shift(-1)
    quadro["target_price_t_plus_1"] = quadro["price_t"].shift(-1)
    quadro["target_log_return_t_plus_1"] = quadro["log_return_t"].shift(-1)
    # Metadado exclusivo da avaliação; nunca é incluído em ``features``.
    quadro["target_has_new_quote"] = quadro["source_observations"].shift(-1).gt(0).astype(int)
    quadro["has_source_observation_t"] = quadro["source_observations"].gt(0).astype(int)
    quadro["price_was_carried"] = quadro["price_was_carried"].astype(int)

    features = [
        "price_t",
        "treasury_10y_t",
        "fed_funds_rate_t",
        "log_price_t",
        "log_return_t",
        "source_observations",
        "has_source_observation_t",
        "price_was_carried",
        "quote_age_days",
    ]
    quadro["treasury_change_t"] = quadro["treasury_10y_t"].diff()
    quadro["fed_funds_change_t"] = quadro["fed_funds_rate_t"].diff()
    features.extend(["treasury_change_t", "fed_funds_change_t"])

    for lag in (1, 4, 13, 26, 52):
        nome = f"price_lag_{lag}"
        quadro[nome] = quadro["price_t"].shift(lag)
        features.append(nome)
    for lag in (1, 2, 4, 8, 13, 26, 52):
        nome = f"return_lag_{lag}"
        quadro[nome] = quadro["log_return_t"].shift(lag)
        features.append(nome)

    for janela in (4, 13, 26, 52):
        preco = quadro["price_t"].shift(1).rolling(janela, min_periods=janela)
        retorno = quadro["log_return_t"].shift(1).rolling(janela, min_periods=janela)
        nomes = [
            f"price_mean_{janela}",
            f"price_std_{janela}",
            f"return_mean_{janela}",
            f"return_std_{janela}",
        ]
        quadro[nomes[0]] = preco.mean()
        quadro[nomes[1]] = preco.std(ddof=0)
        quadro[nomes[2]] = retorno.mean()
        quadro[nomes[3]] = retorno.std(ddof=0)
        features.extend(nomes)

    for coluna, prefixo in (
        ("treasury_10y_t", "treasury"),
        ("fed_funds_rate_t", "fed_funds"),
    ):
        for lag in (1, 4, 13):
            nome = f"{prefixo}_lag_{lag}"
            quadro[nome] = quadro[coluna].shift(lag)
            features.append(nome)

    semana_alvo = quadro["target_date"].dt.isocalendar().week.astype(float)
    mes_alvo = quadro["target_date"].dt.month.astype(float) - 1
    quadro["target_week_sin"] = np.sin(2 * np.pi * semana_alvo / 52)
    quadro["target_week_cos"] = np.cos(2 * np.pi * semana_alvo / 52)
    quadro["target_month_sin"] = np.sin(2 * np.pi * mes_alvo / 12)
    quadro["target_month_cos"] = np.cos(2 * np.pi * mes_alvo / 12)
    features.extend(
        ["target_week_sin", "target_week_cos", "target_month_sin", "target_month_cos"]
    )

    if len(features) != 49:
        raise AssertionError(f"Esperadas 49 features; obtidas {len(features)}.")
    obrigatorias = [
        "DATE",
        "target_date",
        "target_price_t_plus_1",
        "target_log_return_t_plus_1",
        *features,
    ]
    modelavel = quadro.dropna(subset=obrigatorias).reset_index(drop=True)
    return modelavel, features
