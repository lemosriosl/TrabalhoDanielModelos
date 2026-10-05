from pathlib import Path

import pytest

from series_temporais.reporting import preparar_pacote as module


ROOT = Path(__file__).resolve().parents[1]


def test_selection_includes_raw_data_and_excludes_prepared_data():
    files = {path.relative_to(ROOT).as_posix() for path in module.listar_arquivos(ROOT)}
    assert all(f"data/base_{base:02d}/raw.csv" in files for base in range(1, 6))
    assert not any(path.endswith(("prepared.csv", "train.csv", "test.csv")) for path in files)
    assert "docs/triagem_sem_reexecucao.md" in files
    assert "results/comparacao_pareada_hw_sarimax.csv" in files


def test_staging_never_replaces_an_existing_folder(tmp_path, monkeypatch):
    root = tmp_path / "project"
    source = root / "entrega" / "relatorio_v2.html"
    source.parent.mkdir(parents=True)
    source.write_text("relatorio", encoding="utf-8")
    monkeypatch.setattr(module, "listar_arquivos", lambda _: [source])
    destination = tmp_path / "staging"
    module.preparar_pacote(root, destination)
    assert (destination / "relatorio_v2.html").read_text(encoding="utf-8") == "relatorio"
    assert "NÃO INCLUÍDO" in (destination / "LEIA_ANTES_DE_ENVIAR.md").read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        module.preparar_pacote(root, destination)
