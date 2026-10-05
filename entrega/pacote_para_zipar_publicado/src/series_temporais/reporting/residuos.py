"""Exportação reproduzível das previsões individuais do XGBoost."""

from pathlib import Path

import numpy as np
import pandas as pd


def salvar_residuos_nivel(predictions: pd.DataFrame, root: Path, base: int,
                         *, expected_rows: int, smoke: bool = False) -> Path:
    """Salva todas as previsões das Bases 1–4 sem modificar o quadro recebido."""
    if base not in (1, 2, 3, 4):
        raise ValueError("Use o exportador específico para a Base 5.")
    required = ["origin_time", "target_time", "y_true", "y_pred_xgb",
                "y_pred_persistencia", "residuo_xgb", "model_refit_origin",
                "training_target_cutoff"]
    missing = set(required).difference(predictions.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    frame = predictions.copy()
    if len(frame) != expected_rows or expected_rows <= 0:
        raise ValueError("Quantidade de previsões incompatível com o teste.")
    origins = pd.to_datetime(frame.origin_time)
    targets = pd.to_datetime(frame.target_time)
    cutoffs = pd.to_datetime(frame.training_target_cutoff)
    refits = pd.to_datetime(frame.model_refit_origin)
    if any(values.isna().any() for values in (origins, targets, cutoffs, refits)):
        raise ValueError("Datas ausentes.")
    if not origins.is_monotonic_increasing or origins.duplicated().any():
        raise ValueError("Origens fora de ordem ou duplicadas.")
    if not ((targets > origins) & (cutoffs <= refits) & (refits <= origins)).all():
        raise ValueError("Previsões sem causalidade temporal.")
    if not np.isfinite(frame[required[2:6]].to_numpy(dtype=float)).all():
        raise ValueError("Valores não finitos.")
    if not np.allclose(frame.residuo_xgb, frame.y_true - frame.y_pred_xgb):
        raise ValueError("Resíduos inconsistentes.")
    frame["erro_absoluto_xgb"] = frame.residuo_xgb.abs()
    frame["erro_quadratico_xgb"] = frame.residuo_xgb.pow(2)
    directory = Path(root) / "results" / "residuals"
    directory.mkdir(parents=True, exist_ok=True)
    suffix = "_smoke" if smoke else ""
    path = directory / f"base_{base:02d}_XGBoost{suffix}.csv"
    frame.to_csv(path, index=False, encoding="utf-8")
    return path


def plotar_residuos_temporais_xgboost(frame, base, *, frequency,
                                     expected_rows=None, expected_mae=None):
    """Figura do erro por data do alvo; lacunas quebram a linha, sem imputação."""
    import matplotlib.pyplot as plt

    if base not in (1, 2, 3, 4, 5):
        raise ValueError("Base XGBoost inválida.")
    if base == 5:
        origin, target = "DATE", "target_date"
        real, predicted, residual = "y_true_return", "y_pred_return_xgb", "residual_return_xgb"
    else:
        origin, target = "origin_time", "target_time"
        real, predicted, residual = "y_true", "y_pred_xgb", "residuo_xgb"
    required = [origin, target, real, predicted, residual,
                "model_refit_origin", "training_target_cutoff"]
    if not set(required).issubset(frame.columns):
        raise ValueError("Colunas incompletas para o gráfico de resíduos.")
    if frame.empty or (expected_rows is not None and len(frame) != expected_rows):
        raise ValueError("Quantidade de resíduos incompatível com a execução.")
    dates = {col: pd.to_datetime(frame[col], errors="raise")
             for col in (origin, target, "model_refit_origin", "training_target_cutoff")}
    if any(series.isna().any() for series in dates.values()):
        raise ValueError("Datas ausentes nos resíduos.")
    offset = pd.tseries.frequencies.to_offset(frequency)
    if (dates[origin].duplicated().any() or not dates[origin].is_monotonic_increasing
            or not dates[target].eq(dates[origin] + offset).all()
            or not dates["training_target_cutoff"].le(dates["model_refit_origin"]).all()
            or not dates["model_refit_origin"].le(dates[origin]).all()):
        raise ValueError("Contrato temporal inválido para os resíduos.")
    numbers = frame[[real, predicted, residual]].to_numpy(dtype=float)
    if not np.isfinite(numbers).all():
        raise ValueError("Resíduos ou previsões não finitos.")
    if not np.allclose(numbers[:, 2], numbers[:, 0] - numbers[:, 1]):
        raise ValueError("Resíduos inconsistentes com real menos previsto.")
    mae = float(np.abs(numbers[:, 2]).mean())
    if expected_mae is not None and not np.isclose(mae, expected_mae, rtol=1e-9, atol=1e-10):
        raise ValueError("MAE dos resíduos diverge do consolidado XGBoost.")
    values = pd.Series(numbers[:, 2], index=pd.DatetimeIndex(dates[target]))
    grid = pd.date_range(values.index.min(), values.index.max(), freq=offset)
    if len(values.index.difference(grid)):
        raise ValueError("Datas dos resíduos fora da grade declarada.")
    plotted = values.reindex(grid)  # NaN apenas para quebrar o traçado nas lacunas.
    labels = {1: "Close (unidade original)", 2: "traffic_volume (unidade original)",
              3: "PM2.5 (unidade original)", 4: "Temperatura (°C)",
              5: "Retorno logarítmico (adimensional)"}
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(plotted.index, plotted.to_numpy(), color="#0072B2", linewidth=.8,
            marker=".", markersize=2, label="Resíduo XGBoost: real − previsto")
    ax.axhline(0, color="#666666", linestyle="--", linewidth=1, label="Erro zero")
    ax.set(title=f"Base {base} — resíduos XGBoost fora da amostra ({len(values):,} previsões)",
           xlabel="Data do alvo", ylabel=labels[base])
    ax.grid(alpha=.25)
    ax.legend(loc="best")
    fig.tight_layout()
    audit = {"base_id": f"base_{base:02d}", "origens_avaliadas": len(values),
             "mae": mae, "frequencia": frequency,
             "inicio_alvo": str(values.index.min()), "fim_alvo": str(values.index.max()),
             "lacunas_no_tracado": int(plotted.isna().sum()), "residuo": "real - previsto"}
    return fig, audit


def grafico_residuos_xgboost(root, base, *, predictions=None, smoke=False):
    """Reproduz só a figura: CSV existente ou quadro em memória, sem estimador."""
    import hashlib
    import yaml

    root = Path(root)
    metadata = yaml.safe_load((root / f"data/base_{base:02d}/metadata.yaml").read_text(encoding="utf-8"))
    suffix = "_smoke" if smoke else ""
    path = root / f"results/residuals/base_{base:02d}_XGBoost{suffix}.csv"
    expected_rows, expected_mae = None, None
    if predictions is None:
        if not path.exists():
            raise FileNotFoundError(f"CSV de resíduos ausente: {path}. Recupere o vetor completo desta execução.")
        predictions = pd.read_csv(path)
        if not smoke:
            metrics = pd.read_csv(root / "results/metrics.csv")
            selected = metrics.loc[metrics.base_id.eq(f"base_{base:02d}") & metrics.modelo.eq("XGBoost")]
            if len(selected) != 1:
                raise ValueError("Registro XGBoost ausente ou duplicado no consolidado.")
            row = selected.iloc[0]
            if row.alvo != metadata["target"] or row.frequencia != metadata["frequency"]:
                raise ValueError("Alvo/frequência do consolidado divergem dos metadados.")
            expected_rows, expected_mae = int(row.origens_avaliadas), float(row.mae)
        source = {"fonte": str(path.relative_to(root)),
                  "csv_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    else:
        source = {"fonte": "quadro predictions em memória"}
    fig, audit = plotar_residuos_temporais_xgboost(
        predictions, base, frequency=metadata["frequency"],
        expected_rows=expected_rows, expected_mae=expected_mae)
    audit.update(source, modo="smoke" if smoke else "full", alvo=metadata["target"])
    if smoke:
        fig.axes[0].set_title(fig.axes[0].get_title() + " — TESTE REDUZIDO")
    return fig, audit


def salvar_residuos_base5(predictions: pd.DataFrame, root: Path, *,
                         smoke: bool = False, expected_rows: int = 586) -> Path:
    """Exporta o alvo canônico em retorno e sua conversão para preço."""
    required = ["DATE", "target_date", "price_t", "target_price_t_plus_1",
                "y_true_return", "y_pred_return_xgb", "y_pred_return_zero",
                "residual_return_xgb", "price_pred_xgb",
                "price_pred_persistencia", "residual_price_xgb",
                "target_has_new_quote", "price_was_carried",
                "model_refit_origin", "training_target_cutoff"]
    missing = set(required).difference(predictions.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    frame = predictions.copy()
    origins = pd.to_datetime(frame.DATE)
    targets = pd.to_datetime(frame.target_date)
    cutoffs = pd.to_datetime(frame.training_target_cutoff)
    refits = pd.to_datetime(frame.model_refit_origin)
    if any(values.isna().any() for values in (origins, targets, cutoffs, refits)):
        raise ValueError("Datas ausentes.")
    if not origins.is_monotonic_increasing or origins.duplicated().any():
        raise ValueError("Origens fora de ordem ou duplicadas.")
    if not ((targets > origins) & (cutoffs <= refits) & (refits <= origins)).all():
        raise ValueError("Previsões sem causalidade temporal.")
    numeric = required[2:13]
    if not np.isfinite(frame[numeric].to_numpy(dtype=float)).all():
        raise ValueError("Valores não finitos.")
    if not frame[["price_t", "target_price_t_plus_1", "price_pred_xgb", "price_pred_persistencia"]].gt(0).all().all():
        raise ValueError("Preços devem ser positivos.")
    if not frame[["target_has_new_quote", "price_was_carried"]].isin([0, 1]).all().all():
        raise ValueError("Indicadores de cobertura inválidos.")
    if not np.allclose(frame.price_pred_xgb, frame.price_t * np.exp(frame.y_pred_return_xgb)):
        raise ValueError("Conversão retorno–preço inconsistente.")
    if not np.allclose(frame.y_true_return, np.log(frame.target_price_t_plus_1 / frame.price_t)):
        raise ValueError("Retorno real inconsistente com os preços.")
    if not np.allclose(frame.y_pred_return_zero, 0) or not np.allclose(frame.price_pred_persistencia, frame.price_t):
        raise ValueError("Persistência inconsistente.")
    if not np.allclose(frame.residual_price_xgb, frame.target_price_t_plus_1 - frame.price_pred_xgb):
        raise ValueError("Resíduos inconsistentes.")
    if not np.allclose(frame.residual_return_xgb, frame.y_true_return - frame.y_pred_return_xgb):
        raise ValueError("Resíduos em retorno inconsistentes.")
    if expected_rows <= 0 or len(frame) != expected_rows:
        raise ValueError(f"Esperadas {expected_rows} linhas; obtidas {len(frame)}.")
    for scale in ("return", "price"):
        frame[f"absolute_error_{scale}_xgb"] = frame[f"residual_{scale}_xgb"].abs()
        frame[f"squared_error_{scale}_xgb"] = frame[f"residual_{scale}_xgb"].pow(2)
    directory = Path(root) / "results" / "residuals"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("base_05_XGBoost_smoke.csv" if smoke else "base_05_XGBoost.csv")
    frame.to_csv(path, index=False, encoding="utf-8")
    return path
