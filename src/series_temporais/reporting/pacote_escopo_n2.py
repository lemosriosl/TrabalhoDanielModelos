"""Monta apenas os artefatos exigidos para a entrega N2.

O pacote não contém notas internas, testes, versões antigas ou rankings não
homologados. A seleção preserva os insumos do gerador do relatório e o código
necessário para examinar as análises apresentadas.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


REPORT_SOURCE = (
    "docs/relatorio/modelo.html",
    "docs/relatorio/v2.css",
    "docs/relatorio/v2.js",
    "docs/relatorio/v2-audit.css",
    "docs/relatorio/v2-audit.js",
)
RESULT_SOURCE = (
    "results/metrics.csv",
    "results/metricas_individuais_auditadas.csv",
    "results/comparacao_pareada_hw_sarimax.csv",
    "results/ljung_box_auditado.csv",
    "results/achados_auditoria.json",
    "results/extraidos_do_remoto/random_forest_metrics.csv",
)
EXCLUDED_CODE = {
    "src/series_temporais/reporting/gerar_relatorio.py",  # versão anterior
    "src/series_temporais/reporting/preparar_pacote.py",  # empacotamento antigo
    "src/series_temporais/reporting/pacote_escopo_n2.py",  # empacotamento, não análise
    "src/series_temporais/reporting/ranking_descritivo.py",  # posterior ao relatório
}


def selecionar_arquivos(root: Path) -> dict[Path, Path]:
    """Mapeia cada fonte para seu caminho no pacote, sem itens suplementares."""
    root = root.resolve()
    mapping: dict[Path, Path] = {}

    def include(relative: str, packaged: str | None = None) -> None:
        source = root / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        target = Path(packaged or relative)
        if target in mapping.values():
            raise ValueError(f"Destino duplicado: {target}")
        mapping[source] = target

    include("entrega/relatorio_v2.pdf", "relatorio_v2.pdf")
    include("entrega/relatorio_v2.html", "relatorio_v2.html")
    for name in ("projeto.yaml", "requirements.txt", "pyproject.toml"):
        include(name)
    for name in REPORT_SOURCE + RESULT_SOURCE:
        include(name)
    for base in range(1, 6):
        for name in ("raw.csv", "metadata.yaml"):
            include(f"data/base_{base:02d}/{name}")
    for source in sorted((root / "notebooks").glob("*.ipynb")):
        if "SARIMAX_fast" not in source.name and "RF_preco" not in source.name:
            include(source.relative_to(root).as_posix())
    for source in sorted((root / "src" / "series_temporais").rglob("*.py")):
        relative = source.relative_to(root).as_posix()
        if relative not in EXCLUDED_CODE and "/models/" not in relative:
            include(relative)
    for name in ("scripts/extract_remote_rf_metrics.py", "scripts/run_frozen_sarimax_final.py"):
        include(name)
    for source in sorted((root / "results" / "figuras_sarimax").glob("*")):
        if source.is_file():
            include(source.relative_to(root).as_posix())
    return mapping


def preparar_pacote_estrito(root: Path, destination: Path, registro: Path) -> Path:
    """Cria uma pasta nova; jamais sobrescreve uma entrega existente."""
    root = root.resolve()
    destination = destination.resolve()
    registro = registro.resolve()
    if destination.exists():
        raise FileExistsError(destination)
    if not registro.is_file() or registro.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"Registro de demandas em PDF ausente: {registro}")
    mapping = selecionar_arquivos(root)
    mapping[registro] = Path("registro_demandas.pdf")
    destination.mkdir(parents=True)
    for source, relative in mapping.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    verificar_pacote(root, destination, registro)
    return destination


def verificar_pacote(root: Path, destination: Path, registro: Path) -> int:
    """Verifica lista exata e hashes, inclusive do registro externo."""
    mapping = selecionar_arquivos(root)
    mapping[registro.resolve()] = Path("registro_demandas.pdf")
    expected = {relative.as_posix() for relative in mapping.values()}
    observed = {path.relative_to(destination).as_posix()
                for path in destination.rglob("*") if path.is_file()}
    if observed != expected:
        raise ValueError(f"Arquivos faltantes: {sorted(expected-observed)}; extras: {sorted(observed-expected)}")
    for source, relative in mapping.items():
        if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256((destination / relative).read_bytes()).digest():
            raise ValueError(f"Conteúdo divergente: {relative}")
    return len(mapping)
