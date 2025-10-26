# app.py
# Streamlit Data Dashboard for Excel/CSV analytics

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# --------------------- Translations ---------------------
TRANSLATIONS = {
    "en": {
        "title": "Data Analyzer & Dashboard",
        "upload": "Upload Excel or CSV file",
        "use_sample": "Use sample data",
        "total": "Total of everything (sum of numeric values)",
        "pivot_config": "Pivot Table Configuration",
        "row_field": "Row Field (Group By)",
        "column_field": "Column Field (Optional)",
        "agg_type": "Aggregation Type",
        "value_column": "Value Column",
        "generate_pivot": "Generate Pivot Table",
        "kpis": "Key Performance Indicators",
        "stats": "Statistics Summary",
        "charts": "Charts & Visuals",
        "chart_type": "Chart Type",
        "forecast": "Simple Forecasting",
        "forecast_periods": "Forecast periods (steps)",
        "insights": "Automated Insights",
        "language": "Language",
        "theme": "Dark Mode",
    },
    "ar": {
        "title": "لوحة تحليل البيانات",
        "upload": "رفع ملف Excel أو CSV",
        "use_sample": "استخدام بيانات العينة",
        "total": "مجموع كل القيم الرقمية",
        "pivot_config": "إعداد الجدول المحوري",
        "row_field": "حقل الصف (تجميع حسب)",
        "column_field": "حقل العمود (اختياري)",
        "agg_type": "نوع التجميع",
        "value_column": "عمود القيمة",
        "generate_pivot": "إنشاء جدول محوري",
        "kpis": "مؤشرات الأداء الرئيسية",
        "stats": "ملخص الإحصائيات",
        "charts": "المخططات والمرئيات",
        "chart_type": "نوع المخطط",
        "forecast": "التنبؤ البسيط",
        "forecast_periods": "فترات التنبؤ",
        "insights": "رؤى تلقائية",
        "language": "اللغة",
        "theme": "الوضع الداكن",
    },
}

def t(key):
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# --------------------- Helper Functions ---------------------
def read_file(uploaded_file):
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    return df

def forecast_series(series, periods=6):
    s = series.dropna()
    if len(s) < 3:
        return pd.DataFrame()
    x = np.arange(len(s))
    coeffs = np.polyfit(x, s, 1 if len(s) < 6 else 2)
    model = np.poly1d(coeffs)
    future_x = np.arange(len(s), len(s) + periods)
    forecast = model(future_x)
    future_idx = [f"F{i+1}" for i in range(periods)]
    return pd.DataFrame({"Forecast": forecast}, index=future_idx)

# --------------------- Streamlit UI ---------------------
st.set_page_config(page_title="Data Dashboard", layout="wide")

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

with st.sidebar:
    lang_choice = st.radio("🌍 " + t("language"), ["English", "Arabic"])
    st.session_state["lang"] = "ar" if lang_choice == "Arabic" else "en"
    dark_mode = st.checkbox(t("theme"))

st.title(t("title"))

uploaded = st.file_uploader(t("upload"), type=["csv", "xlsx"])
use_sample = st.button(t("use_sample"))

if uploaded:
    df = read_file(uploaded)
elif use_sample:
    df = pd.DataFrame({
        "Date": pd.date_range(end=datetime.today(), periods=12, freq="M"),
        "Category": ["A", "B", "C"] * 4,
        "Sales": np.random.randint(100, 1000, 12),
        "Quantity": np.random.randint(1, 20, 12),
        "Region": ["North", "South", "East", "West"] * 3
    })
else:
    df = None

if df is not None:
    st.success("✅ Data loaded successfully")
    
    # KPIs
    st.subheader(t("kpis"))
    numeric = df.select_dtypes(include=[np.number])
    total = numeric.sum().sum()
    st.metric(t("total"), f"{total:,.2f}")

    # Statistics Summary
    st.subheader(t("stats"))
    st.dataframe(numeric.agg(["count", "mean", "median", "max", "min", "std"]).transpose())

    # Pivot Table
    st.subheader(t("pivot_config"))
    cols = df.columns.tolist()
    row_field = st.multiselect(t("row_field"), cols)
    col_field = st.selectbox(t("column_field"), [""] + cols)
    value_col = st.selectbox(t("value_column"), [""] + cols)
    agg_type = st.selectbox(t("agg_type"), ["sum", "mean", "median", "count", "min", "max"])
    if st.button(t("generate_pivot")):
        func_map = {"sum": np.sum, "mean": np.mean, "median": np.median, "count": "count", "min": np.min, "max": np.max}
        pivot = pd.pivot_table(df, index=row_field, columns=col_field if col_field else None,
                               values=value_col if value_col else None, aggfunc=func_map[agg_type], margins=True)
        st.dataframe(pivot)

    # Charts
    st.subheader(t("charts"))
    chart_type = st.selectbox(t("chart_type"), ["Line", "Bar", "Area", "Pie", "Scatter"])
    x_col = st.selectbox("X", cols)
    y_col = st.selectbox("Y", cols)
    if st.button("Plot"):
        if chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col)
        elif chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col)
        elif chart_type == "Area":
            fig = px.area(df, x=x_col, y=y_col)
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_col, y=y_col)
        st.plotly_chart(fig, use_container_width=True)

    # Forecasting
    st.subheader(t("forecast"))
    fcol = st.selectbox("Select column to forecast", numeric.columns)
    periods = st.number_input(t("forecast_periods"), min_value=1, max_value=24, value=6)
    if st.button("Run Forecast"):
        forecast = forecast_series(numeric[fcol], periods)
        if forecast.empty:
            st.warning("Not enough data to forecast.")
        else:
            st.line_chart(pd.concat([numeric[fcol].rename("Actual"), forecast["Forecast"]]))

    # Insights
    st.subheader(t("insights"))
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    missing = df.isna().sum()
    st.write("Missing values:", missing[missing > 0])
    if len(numeric.columns) > 1:
        st.write("Correlation matrix:")
        st.dataframe(numeric.corr())

else:
    st.info("⬆️ " + t("upload") + " or click “" + t("use_sample") + "”")

