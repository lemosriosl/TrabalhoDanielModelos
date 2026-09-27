"""Executa seleção interna e avaliação final SARIMAX das Bases 1 e 2.

Uso:
    PYTHONPATH=src py -3.11 scripts/executar_sarimax_bases_1_2.py

O protocolo está documentado no ADR-005. Os arquivos são sempre derivados
pelas rotinas abaixo; nenhum resultado é preenchido manualmente.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import acf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
matplotlib.use("Agg")

from series_temporais.models.sarimax import SarimaxConfig, diagnostico_ljung_box
from series_temporais.models.sarimax_experimento import selecionar_ordem, walk_forward_horario


def _escrever_acf(residuos: pd.Series, pasta: Path, base: str, max_lag: int) -> None:
    limite = min(max_lag, len(residuos) - 1)
    valores = acf(residuos, nlags=limite, fft=True)
    pd.DataFrame({"lag": np.arange(len(valores)), "acf_residuo_sarimax": valores}).to_csv(
        pasta / f"sarimax_{base}_acf.csv", index=False
    )
    figura, eixo = plt.subplots(figsize=(10, 4))
    eixo.stem(np.arange(1, len(valores)), valores[1:], basefmt=" ")
    eixo.axhline(0, color="black", linewidth=0.8)
    limite_ic = 1.96 / np.sqrt(len(residuos))
    eixo.axhline(limite_ic, color="#d55e00", linestyle="--", linewidth=1, label="IC 95% aproximado")
    eixo.axhline(-limite_ic, color="#d55e00", linestyle="--", linewidth=1)
    eixo.set(title=f"ACF dos resíduos — SARIMAX {base.upper()}", xlabel="Defasagem", ylabel="ACF")
    eixo.legend()
    figura.tight_layout()
    figura.savefig(pasta / f"sarimax_{base}_acf_residuos.png", dpi=160)
    plt.close(figura)


def _executar(
    *,
    base: str,
    serie: pd.Series,
    inicio_teste: pd.Timestamp,
    inicio_validacao: pd.Timestamp,
    candidatas: list[SarimaxConfig],
    lags_ljung: list[int],
    max_lag_acf: int,
    pasta: Path,
    nota_serie: str,
) -> None:
    treino = serie.loc[serie.index < inicio_teste]
    escolhida, selecao = selecionar_ordem(treino, inicio_validacao, candidatas)
    previsoes, registro = walk_forward_horario(serie, inicio_teste, escolhida)
    residuos = previsoes[
        ["origin_time", "target_time", "residuo_sarimax", "erro_absoluto_sarimax", "erro_quadratico_sarimax"]
    ]
    ljung_box = diagnostico_ljung_box(previsoes, lags_ljung).reset_index(names="lag")

    pasta.mkdir(parents=True, exist_ok=True)
    selecao.to_csv(pasta / f"sarimax_{base}_selecao_ordens.csv", index=False)
    previsoes.to_csv(pasta / f"sarimax_{base}_previsoes.csv", index=False)
    residuos.to_csv(pasta / f"sarimax_{base}_residuos.csv", index=False)
    ljung_box.to_csv(pasta / f"sarimax_{base}_ljung_box.csv", index=False)
    _escrever_acf(previsoes["residuo_sarimax"], pasta, base, max_lag_acf)

    registro.update(
        {
            "base": base,
            "inicio_teste": str(inicio_teste),
            "inicio_validacao_interna": str(inicio_validacao),
            "janela": "expansiva",
            "horizonte": 1,
            "metrica_selecao": "MAE na cauda cronológica do treino",
            "variaveis_exogenas": [],
            "justificativa_sem_exogenas": "covariáveis observadas não são conhecidas no instante da previsão; nenhuma fonte de previsão externa foi fornecida",
            "nota_serie": nota_serie,
            "versao_pandas": pd.__version__,
            "versao_statsmodels": statsmodels.__version__,
        }
    )
    with (pasta / f"sarimax_{base}_registro.json").open("w", encoding="utf-8") as destino:
        json.dump(registro, destino, ensure_ascii=False, indent=2)


def executar_base1() -> None:
    pasta = ROOT / "trabalho" / "bases" / "grupo1" / "modelos"
    dados = pd.read_csv(ROOT / "trabalho" / "bases" / "grupo1" / "base1_limpa_preparada.csv")
    serie = dados.set_index(pd.to_datetime(dados["Date"]))["Close"].asfreq("D")
    inicio_teste = pd.Timestamp("2022-06-09")
    treino = serie.loc[serie.index < inicio_teste]
    inicio_validacao = treino.index[int(len(treino) * 0.80)]
    candidatas = [
        SarimaxConfig(order=(1, 1, 1)),
        SarimaxConfig(order=(2, 1, 1)),
        SarimaxConfig(order=(1, 1, 2)),
    ]
    _executar(
        base="base1",
        serie=serie,
        inicio_teste=inicio_teste,
        inicio_validacao=inicio_validacao,
        candidatas=candidatas,
        lags_ljung=[7, 14, 30],
        max_lag_acf=40,
        pasta=pasta,
        nota_serie="Grade diária completa; alvo Close em USD/BTC.",
    )


def executar_base2() -> None:
    pasta = ROOT / "trabalho" / "bases" / "grupo2" / "modelos"
    dados = pd.read_csv(ROOT / "trabalho" / "bases" / "grupo2" / "base2_limpa_preparada.csv")
    serie = dados.set_index(pd.to_datetime(dados["date_time"]))["traffic_volume"].asfreq("h")
    inicio_teste = pd.Timestamp("2017-10-26 18:00:00")
    treino = serie.loc[serie.index < inicio_teste]
    posicao_validacao = int(treino.notna().sum() * 0.80)
    inicio_validacao = treino.dropna().index[posicao_validacao]
    candidatas = [
        SarimaxConfig(order=(1, 0, 1), seasonal_order=(1, 0, 1, 24)),
        SarimaxConfig(order=(2, 0, 1), seasonal_order=(1, 0, 1, 24)),
        SarimaxConfig(order=(1, 1, 1), seasonal_order=(1, 0, 1, 24)),
    ]
    _executar(
        base="base2",
        serie=serie,
        inicio_teste=inicio_teste,
        inicio_validacao=inicio_validacao,
        candidatas=candidatas,
        lags_ljung=[24, 168],
        max_lag_acf=168,
        pasta=pasta,
        nota_serie="Grade horária; 11.976 lacunas reais do alvo são mantidas como ausentes e não pontuadas.",
    )


if __name__ == "__main__":
    executar_base1()
    executar_base2()
