"""Engenharia de features temporais sem acesso a observações futuras."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


class Disponibilidade(str, Enum):
    """Momento em que uma covariável pode ser usada."""

    NA_ORIGEM = "na_origem"
    COM_ATRASO = "com_atraso"
    CONHECIDO_ANTECIPADAMENTE = "conhecido_antecipadamente"
    PROIBIDA = "proibida"


@dataclass(frozen=True)
class CovariavelTemporal:
    """Regra auditável de disponibilidade de uma covariável."""

    disponibilidade: Disponibilidade = Disponibilidade.NA_ORIGEM
    atraso: int = 0

    def __post_init__(self) -> None:
        if self.atraso < 0:
            raise ValueError("O atraso de uma covariável não pode ser negativo.")
        if self.disponibilidade == Disponibilidade.COM_ATRASO and self.atraso < 1:
            raise ValueError("Covariável publicada com atraso exige atraso >= 1.")
        if self.disponibilidade == Disponibilidade.NA_ORIGEM and self.atraso:
            raise ValueError("Use COM_ATRASO para configurar deslocamento positivo.")
        if (
            self.disponibilidade == Disponibilidade.CONHECIDO_ANTECIPADAMENTE
            and self.atraso
        ):
            raise ValueError(
                "Covariável conhecida antecipadamente não usa atraso; "
                "o valor é lido na data-alvo."
            )


def _inteiros_positivos(valores: Iterable[int], nome: str) -> tuple[int, ...]:
    resultado = tuple(dict.fromkeys(valores))
    if any(not isinstance(valor, (int, np.integer)) or valor <= 0 for valor in resultado):
        raise ValueError(f"{nome} deve conter somente inteiros positivos.")
    return resultado


def _validar_grade(
    dados: pd.DataFrame,
    *,
    time_col: str,
    expected_step: pd.Timedelta,
) -> pd.DataFrame:
    if expected_step <= pd.Timedelta(0):
        raise ValueError("expected_step deve ser positivo.")

    quadro = dados.copy()
    quadro[time_col] = pd.to_datetime(quadro[time_col], errors="raise")
    if quadro[time_col].isna().any():
        raise ValueError("A coluna temporal contém valores ausentes.")
    if quadro[time_col].duplicated().any():
        raise ValueError("A coluna temporal contém timestamps duplicados.")
    if not quadro[time_col].is_monotonic_increasing:
        raise ValueError("Os dados devem estar em ordem temporal crescente.")

    intervalos = quadro[time_col].diff().dropna()
    if not intervalos.eq(expected_step).all():
        raise ValueError(
            "A grade temporal deve ser regular antes da criação de features; "
            "preserve lacunas como linhas explícitas."
        )
    return quadro


def build_one_step_frame(
    dados: pd.DataFrame,
    *,
    time_col: str,
    target_col: str,
    external_cols: Sequence[str] = (),
    expected_step: pd.Timedelta | str,
    lags: Iterable[int] = (),
    windows: Iterable[int] = (),
    availability: Mapping[str, CovariavelTemporal] | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Constrói um quadro supervisionado para prever exatamente um passo.

    A linha representa uma origem ``t``. O alvo é ``y(t+1) - y(t)``; features
    externas são estados conhecidos em ``t`` ou estados anteriores conforme a
    regra de disponibilidade. Janelas do alvo terminam em ``t-1`` porque
    ``level_t`` já representa o valor conhecido em ``t``.
    """

    external_cols = tuple(dict.fromkeys(external_cols))
    required = {time_col, target_col, *external_cols}
    missing = sorted(required.difference(dados.columns))
    if missing:
        raise KeyError(f"Colunas ausentes: {missing}")
    if target_col in external_cols:
        raise ValueError("O alvo não pode ser declarado como covariável.")

    step = pd.Timedelta(expected_step)
    lags = _inteiros_positivos(lags, "lags")
    windows = _inteiros_positivos(windows, "windows")
    quadro = _validar_grade(dados, time_col=time_col, expected_step=step)
    regras = dict(availability or {})
    desconhecidas = sorted(set(regras).difference(external_cols))
    if desconhecidas:
        raise KeyError(f"Regras para covariáveis não declaradas: {desconhecidas}")

    saida = pd.DataFrame(index=quadro.index)
    saida["origin_time"] = quadro[time_col]
    saida["target_time"] = quadro[time_col].shift(-1)
    saida["level_t"] = quadro[target_col]
    saida["y_true"] = quadro[target_col].shift(-1)
    saida["target_delta"] = saida["y_true"] - saida["level_t"]
    features = ["level_t"]

    for coluna in external_cols:
        regra = regras.get(coluna, CovariavelTemporal())
        if regra.disponibilidade == Disponibilidade.PROIBIDA:
            raise ValueError(f"A covariável {coluna!r} foi classificada como proibida.")
        if regra.disponibilidade == Disponibilidade.CONHECIDO_ANTECIPADAMENTE:
            # Calendário/feriado: o valor da data-alvo já é conhecido na origem.
            nome = f"{coluna}_alvo"
            saida[nome] = quadro[coluna].shift(-1)
        else:
            deslocamento = regra.atraso
            nome = f"{coluna}_t" if deslocamento == 0 else f"{coluna}_lag_{deslocamento}"
            saida[nome] = quadro[coluna].shift(deslocamento)
        features.append(nome)

    for lag in lags:
        nome = f"target_lag_{lag}"
        saida[nome] = quadro[target_col].shift(lag)
        features.append(nome)

    historico_anterior = quadro[target_col].shift(1)
    for janela in windows:
        media = f"target_mean_{janela}"
        desvio = f"target_std_{janela}"
        rolling = historico_anterior.rolling(janela, min_periods=janela)
        saida[media] = rolling.mean()
        saida[desvio] = rolling.std(ddof=0)
        features.extend([media, desvio])

    alvo_data = saida["target_time"]
    ciclos = (
        ("hour", alvo_data.dt.hour, 24),
        ("dow", alvo_data.dt.dayofweek, 7),
        ("month", alvo_data.dt.month - 1, 12),
    )
    for rotulo, valor, periodo in ciclos:
        seno = f"target_{rotulo}_sin"
        cosseno = f"target_{rotulo}_cos"
        angulo = 2 * np.pi * valor / periodo
        saida[seno] = np.sin(angulo)
        saida[cosseno] = np.cos(angulo)
        features.extend([seno, cosseno])

    par_de_um_passo = saida["target_time"].sub(saida["origin_time"]).eq(step)
    colunas_obrigatorias = ["origin_time", "target_time", "y_true", "target_delta", *features]
    saida = saida.loc[par_de_um_passo].dropna(subset=colunas_obrigatorias)
    return saida.reset_index(drop=True), features


def chronological_train_test(
    quadro: pd.DataFrame,
    train_ratio: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa cronologicamente e purga alvos que cruzam a fronteira."""

    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio deve estar estritamente entre 0 e 1.")
    required = {"origin_time", "target_time"}
    if not required.issubset(quadro):
        raise KeyError("O quadro deve conter origin_time e target_time.")
    if len(quadro) < 3:
        raise ValueError("São necessárias ao menos três amostras para o corte.")
    if not quadro["origin_time"].is_monotonic_increasing:
        raise ValueError("O quadro deve estar em ordem temporal crescente.")

    corte = int(len(quadro) * train_ratio)
    if corte <= 0 or corte >= len(quadro):
        raise ValueError("O corte solicitado produz treino ou teste vazio.")
    inicio_teste = quadro.iloc[corte]["origin_time"]
    treino = quadro.iloc[:corte]
    treino = treino.loc[treino["target_time"] < inicio_teste]
    teste = quadro.iloc[corte:]
    if treino.empty or teste.empty:
        raise ValueError("A purga temporal produziu treino ou teste vazio.")
    return treino.reset_index(drop=True), teste.reset_index(drop=True)


def catalogo_features(
    nomes: Sequence[str],
    *,
    status_por_feature: Mapping[str, str] | None = None,
    nota_por_feature: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Classifica cada feature pela informação temporal que ela pode usar."""

    status = status_por_feature or {}
    notas = nota_por_feature or {}
    linhas = []
    for nome in nomes:
        linha = _descrever_feature(nome)
        linha["status"] = status.get(nome, "derivada")
        linha["nota"] = notas.get(nome, "")
        linhas.append(linha)
    return pd.DataFrame(linhas)


def _descrever_feature(nome: str) -> dict[str, str]:
    if nome == "level_t":
        grupo, disponibilidade, descricao = (
            "alvo_na_origem",
            "conhecido em t",
            "Nível do alvo observado na origem.",
        )
    elif nome.endswith("_alvo"):
        grupo, disponibilidade, descricao = (
            "conhecido_antecipadamente",
            "conhecido antecipadamente",
            "Valor da data-alvo já conhecido na origem (calendário/feriado).",
        )
    elif nome.startswith("target_lag_") or "_lag_" in nome:
        grupo, disponibilidade, descricao = (
            "defasagem",
            "somente passado",
            "Defasagem positiva; exclui a observação da data-alvo.",
        )
    elif nome.startswith(("target_mean_", "target_std_")) or any(
        trecho in nome for trecho in ("_mean_", "_std_")
    ):
        grupo, disponibilidade, descricao = (
            "janela_deslocada",
            "termina em t-1",
            "Janela móvel deslocada para não incluir o valor previsto.",
        )
    elif nome.startswith("target_") and nome.endswith(("_sin", "_cos")):
        grupo, disponibilidade, descricao = (
            "calendario",
            "conhecido antecipadamente",
            "Codificação cíclica da data-alvo.",
        )
    elif nome.endswith("_change_t"):
        grupo, disponibilidade, descricao = (
            "variacao_na_origem",
            "conhecida em t",
            "Variação calculada até a origem.",
        )
    elif nome in {
        "source_observations",
        "has_source_observation_t",
        "price_was_carried",
        "quote_age_days",
    }:
        grupo, disponibilidade, descricao = (
            "cobertura",
            "conhecida em t",
            "Cobertura já observada na origem.",
        )
    elif nome.endswith("_t"):
        grupo, disponibilidade, descricao = (
            "estado_na_origem",
            "conhecido em t",
            "Valor observado na origem para prever o passo seguinte.",
        )
    else:
        grupo, disponibilidade, descricao = (
            "revisar",
            "indefinida",
            "Classificação não reconhecida.",
        )
    return {
        "feature": nome,
        "grupo": grupo,
        "disponibilidade": disponibilidade,
        "descricao": descricao,
    }


def choque_futuro_nao_altera_features(
    dados: pd.DataFrame,
    *,
    time_col: str,
    indice_inicial_do_choque: int,
    colunas: Sequence[str],
    valor: float = 1_000_000_000.0,
    **kwargs,
) -> dict[str, float | int | bool]:
    """Reconstrói o quadro após alterar só o futuro e compara as features anteriores."""

    if indice_inicial_do_choque <= 0:
        raise ValueError("O choque precisa deixar ao menos uma origem anterior.")
    original, features = build_one_step_frame(dados, time_col=time_col, **kwargs)
    alterado = dados.copy()
    alterado.loc[indice_inicial_do_choque:, list(colunas)] = valor
    reconstruido, _ = build_one_step_frame(alterado, time_col=time_col, **kwargs)
    limite = pd.to_datetime(dados.loc[indice_inicial_do_choque - 1, time_col])
    antes = original.loc[original["origin_time"].le(limite), features].reset_index(drop=True)
    depois = reconstruido.loc[reconstruido["origin_time"].le(limite), features].reset_index(drop=True)
    iguais = antes.equals(depois)
    diferenca = 0.0 if iguais or antes.empty else float((antes - depois).abs().to_numpy().max())
    return {
        "origens_comparadas": int(len(antes)),
        "diferenca_maxima": diferenca,
        "iguais": bool(iguais),
    }


def longest_observed_run(serie: pd.Series, minimum_length: int = 1) -> pd.Series:
    """Retorna o maior trecho contíguo sem ausências, sem interpolar."""

    if minimum_length < 1:
        raise ValueError("minimum_length deve ser positivo.")
    observado = serie.notna()
    if not observado.any():
        raise ValueError("A série não possui valores observados.")
    grupos = observado.ne(observado.shift(fill_value=False)).cumsum()
    candidatos = serie.loc[observado].groupby(grupos.loc[observado])
    trecho = max((grupo for _, grupo in candidatos), key=len)
    if len(trecho) < minimum_length:
        raise ValueError(
            f"O maior trecho observado tem {len(trecho)} linhas; "
            f"são necessárias {minimum_length}."
        )
    return trecho
