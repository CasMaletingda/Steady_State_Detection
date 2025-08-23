import io
import matplotlib.pyplot as plt
import pandas as pd


def plot_series(time: pd.Series, y: pd.Series, steady_y: pd.Series, title: str):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(title)
    ax.plot(time, y, color='skyblue', label='Original data')
    ax.plot(time, steady_y, color='green', label='Steady')
    ax.set_xlabel("Date_Time")
    ax.set_ylabel("Value")
    ax.grid(axis='y', linestyle='-')
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf


def plot_all(df: pd.DataFrame, steady_df: pd.DataFrame):
    time = df['Time']
    plots = []
    for col in df.columns:
        if col == 'Time':
            continue
        buf = plot_series(time, df[col], steady_df[col], col)
        plots.append((col, buf))
    return plots
