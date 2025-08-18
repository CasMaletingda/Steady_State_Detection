import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    if 'Time' in df.columns:
        try:
            df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        except Exception:
            df['Time'] = pd.to_datetime(df['Time'])
    else:
        df['Time'] = range(len(df))
    return df
