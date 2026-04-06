from __future__ import annotations

from typing import Sequence

import numpy as np


def point_loss(y_true: np.ndarray, y_pred: np.ndarray, metric: str = "mse") -> float:
    diff = y_pred - y_true
    if metric == "mse":
        return float(np.mean(diff**2))
    if metric == "mae":
        return float(np.mean(np.abs(diff)))
    raise ValueError("metric must be one of {'mse', 'mae'}")


def pinball_loss(y_true: np.ndarray, y_quantiles: np.ndarray, quantiles: Sequence[float]) -> float:
    q = np.asarray(list(quantiles), dtype=np.float64)
    y = y_true[..., None]
    e = y - y_quantiles
    loss = np.maximum(q * e, (q - 1.0) * e)
    return float(np.mean(loss))


def quantile_crossing_penalty(y_quantiles: np.ndarray, margin: float = 0.0) -> float:
    """Penalize violations q_i <= q_j for i < j."""
    if y_quantiles.shape[-1] < 2:
        return 0.0
    left = y_quantiles[..., :-1]
    right = y_quantiles[..., 1:]
    violation = left - right + margin
    return float(np.mean(np.maximum(0.0, violation)))


def horizon_smoothness_loss(
    y_quantiles: np.ndarray,
    quantiles: Sequence[float],
    lower_q: float = 0.05,
    upper_q: float = 0.95,
) -> float:
    q = list(float(v) for v in quantiles)
    lo_idx = q.index(lower_q)
    hi_idx = q.index(upper_q)
    width = y_quantiles[..., hi_idx] - y_quantiles[..., lo_idx]
    if width.shape[1] <= 1:
        return 0.0
    delta = width[:, 1:, :] - width[:, :-1, :]
    return float(np.mean(delta**2))


def trajectory_consistency_loss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Lightweight batch-level distribution alignment term.

    Uses distance-matrix alignment between true and predicted trajectories.
    """
    flat_true = y_true.reshape(y_true.shape[0], -1)
    flat_pred = y_pred.reshape(y_pred.shape[0], -1)

    true_d = np.linalg.norm(flat_true[:, None, :] - flat_true[None, :, :], axis=-1)
    pred_d = np.linalg.norm(flat_pred[:, None, :] - flat_pred[None, :, :], axis=-1)
    return float(np.mean(np.abs(true_d - pred_d)))
