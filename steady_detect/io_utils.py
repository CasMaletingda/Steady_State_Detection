import pandas as pd

def load_data(path):
    df = pd.read_excel(path)

    # 时间列处理
    if 'Time' in df.columns:
        try:
            df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        except Exception:
            df['Time'] = pd.to_datetime(df['Time'])
    else:
        df['Time'] = range(len(df))

    # 缺失值插值处理
    df = df.interpolate(method='linear')

    return df
