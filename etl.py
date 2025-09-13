# etl.py - ETL helper functions
import pandas as pd
import numpy as np

def load_dataframe(path_or_buffer):
    if hasattr(path_or_buffer, "read"):
        name = getattr(path_or_buffer, "name", "")
        if str(name).lower().endswith(".csv"):
            return pd.read_csv(path_or_buffer)
        else:
            return pd.read_excel(path_or_buffer)
    else:
        if str(path_or_buffer).lower().endswith(".csv"):
            return pd.read_csv(path_or_buffer)
        else:
            return pd.read_excel(path_or_buffer)

def detect_missing(df):
    return df.isnull().sum()

def fill_missing(df, strategy="mean", columns=None):
    df = df.copy()
    cols = columns or df.columns.tolist()
    if strategy == "drop_rows":
        return df.dropna(subset=cols)
    if strategy == "drop_columns":
        return df.dropna(axis=1, how="all")
    if strategy == "mean":
        for c in cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].fillna(df[c].mean())
    if strategy == "median":
        for c in cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].fillna(df[c].median())
    if strategy == "mode":
        for c in cols:
            m = df[c].mode(dropna=True)
            if not m.empty:
                df[c] = df[c].fillna(m.iloc[0])
    return df

def zscore_outliers(df, columns, thresh=3.0):
    df = df.copy()
    mask = pd.DataFrame(False, index=df.index, columns=columns)
    for c in columns:
        col = df[c]
        if col.std(ddof=0) == 0 or col.dropna().empty:
            continue
        z = (col - col.mean()) / col.std(ddof=0)
        mask[c] = z.abs() > thresh
    return mask

def iqr_outliers(df, columns, k=1.5):
    df = df.copy()
    mask = pd.DataFrame(False, index=df.index, columns=columns)
    for c in columns:
        col = df[c]
        if col.dropna().empty:
            continue
        q1 = col.quantile(0.25)
        q3 = col.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - k * iqr
        upper = q3 + k * iqr
        mask[c] = (col < lower) | (col > upper)
    return mask