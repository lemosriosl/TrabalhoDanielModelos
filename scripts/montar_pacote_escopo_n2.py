"""Monta uma pasta nova contendo somente os itens exigidos na entrega N2."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from series_temporais.reporting.pacote_escopo_n2 import preparar_pacote_estrito  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registro-diario", type=Path, required=True)
    parser.add_argument("--destino", type=Path, required=True)
    args = parser.parse_args()
    print(preparar_pacote_estrito(ROOT, args.destino, args.registro_diario))


if __name__ == "__main__":
    main()
