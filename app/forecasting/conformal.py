from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np


EPS = 1e-8


def _quantile_level(alpha: float, n: int) -> float:
    return min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)


@dataclass
class SplitConformalCalibrator:
    alpha: float = 0.1
    mode: str = "horizon"  # one of none/horizon/joint/both
    adaptive: bool = False
    rolling_window: int = 512
    ema_decay: float = 0.95
    horizon_correction_: np.ndarray | None = None
    joint_correction_: float | None = None
    _horizon_scores: deque[np.ndarray] = field(default_factory=deque, init=False)
    _joint_scores: deque[float] = field(default_factory=deque, init=False)

    def fit_horizon(self, q_lo: np.ndarray, q_hi: np.ndarray, y_true: np.ndarray) -> np.ndarray:
        scores = np.maximum(q_lo - y_true, y_true - q_hi)  # [N, H, D]
        horizon_scores = np.max(scores, axis=2)  # [N, H]
        n = horizon_scores.shape[0]
        level = _quantile_level(self.alpha, n)
        self.horizon_correction_ = np.quantile(horizon_scores, level, axis=0)
        return self.horizon_correction_

    def apply_horizon(self, q_lo: np.ndarray, q_hi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if self.horizon_correction_ is None:
            raise ValueError("horizon_correction_ is not fitted")
        corr = self.horizon_correction_[None, :, None]
        return q_lo - corr, q_hi + corr

    def fit_joint(self, mu: np.ndarray, scale: np.ndarray, y_true: np.ndarray) -> float:
        z = np.abs(y_true - mu) / (scale + EPS)
        scores = np.max(z.reshape(z.shape[0], -1), axis=1)
        n = scores.shape[0]
        level = _quantile_level(self.alpha, n)
        self.joint_correction_ = float(np.quantile(scores, level))
        return self.joint_correction_

    def apply_joint(self, mu: np.ndarray, scale: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if self.joint_correction_ is None:
            raise ValueError("joint_correction_ is not fitted")
        w = self.joint_correction_ * (scale + EPS)
        return mu - w, mu + w

    def update(
        self,
        q_lo: np.ndarray,
        q_hi: np.ndarray,
        y_true: np.ndarray,
        mu: np.ndarray | None = None,
        scale: np.ndarray | None = None,
    ) -> None:
        if not self.adaptive:
            return

        if self.mode in {"horizon", "both"}:
            scores = np.max(np.maximum(q_lo - y_true, y_true - q_hi), axis=2)
            self._horizon_scores.append(scores)
            while len(self._horizon_scores) > self.rolling_window:
                self._horizon_scores.popleft()
            stacked = np.concatenate(list(self._horizon_scores), axis=0)
            level = _quantile_level(self.alpha, stacked.shape[0])
            fresh = np.quantile(stacked, level, axis=0)
            if self.horizon_correction_ is None:
                self.horizon_correction_ = fresh
            else:
                self.horizon_correction_ = self.ema_decay * self.horizon_correction_ + (1 - self.ema_decay) * fresh

        if self.mode in {"joint", "both"} and mu is not None and scale is not None:
            z = np.abs(y_true - mu) / (scale + EPS)
            score = np.max(z.reshape(z.shape[0], -1), axis=1)
            self._joint_scores.extend(score.tolist())
            while len(self._joint_scores) > self.rolling_window:
                self._joint_scores.popleft()
            arr = np.asarray(self._joint_scores)
            level = _quantile_level(self.alpha, arr.shape[0])
            fresh = float(np.quantile(arr, level))
            if self.joint_correction_ is None:
                self.joint_correction_ = fresh
            else:
                self.joint_correction_ = self.ema_decay * self.joint_correction_ + (1 - self.ema_decay) * fresh

    def reset(self) -> None:
        self.horizon_correction_ = None
        self.joint_correction_ = None
        self._horizon_scores.clear()
        self._joint_scores.clear()

    def maybe_reset_on_coverage_drop(
        self,
        recent_coverage: float,
        target_coverage: float,
        tolerance: float = 0.08,
    ) -> bool:
        if recent_coverage < (target_coverage - tolerance):
            self.reset()
            return True
        return False
