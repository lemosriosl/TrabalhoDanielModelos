"""Gera os notebooks SARIMAX das Bases 1 e 2 no padrão dos demais modelos."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def celula_base(base: int) -> str:
    if base == 1:
        return """BASE_DIR = ROOT / 'trabalho/bases/grupo1'
df = pd.read_csv(BASE_DIR / 'base1_limpa_preparada.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date').asfreq('D')
df['Open_lag1'] = df['Open'].shift(1)
df['High_lag1'] = df['High'].shift(1)
df['Low_lag1'] = df['Low'].shift(1)
df['Volume_lag1'] = np.log1p(df['Volume'].shift(1))
df = df.dropna()
TARGET = 'Close'
TEST_START = pd.Timestamp('2022-06-09')
SEASONAL_PERIOD = 7
EXOG_SETS = {
    'sem_exogenas': [],
    'ohlcv_defasado': ['Open_lag1', 'High_lag1', 'Low_lag1', 'Volume_lag1'],
}
ORDERS = [(1, 1, 1), (2, 1, 1), (1, 1, 2)]
SEASONAL_ORDERS = [(0, 0, 0, 0)]
LJUNG_LAGS = [7, 14, 30]
OUTPUT_PREFIX = 'sarimax_base1_pipeline'"""
    return """BASE_DIR = ROOT / 'trabalho/bases/grupo2'
df = pd.read_csv(BASE_DIR / 'base2_limpa_preparada.csv')
df['date_time'] = pd.to_datetime(df['date_time'])
df = df.set_index('date_time').asfreq('h')
df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
df['dow_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
df['dow_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)
df['is_holiday'] = (df['holiday'].notna() & df['holiday'].ne('None')).astype(int)
TARGET = 'traffic_volume'
TEST_START = pd.Timestamp('2017-10-26 18:00:00')
SEASONAL_PERIOD = 24
EXOG_SETS = {
    'sem_exogenas': [],
    'calendario': ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'is_holiday'],
}
ORDERS = [(1, 0, 1), (2, 0, 1), (1, 1, 1)]
SEASONAL_ORDERS = [(1, 0, 1, 24)]
LJUNG_LAGS = [24, 168]
OUTPUT_PREFIX = 'sarimax_base2_pipeline'"""


def gerar(base: int) -> None:
    nb = nbf.v4.new_notebook()
    nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.cells = [
        nbf.v4.new_markdown_cell(
            f"# Base {base} — Pipeline SARIMAX\n\n"
            "Adaptação da pipeline `docs/Pipes de exemplo/atividade_sarimax.ipynb`. "
            "A seleção ocorre somente no treino e compara SARIMA sem exógenas com SARIMAX. "
            "As exógenas usadas abaixo são conhecidas na origem ou defasadas para evitar vazamento."
        ),
        nbf.v4.new_code_cell(
            """from pathlib import Path
import json
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox

ROOT = Path.cwd()
while not (ROOT / 'pyproject.toml').exists():
    if ROOT == ROOT.parent:
        raise FileNotFoundError('Raiz do projeto não encontrada.')
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'src'))

from series_temporais.models.pipeline_sarimax import prever_referencia

plt.style.use('seaborn-v0_8-whitegrid')
pd.set_option('display.max_columns', 100)"""
        ),
        nbf.v4.new_markdown_cell("## 1. Dados, alvo, corte temporal e exógenas"),
        nbf.v4.new_code_cell(celula_base(base)),
        nbf.v4.new_code_cell(
            """train = df.loc[df.index < TEST_START].copy()
test = df.loc[df.index >= TEST_START].copy()
validation_start = train.dropna(subset=[TARGET]).index[int(train[TARGET].notna().sum() * 0.80)]
fit_train = train.loc[train.index < validation_start]
validation = train.loc[train.index >= validation_start]

display(pd.DataFrame({
    'conjunto': ['ajuste interno', 'validação interna', 'teste final'],
    'inicio': [fit_train.index.min(), validation.index.min(), test.index.min()],
    'fim': [fit_train.index.max(), validation.index.max(), test.index.max()],
    'alvos observados': [fit_train[TARGET].notna().sum(), validation[TARGET].notna().sum(), test[TARGET].notna().sum()],
}))"""
        ),
        nbf.v4.new_markdown_cell("## 2. Busca de candidatos no trecho de treino"),
        nbf.v4.new_code_cell(
            """linhas = []
for order in ORDERS:
    for seasonal_order in SEASONAL_ORDERS:
        for nome_exog, colunas in EXOG_SETS.items():
            x_fit = fit_train[colunas] if colunas else None
            x_val = validation[colunas] if colunas else None
            previsoes, registro = prever_referencia(
                fit_train[TARGET], validation[TARGET],
                order=order, seasonal_order=seasonal_order,
                treino_x=x_fit, futuro_x=x_val, maxiter=100,
            )
            linhas.append({
                'order': str(order), 'seasonal_order': str(seasonal_order),
                'exogenas': nome_exog, **registro,
            })

selecao = pd.DataFrame(linhas).sort_values(['MAE', 'BIC']).reset_index(drop=True)
display(selecao)
validos = selecao[selecao['convergiu']]
melhor = (validos if not validos.empty else selecao).iloc[0]
print('Configuração escolhida:')
display(melhor.to_frame('valor'))"""
        ),
        nbf.v4.new_markdown_cell("## 3. Ajuste final e previsão fora da amostra"),
        nbf.v4.new_code_cell(
            """import ast

order_final = ast.literal_eval(melhor['order'])
seasonal_final = ast.literal_eval(melhor['seasonal_order'])
colunas_finais = EXOG_SETS[melhor['exogenas']]
previsoes, registro_final = prever_referencia(
    train[TARGET], test[TARGET],
    order=order_final, seasonal_order=seasonal_final,
    treino_x=train[colunas_finais] if colunas_finais else None,
    futuro_x=test[colunas_finais] if colunas_finais else None,
    maxiter=100,
)

registro_final.update({
    'base': f'base{BASE_DIR.name[-1]}',
    'inicio_teste': str(TEST_START),
    'exogenas': colunas_finais,
    'fonte_pipeline': 'docs/Pipes de exemplo/atividade_sarimax.ipynb',
})
display(pd.Series(registro_final, name='valor').to_frame())

selecao.to_csv(BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_selecao.csv', index=False)
previsoes.to_csv(BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_previsoes.csv')
with (BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_registro.json').open('w', encoding='utf-8') as arquivo:
    json.dump(registro_final, arquivo, ensure_ascii=False, indent=2)"""
        ),
        nbf.v4.new_code_cell(
            """fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(previsoes.index, previsoes['y_true'], color='black', linewidth=1.2, label='Real')
ax.plot(previsoes.index, previsoes['y_pred_sarimax'], color='#e25c3e', linewidth=1.1, label='SARIMAX')
ax.set(title='SARIMAX — previsão versus valor real', ylabel=TARGET)
ax.legend()
plt.tight_layout()
plt.show()"""
        ),
        nbf.v4.new_markdown_cell("## 4. Diagnóstico dos resíduos"),
        nbf.v4.new_code_cell(
            """residuos = previsoes['residuo_sarimax'].dropna()
lag_acf = min(max(LJUNG_LAGS), len(residuos) // 4)
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
axes[0, 0].plot(residuos.index, residuos, linewidth=0.7)
axes[0, 0].axhline(0, color='black', linestyle='--')
axes[0, 0].set_title('Resíduos ao longo do tempo')
plot_acf(residuos, lags=lag_acf, ax=axes[0, 1], title='ACF dos resíduos')
stats.probplot(residuos, dist='norm', plot=axes[1, 0])
axes[1, 0].set_title('Q-Q Plot')
axes[1, 1].hist(residuos, bins=30, density=True, alpha=0.75)
axes[1, 1].set_title('Distribuição dos resíduos')
plt.tight_layout()
plt.show()

lags_validos = [lag for lag in LJUNG_LAGS if lag < len(residuos)]
ljung = acorr_ljungbox(residuos, lags=lags_validos, return_df=True)
ljung['rejeita_ruido_branco_5pct'] = ljung['lb_pvalue'] < 0.05
display(ljung)
ljung.to_csv(BASE_DIR / 'modelos' / f'{OUTPUT_PREFIX}_ljung_box.csv')"""
        ),
        nbf.v4.new_markdown_cell(
            "## 5. Leitura dos resultados\n\n"
            "- A configuração final é escolhida por MAE de validação e BIC, priorizando candidatos convergentes.\n"
            "- Os coeficientes das exógenas podem ser consultados em `resultado.params` durante uma execução detalhada.\n"
            "- `p < 0,05` no Ljung–Box indica autocorrelação residual e necessidade de revisão do modelo."
        ),
    ]
    destino = ROOT / "trabalho" / "bases" / f"grupo{base}" / "modelos" / f"grupo{base}_SARIMAX.ipynb"
    nbf.write(nb, destino)


if __name__ == "__main__":
    gerar(1)
    gerar(2)
