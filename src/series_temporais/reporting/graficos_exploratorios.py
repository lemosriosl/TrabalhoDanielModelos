"""Padrão visual e utilitários comuns para os gráficos exploratórios.

O módulo não decide alvo, horizonte ou imputação. Ele padroniza apenas a
apresentação e deixa explícito quando uma série foi regularizada para uma
figura exploratória.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np


PALETA = {
    "serie": "#0072B2",
    "secundaria": "#D55E00",
    "sazonalidade": "#009E73",
    "tendencia": "#CC79A7",
    "residuo": "#E69F00",
    "ausencia": "#D55E00",
    "referencia": "#666666",
}

ROTULOS_DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def aplicar_estilo() -> None:
    """Aplica o estilo único do projeto às figuras matplotlib."""
    import matplotlib.pyplot as plt

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 160,
            "figure.figsize": (12, 5),
            "axes.titlesize": 13,
            "axes.titleweight": "normal",
            "axes.labelsize": 10,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linewidth": 0.6,
            "legend.frameon": False,
            "font.size": 10,
        }
    )


def finalizar_figura(fig, titulo: str, caminho: Path | None = None):
    """Aplica título, layout e, opcionalmente, salva a figura em PNG."""
    fig.suptitle(titulo, x=0.02, ha="left", fontsize=13, fontweight="normal")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    if caminho is not None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(caminho, bbox_inches="tight")
    return fig


def plotar_acf(ax, serie, *, lags: int, unidade: str):
    """Plota ACF somente de uma série regular, identificando a defasagem."""
    from statsmodels.graphics.tsaplots import plot_acf

    valores = np.asarray(serie, dtype=float)
    if np.isnan(valores).any():
        raise ValueError("A ACF exige uma série regular sem valores ausentes.")
    plot_acf(valores, lags=lags, ax=ax, color=PALETA["serie"])
    ax.set_xlabel(f"Defasagem ({unidade})")
    ax.set_ylabel("Autocorrelação")
    return ax


def preparar_eixo(ax, xlabel: str, ylabel: str, *, xrotation: int = 0) -> None:
    """Aplica rótulos com unidade e formatação consistente a um eixo."""
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xrotation:
        ax.tick_params(axis="x", labelrotation=xrotation)


def marcar_ausencias(ax, datas: Iterable, ausente: Iterable[bool], *, label: str = "Ausência") -> None:
    """Marca instantes ausentes sem criar valores artificiais na série."""
    datas = np.asarray(list(datas))
    ausente = np.asarray(list(ausente), dtype=bool)
    if ausente.any():
        ax.scatter(datas[ausente], np.zeros(ausente.sum()), s=10, color=PALETA["ausencia"], label=label, zorder=3)


def forca_sazonalidade(residuo, sazonalidade) -> float:
    """Calcula a força da sazonalidade com a definição usada no projeto."""
    residuo = np.asarray(residuo, dtype=float)
    sazonalidade = np.asarray(sazonalidade, dtype=float)
    denominador = np.nanvar(sazonalidade + residuo)
    if denominador == 0:
        return float("nan")
    return float(max(0.0, 1.0 - np.nanvar(residuo) / denominador))


def forca_tendencia(residuo, tendencia) -> float:
    """Calcula a força da tendência com a definição usada no projeto."""
    residuo = np.asarray(residuo, dtype=float)
    tendencia = np.asarray(tendencia, dtype=float)
    denominador = np.nanvar(tendencia + residuo)
    if denominador == 0:
        return float("nan")
    return float(max(0.0, 1.0 - np.nanvar(residuo) / denominador))
