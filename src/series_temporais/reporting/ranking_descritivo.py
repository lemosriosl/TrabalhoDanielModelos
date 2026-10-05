"""Ranking descritivo dos modelos sem alegar comparabilidade homologada.

O ranking ordena MAE apenas dentro de cada base. Ele nunca calcula média bruta
de MAEs entre bases e mantém explícitas as diferenças de origens e cobertura.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


MODELOS_ESPERADOS = {"Holt-Winters", "SARIMAX", "Random Forest", "XGBoost"}
BASES_ESPERADAS = {f"base_{number:02d}" for number in range(1, 6)}


def _validar_metricas(metricas: pd.DataFrame) -> pd.DataFrame:
    required = {
        "base_id",
        "modelo",
        "mae",
        "origens",
        "origens_horizonte_1",
        "mae_horizonte_1",
        "fonte",
        "tipo_fonte",
    }
    missing = sorted(required.difference(metricas.columns))
    if missing:
        raise KeyError(f"Métricas sem colunas obrigatórias: {missing}")
    frame = metricas.copy()
    if frame.duplicated(["base_id", "modelo"]).any():
        raise ValueError("Cada combinação de base e modelo deve ser única.")
    frame["mae"] = pd.to_numeric(frame["mae"], errors="raise")
    frame["origens"] = pd.to_numeric(frame["origens"], errors="raise").astype(int)
    frame["mae_horizonte_1"] = pd.to_numeric(frame["mae_horizonte_1"], errors="coerce")
    frame["origens_horizonte_1"] = pd.to_numeric(
        frame["origens_horizonte_1"], errors="coerce"
    )
    if not np.isfinite(frame["mae"]).all() or frame["mae"].lt(0).any():
        raise ValueError("MAEs devem ser finitos e não negativos.")
    if frame["origens"].le(0).any():
        raise ValueError("A quantidade de origens deve ser positiva.")
    return frame


def gerar_ranking_descritivo(metricas: pd.DataFrame) -> pd.DataFrame:
    """Ordena modelos por base e sinaliza por que o ranking não é oficial."""

    frame = _validar_metricas(metricas)
    frame["mae_usada"] = frame["mae_horizonte_1"].fillna(frame["mae"])
    frame["origens_usadas"] = (
        frame["origens_horizonte_1"].fillna(frame["origens"]).astype(int)
    )
    frame["criterio_mae"] = np.where(
        frame["mae_horizonte_1"].notna(),
        "mae_horizonte_1",
        "mae_registrada",
    )

    ranked: list[pd.DataFrame] = []
    for base_id, group in frame.groupby("base_id", sort=True):
        group = group.copy()
        group["posicao_descritiva_base"] = (
            group["mae_usada"].rank(method="min", ascending=True).astype(int)
        )
        group["vencedor_descritivo_base"] = group["posicao_descritiva_base"].eq(1)
        presentes = set(group["modelo"])
        faltantes = sorted(MODELOS_ESPERADOS.difference(presentes))
        contagens = sorted(group["origens_usadas"].unique().tolist())
        motivos: list[str] = []
        if faltantes:
            motivos.append("modelos ausentes: " + ", ".join(faltantes))
        if len(contagens) > 1:
            motivos.append(
                "quantidades de origens diferentes: "
                + ", ".join(str(value) for value in contagens)
            )
        else:
            motivos.append(
                "contagens iguais não comprovam origens idênticas; faltam previsões "
                "por origem de RF/XGBoost para pareamento"
            )
        group["comparacao_homologada"] = False
        group["motivo_nao_homologacao"] = "; ".join(motivos)
        group["modelos_disponiveis_base"] = len(group)
        ranked.append(group)

    result = pd.concat(ranked, ignore_index=True)
    summary = (
        result.groupby("modelo", as_index=False)
        .agg(
            bases_avaliadas_modelo=("base_id", "nunique"),
            vitorias_descritivas_modelo=("vencedor_descritivo_base", "sum"),
            posicao_media_descritiva_modelo=("posicao_descritiva_base", "mean"),
        )
    )
    result = result.merge(summary, on="modelo", how="left", validate="many_to_one")
    result["elegivel_vencedor_geral"] = result["bases_avaliadas_modelo"].eq(
        len(BASES_ESPERADAS)
    )
    eligible = summary.loc[
        summary["bases_avaliadas_modelo"].eq(len(BASES_ESPERADAS))
    ].sort_values(
        ["vitorias_descritivas_modelo", "posicao_media_descritiva_modelo", "modelo"],
        ascending=[False, True, True],
        kind="stable",
    )
    winner = None if eligible.empty else str(eligible.iloc[0]["modelo"])
    result["vencedor_descritivo_geral"] = result["modelo"].eq(winner)
    result["criterio_vencedor_geral"] = (
        "mais vitórias por base; desempate por menor posição média; exige cobertura 5/5"
    )
    result["escopo"] = (
        "descritivo_nao_homologado; MAE comparada somente dentro de cada base"
    )

    columns = [
        "base_id",
        "modelo",
        "mae_usada",
        "criterio_mae",
        "origens_usadas",
        "posicao_descritiva_base",
        "vencedor_descritivo_base",
        "modelos_disponiveis_base",
        "comparacao_homologada",
        "motivo_nao_homologacao",
        "bases_avaliadas_modelo",
        "vitorias_descritivas_modelo",
        "posicao_media_descritiva_modelo",
        "elegivel_vencedor_geral",
        "vencedor_descritivo_geral",
        "criterio_vencedor_geral",
        "fonte",
        "tipo_fonte",
        "escopo",
    ]
    return result.loc[:, columns].sort_values(
        ["base_id", "posicao_descritiva_base", "modelo"], kind="stable"
    ).reset_index(drop=True)


def salvar_ranking_descritivo(root: Path, output: Path | None = None) -> Path:
    root = root.resolve()
    source = root / "results" / "metricas_individuais_auditadas.csv"
    target = output or root / "results" / "ranking_descritivo_modelos.csv"
    ranking = gerar_ranking_descritivo(pd.read_csv(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(target, index=False, encoding="utf-8")
    return target


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(salvar_ranking_descritivo(root, args.output))


if __name__ == "__main__":
    main()
