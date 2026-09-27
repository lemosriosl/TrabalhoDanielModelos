"""Seleção e avaliação final eficiente do SARIMAX da Base 2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import statsmodels

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from series_temporais.models.sarimax import SarimaxConfig, diagnostico_ljung_box
from series_temporais.models.sarimax_eficiente import avaliar_incremental
from executar_sarimax_bases_1_2 import _escrever_acf


def main() -> None:
    pasta = ROOT / "trabalho" / "bases" / "grupo2" / "modelos"
    dados = pd.read_csv(ROOT / "trabalho" / "bases" / "grupo2" / "base2_limpa_preparada.csv")
    serie = dados.set_index(pd.to_datetime(dados["date_time"]))["traffic_volume"].asfreq("h")
    inicio_teste = pd.Timestamp("2017-10-26 18:00:00")
    treino = serie.loc[serie.index < inicio_teste]
    inicio_validacao = treino.dropna().index[int(treino.notna().sum() * 0.80)]
    candidatas = [
        SarimaxConfig(order=(1, 0, 1), seasonal_order=(1, 0, 1, 24)),
        SarimaxConfig(order=(2, 0, 1), seasonal_order=(1, 0, 1, 24)),
        SarimaxConfig(order=(1, 1, 1), seasonal_order=(1, 0, 1, 24)),
    ]
    linhas = []
    for numero, candidata in enumerate(candidatas, start=1):
        previsoes_validacao, registro_validacao = avaliar_incremental(treino, inicio_validacao, candidata)
        linhas.append({
            "candidato": numero, "ordem": registro_validacao["ordem"],
            "ordem_sazonal": registro_validacao["ordem_sazonal"],
            "MAE_validacao": registro_validacao["MAE"], "RMSE_validacao": registro_validacao["RMSE"],
            "observacoes_avaliadas": registro_validacao["observacoes_avaliadas"],
            "segundos_total": registro_validacao["segundos_ajuste_inicial"] + registro_validacao["segundos_walk_forward"],
        })
    selecao = pd.DataFrame(linhas).sort_values(["MAE_validacao", "candidato"]).reset_index(drop=True)
    escolhida = candidatas[int(selecao.loc[0, "candidato"]) - 1]
    previsoes, registro = avaliar_incremental(serie, inicio_teste, escolhida)
    residuos = previsoes[["origin_time", "target_time", "residuo_sarimax", "erro_absoluto_sarimax", "erro_quadratico_sarimax"]]
    ljung = diagnostico_ljung_box(previsoes, [24, 168]).reset_index(names="lag")
    pasta.mkdir(parents=True, exist_ok=True)
    selecao.to_csv(pasta / "sarimax_base2_selecao_ordens.csv", index=False)
    previsoes.to_csv(pasta / "sarimax_base2_previsoes.csv", index=False)
    residuos.to_csv(pasta / "sarimax_base2_residuos.csv", index=False)
    ljung.to_csv(pasta / "sarimax_base2_ljung_box.csv", index=False)
    _escrever_acf(previsoes.residuo_sarimax, pasta, "base2", 168)
    registro.update({
        "base": "base2", "inicio_teste": str(inicio_teste), "inicio_validacao_interna": str(inicio_validacao),
        "janela": "expansiva", "horizonte": 1, "metrica_selecao": "MAE na cauda cronológica do treino",
        "variaveis_exogenas": [],
        "justificativa_sem_exogenas": "covariáveis observadas não são conhecidas no instante da previsão; nenhuma fonte de previsão externa foi fornecida",
        "nota_serie": "Grade horária; lacunas reais do alvo foram mantidas e excluídas da avaliação.",
        "versao_pandas": pd.__version__, "versao_statsmodels": statsmodels.__version__,
        "atualizacao_estado": "statsmodels results.extend após cada previsão; sem reestimar parâmetros no teste",
    })
    with (pasta / "sarimax_base2_registro.json").open("w", encoding="utf-8") as arquivo:
        json.dump(registro, arquivo, ensure_ascii=False, indent=2)
    print("SARIMAX Base 2 concluído", flush=True)


if __name__ == "__main__":
    main()
