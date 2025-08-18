import io
import matplotlib.pyplot as plt
import pandas as pd

from .steady import steady_mask_for_series

def plot_series(time: pd.Series, y: pd.Series, title: str):
    mask = steady_mask_for_series(y)
    steady = y.where(mask, float('nan'))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(title)
    ax.plot(time, y, color='skyblue', label='Original data')
    ax.plot(time, steady, color='green', label='Steady')
    ax.set_xlabel("Date_Time")
    ax.set_ylabel("Value")
    ax.grid(axis='y', linestyle='-')
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

def plot_all(df: pd.DataFrame):
    time = df['Time']
    plots = []
    for col in df.columns:
        if col == 'Time':
            continue
        buf = plot_series(time, df[col], col)
        plots.append((col, buf))
    return plots
