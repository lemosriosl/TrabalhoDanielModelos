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


def figuras_stl(raiz: Path) -> list[dict]:
    figures = []
    for base, (name, cell_index) in enumerate(STL_FIGURES, start=1):
        notebook = json.loads((raiz / 'notebooks' / name).read_text(encoding='utf-8'))
        output = next((item for item in notebook['cells'][cell_index].get('outputs', [])
                       if 'image/png' in item.get('data', {})), None)
        if output is None:
            raise ValueError(f'Figura STL ausente: {name} célula {cell_index}')
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
    findings = json.loads((raiz / 'results' / 'achados_auditoria.json').read_text(encoding='utf-8'))
    if len(metrics) != 5 or len({row['base_id'] for row in metrics}) != 5:
        raise ValueError('Esperadas cinco bases XGBoost no consolidado.')
    metrics.sort(key=lambda row: row['base_id'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=raiz, text=True).strip()
    snapshot = json.dumps({'commit': commit, 'metrics': metrics, 'individual': individual,
                           'diagnostics': diagnostics, 'findings': findings,
                           'stl_figures': figuras_stl(raiz)}, ensure_ascii=False).replace('<', '\\u003c')
    html = html.replace('</head>', '<style>\n' + css + '\n</style>\n<style>\n' + audit_css + '\n</style>\n</head>', 1)
    html = html.replace('</body>', '<script>window.REPORT_V2_SNAPSHOT=' + snapshot + ';</script>\n<script>\n' + js + '\n</script>\n<script>\n' + audit_js + '\n</script>\n</body>', 1)
    html = html.replace('<title>Séries Temporais | Relatório técnico</title>', '<title>Séries Temporais | Relatório v2</title>', 1)
    html = html.replace("a.download='relatorio_series_temporais.html'", "a.download='relatorio_series_temporais_v2.html'", 1)
    destino = raiz / 'entrega' / 'relatorio_v2.html'
    destino.write_text(html, encoding='utf-8')
    return destino


if __name__ == '__main__':
    print(gerar(Path(__file__).resolve().parents[3]))
