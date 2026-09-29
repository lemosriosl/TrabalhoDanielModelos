from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_minimal_project_context_exists():
    for path in ("AGENTS.md", "projeto.yaml", "tarefas.csv", "docs/decisoes.md"):
        assert (ROOT / path).is_file()


def test_each_base_has_raw_data_and_metadata():
    for number in range(1, 6):
        base = ROOT / "data" / f"base_{number:02d}"
        assert (base / "raw.csv").is_file()
        assert (base / "metadata.yaml").is_file()


def test_activity_and_delivery_locations_exist():
    assert (ROOT / "docs" / "atividade" / "n2_series_temporais.pdf").is_file()
    assert (ROOT / "entrega").is_dir()
