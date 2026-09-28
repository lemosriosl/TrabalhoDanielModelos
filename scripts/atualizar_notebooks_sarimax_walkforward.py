"""Troca a avaliação final dos notebooks SARIMAX por walk-forward de um passo."""

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
CODIGO = """import ast
from series_temporais.models.pipeline_sarimax_walkforward import prever_walk_forward_referencia

order_final = ast.literal_eval(melhor['order'])
seasonal_final = ast.literal_eval(melhor['seasonal_order'])
colunas_finais = EXOG_SETS[melhor['exogenas']]
previsoes, registro_final = prever_walk_forward_referencia(
    df[TARGET], TEST_START,
    order=order_final, seasonal_order=seasonal_final,
    exogenas=df[colunas_finais] if colunas_finais else None,
    maxiter=100,
)
registro_final.update({
    'base': f'base{BASE_DIR.name[-1]}', 'inicio_teste': str(TEST_START),
    'horizonte': 1, 'janela': 'expansiva', 'exogenas': colunas_finais,
    'fonte_pipeline': 'docs/Pipes de exemplo/atividade_sarimax.ipynb',
})
display(pd.Series(registro_final, name='valor').to_frame())
selecao.to_csv(BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_selecao.csv', index=False)
previsoes.to_csv(BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_previsoes.csv')
with (BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_registro.json').open('w', encoding='utf-8') as arquivo:
    json.dump(registro_final, arquivo, ensure_ascii=False, indent=2)"""

for base in (1, 2):
    caminho = ROOT / "trabalho" / "bases" / f"grupo{base}" / "modelos" / f"grupo{base}_SARIMAX.ipynb"
    notebook = nbformat.read(caminho, as_version=4)
    for indice, celula in enumerate(notebook.cells):
        if celula.cell_type == "markdown" and "## 3. Ajuste final" in celula.source:
            notebook.cells[indice + 1].source = CODIGO
            break
    nbformat.write(notebook, caminho)
