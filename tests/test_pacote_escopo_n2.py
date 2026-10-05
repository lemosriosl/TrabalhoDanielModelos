from pathlib import Path

import pytest

from series_temporais.reporting import pacote_escopo_n2 as module


ROOT = Path(__file__).resolve().parents[1]


def test_selecao_cobre_escopo_sem_arquivos_suplementares():
    names = {path.as_posix() for path in module.selecionar_arquivos(ROOT).values()}
    assert {f"data/base_{base:02d}/raw.csv" for base in range(1, 6)} <= names
    assert {"relatorio_v2.pdf", "relatorio_v2.html",
            "results/metricas_individuais_auditadas.csv",
            "docs/relatorio/modelo.html"} <= names
    assert not any(name.startswith(("tests/", "references/")) for name in names)
    assert not any("SARIMAX_fast" in name or "RF_preco" in name for name in names)
    assert not any(name.endswith(("README.md", "AGENTS.md", "ranking_descritivo_modelos.csv")) for name in names)


def test_pacote_nao_sobrescreve_e_detecta_extras(tmp_path, monkeypatch):
    source = tmp_path / "relatorio.html"
    source.write_text("relatorio", encoding="utf-8")
    registro = tmp_path / "demandas.pdf"
    registro.write_bytes(b"%PDF-1.4\n")
    monkeypatch.setattr(module, "selecionar_arquivos", lambda _: {source: Path("relatorio.html")})
    destination = tmp_path / "entrega"
    module.preparar_pacote_estrito(tmp_path, destination, registro)
    assert module.verificar_pacote(tmp_path, destination, registro) == 2
    with pytest.raises(FileExistsError):
        module.preparar_pacote_estrito(tmp_path, destination, registro)
    (destination / "extra.txt").write_text("extra", encoding="utf-8")
    with pytest.raises(ValueError, match="extras"):
        module.verificar_pacote(tmp_path, destination, registro)
