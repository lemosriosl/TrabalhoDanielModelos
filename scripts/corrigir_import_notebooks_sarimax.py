from pathlib import Path
import nbformat

ROOT = Path(__file__).resolve().parents[1]
for base in (1, 2):
    caminho = ROOT / "trabalho" / "bases" / f"grupo{base}" / "modelos" / f"grupo{base}_SARIMAX.ipynb"
    notebook = nbformat.read(caminho, as_version=4)
    for celula in notebook.cells:
        if celula.cell_type == "code" and "pipeline_sarimax_walkforward import" in celula.source:
            celula.source = celula.source.replace("from series_temporais.models.pipeline_sarimax_walkforward import prever_walk_forward_referencia", "from series_temporais.models.pipeline_sarimax_walkforward_v2 import prever_walk_forward_referencia_v2").replace("prever_walk_forward_referencia(", "prever_walk_forward_referencia_v2(")
    nbformat.write(notebook, caminho)
