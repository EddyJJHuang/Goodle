from __future__ import annotations

from typing import Sequence

import numpy as np


def empirical_coverage_by_horizon(y_true: np.ndarray, q_lo: np.ndarray, q_hi: np.ndarray) -> np.ndarray:
    inside = (y_true >= q_lo) & (y_true <= q_hi)
    return inside.mean(axis=(0, 2))


def average_coverage(y_true: np.ndarray, q_lo: np.ndarray, q_hi: np.ndarray) -> float:
    return float(empirical_coverage_by_horizon(y_true, q_lo, q_hi).mean())


def mean_interval_width(q_lo: np.ndarray, q_hi: np.ndarray) -> float:
    return float(np.mean(q_hi - q_lo))


def winkler_score(y_true: np.ndarray, q_lo: np.ndarray, q_hi: np.ndarray, alpha: float = 0.1) -> float:
    width = q_hi - q_lo
    below = y_true < q_lo
    above = y_true > q_hi
    penalty = (2.0 / alpha) * ((q_lo - y_true) * below + (y_true - q_hi) * above)
    return float(np.mean(width + penalty))


def wis(y_true: np.ndarray, y_quantiles: np.ndarray, quantiles: Sequence[float]) -> float:
    """Simple weighted interval score approximation.

    Assumes a symmetric quantile set containing 0.5.
    """
    q = list(quantiles)
    if 0.5 not in q:
        raise ValueError("quantiles must include 0.5")
    median = y_quantiles[..., q.index(0.5)]
    score = np.abs(y_true - median)

    lower = [v for v in q if v < 0.5]
    for l in lower:
        u = 1.0 - l
        if u not in q:
            continue
        lo = y_quantiles[..., q.index(l)]
        hi = y_quantiles[..., q.index(u)]
        alpha = 2.0 * l
        width = hi - lo
        below = y_true < lo
        above = y_true > hi
        penalty = (2.0 / alpha) * ((lo - y_true) * below + (y_true - hi) * above)
        score = score + 0.5 * (width + penalty)

    return float(np.mean(score))


def joint_trajectory_coverage(y_true: np.ndarray, q_lo: np.ndarray, q_hi: np.ndarray) -> float:
    inside = (y_true >= q_lo) & (y_true <= q_hi)
    joint = np.all(inside, axis=(1, 2))
    return float(np.mean(joint))
