"""Gera uma v2 independente, sem modificar o relatório v1 ou resultados."""
from pathlib import Path
import csv
import json
import subprocess


def gerar(raiz: Path) -> Path:
    fontes = raiz / 'docs' / 'relatorio'
    html = (fontes / 'modelo.html').read_text(encoding='utf-8')
    css = (fontes / 'v2.css').read_text(encoding='utf-8')
    js = (fontes / 'v2.js').read_text(encoding='utf-8')
    audit_css = (fontes / 'v2-audit.css').read_text(encoding='utf-8')
    audit_js = (fontes / 'v2-audit.js').read_text(encoding='utf-8')
    with (raiz / 'results' / 'metrics.csv').open(encoding='utf-8', newline='') as stream:
        metrics = [row for row in csv.DictReader(stream) if row['modelo'] == 'XGBoost']
    if len(metrics) != 5 or len({row['base_id'] for row in metrics}) != 5:
        raise ValueError('Esperadas cinco bases XGBoost no consolidado.')
    metrics.sort(key=lambda row: row['base_id'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=raiz, text=True).strip()
    snapshot = json.dumps({'commit': commit, 'metrics': metrics}, ensure_ascii=False).replace('<', '\\u003c')
    html = html.replace('</head>', '<style>\n' + css + '\n</style>\n<style>\n' + audit_css + '\n</style>\n</head>', 1)
    html = html.replace('</body>', '<script>window.REPORT_V2_SNAPSHOT=' + snapshot + ';</script>\n<script>\n' + js + '\n</script>\n<script>\n' + audit_js + '\n</script>\n</body>', 1)
    html = html.replace('<title>Séries Temporais | Relatório técnico</title>', '<title>Séries Temporais | Relatório v2</title>', 1)
    html = html.replace("a.download='relatorio_series_temporais.html'", "a.download='relatorio_series_temporais_v2.html'", 1)
    destino = raiz / 'entrega' / 'relatorio_v2.html'
    destino.write_text(html, encoding='utf-8')
    return destino


if __name__ == '__main__':
    print(gerar(Path(__file__).resolve().parents[3]))
