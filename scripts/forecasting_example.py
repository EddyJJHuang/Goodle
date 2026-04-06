"""Minimal end-to-end demo for probabilistic + conformal forecasting pipeline."""

from __future__ import annotations

import numpy as np

from app.forecasting.pipeline import ForecastConfig, ForecastPipeline


def dummy_backbone(x: np.ndarray) -> np.ndarray:
    # Mimic direct multi-horizon forecasting [B, H, D]
    b = x.shape[0]
    h = 96
    d = 3
    base = x.mean(axis=1, keepdims=True)[..., :d]
    trend = np.linspace(0.0, 1.0, h)[None, :, None]
    return np.repeat(base, h, axis=1) + 0.1 * trend


def main() -> None:
    rng = np.random.default_rng(42)
    x = rng.normal(size=(32, 192, 3)).astype(np.float32)
    y = dummy_backbone(x) + rng.normal(scale=0.15, size=(32, 96, 3)).astype(np.float32)

    cfg = ForecastConfig(
        pred_len=96,
        use_quantile_head=True,
        use_conformal=True,
        conformal_mode="horizon",
        conformal_alpha=0.1,
        use_crossing_penalty=True,
        use_smoothness_loss=True,
    )

    pipeline = ForecastPipeline(dummy_backbone, cfg)

    raw_lower = rng.normal(size=(32, 96, 3, 3)).astype(np.float32)
    raw_upper = rng.normal(size=(32, 96, 3, 3)).astype(np.float32)
    outputs = pipeline.predict(x, raw_lower, raw_upper)

    losses = pipeline.training_loss(y, outputs)
    print("training losses:", losses)

    # Split conformal on a calibration split (here: reusing same data for demonstration only)
    pipeline.fit_conformal(y, outputs)
    calibrated = pipeline.apply_conformal(outputs)
    metrics = pipeline.probabilistic_metrics(y, calibrated)
    print("probabilistic metrics:", metrics)


if __name__ == "__main__":
    main()
