from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_estrutura_minima_do_trabalho_existe():
    caminhos = [
        "AGENTS.md",
        "config/projeto.yaml",
        "collaboration/demandas.csv",
        "docs/plano.md",
        "bases/grupo1.csv",
        "bases/grupo5.csv",
        "results/metrics",
        "report/html",
        "report/pdf",
        "entrega",
    ]

    for caminho in caminhos:
        assert (ROOT / caminho).exists(), caminho

