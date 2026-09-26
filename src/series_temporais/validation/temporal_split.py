"""Divisões temporais expansivas com purga na fronteira."""

from __future__ import annotations

import numpy as np
import pandas as pd


def purged_time_series_splits(
    origin_time,
    target_time,
    *,
    n_splits: int = 3,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Cria dobras expansivas e remove do treino alvos que alcançam a validação."""

    origens = pd.Series(pd.to_datetime(origin_time, errors="raise")).reset_index(drop=True)
    alvos = pd.Series(pd.to_datetime(target_time, errors="raise")).reset_index(drop=True)
    if len(origens) != len(alvos):
        raise ValueError("origin_time e target_time devem ter o mesmo tamanho.")
    if n_splits < 1:
        raise ValueError("n_splits deve ser positivo.")
    if len(origens) < n_splits + 1:
        raise ValueError("Há poucas amostras para o número de dobras solicitado.")
    if origens.isna().any() or alvos.isna().any():
        raise ValueError("Datas de origem e alvo não podem ser ausentes.")
    if not origens.is_monotonic_increasing:
        raise ValueError("As origens devem estar em ordem temporal crescente.")
    if not alvos.gt(origens).all():
        raise ValueError("Cada target_time deve ser posterior à sua origin_time.")

    tamanho_validacao = len(origens) // (n_splits + 1)
    if tamanho_validacao == 0:
        raise ValueError("As dobras de validação ficariam vazias.")

    splits: list[tuple[np.ndarray, np.ndarray]] = []
    for dobra in range(n_splits):
        inicio = len(origens) - (n_splits - dobra) * tamanho_validacao
        fim = inicio + tamanho_validacao
        if dobra == n_splits - 1:
            fim = len(origens)
        validacao = np.arange(inicio, fim, dtype=int)
        primeira_origem = origens.iloc[inicio]
        ajuste = np.flatnonzero((np.arange(len(origens)) < inicio) & (alvos < primeira_origem))
        if len(ajuste) == 0 or len(validacao) == 0:
            raise ValueError("A purga produziu uma dobra vazia.")
        splits.append((ajuste, validacao))
    return splits
