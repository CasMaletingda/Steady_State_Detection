import numpy as np
import pandas as pd
from . import config as C


def _runs_from_mask(mask: pd.Series):
    a = mask.values.astype(bool)
    edges = np.flatnonzero(np.diff(np.r_[False, a, False]))
    return list(zip(edges[0::2], edges[1::2])), a


def _robust_sigma(y: pd.Series) -> float:
    mad = np.nanmedian(np.abs(y - np.nanmedian(y)))
    return 1.4826 * mad


def steady_mask_for_series(y: pd.Series) -> pd.Series:
    y = y.astype(float)

    # 阈值基准
    robust_sigma = _robust_sigma(y)
    if not np.isfinite(robust_sigma) or robust_sigma < C.EPS:
        robust_sigma = float(np.nanstd(y))
    gstd = float(np.nanstd(y))

    thr_std = max(gstd * C.THR_K, robust_sigma * C.STD_MIN_FRAC)
    thr_range = max(gstd * C.RANGE_K, robust_sigma * C.RANGE_MIN_FRAC)
    thr_slope = max(C.SLOPE_K, C.EPS)

    # 滚动统计
    minp = max(10, C.WINDOW // 3)
    roll_std = y.rolling(C.WINDOW, center=True, min_periods=minp).std()
    roll_max = y.rolling(C.WINDOW, center=True, min_periods=minp).max()
    roll_min = y.rolling(C.WINDOW, center=True, min_periods=minp).min()
    roll_range = roll_max - roll_min
    rel_diff = y.pct_change(fill_method=None)
    roll_slope = rel_diff.rolling(C.WINDOW, center=True, min_periods=minp).median().abs()

    if gstd < C.EPS and robust_sigma < C.EPS:
        mask = pd.Series(True, index=y.index)
    else:
        mask = (roll_std < thr_std) & (roll_range < thr_range) & (roll_slope < thr_slope)

    # 过滤过短稳定区间
    runs, a = _runs_from_mask(mask)
    for s, e in runs:
        L = e - s
        if L < C.MIN_STEADY_LEN:
            a[s:e] = False
            continue

        ys = y.iloc[s:e].dropna().values
        if len(ys) < 5:
            a[s:e] = False
            continue

        mean_abs = abs(np.nanmean(ys)) or 1.0
        drop = False

        # 线性总漂移
        if np.nanstd(ys) >= C.EPS:
            try:
                k = np.polyfit(np.arange(len(ys), dtype=float), ys, 1)[0]
                rel_drift = abs(k) * (len(ys) - 1) / mean_abs
                if rel_drift >= C.DRIFT_K:
                    drop = True
            except np.linalg.LinAlgError:
                drop = True

        # 首尾20%中位差
        m = max(1, int(len(ys) * 0.2))
        rel_step = abs(np.nanmedian(ys[-m:]) - np.nanmedian(ys[:m])) / mean_abs
        if rel_step >= C.STEP_K:
            drop = True

        if drop:
            a[s:e] = False

    return pd.Series(a, index=y.index)


def detect_steady(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out['Time'] = df['Time']
    for col in df.columns:
        if col == 'Time':
            continue
        y = df[col]
        mask = steady_mask_for_series(y)
        out[col] = y.where(mask, float('nan'))
    return out
