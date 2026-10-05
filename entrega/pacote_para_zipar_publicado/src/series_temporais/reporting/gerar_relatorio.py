"""Gera o HTML autocontido a partir da fonte revisada do relatório."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def gerar_relatorio(raiz: Path, site: Path | None = None) -> Path:
    fonte = raiz / "docs" / "relatorio" / "modelo.html"
    destino = raiz / "entrega" / "relatorio.html"
    if not fonte.is_file():
        raise FileNotFoundError(fonte)
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fonte, destino)
    if site is not None:
        publicacao = site / "dist" / "index.html"
        publicacao.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fonte, publicacao)
    return destino


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--site", type=Path)
    args = parser.parse_args()
    print(gerar_relatorio(args.raiz, args.site))
