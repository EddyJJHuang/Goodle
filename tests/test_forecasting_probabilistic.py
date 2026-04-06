import numpy as np

from app.forecasting.conformal import SplitConformalCalibrator
from app.forecasting.pipeline import ForecastConfig, ForecastPipeline
from app.forecasting.quantile import MonotonicQuantileHead


def test_monotonic_quantile_head_orders_quantiles():
    rng = np.random.default_rng(0)
    median = rng.normal(size=(2, 96, 4))
    head = MonotonicQuantileHead([0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95])
    q = head.build(
        median,
        raw_lower_increments=rng.normal(size=(2, 96, 4, 3)),
        raw_upper_increments=rng.normal(size=(2, 96, 4, 3)),
    )
    assert q.shape == (2, 96, 4, 7)
    assert np.all(q[..., :-1] <= q[..., 1:])


def test_horizon_conformal_calibration_widens_intervals():
    rng = np.random.default_rng(1)
    n, h, d = 20, 96, 2
    y = rng.normal(size=(n, h, d))
    q_lo = y - 0.05
    q_hi = y + 0.05

    cal = SplitConformalCalibrator(alpha=0.1, mode="horizon")
    cal.fit_horizon(q_lo, q_hi, y)
    lo2, hi2 = cal.apply_horizon(q_lo, q_hi)

    assert lo2.shape == q_lo.shape
    assert hi2.shape == q_hi.shape
    assert np.all(lo2 <= q_lo)
    assert np.all(hi2 >= q_hi)


def test_pipeline_backward_compat_point_only():
    def backbone(x):
        return x[:, :96, :]

    cfg = ForecastConfig(use_quantile_head=False, use_conformal=False)
    pipeline = ForecastPipeline(backbone, cfg)

    x = np.ones((4, 128, 3), dtype=np.float32)
    y = np.ones((4, 96, 3), dtype=np.float32)
    out = pipeline.predict(x)

    assert set(out.keys()) == {"point"}
    losses = pipeline.training_loss(y, out)
    assert "point" in losses
    assert "total" in losses
