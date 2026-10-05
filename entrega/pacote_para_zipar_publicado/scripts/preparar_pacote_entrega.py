"""Prepara `entrega/pacote_para_zipar` sem criar o ZIP final."""

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from series_temporais.reporting.preparar_pacote import preparar_pacote  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registro-diario", type=Path)
    parser.add_argument("--destino", type=Path, default=ROOT / "entrega" / "pacote_para_zipar")
    args = parser.parse_args()
    print(preparar_pacote(ROOT, args.destino, args.registro_diario))


if __name__ == "__main__":
    main()
