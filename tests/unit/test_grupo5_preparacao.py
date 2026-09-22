import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'trabalho/bases/grupo5/eda_preparacao_base_5_ouro.ipynb'


def test_grupo5_new_sem_vazamento_no_corte_exploratorio(monkeypatch):
    monkeypatch.chdir(ROOT)
    cells = json.loads(NOTEBOOK.read_text(encoding='utf-8'))['cells']
    scope = {'display': lambda *args: None}
    for index in (1, 3, 5, 9, 11):
        exec(compile(''.join(cells[index]['source']), f'cell_{index}', 'exec'), scope)

    assert len(scope['df']) == 12009
    assert scope['df'].VALUE.isna().sum() == 368
    assert len(scope['model_df']) == 11618
    assert {'TARGET_UP', 'IS_HOLIDAY', 'target_gap_days'}.isdisjoint(scope['feature_columns'])
    assert scope['train_df'].target_date.max() < scope['test_df'].DATE.min()
    assert scope['model_df'].target_date.gt(scope['model_df'].DATE).all()
