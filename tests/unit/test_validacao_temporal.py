import numpy as np
import pandas as pd
import pytest

from series_temporais.validation.temporal_split import purged_time_series_splits


def test_dobras_sao_expansivas_ordenadas_e_purgadas():
    origens = pd.Series(pd.date_range("2025-01-01", periods=40, freq="D"))
    alvos = origens + pd.Timedelta(days=1)
    splits = purged_time_series_splits(origens, alvos, n_splits=3)

    assert len(splits) == 3
    tamanhos_treino = []
    for treino, validacao in splits:
        tamanhos_treino.append(len(treino))
        assert np.all(np.diff(treino) == 1)
        assert np.all(np.diff(validacao) == 1)
        assert alvos.iloc[treino].max() < origens.iloc[validacao].min()
        assert treino.max() < validacao.min()
    assert tamanhos_treino == sorted(tamanhos_treino)


def test_dobras_rejeitam_alvo_na_origem_ou_no_passado():
    origens = pd.Series(pd.date_range("2025-01-01", periods=12, freq="D"))
    with pytest.raises(ValueError, match="posterior"):
        purged_time_series_splits(origens, origens, n_splits=3)
