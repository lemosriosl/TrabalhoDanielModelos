"""Avaliação walk-forward causal compartilhada pelos modelos."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
import pandas as pd


def _validate_frames(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    origin_col: str,
    target_time_col: str,
    target_col: str,
    feature_cols: Sequence[str] = (),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {origin_col, target_time_col, target_col, *feature_cols}
    for name, frame in (("train", train), ("test", test)):
        missing = sorted(required.difference(frame.columns))
        if missing:
            raise KeyError(f"{name} não contém as colunas obrigatórias: {missing}")
        if frame.empty:
            raise ValueError(f"{name} não pode ser vazio.")

    train = train.copy()
    test = test.copy()
    for frame in (train, test):
        frame[origin_col] = pd.to_datetime(frame[origin_col], errors="raise")
        frame[target_time_col] = pd.to_datetime(frame[target_time_col], errors="raise")
        if not frame[origin_col].is_monotonic_increasing:
            raise ValueError("As origens devem estar em ordem temporal crescente.")
        if not frame[target_time_col].gt(frame[origin_col]).all():
            raise ValueError("Cada alvo deve ser posterior à sua origem.")
    if not train[target_time_col].le(test[origin_col].min()).all():
        raise ValueError("O treino contém alvo que alcança a primeira origem de teste.")
    return train.reset_index(drop=True), test.reset_index(drop=True)


def walk_forward_refit(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    origin_col: str,
    target_time_col: str,
    target_col: str,
    feature_cols: Sequence[str],
    estimator_factory: Callable[[], Any],
    refit_every: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reajusta periodicamente e prevê um passo com as features de cada origem.

    ``estimator_factory`` deve devolver um estimador novo com ``fit`` e
    ``predict``. Os hiperparâmetros pertencem à fábrica e, portanto, precisam
    ser definidos antes desta função ser chamada.
    """

    if isinstance(refit_every, bool) or not isinstance(refit_every, (int, np.integer)) or refit_every < 1:
        raise ValueError("refit_every deve ser um inteiro positivo.")
    train, test = _validate_frames(
        train,
        test,
        origin_col=origin_col,
        target_time_col=target_time_col,
        target_col=target_col,
        feature_cols=feature_cols,
    )
    predictions: list[dict[str, Any]] = []
    fits: list[dict[str, Any]] = []

    for position, (_, row) in enumerate(test.iterrows()):
        origin = row[origin_col]
        if position % refit_every == 0:
            revealed = test.loc[test[target_time_col] <= origin]
            history = pd.concat([train, revealed], ignore_index=True)
            cutoff = history[target_time_col].max()
            if not cutoff <= origin:
                raise AssertionError("O histórico contém alvo posterior à origem da previsão.")
            estimator = estimator_factory()
            estimator.fit(history.loc[:, feature_cols], history[target_col])
            refit_origin = origin
            fits.append({
                "model_refit_origin": origin,
                "training_target_cutoff": cutoff,
                "training_rows": len(history),
                "test_position": position,
            })
        value = float(np.asarray(estimator.predict(row.loc[feature_cols].to_frame().T))[0])
        if not np.isfinite(value):
            raise ValueError("A previsão deve ser finita.")

        predictions.append(
            {
                "origin_time": origin,
                "target_time": row[target_time_col],
                "y_true": float(row[target_col]),
                "y_pred": value,
                "model_refit_origin": refit_origin,
                "training_target_cutoff": cutoff,
            }
        )

    prediction_frame = pd.DataFrame(predictions)
    validate_prediction_frame(prediction_frame)
    return prediction_frame, pd.DataFrame(fits)


def walk_forward_callback(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    origin_col: str,
    target_time_col: str,
    target_col: str,
    predict_one: Callable[[pd.DataFrame, pd.Series], float],
) -> pd.DataFrame:
    """Executa walk-forward para modelos com atualização própria de estado.

    A função ``predict_one`` recebe somente o histórico revelado e a linha da
    origem atual; ela deve retornar a previsão de um passo.
    """

    train, test = _validate_frames(
        train,
        test,
        origin_col=origin_col,
        target_time_col=target_time_col,
        target_col=target_col,
    )
    rows: list[dict[str, Any]] = []
    for _, row in test.iterrows():
        origin = row[origin_col]
        history = pd.concat([train, test.loc[test[target_time_col] <= origin]], ignore_index=True)
        cutoff = history[target_time_col].max()
        value = float(predict_one(history, row))
        rows.append(
            {
                "origin_time": origin,
                "target_time": row[target_time_col],
                "y_true": float(row[target_col]),
                "y_pred": value,
                "training_target_cutoff": cutoff,
            }
        )
    frame = pd.DataFrame(rows)
    validate_prediction_frame(frame)
    return frame


def validate_prediction_frame(predictions: pd.DataFrame) -> None:
    """Garante o contrato causal e de horizonte único das previsões."""

    required = {"origin_time", "target_time", "y_true", "y_pred", "training_target_cutoff"}
    missing = sorted(required.difference(predictions.columns))
    if missing:
        raise KeyError(f"Previsões sem colunas obrigatórias: {missing}")
    if predictions.empty:
        raise ValueError("Não há previsões para avaliar.")
    frame = predictions.copy()
    for column in ("origin_time", "target_time", "training_target_cutoff"):
        frame[column] = pd.to_datetime(frame[column], errors="raise")
    if not frame.origin_time.is_monotonic_increasing:
        raise ValueError("As origens das previsões devem estar ordenadas.")
    if frame.origin_time.duplicated().any():
        raise ValueError("Cada origem deve ter exatamente uma previsão.")
    if not frame.target_time.gt(frame.origin_time).all():
        raise ValueError("A previsão não possui horizonte positivo.")
    if not frame.training_target_cutoff.le(frame.origin_time).all():
        raise ValueError("Há informação futura no histórico de uma previsão.")
    if not np.isfinite(frame[["y_true", "y_pred"]].to_numpy(dtype=float)).all():
        raise ValueError("Valores reais e previstos devem ser finitos.")


def validate_prediction_contract(
    predictions: pd.DataFrame,
    expected_test: pd.DataFrame,
    *,
    expected_origin_col: str = "DATE",
    expected_target_time_col: str = "target_date",
    expected_target_col: str,
) -> None:
    """Confirma que um modelo avaliou exatamente as origens e o alvo canônicos."""

    validate_prediction_frame(predictions)
    required = {expected_origin_col, expected_target_time_col, expected_target_col}
    missing = sorted(required.difference(expected_test.columns))
    if missing:
        raise KeyError(f"Teste canônico sem colunas obrigatórias: {missing}")
    if len(predictions) != len(expected_test):
        raise ValueError("O modelo não produziu uma previsão para cada origem canônica.")

    origins = pd.to_datetime(predictions["origin_time"], errors="raise").reset_index(drop=True)
    targets = pd.to_datetime(predictions["target_time"], errors="raise").reset_index(drop=True)
    expected_origins = pd.to_datetime(
        expected_test[expected_origin_col], errors="raise"
    ).reset_index(drop=True)
    expected_targets = pd.to_datetime(
        expected_test[expected_target_time_col], errors="raise"
    ).reset_index(drop=True)
    if not origins.equals(expected_origins):
        raise ValueError("As origens previstas divergem do teste canônico.")
    if not targets.equals(expected_targets):
        raise ValueError("Os instantes-alvo divergem do teste canônico.")
    if not np.allclose(
        predictions["y_true"].to_numpy(dtype=float),
        expected_test[expected_target_col].to_numpy(dtype=float),
        equal_nan=False,
    ):
        raise ValueError("Os valores reais divergem do alvo canônico.")
