"""Gera uma v2 independente, sem modificar o relatório v1 ou resultados."""
from pathlib import Path
import csv
import json
import subprocess


STL_FIGURES = [
    ('base_01-graficos_exploratorios_stl_sazonalidade_base1.ipynb', 4),
    ('base_02-graficos_exploratorios_stl_sazonalidade_base2.ipynb', 4),
    ('base_03-grupo3_RF.ipynb', 8),
    ('base_04-grupo4_RF.ipynb', 8),
    ('base_05-grupo5_RF_retorno.ipynb', 10),
]
RF_IMPORTANCE_FIGURES = [
    (f'base_{base:02d}-grupo{base}_RF.ipynb', 14) for base in range(1, 5)
] + [('base_05-grupo5_RF_retorno.ipynb', 16)]
HW_RESIDUAL_FIGURES = [
    (f'base_{base:02d}-grupo{base}_HW.ipynb', 8) for base in range(1, 5)
] + [('base_05-grupo5_HW.ipynb', 25)]
HW_ACF_FIGURES = [
    (f'base_{base:02d}-grupo{base}_HW.ipynb', 10) for base in range(1, 5)
] + [('base_05-grupo5_HW.ipynb', 27)]
RF_RESIDUAL_FIGURES = [
    (f'base_{base:02d}-grupo{base}_RF.ipynb', 21) for base in range(1, 5)
] + [('base_05-grupo5_RF_retorno.ipynb', 23)]
RF_ACF_FIGURES = [
    (f'base_{base:02d}-grupo{base}_RF.ipynb', 23) for base in range(1, 5)
] + [('base_05-grupo5_RF_retorno.ipynb', 25)]
XGB_DIAGNOSTIC_FIGURES = [
    (f'base_{base:02d}-grupo{base}_XGBoost.ipynb', 10) for base in range(1, 6)
]


def figuras_notebook(raiz: Path, specs: list[tuple[str, int]]) -> list[dict]:
    figures = []
    for base, (name, cell_index) in enumerate(specs, start=1):
        notebook = json.loads((raiz / 'notebooks' / name).read_text(encoding='utf-8'))
        output = next((item for item in notebook['cells'][cell_index].get('outputs', [])
                       if 'image/png' in item.get('data', {})), None)
        if output is None:
            raise ValueError(f'Figura executada ausente: {name} célula {cell_index}')
        raw = output['data']['image/png']
        figures.append({'base': base, 'source': f'notebooks/{name}#cell-{cell_index}',
                        'data': 'data:image/png;base64,' + (''.join(raw) if isinstance(raw, list) else raw)})
    return figures


def gerar(raiz: Path) -> Path:
    fontes = raiz / 'docs' / 'relatorio'
    html = (fontes / 'modelo.html').read_text(encoding='utf-8')
    css = (fontes / 'v2.css').read_text(encoding='utf-8')
    js = (fontes / 'v2.js').read_text(encoding='utf-8')
    audit_css = (fontes / 'v2-audit.css').read_text(encoding='utf-8')
    audit_js = (fontes / 'v2-audit.js').read_text(encoding='utf-8')
    with (raiz / 'results' / 'metrics.csv').open(encoding='utf-8', newline='') as stream:
        metrics = [row for row in csv.DictReader(stream) if row['modelo'] == 'XGBoost']
    with (raiz / 'results' / 'metricas_individuais_auditadas.csv').open(encoding='utf-8', newline='') as stream:
        individual = list(csv.DictReader(stream))
    with (raiz / 'results' / 'ljung_box_auditado.csv').open(encoding='utf-8', newline='') as stream:
        diagnostics = list(csv.DictReader(stream))
    with (raiz / 'results' / 'comparacao_pareada_hw_sarimax.csv').open(encoding='utf-8', newline='') as stream:
        paired = list(csv.DictReader(stream))
    findings = json.loads((raiz / 'results' / 'achados_auditoria.json').read_text(encoding='utf-8'))
    if len(metrics) != 5 or len({row['base_id'] for row in metrics}) != 5:
        raise ValueError('Esperadas cinco bases XGBoost no consolidado.')
    if len(paired) != 4 or {row['base_id'] for row in paired} != {'base_01', 'base_02', 'base_03', 'base_05'}:
        raise ValueError('Esperadas quatro linhas na comparação exploratória HW/SARIMAX.')
    metrics.sort(key=lambda row: row['base_id'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=raiz, text=True).strip()
    snapshot = json.dumps({'commit': commit, 'metrics': metrics, 'individual': individual,
                           'diagnostics': diagnostics, 'findings': findings, 'paired': paired,
                           'stl_figures': figuras_notebook(raiz, STL_FIGURES),
                           'hw_residual_figures': figuras_notebook(raiz, HW_RESIDUAL_FIGURES),
                           'hw_acf_figures': figuras_notebook(raiz, HW_ACF_FIGURES),
                           'rf_residual_figures': figuras_notebook(raiz, RF_RESIDUAL_FIGURES),
                           'rf_importance_figures': figuras_notebook(raiz, RF_IMPORTANCE_FIGURES),
                           'rf_acf_figures': figuras_notebook(raiz, RF_ACF_FIGURES),
                           'xgb_diagnostic_figures': figuras_notebook(raiz, XGB_DIAGNOSTIC_FIGURES)},
                          ensure_ascii=False).replace('<', '\\u003c')
    html = html.replace('</head>', '<style>\n' + css + '\n</style>\n<style>\n' + audit_css + '\n</style>\n</head>', 1)
    html = html.replace('</body>', '<script>window.REPORT_V2_SNAPSHOT=' + snapshot + ';</script>\n<script>\n' + js + '\n</script>\n<script>\n' + audit_js + '\n</script>\n</body>', 1)
    html = html.replace('<title>Séries Temporais | Relatório técnico</title>', '<title>Séries Temporais | Relatório v2</title>', 1)
    html = html.replace("a.download='relatorio_series_temporais.html'", "a.download='relatorio_series_temporais_v2.html'", 1)
    destino = raiz / 'entrega' / 'relatorio_v2.html'
    destino.write_text(html, encoding='utf-8')
    return destino


if __name__ == '__main__':
    print(gerar(Path(__file__).resolve().parents[3]))
