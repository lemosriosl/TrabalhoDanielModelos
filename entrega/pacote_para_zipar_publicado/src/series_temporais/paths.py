"""Resolução única de caminhos do projeto e de suas bases."""

from __future__ import annotations

from pathlib import Path


def project_root(start: Path | None = None) -> Path:
    """Encontra a raiz a partir do diretório atual ou de um caminho informado."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "data").is_dir():
            return candidate
    raise FileNotFoundError("Raiz do projeto não encontrada.")


def base_dir(number: int, start: Path | None = None) -> Path:
    """Retorna a pasta canônica de uma das cinco bases."""
    if number not in range(1, 6):
        raise ValueError("A base deve estar entre 1 e 5.")
    path = project_root(start) / "data" / f"base_{number:02d}"
    if not path.is_dir():
        raise FileNotFoundError(path)
    return path


def base_file(number: int, name: str, start: Path | None = None) -> Path:
    """Retorna um arquivo existente da pasta canônica de uma base."""
    path = base_dir(number, start) / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path
