"""Prepara `entrega/pacote_para_zipar` sem criar o ZIP final."""

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from series_temporais.reporting.preparar_pacote import preparar_pacote, atualizar_pacote  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registro-diario", type=Path)
    parser.add_argument("--destino", type=Path, default=ROOT / "entrega" / "pacote_para_zipar")
    parser.add_argument("--atualizar", action="store_true",
                        help="Atualiza uma pré-entrega íntegra já gerada, sem remover arquivos.")
    args = parser.parse_args()
    if args.atualizar:
        if args.registro_diario:
            parser.error("--registro-diario exige uma pasta nova, sem --atualizar")
        print(atualizar_pacote(ROOT, args.destino))
    else:
        print(preparar_pacote(ROOT, args.destino, args.registro_diario))


if __name__ == "__main__":
    main()
