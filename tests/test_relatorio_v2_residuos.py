import json

import pytest

from series_temporais.reporting.gerar_relatorio_v2 import figuras_residuos_xgboost


def test_figuras_residuos_por_tag_independente_da_posicao(tmp_path):
    (tmp_path / 'notebooks').mkdir()
    for base in range(1, 6):
        cells = [{}] * base + [{'metadata': {'tags': ['residuos-temporais-xgboost']},
                                'outputs': [{'data': {'image/png': 'aW1hZ2U='}}]}]
        path = tmp_path / 'notebooks' / f'base_{base:02d}-grupo{base}_XGBoost.ipynb'
        path.write_text(json.dumps({'cells': cells}), encoding='utf-8')
    figures = figuras_residuos_xgboost(tmp_path)
    assert [f['base'] for f in figures] == [1, 2, 3, 4, 5]
    assert all(f'#cell-{base}' in f['source'] for base, f in enumerate(figures, 1))


def test_figuras_residuos_exigem_celula_identificada(tmp_path):
    (tmp_path / 'notebooks').mkdir()
    (tmp_path / 'notebooks' / 'base_01-grupo1_XGBoost.ipynb').write_text(
        json.dumps({'cells': [{}]}), encoding='utf-8')
    with pytest.raises(ValueError, match='Esperada uma célula'):
        figuras_residuos_xgboost(tmp_path)
