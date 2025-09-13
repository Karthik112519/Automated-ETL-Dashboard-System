# visuals.py - Plotly visual helpers
import plotly.express as px
import pandas as pd

def box_plot(df, column):
    return px.box(df, y=column, title=f"Box plot — {column}")

def histogram(df, column, nbins=30):
    return px.histogram(df, x=column, nbins=nbins, title=f"Histogram — {column}")

def scatter_plot(df, x, y, color=None):
    return px.scatter(df, x=x, y=y, color=color, title=f"{y} vs {x}")

def bar_agg(df, x, y, agg="mean"):
    if agg == "count":
        grouped = df.groupby(x).size().reset_index(name="count")
        return px.bar(grouped, x=x, y="count", title=f"Count by {x}")
    grouped = df.groupby(x)[y].agg(agg).reset_index()
    return px.bar(grouped, x=x, y=y, title=f"{agg.title()} of {y} by {x}")