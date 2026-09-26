from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_estrutura_minima_do_trabalho_existe():
    caminhos = [
        "AGENTS.md",
        "config/projeto.yaml",
        "collaboration/demandas.csv",
        "docs/plano.md",
        "trabalho/bases/grupo1/grupo1.csv",
        "trabalho/bases/grupo5/grupo5.csv",
        "results/metrics",
        "report/html",
        "report/pdf",
        "trabalho/entrega",
    ]

    for caminho in caminhos:
        assert (ROOT / caminho).exists(), caminho

