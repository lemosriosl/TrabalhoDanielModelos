"""Monta uma pasta local de pré-entrega, sem criar ZIP nem ocultar pendências."""

from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path


REQUIRED = (
    "entrega/relatorio_v2.html", "entrega/relatorio_v2.pdf",
    "projeto.yaml", "requirements.txt", "pyproject.toml",
    "results/metrics.csv", "results/metricas_individuais_auditadas.csv",
    "results/comparacao_pareada_hw_sarimax.csv",
)


def listar_arquivos(root: Path) -> list[Path]:
    """Inclui fontes e dados brutos; exclui preparados e resultados locais ambíguos."""
    files = {root / rel for rel in REQUIRED}
    files.update(root / rel for rel in (
        "README.md", "AGENTS.md", "entrega/README.md",
        "entrega/conceito_walk_forward.md", "results/README.md",
        "results/ljung_box_auditado.csv", "results/achados_auditoria.json",
        "data/dicionario_variaveis_externas.md",
    ))
    for folder, pattern in (("src", "*.py"), ("scripts", "*.py"),
                            ("notebooks", "*.ipynb"), ("docs", "*"),
                            ("tests", "*.py"), ("results/extraidos_do_remoto", "*"),
                            ("results/figuras_sarimax", "*")):
        directory = root / folder
        if directory.exists():
            files.update(path for path in directory.rglob(pattern) if path.is_file())
    for base in range(1, 6):
        directory = root / "data" / f"base_{base:02d}"
        files.add(directory / "raw.csv")
        files.update(path for path in directory.iterdir()
                     if path.is_file() and path.name not in {"prepared.csv", "train.csv", "test.csv"})
    missing = sorted(str(path.relative_to(root)) for path in files if not path.is_file())
    if missing:
        raise FileNotFoundError(f"Arquivos obrigatórios ausentes: {missing}")
    return sorted(files)


def _caminho_no_pacote(source: Path, root: Path) -> Path:
    relative = source.relative_to(root)
    if relative.parent == Path("entrega"):
        return (Path(source.name) if source.name.startswith("relatorio_v2.")
                else Path("documentacao_entrega") / source.name)
    return relative


def _aviso_pre_entrega(registro_diario_incluido: bool) -> str:
    status = [
        "# Pré-entrega para revisão - não enviar automaticamente",
        "",
        "O PDF e o HTML devem ter o mesmo conteúdo. Este pacote inclui as cinco bases brutas,",
        "notebooks, código, fonte do relatório e resultados auditados. O arquivo",
        "`results/metrics.csv` contém somente cinco linhas XGBoost: **não é o ranking final**.",
        "`results/comparacao_pareada_hw_sarimax.csv` é exploratório e cobre só dois modelos.",
        "Consulte `docs/triagem_sem_reexecucao.md` antes de usar os números.",
        "",
        "## Bloqueios para a entrega integral",
        "",
        "- Origens e horizontes dos quatro modelos não estão homologados; não há vitórias ou posição média válidas.",
        "- SARIMAX da Base 4 não possui avaliação final extensa; a pipe rápida do notebook não a substitui.",
        "- CSVs integrais de RF/XGBoost não foram recuperados para todas as bases.",
        "- Revisão humana e eventual orientação do professor sobre a entrega parcial permanecem necessárias.",
        "- Registro diário real: " + ("incluído para revisão." if registro_diario_incluido
                                   else "NÃO INCLUÍDO; acompanhamento externo será revisto pelo grupo."),
        "",
        "Não crie o ZIP final até conferir esses bloqueios e o manifesto de hashes.",
    ]
    return "\n".join(status) + "\n"


def preparar_pacote(root: Path, destination: Path, registro_diario: Path | None = None) -> Path:
    """Cria destino novo; nunca apaga nem sobrescreve uma pré-entrega existente."""
    root = root.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"Preserve ou renomeie a pasta existente antes de gerar outra: {destination}")
    selected = listar_arquivos(root)
    if registro_diario is not None and not registro_diario.is_file():
        raise FileNotFoundError(registro_diario)
    destination.mkdir(parents=True)
    manifest = []
    for source in selected:
        packaged = _caminho_no_pacote(source, root)
        target = destination / packaged
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest.append((target.relative_to(destination).as_posix(), target.stat().st_size,
                         hashlib.sha256(target.read_bytes()).hexdigest()))
    if registro_diario is not None:
        target = destination / "registro_diario" / registro_diario.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registro_diario, target)
        manifest.append((target.relative_to(destination).as_posix(), target.stat().st_size,
                         hashlib.sha256(target.read_bytes()).hexdigest()))
    with (destination / "manifesto_arquivos.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("arquivo", "bytes", "sha256"))
        writer.writerows(sorted(manifest))
    (destination / "LEIA_ANTES_DE_ENVIAR.md").write_text(
        _aviso_pre_entrega(registro_diario is not None), encoding="utf-8")
    return destination


def atualizar_pacote(root: Path, destination: Path) -> Path:
    """Atualiza somente uma pré-entrega íntegra, sem remover arquivos existentes."""
    root = root.resolve()
    destination = destination.resolve()
    manifest_path = destination / "manifesto_arquivos.csv"
    warning_path = destination / "LEIA_ANTES_DE_ENVIAR.md"
    if not manifest_path.is_file() or not warning_path.is_file():
        raise FileNotFoundError("Destino não é uma pré-entrega gerada pelo projeto.")
    with manifest_path.open(encoding="utf-8", newline="") as stream:
        previous = list(csv.DictReader(stream))
    previous_names = {row["arquivo"] for row in previous}
    if len(previous_names) != len(previous):
        raise ValueError("Manifesto anterior contém nomes duplicados.")
    observed_names = {path.relative_to(destination).as_posix()
                      for path in destination.rglob("*") if path.is_file()}
    if observed_names != previous_names | {"manifesto_arquivos.csv", "LEIA_ANTES_DE_ENVIAR.md"}:
        raise ValueError("Destino possui arquivo não previsto ou falta arquivo manifestado.")
    for row in previous:
        source = destination / row["arquivo"]
        if (source.stat().st_size != int(row["bytes"])
                or hashlib.sha256(source.read_bytes()).hexdigest() != row["sha256"]):
            raise ValueError(f"Pré-entrega modificada após a geração: {row['arquivo']}")
    selected = listar_arquivos(root)
    current_names = {_caminho_no_pacote(source, root).as_posix() for source in selected}
    if not previous_names.issubset(current_names):
        raise ValueError("A seleção atual removeria arquivos da pré-entrega; revisão manual necessária.")
    updated = []
    for source in selected:
        relative = _caminho_no_pacote(source, root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        updated.append((relative.as_posix(), target.stat().st_size,
                        hashlib.sha256(target.read_bytes()).hexdigest()))
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("arquivo", "bytes", "sha256"))
        writer.writerows(sorted(updated))
    warning_path.write_text(_aviso_pre_entrega(False), encoding="utf-8")
    return destination
