"""Gera notebooks de preparação e EDA/STL das Bases 1 e 2.

Execute a partir da raiz do repositório e, em seguida, rode o nbconvert para
armazenar os gráficos e tabelas como saídas reproduzíveis dos notebooks.
"""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def _notebook(cells: list) -> nbf.NotebookNode:
    return nbf.v4.new_notebook(
        cells=cells,
        metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    )


def _code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source.strip())


def _md(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source.strip())


def gerar_limpeza_base1() -> nbf.NotebookNode:
    return _notebook([
        _md("""# Base 1 — Limpeza e preparação\n\nA base original é mantida intacta. A separação é cronológica em 70% treino e 30% teste, sem embaralhamento."""),
        _code("""
from pathlib import Path
import sys
import pandas as pd
from IPython.display import display

ROOT = Path.cwd()
while not (ROOT / 'pyproject.toml').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'src'))
from series_temporais.data.preparacao_bases_1_2 import preparar_base1, salvar_preparacao

BASE_DIR = ROOT / 'trabalho/bases/grupo1'
clean, train, test, audit = preparar_base1(BASE_DIR / 'grupo1.csv')
salvar_preparacao(BASE_DIR, 'base1', clean, train, test)
display(pd.Series(audit, name='valor').to_frame())
display(pd.DataFrame({'conjunto': ['treino', 'teste'], 'linhas': [len(train), len(test)], 'inicio': [train.Date.min(), test.Date.min()], 'fim': [train.Date.max(), test.Date.max()]}))
"""),
        _md("""## Decisões\n\n- Datas já estão ordenadas, sem duplicidades e sem lacunas diárias.\n- Não há imputação nem remoção automática de picos.\n- `Adj Close` é idêntica a `Close`; é preservada no artefato preparado, mas não deve entrar como feature por duplicar o alvo.\n- O corte é estrutural; o walk-forward será definido posteriormente pelo grupo."""),
    ])


def gerar_limpeza_base2() -> nbf.NotebookNode:
    return _notebook([
        _md("""# Base 2 — Limpeza e preparação\n\nA base original é mantida intacta. A consolidação de timestamps repetidos segue a proposta ADR-003 e a separação é cronológica em 80% treino e 20% teste."""),
        _code("""
from pathlib import Path
import sys
import pandas as pd
from IPython.display import display

ROOT = Path.cwd()
while not (ROOT / 'pyproject.toml').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'src'))
from series_temporais.data.preparacao_bases_1_2 import preparar_base2, salvar_preparacao

BASE_DIR = ROOT / 'trabalho/bases/grupo2'
clean, train, test, audit = preparar_base2(BASE_DIR / 'grupo2.csv')
salvar_preparacao(BASE_DIR, 'base2', clean, train, test)
display(pd.Series(audit, name='valor').to_frame())
display(pd.DataFrame({'conjunto': ['treino', 'teste'], 'linhas': [len(train), len(test)], 'inicio': [train.date_time.min(), test.date_time.min()], 'fim': [train.date_time.max(), test.date_time.max()]}))
"""),
        _md("""## Decisões\n\n- A string `None` em `holiday` representa ausência de feriado, não valor nulo.\n- Para um mesmo horário, campos numéricos são agregados pela média e categorias pela moda determinística.\n- A grade de uma hora preserva lacunas como `NaN`; o alvo não é interpolado.\n- A proposta precisa de revisão do grupo antes de ser marcada como aceita no ADR-003."""),
    ])


COMMON = """
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
from statsmodels.tsa.seasonal import STL
from statsmodels.graphics.tsaplots import plot_acf

ROOT = Path.cwd()
while not (ROOT / 'pyproject.toml').exists():
    ROOT = ROOT.parent
sns.set_theme(style='whitegrid')

def seasonal_strength(result):
    denom = np.nanvar(result.seasonal + result.resid)
    return np.nan if denom == 0 else max(0.0, 1 - np.nanvar(result.resid) / denom)

def trend_strength(result):
    denom = np.nanvar(result.trend + result.resid)
    return np.nan if denom == 0 else max(0.0, 1 - np.nanvar(result.resid) / denom)
"""


def gerar_eda_base1() -> nbf.NotebookNode:
    return _notebook([
        _md("""# Base 1 — Gráficos exploratórios e STL\n\nA exploração usa os dados preparados. A STL é aplicada somente ao trecho de treino, sem consultar o teste."""),
        _code(COMMON + """
BASE_DIR = ROOT / 'trabalho/bases/grupo1'
df = pd.read_csv(BASE_DIR / 'base1_limpa_preparada.csv', parse_dates=['Date'])
train = pd.read_csv(BASE_DIR / 'base1_treino_preparada.csv', parse_dates=['Date'])
df['retorno_pct'] = df['Close'].pct_change() * 100
display(df[['Close', 'Volume', 'retorno_pct']].describe().T)
"""),
        _code("""
fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=False)
axes[0].plot(df['Date'], df['Close'], lw=.8, color='#e69f00')
axes[0].set(title='Bitcoin — preço de fechamento diário', ylabel='USD/BTC')
recent = df.tail(180)
axes[1].plot(recent['Date'], recent['Close'], lw=1, color='#0072b2')
axes[1].set(title='Bitcoin — últimos 180 dias da base', ylabel='USD/BTC', xlabel='Data')
plt.tight_layout(); plt.show()

fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))
sns.histplot(df['retorno_pct'].dropna(), bins=60, ax=axes[0], color='#009e73')
axes[0].set(title='Distribuição dos retornos diários', xlabel='Retorno (%)')
axes[1].plot(df['Date'], np.log1p(df['Volume']), lw=.7, color='#cc79a7')
axes[1].set(title='Volume diário em escala logarítmica', xlabel='Data', ylabel='log(1 + volume)')
plt.tight_layout(); plt.show()
"""),
        _code("""
weekday = df.assign(dia=df['Date'].dt.day_name()).groupby('dia')['retorno_pct'].mean().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))
weekday.plot.bar(ax=axes[0], color='#56b4e9')
axes[0].set(title='Retorno médio por dia da semana', xlabel='', ylabel='Retorno médio (%)')
plot_acf(df['retorno_pct'].dropna(), lags=40, ax=axes[1])
axes[1].set_title('ACF dos retornos diários')
plt.tight_layout(); plt.show()
"""),
        _code("""
serie = train.set_index('Date')['Close'].asfreq('D')
results = {}
for label, period in {'semanal (7)': 7, 'anual (365)': 365}.items():
    result = STL(serie, period=period, robust=True).fit()
    results[label] = result
    result.plot().set_size_inches(15, 8)
    plt.suptitle(f'Base 1 — STL {label}', y=1.02)
    plt.tight_layout(); plt.show()
display(pd.DataFrame([{'período': k, 'observações/ciclo': 7 if '7' in k else 365, 'força sazonal': seasonal_strength(v), 'força tendência': trend_strength(v)} for k, v in results.items()]).round(4))
"""),
        _md("""## Interpretação\n\nA força sazonal é calculada por `max(0, 1 - Var(resíduo) / Var(sazonal + resíduo))`. Os períodos de 7 e 365 dias são candidatos exploratórios; sua escolha para um modelo depende também da validação walk-forward."""),
    ])


def gerar_eda_base2() -> nbf.NotebookNode:
    return _notebook([
        _md("""# Base 2 — Gráficos exploratórios e STL\n\nA exploração usa a grade horária preparada. Para não interpolar o alvo, a STL é calculada no maior trecho contínuo observado dentro do treino."""),
        _code(COMMON + """
BASE_DIR = ROOT / 'trabalho/bases/grupo2'
df = pd.read_csv(BASE_DIR / 'base2_limpa_preparada.csv', parse_dates=['date_time'])
train = pd.read_csv(BASE_DIR / 'base2_treino_preparada.csv', parse_dates=['date_time'])
df['hora'] = df['date_time'].dt.hour
df['dia_semana'] = df['date_time'].dt.day_name()
df['mes'] = df['date_time'].dt.month
display(df['traffic_volume'].describe().to_frame('traffic_volume'))
print('Lacunas horárias no artefato preparado:', int(df['traffic_volume'].isna().sum()))
"""),
        _code("""
fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=False)
axes[0].plot(df['date_time'], df['traffic_volume'], lw=.35, color='#0072b2')
axes[0].set(title='I-94 — volume de tráfego horário', ylabel='Veículos/hora')
recent = df.dropna(subset=['traffic_volume']).tail(24 * 14)
axes[1].plot(recent['date_time'], recent['traffic_volume'], lw=.8, color='#e69f00')
axes[1].set(title='I-94 — últimas duas semanas observadas', ylabel='Veículos/hora', xlabel='Data')
plt.tight_layout(); plt.show()
"""),
        _code("""
fig, axes = plt.subplots(1, 3, figsize=(18, 4.5))
df.groupby('hora')['traffic_volume'].mean().plot(ax=axes[0], marker='o', color='#009e73')
axes[0].set(title='Média por hora', xlabel='Hora', ylabel='Veículos/hora')
order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
df.groupby('dia_semana')['traffic_volume'].mean().reindex(order).plot.bar(ax=axes[1], color='#56b4e9')
axes[1].set(title='Média por dia da semana', xlabel='', ylabel='Veículos/hora')
sns.histplot(df['traffic_volume'].dropna(), bins=60, ax=axes[2], color='#cc79a7')
axes[2].set(title='Distribuição do volume', xlabel='Veículos/hora')
plt.tight_layout(); plt.show()

fig, ax = plt.subplots(figsize=(15, 2.5))
missing = df['traffic_volume'].isna()
ax.scatter(df.loc[missing, 'date_time'], np.ones(missing.sum()), s=3, color='#d55e00')
ax.set(title='Lacunas do alvo após regularização', xlabel='Data', yticks=[])
plt.tight_layout(); plt.show()
"""),
        _code("""
train_start, train_end = train['date_time'].min(), train['date_time'].max()
serie_treino = df.set_index('date_time').loc[train_start:train_end, 'traffic_volume'].asfreq('h')
observada = serie_treino.notna()
blocks = observada.ne(observada.shift()).cumsum()
sizes = observada.groupby(blocks).agg(['first', 'size'])
valid_blocks = sizes[sizes['first']]
block_id = valid_blocks['size'].idxmax()
maior_trecho = serie_treino[blocks.eq(block_id)]
print('Maior trecho horário contínuo no treino:', len(maior_trecho), 'observações')
if len(maior_trecho) < 2 * 168:
    raise ValueError('Trecho contínuo insuficiente para STL diária e semanal.')

results = {}
for label, period in {'diária (24)': 24, 'semanal (168)': 168}.items():
    result = STL(maior_trecho, period=period, robust=True).fit()
    results[label] = result
    result.plot().set_size_inches(15, 8)
    plt.suptitle(f'Base 2 — STL {label}', y=1.02)
    plt.tight_layout(); plt.show()
display(pd.DataFrame([{'período': k, 'observações/ciclo': 24 if '24' in k else 168, 'força sazonal': seasonal_strength(v), 'força tendência': trend_strength(v)} for k, v in results.items()]).round(4))
"""),
        _md("""## Interpretação\n\nA STL é exploratória e utiliza somente o maior trecho contínuo de treino; não houve interpolação do alvo. Os períodos de 24 e 168 horas são candidatos para validação posterior, não uma decisão final de modelagem."""),
    ])


def write_notebook(path: Path, notebook: nbf.NotebookNode) -> None:
    path.write_text(nbf.writes(notebook), encoding='utf-8')


if __name__ == '__main__':
    write_notebook(ROOT / 'trabalho/bases/grupo1/limpeza_preparacao_base1.ipynb', gerar_limpeza_base1())
    write_notebook(ROOT / 'trabalho/bases/grupo2/limpeza_preparacao_base2.ipynb', gerar_limpeza_base2())
    write_notebook(ROOT / 'trabalho/bases/grupo1/graficos_exploratorios_stl_sazonalidade_base1.ipynb', gerar_eda_base1())
    write_notebook(ROOT / 'trabalho/bases/grupo2/graficos_exploratorios_stl_sazonalidade_base2.ipynb', gerar_eda_base2())
