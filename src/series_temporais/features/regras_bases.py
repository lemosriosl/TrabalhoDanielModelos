"""Regras explícitas de disponibilidade por base.

Centraliza o que cada notebook de feature engineering e de Random Forest deve
usar, para não espalhar listas litadas e classificações implícitas. Variáveis
ainda pendentes de confirmação econômica ficam marcadas como ``em_validacao``
ou ``provisorio``, sem inventar atraso de publicação.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from series_temporais.features.temporal import (
    CovariavelTemporal,
    Disponibilidade,
    catalogo_features,
)


@dataclass(frozen=True)
class RegraCovariavelBase:
    """Covariável candidata a feature, com status auditável."""

    coluna: str
    disponibilidade: Disponibilidade
    atraso: int = 0
    status: str = "em_validacao"
    justificativa: str = ""

    def temporal(self) -> CovariavelTemporal:
        return CovariavelTemporal(self.disponibilidade, self.atraso)

    def nome_feature(self) -> str:
        if self.disponibilidade == Disponibilidade.CONHECIDO_ANTECIPADAMENTE:
            return f"{self.coluna}_alvo"
        if self.atraso:
            return f"{self.coluna}_lag_{self.atraso}"
        return f"{self.coluna}_t"


@dataclass(frozen=True)
class EspecificacaoBase:
    """Contrato de um passo por base."""

    base_id: str
    time_col: str
    target_col: str
    expected_step: str
    lags: tuple[int, ...]
    windows: tuple[int, ...]
    covariaveis: tuple[RegraCovariavelBase, ...]
    proibidas: tuple[str, ...] = ()
    notas: str = ""

    def external_cols(self) -> list[str]:
        return [regra.coluna for regra in self.covariaveis]

    def availability(self) -> dict[str, CovariavelTemporal]:
        return {regra.coluna: regra.temporal() for regra in self.covariaveis}

    def status_por_feature(self) -> dict[str, str]:
        mapa = {regra.nome_feature(): regra.status for regra in self.covariaveis}
        mapa["level_t"] = "aprovado"
        return mapa

    def nota_por_feature(self) -> dict[str, str]:
        return {regra.nome_feature(): regra.justificativa for regra in self.covariaveis}

    def tabela_disponibilidade(self) -> pd.DataFrame:
        linhas = [
            {
                "coluna": regra.coluna,
                "disponibilidade": regra.disponibilidade.value,
                "atraso": regra.atraso,
                "feature": regra.nome_feature(),
                "status": regra.status,
                "justificativa": regra.justificativa,
            }
            for regra in self.covariaveis
        ]
        for coluna in self.proibidas:
            linhas.append(
                {
                    "coluna": coluna,
                    "disponibilidade": Disponibilidade.PROIBIDA.value,
                    "atraso": 0,
                    "feature": "",
                    "status": "excluido",
                    "justificativa": "Proibida no quadro modelável.",
                }
            )
        return pd.DataFrame(linhas)

    def catalogo(self, features: list[str]) -> pd.DataFrame:
        return catalogo_features(
            features,
            status_por_feature=self.status_por_feature(),
            nota_por_feature=self.nota_por_feature(),
        )


def _na_origem(coluna: str, *, status: str, justificativa: str) -> RegraCovariavelBase:
    return RegraCovariavelBase(
        coluna=coluna,
        disponibilidade=Disponibilidade.NA_ORIGEM,
        status=status,
        justificativa=justificativa,
    )


def _antecipada(coluna: str, *, status: str, justificativa: str) -> RegraCovariavelBase:
    return RegraCovariavelBase(
        coluna=coluna,
        disponibilidade=Disponibilidade.CONHECIDO_ANTECIPADAMENTE,
        status=status,
        justificativa=justificativa,
    )


BASE_1 = EspecificacaoBase(
    base_id="base_01",
    time_col="Date",
    target_col="Close",
    expected_step="1D",
    lags=(1, 2, 3, 7, 14, 30),
    windows=(7, 14, 30),
    covariaveis=(
        _na_origem(
            "Open",
            status="em_validacao",
            justificativa="Usada após o fechamento de t para prever t+1; horário intradiário pendente.",
        ),
        _na_origem(
            "High",
            status="em_validacao",
            justificativa="Conhecida só após o dia t; válida no cenário pós-fechamento.",
        ),
        _na_origem(
            "Low",
            status="em_validacao",
            justificativa="Conhecida só após o dia t; válida no cenário pós-fechamento.",
        ),
        _na_origem(
            "Volume",
            status="em_validacao",
            justificativa="Volume acumulado de t, disponível no fechamento.",
        ),
    ),
    proibidas=("Adj Close",),
    notas="Cenário de origem: após o fechamento de t, prever o passo diário seguinte.",
)

BASE_2 = EspecificacaoBase(
    base_id="base_02",
    time_col="date_time",
    target_col="traffic_volume",
    expected_step="1h",
    lags=(1, 2, 3, 24, 48, 168),
    windows=(24, 168),
    covariaveis=(
        _antecipada(
            "is_holiday",
            status="aprovado",
            justificativa="Feriado da data-alvo; calendário conhecido antecipadamente.",
        ),
        _na_origem(
            "temp",
            status="em_validacao",
            justificativa="Observada na hora t; não simula previsão meteorológica futura.",
        ),
        _na_origem(
            "rain_1h",
            status="em_validacao",
            justificativa="Acumulado observado na hora t.",
        ),
        _na_origem(
            "snow_1h",
            status="em_validacao",
            justificativa="Acumulado observado na hora t.",
        ),
        _na_origem(
            "clouds_all",
            status="em_validacao",
            justificativa="Cobertura observada na hora t.",
        ),
    ),
    proibidas=("weather_main", "weather_description", "holiday"),
    notas="holiday textual vira is_holiday binário da data-alvo; categorias climáticas ficam fora.",
)

BASE_3 = EspecificacaoBase(
    base_id="base_03",
    time_col="datetime",
    target_col="PM2.5",
    expected_step="1h",
    lags=(1, 2, 3, 24, 48, 168),
    windows=(24, 168),
    covariaveis=tuple(
        _na_origem(
            coluna,
            status="em_validacao",
            justificativa="Simultânea ao alvo; usada só como estado de t para prever t+1.",
        )
        for coluna in (
            "PM10",
            "SO2",
            "NO2",
            "CO",
            "O3",
            "TEMP",
            "PRES",
            "DEWP",
            "RAIN",
            "WSPM",
            "wd_sin",
            "wd_cos",
        )
    ),
    proibidas=("No", "station", "wd"),
    notas="Sem interpolação global; linhas incompletas saem do quadro.",
)

BASE_4 = EspecificacaoBase(
    base_id="base_04",
    time_col="Date Time",
    target_col="T (degC)",
    expected_step="10min",
    lags=(1, 2, 6, 12, 144, 1008),
    windows=(6, 144, 1008),
    covariaveis=tuple(
        _na_origem(
            coluna,
            status="em_validacao",
            justificativa="Medição simultânea; entra em t para prever o intervalo seguinte.",
        )
        for coluna in (
            "p (mbar)",
            "Tpot (K)",
            "Tdew (degC)",
            "rh (%)",
            "VPmax (mbar)",
            "VPact (mbar)",
            "VPdef (mbar)",
            "sh (g/kg)",
            "H2OC (mmol/mol)",
            "rho (g/m**3)",
            "wv (m/s)",
            "max. wv (m/s)",
            "wd_sin",
            "wd_cos",
        )
    ),
    proibidas=("wd (deg)",),
    notas="Alvo provisório T (degC); -9999 deve ser ausência antes das features.",
)

BASE_5_STATUS = {
    "price_t": "aprovado",
    "log_price_t": "aprovado",
    "log_return_t": "aprovado",
    "source_observations": "aprovado",
    "has_source_observation_t": "aprovado",
    "price_was_carried": "aprovado",
    "quote_age_days": "aprovado",
    "treasury_10y_t": "provisorio",
    "fed_funds_rate_t": "provisorio",
    "treasury_change_t": "provisorio",
    "fed_funds_change_t": "provisorio",
}

BASE_5_NOTAS = {
    "treasury_10y_t": "Fonte/unidade/atraso de publicação ainda pendentes.",
    "fed_funds_rate_t": "Fonte/unidade/atraso de publicação ainda pendentes.",
    "treasury_change_t": "Derivada da taxa provisória na origem.",
    "fed_funds_change_t": "Derivada da taxa provisória na origem.",
}


ESPECIFICACOES: Mapping[str, EspecificacaoBase] = {
    "base_01": BASE_1,
    "base_02": BASE_2,
    "base_03": BASE_3,
    "base_04": BASE_4,
}


def especificacao(base_id: str) -> EspecificacaoBase:
    try:
        return ESPECIFICACOES[base_id]
    except KeyError as exc:
        raise KeyError(f"Base desconhecida: {base_id!r}") from exc


def preparar_entrada_base2(dados: pd.DataFrame) -> pd.DataFrame:
    """Cria o indicador binário de feriado sem usar a coluna textual em X."""

    if "holiday" not in dados.columns:
        raise KeyError("A Base 2 exige a coluna holiday para derivar is_holiday.")
    quadro = dados.copy()
    quadro["is_holiday"] = quadro["holiday"].notna().astype(int)
    return quadro


def validar_proibidas(colunas_usadas: list[str], espec: EspecificacaoBase) -> None:
    """Garante que colunas proibidas não entrem como covariáveis."""

    conflito = sorted(set(colunas_usadas).intersection(espec.proibidas))
    if conflito:
        raise ValueError(f"Colunas proibidas em uso na {espec.base_id}: {conflito}")


def catalogo_base5(features: list[str]) -> pd.DataFrame:
    """Catálogo da Base 5 com status provisório das taxas."""

    status = dict(BASE_5_STATUS)
    for nome in features:
        status.setdefault(
            nome,
            "aprovado"
            if nome.startswith(("price_", "return_", "target_"))
            or nome.endswith(("_sin", "_cos"))
            or "lag_" in nome
            else "em_validacao",
        )
    return catalogo_features(
        features,
        status_por_feature=status,
        nota_por_feature=BASE_5_NOTAS,
    )
