# app_modular.py - modular Streamlit app that imports etl.py, visuals.py, report_gen.py
import streamlit as st
from etl import load_dataframe, detect_missing, fill_missing, zscore_outliers, iqr_outliers
from visuals import box_plot, histogram, scatter_plot, bar_agg
from report_gen import generate_pptx, generate_pdf
import pandas as pd
import numpy as np
import os, datetime

st.set_page_config(page_title="Automated ETL + Dashboard (Modular)", layout="wide")
st.title("Automated ETL + Dashboard (Modular)")

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.cleaned = None
    st.session_state.saved_plots = []

menu = st.sidebar.radio("Menu", ["Upload", "Clean", "Visualize", "Export", "About"])

if menu == "Upload":
    uploaded = st.file_uploader("Upload CSV/XLSX", type=["csv", "xls", "xlsx"])
    if uploaded:
        df = load_dataframe(uploaded)
        st.session_state.df = df.copy()
        st.session_state.cleaned = df.copy()
        st.success(f"Loaded {df.shape[0]} rows x {df.shape[1]} cols")
        st.dataframe(df.head())

if menu == "Clean":
    if st.session_state.cleaned is None:
        st.info("Please upload data first.")
    else:
        df = st.session_state.cleaned
        st.write("Missing values:")
        st.write(detect_missing(df))
        strategy = st.selectbox("Missing strategy", ["none","drop_rows","drop_columns","mean","median","mode"])
        cols = st.multiselect("Columns (leave empty=all)", df.columns.tolist())
        if st.button("Apply missing"):
            st.session_state.cleaned = fill_missing(df, strategy=strategy, columns=cols if cols else None)
            st.success("Missing value strategy applied.")
        # Outliers
        numeric = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric:
            method = st.selectbox("Outlier method", ["zscore","iqr"])
            sel = st.multiselect("Cols to check", numeric, default=numeric)
            if st.button("Detect outliers"):
                if method=="zscore":
                    mask = zscore_outliers(st.session_state.cleaned, sel)
                else:
                    mask = iqr_outliers(st.session_state.cleaned, sel)
                st.write("Outlier rows:", mask.any(axis=1).sum())
                st.write(mask.head())

if menu == "Visualize":
    if st.session_state.cleaned is None:
        st.info("Upload and clean data first.")
    else:
        df = st.session_state.cleaned
        ptype = st.selectbox("Plot", ["Box","Histogram","Scatter","Bar"])
        if ptype in ["Box","Histogram"]:
            num = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            col = st.selectbox("Column", num)
            if ptype=="Box":
                fig = box_plot(df, col)
            else:
                fig = histogram(df, col)
        elif ptype=="Scatter":
            nums = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            x = st.selectbox("X", nums, index=0)
            y = st.selectbox("Y", nums, index=1 if len(nums)>1 else 0)
            fig = scatter_plot(df, x, y)
        else:
            cats = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
            cat = st.selectbox("Cat", cats)
            num = st.selectbox("Num", [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])])
            fig = bar_agg(df, cat, num, agg="mean")
        st.plotly_chart(fig)
        if st.button("Save plot"):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"assets/plot_{ts}.png"
            try:
                fig.write_image(fname, scale=2)
            except Exception:
                fig.write_image(fname)
            st.session_state.saved_plots.append(fname)
            st.success(f"Saved {fname}")

if menu == "Export":
    if st.session_state.cleaned is None:
        st.info("No cleaned data.")
    else:
        st.download_button("Download cleaned CSV", data=st.session_state.cleaned.to_csv(index=False).encode("utf-8"), file_name="cleaned.csv")
        if st.button("Generate PPTX & PDF report"):
            pptx = generate_pptx(st.session_state.cleaned, st.session_state.saved_plots, out_path="report/ETL_Report_modular.pptx")
            pdf = generate_pdf(st.session_state.cleaned, out_path="report/ETL_Report_modular.pdf")
            st.success("Generated report files.")
            with open(pptx, "rb") as f:
                st.download_button("Download PPTX", f, file_name="ETL_Report_modular.pptx")
            with open(pdf, "rb") as f:
                st.download_button("Download PDF", f, file_name="ETL_Report_modular.pdf")

if menu == "About":
    st.write("Modular version. Files: etl.py, visuals.py, report_gen.py, app_modular.py")