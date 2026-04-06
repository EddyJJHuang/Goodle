from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np

from .conformal import SplitConformalCalibrator
from .losses import (
    horizon_smoothness_loss,
    pinball_loss,
    point_loss,
    quantile_crossing_penalty,
    trajectory_consistency_loss,
)
from .metrics import (
    average_coverage,
    joint_trajectory_coverage,
    mean_interval_width,
    winkler_score,
)
from .quantile import MonotonicQuantileHead


Array = np.ndarray


@dataclass
class ForecastConfig:
    pred_len: int = 96
    use_quantile_head: bool = False
    quantiles: list[float] = field(default_factory=lambda: [0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95])
    use_conformal: bool = False
    conformal_mode: str = "none"  # none|horizon|joint|both
    adaptive_conformal: bool = False
    conformal_alpha: float = 0.1
    use_crossing_penalty: bool = False
    use_smoothness_loss: bool = False
    use_joint_regularizer: bool = False

    point_loss_type: str = "mse"
    lambda_pinball: float = 1.0
    lambda_crossing: float = 0.1
    lambda_smoothness: float = 0.05
    lambda_joint: float = 0.02


class ForecastPipeline:
    """Backward-compatible wrapper that upgrades point forecasters.

    `backbone` should be a callable returning [B,H,D] point forecasts.
    """

    def __init__(self, backbone: Callable[[Array], Array], config: ForecastConfig):
        self.backbone = backbone
        self.config = config
        self.quantile_head = MonotonicQuantileHead(config.quantiles)
        self.calibrator: SplitConformalCalibrator | None = None
        if config.use_conformal and config.conformal_mode != "none":
            self.calibrator = SplitConformalCalibrator(
                alpha=config.conformal_alpha,
                mode=config.conformal_mode,
                adaptive=config.adaptive_conformal,
            )

    def predict(
        self,
        x: Array,
        raw_lower_increments: Array | None = None,
        raw_upper_increments: Array | None = None,
    ) -> dict[str, Array]:
        point = self.backbone(x)
        out: dict[str, Array] = {"point": point}

        if self.config.use_quantile_head:
            q_pred = self.quantile_head.build(point, raw_lower_increments, raw_upper_increments)
            out["quantiles"] = q_pred
        return out

    def training_loss(self, y_true: Array, outputs: dict[str, Array]) -> dict[str, float]:
        losses: dict[str, float] = {}
        point = outputs["point"]
        losses["point"] = point_loss(y_true, point, self.config.point_loss_type)
        total = losses["point"]

        if self.config.use_quantile_head and "quantiles" in outputs:
            q_pred = outputs["quantiles"]
            losses["pinball"] = pinball_loss(y_true, q_pred, self.quantile_head.quantiles)
            total += self.config.lambda_pinball * losses["pinball"]

            if self.config.use_crossing_penalty:
                losses["crossing"] = quantile_crossing_penalty(q_pred)
                total += self.config.lambda_crossing * losses["crossing"]

            if self.config.use_smoothness_loss:
                losses["smoothness"] = horizon_smoothness_loss(q_pred, self.quantile_head.quantiles)
                total += self.config.lambda_smoothness * losses["smoothness"]

        if self.config.use_joint_regularizer:
            losses["joint_consistency"] = trajectory_consistency_loss(y_true, point)
            total += self.config.lambda_joint * losses["joint_consistency"]

        losses["total"] = total
        return losses

    def fit_conformal(self, y_true: Array, outputs: dict[str, Array], lower_q: float = 0.05, upper_q: float = 0.95) -> None:
        if self.calibrator is None or "quantiles" not in outputs:
            return
        q_pred = outputs["quantiles"]
        q = self.quantile_head.quantiles

        q_lo = q_pred[..., q.index(lower_q)]
        q_hi = q_pred[..., q.index(upper_q)]
        self.calibrator.fit_horizon(q_lo, q_hi, y_true)

        if self.config.conformal_mode in {"joint", "both"}:
            mu = outputs["point"]
            scale = np.maximum((q_hi - q_lo) / 2.0, 1e-6)
            self.calibrator.fit_joint(mu, scale, y_true)

    def apply_conformal(self, outputs: dict[str, Array], lower_q: float = 0.05, upper_q: float = 0.95) -> dict[str, Array]:
        if self.calibrator is None or "quantiles" not in outputs:
            return outputs
        out = dict(outputs)
        q_pred = outputs["quantiles"].copy()
        q = self.quantile_head.quantiles

        lo_idx, hi_idx = q.index(lower_q), q.index(upper_q)
        q_lo, q_hi = q_pred[..., lo_idx], q_pred[..., hi_idx]

        if self.config.conformal_mode in {"horizon", "both"}:
            q_lo, q_hi = self.calibrator.apply_horizon(q_lo, q_hi)

        if self.config.conformal_mode in {"joint", "both"}:
            mu = outputs["point"]
            scale = np.maximum((q_hi - q_lo) / 2.0, 1e-6)
            q_lo, q_hi = self.calibrator.apply_joint(mu, scale)

        q_pred[..., lo_idx] = q_lo
        q_pred[..., hi_idx] = q_hi
        out["quantiles"] = q_pred
        out["interval_low"] = q_lo
        out["interval_high"] = q_hi
        return out

    def probabilistic_metrics(self, y_true: Array, outputs: dict[str, Array], alpha: float | None = None) -> dict[str, float]:
        if "interval_low" not in outputs or "interval_high" not in outputs:
            return {}
        alpha = self.config.conformal_alpha if alpha is None else alpha
        lo, hi = outputs["interval_low"], outputs["interval_high"]
        return {
            "avg_coverage": average_coverage(y_true, lo, hi),
            "mean_interval_width": mean_interval_width(lo, hi),
            "winkler": winkler_score(y_true, lo, hi, alpha=alpha),
            "joint_trajectory_coverage": joint_trajectory_coverage(y_true, lo, hi),
        }
