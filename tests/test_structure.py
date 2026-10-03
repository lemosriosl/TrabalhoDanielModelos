from pathlib import Path
import json

from series_temporais.paths import base_dir, base_file


ROOT = Path(__file__).resolve().parents[1]


def test_minimal_project_context_exists():
    for path in ("AGENTS.md", "projeto.yaml", "docs/decisoes.md"):
        assert (ROOT / path).is_file()


def test_each_base_has_raw_data_and_metadata():
    for number in range(1, 6):
        base = ROOT / "data" / f"base_{number:02d}"
        assert (base / "raw.csv").is_file()
        assert (base / "metadata.yaml").is_file()


def test_prepared_bases_use_canonical_file_names():
    for number in range(1, 5):
        for name in ("prepared.csv", "train.csv", "test.csv"):
            assert base_file(number, name, ROOT) == ROOT / "data" / f"base_{number:02d}" / name


def test_notebook_code_has_no_legacy_data_paths_or_relative_csv_outputs():
    forbidden = (
        "trabalho/bases",
        "trabalho\\bases",
        "grupo1.csv",
        "grupo2.csv",
        "grupo3.csv",
        "grupo4.csv",
        "grupo5.csv",
        ' / "base1_treino_preparada.csv"',
        ' / "base2_treino_preparada.csv"',
        ' / "base3_treino_preparada.csv"',
        ' / "base4_treino_preparada.csv"',
        ' / "base1_teste_preparada.csv"',
        ' / "base2_teste_preparada.csv"',
        ' / "base3_teste_preparada.csv"',
        ' / "base4_teste_preparada.csv"',
        'to_csv("',
    )
    for notebook_path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        code = "\n".join(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
        )
        assert not any(item in code for item in forbidden), notebook_path.name


def test_activity_and_delivery_locations_exist():
    assert (ROOT / "docs" / "atividade" / "n2_series_temporais.pdf").is_file()
    assert (ROOT / "entrega").is_dir()
