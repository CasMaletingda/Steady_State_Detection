import numpy as np
import pandas as pd
import config as C


def _robust_scale(y: pd.Series) -> pd.Series:
    y = y.astype(float)
    med = np.nanmedian(y)
    mad = np.nanmedian(np.abs(y - med))
    scale = 1.4826 * mad
    if (not np.isfinite(scale)) or (scale < C.EPS):
        s = float(np.nanstd(y))
        scale = s if (np.isfinite(s) and s >= C.EPS) else 1.0
    return (y - med) / (scale + C.EPS)


def _true_runs(mask: pd.Series):
    a = mask.values.astype(bool)
    edges = np.flatnonzero(np.diff(np.r_[False, a, False]))
    return a, list(zip(edges[0::2], edges[1::2]))


def steady_mask_for_series(y: pd.Series) -> pd.Series:
    y = y.astype(float)
    z = _robust_scale(y)

    minp = max(10, C.WINDOW // 3)
    roll_max = z.rolling(C.WINDOW, center=True, min_periods=minp).max()
    roll_min = z.rolling(C.WINDOW, center=True, min_periods=minp).min()
    roll_rng = roll_max - roll_min

    mask = (roll_rng < C.RANGE_K)

    a, runs = _true_runs(mask)
    for s, e in runs:
        L = e - s
        if L < C.MIN_STEADY_LEN:
            a[s:e] = False
            continue

        ys = y.iloc[s:e].dropna().values
        if len(ys) < 5:
            a[s:e] = False
            continue

        # 整段斜率
        try:
            k = np.polyfit(np.arange(len(ys), dtype=float), ys, 1)[0]
            if abs(k) >= C.SEG_SLOPE_K:
                a[s:e] = False
                continue
        except np.linalg.LinAlgError:
            a[s:e] = False
            continue

    return pd.Series(a, index=y.index)


def detect_steady(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out['Time'] = df['Time']
    for col in df.columns:
        if col == 'Time':
            continue
        m = steady_mask_for_series(df[col])
        out[col] = df[col].where(m, np.nan)
    return out
