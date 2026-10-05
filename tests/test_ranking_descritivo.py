import pandas as pd

from series_temporais.reporting.ranking_descritivo import gerar_ranking_descritivo


def _row(base, model, mae, origins):
    return {
        "base_id": base,
        "modelo": model,
        "mae": mae,
        "origens": origins,
        "origens_horizonte_1": pd.NA,
        "mae_horizonte_1": pd.NA,
        "fonte": "teste",
        "tipo_fonte": "teste",
    }


def test_ranking_is_within_each_base_and_marks_winner():
    metrics = pd.DataFrame(
        [
            _row("base_01", "Holt-Winters", 3.0, 10),
            _row("base_01", "SARIMAX", 1.0, 10),
            _row("base_01", "Random Forest", 2.0, 9),
            _row("base_01", "XGBoost", 1.5, 9),
        ]
    )
    ranking = gerar_ranking_descritivo(metrics)
    assert ranking.iloc[0].modelo == "SARIMAX"
    assert ranking.iloc[0].posicao_descritiva_base == 1
    assert bool(ranking.iloc[0].vencedor_descritivo_base)
    assert not ranking.comparacao_homologada.any()
    assert "quantidades de origens diferentes" in ranking.iloc[0].motivo_nao_homologacao


def test_one_step_mae_has_priority_over_raw_mae():
    metrics = pd.DataFrame(
        [
            _row("base_02", "Holt-Winters", 2.0, 10),
            {
                **_row("base_02", "SARIMAX", 1.0, 10),
                "mae_horizonte_1": 3.0,
                "origens_horizonte_1": 9,
            },
        ]
    )
    ranking = gerar_ranking_descritivo(metrics)
    winner = ranking.loc[ranking.vencedor_descritivo_base].iloc[0]
    assert winner.modelo == "Holt-Winters"
    sarimax = ranking.loc[ranking.modelo.eq("SARIMAX")].iloc[0]
    assert sarimax.mae_usada == 3.0
    assert sarimax.origens_usadas == 9


def test_ranking_never_averages_mae_across_bases():
    metrics = pd.DataFrame(
        [_row(f"base_{base:02d}", model, mae, 10) for base in range(1, 6)
         for model, mae in (("Holt-Winters", 2.0), ("Random Forest", 3.0), ("XGBoost", 1.0))]
    )
    ranking = gerar_ranking_descritivo(metrics)
    assert "mae_media" not in ranking.columns
    assert ranking.loc[ranking.modelo.eq("XGBoost"), "vencedor_descritivo_geral"].all()
    assert ranking.loc[ranking.modelo.eq("XGBoost"), "vitorias_descritivas_modelo"].eq(5).all()
