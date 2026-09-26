import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pytest

from series_temporais.reporting.graficos_exploratorios import (
    forca_sazonalidade,
    forca_tendencia,
)

ROOT = Path(__file__).resolve().parents[2]


def test_forcas_decomposicao_ficam_no_intervalo_valido():
    residuo = np.array([0.2, -0.1, 0.1, -0.2])
    sazonalidade = np.array([2.0, -2.0, 2.0, -2.0])
    tendencia = np.array([1.0, 2.0, 3.0, 4.0])
    assert 0 <= forca_sazonalidade(residuo, sazonalidade) <= 1
    assert 0 <= forca_tendencia(residuo, tendencia) <= 1


def test_forca_sem_variacao_e_nan():
    assert np.isnan(forca_sazonalidade([0, 0], [0, 0]))
    assert np.isnan(forca_tendencia([0, 0], [0, 0]))


def test_plotar_acf_rotula_unidade_e_rejeita_ausencias():
    from series_temporais.reporting.graficos_exploratorios import plotar_acf

    fig, ax = plt.subplots()
    plotar_acf(ax, np.arange(20, dtype=float), lags=5, unidade="horas")
    assert ax.get_xlabel() == "Defasagem (horas)"
    plt.close(fig)

    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="série regular"):
        plotar_acf(ax, [1.0, np.nan, 3.0], lags=2, unidade="dias")
    plt.close(fig)


def test_grafico_base5_usa_csv_atual_e_nao_interpola_com_futuro():
    notebook = ROOT / "trabalho/bases/grupo5/graficos_exploratorios_base5.ipynb"
    cells = json.loads(notebook.read_text(encoding="utf-8"))["cells"]
    codigo = "\n".join(
        "".join(cell.get("source", []))
        for cell in cells
        if cell.get("cell_type") == "code"
    )
    assert "grupo5.csv" in codigo
    assert "grupo5_new.csv" not in codigo
    assert "limit_direction='both'" not in codigo
    assert "preparar_ouro_semanal" in codigo
