from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


EPS = 1e-8


def softplus(x: np.ndarray) -> np.ndarray:
    # Stable softplus implementation.
    return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0.0)


@dataclass
class QuantileLayout:
    quantiles: list[float]
    median_idx: int
    lower_qs_desc: list[float]
    upper_qs_asc: list[float]

    @classmethod
    def build(cls, quantiles: Sequence[float]) -> "QuantileLayout":
        q = sorted(float(v) for v in quantiles)
        if not q:
            raise ValueError("quantiles must be non-empty")
        if any(v <= 0.0 or v >= 1.0 for v in q):
            raise ValueError("all quantiles must be in (0,1)")
        if 0.5 not in q:
            q.append(0.5)
            q = sorted(q)
        median_idx = q.index(0.5)
        lower_qs_desc = sorted([v for v in q if v < 0.5], reverse=True)
        upper_qs_asc = sorted([v for v in q if v > 0.5])
        return cls(q, median_idx, lower_qs_desc, upper_qs_asc)


class MonotonicQuantileHead:
    """Build crossing-resistant quantiles around a median/point forecast.

    Inputs are point forecast plus raw lower/upper increments. Increments are
    transformed with softplus and cumulatively summed away from the median.
    """

    def __init__(self, quantiles: Sequence[float]):
        self.layout = QuantileLayout.build(quantiles)

    @property
    def quantiles(self) -> list[float]:
        return self.layout.quantiles

    def build(
        self,
        median: np.ndarray,
        raw_lower_increments: np.ndarray | None = None,
        raw_upper_increments: np.ndarray | None = None,
    ) -> np.ndarray:
        """Construct ordered quantiles.

        Args:
            median: [B, H, D]
            raw_lower_increments: [B, H, D, L] in nearest-to-median order.
            raw_upper_increments: [B, H, D, U] in nearest-to-median order.
        Returns:
            quantiles: [B, H, D, Q]
        """
        if median.ndim != 3:
            raise ValueError("median must have shape [B, H, D]")

        b, h, d = median.shape
        q_out = np.repeat(median[..., None], len(self.layout.quantiles), axis=-1)

        n_lower = len(self.layout.lower_qs_desc)
        n_upper = len(self.layout.upper_qs_asc)

        if n_lower:
            if raw_lower_increments is None:
                raw_lower_increments = np.zeros((b, h, d, n_lower), dtype=median.dtype)
            if raw_lower_increments.shape != (b, h, d, n_lower):
                raise ValueError(
                    f"raw_lower_increments must be {(b, h, d, n_lower)}, got {raw_lower_increments.shape}"
                )
            lower_inc = softplus(raw_lower_increments) + EPS
            lower_offsets = np.cumsum(lower_inc, axis=-1)
            for idx, q in enumerate(self.layout.lower_qs_desc):
                q_out[..., self.layout.quantiles.index(q)] = median - lower_offsets[..., idx]

        if n_upper:
            if raw_upper_increments is None:
                raw_upper_increments = np.zeros((b, h, d, n_upper), dtype=median.dtype)
            if raw_upper_increments.shape != (b, h, d, n_upper):
                raise ValueError(
                    f"raw_upper_increments must be {(b, h, d, n_upper)}, got {raw_upper_increments.shape}"
                )
            upper_inc = softplus(raw_upper_increments) + EPS
            upper_offsets = np.cumsum(upper_inc, axis=-1)
            for idx, q in enumerate(self.layout.upper_qs_asc):
                q_out[..., self.layout.quantiles.index(q)] = median + upper_offsets[..., idx]

        return q_out

    def select(self, quantile_tensor: np.ndarray, q: float) -> np.ndarray:
        idx = self.layout.quantiles.index(float(q))
        return quantile_tensor[..., idx]
