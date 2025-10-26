# streamlit_data_dashboard.py
# Comprehensive Streamlit dashboard for Excel/CSV analysis, pivoting, charts, KPIs,
# simple forecasting, bilingual (English/Arabic), dark/light mode, and export.
# Save this file to a GitHub repo and run with: `streamlit run streamlit_data_dashboard.py`

import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Tuple, List

# ---------------------- Translations ----------------------
TRANSLATIONS = {
    'en': {
        'title': 'Data Analyzer & Dashboard',
        'upload': 'Upload Excel or CSV file',
        'use_sample': 'Or use sample file included in repo',
        'total_everything': 'Total of everything (sum of numeric values):',
        'grand_total': 'Grand total (sum across numeric columns):',
        'pivot_table': 'Pivot Table Configuration',
        'row_field': 'Row Field (Group By)',
        'column_field': 'Column Field (Optional)',
        'agg_type': 'Aggregation Type',
        'value_column': 'Value Column',
        'generate_pivot': 'Generate Pivot Table',
        'stats_summary': 'Statistics Summary',
        'kpis': 'Key Performance Indicators (KPIs)',
        'charts': 'Charts & Visuals',
        'chart_type': 'Chart Type',
        'download_csv': 'Download Result as CSV',
        'download_excel': 'Download Result as Excel',
        'insights': 'Automated Insights',
        'forecasting': 'Simple Forecasting',
        'forecast_periods': 'Forecast periods (steps)',
        'apply': 'Apply',
        'language': 'Change Language',
        'theme': 'Dark Mode',
        'select_x': 'Select X-axis / index (optional)',
        'show_data': 'Show raw data',
        'missing_values': 'Missing values by column',
        'correlations': 'Top correlations',
        'top_values': 'Top values',
        'download_sample': 'Download sample Excel',
        'help': 'Help & Usage',
    },
    'ar': {
        'title': 'محلل البيانات ولوحة التحكم',
        'upload': 'رفع ملف Excel أو CSV',
        'use_sample': 'أو استخدم ملف العينة الموجود في المستودع',
        'total_everything': 'مجموع كل شيء (مجموع القيم الرقمية):',
        'grand_total': 'المجموع الكلي (مجموع عبر الأعمدة الرقمية):',
        'pivot_table': 'تكوين جدول المحورية',
        'row_field': 'حقل الصف (التجميع حسب)',
        'column_field': 'حقل العمود (اختياري)',
        'agg_type': 'نوع التجميع',
        'value_column': 'عمود القيمة',
        'generate_pivot': 'إنشاء جدول محوري',
        'stats_summary': 'ملخص الإحصائيات',
        'kpis': 'مؤشرات الأداء الرئيسية',
        'charts': 'المخططات والمرئيات',
        'chart_type': 'نوع المخطط',
        'download_csv': 'تحميل النتيجة كـ CSV',
        'download_excel': 'تحميل النتيجة كـ Excel',
        'insights': 'رؤى آلية',
        'forecasting': 'التنبؤ البسيط',
        'forecast_periods': 'فترات التنبؤ (خطوات)',
        'apply': 'تطبيق',
        'language': 'تغيير اللغة',
        'theme': 'الوضع المظلم',
        'select_x': 'اختر المحور السيني / الفهرس (اختياري)',
        'show_data': 'عرض البيانات الخام',
        'missing_values': 'القيم المفقودة حسب العمود',
        'correlations': 'أعلى الارتباطات',
        'top_values': 'أعلى القيم',
        'download_sample': 'تحميل ملف العينة',
        'help': 'المساعدة والاستخدام',
    }
}

# ---------------------- Utilities ----------------------

def t(key: str) -> str:
    lang = st.session_state.get('lang', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


def read_file(uploaded_file) -> pd.DataFrame:
    try:
        if uploaded_file is None:
            return None
        name = uploaded_file.name if hasattr(uploaded_file, 'name') else ''
        if name.lower().endswith('.csv') or isinstance(uploaded_file, io.StringIO):
            df = pd.read_csv(uploaded_file)
        else:
            # try excel
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
    return df


def grand_totals(df: pd.DataFrame) -> Tuple[pd.Series, float]:
    numeric = df.select_dtypes(include=[np.number])
    totals = numeric.sum()
    grand = totals.sum()
    return totals, grand


def stats_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] == 0:
        return pd.DataFrame()
    summary = numeric.agg(['count', 'mean', 'median', 'max', 'min', 'std']).transpose()
    summary = summary.rename(columns={'std': 'dev'})
    return summary


def generate_pivot(df: pd.DataFrame, rows: List[str], cols: List[str], values: str, aggfunc: str):
    if not rows:
        st.warning('Please select at least one row field')
        return None
    agg_map = {
        'sum': np.sum,
        'mean': np.mean,
        'median': np.median,
        'count': 'count',
        'min': np.min,
        'max': np.max,
        'std': np.std,
    }
    func = agg_map.get(aggfunc, np.sum)
    try:
        pivot = pd.pivot_table(df, index=rows, columns=cols if cols else None, values=values if values else None, aggfunc=func, margins=True, dropna=False)
    except Exception as e:
        st.error(f'Could not build pivot table: {e}')
        return None
    return pivot


def forecast_series(series: pd.Series, periods: int = 12) -> pd.DataFrame:
    # Simple forecasting using polynomial trend fit on non-null points.
    s = series.dropna()
    if s.empty:
        return pd.DataFrame()
    # if index is datetime try to use integer representation
    idx = s.index
    if pd.api.types.is_datetime64_any_dtype(idx) or isinstance(idx[0], (pd.Timestamp, datetime)):
        x = np.array([(v - idx[0]).days for v in idx], dtype=float)
        step = 1 if len(x) < 2 else np.median(np.diff(x))
        future_x = np.array([x[-1] + step * (i + 1) for i in range(periods)], dtype=float)
        base = idx[0]
        future_idx = [base + timedelta(days=int(round(val))) for val in future_x]
    else:
        x = np.arange(len(s), dtype=float)
        future_x = np.arange(len(s), len(s) + periods, dtype=float)
        future_idx = list(range(len(s), len(s) + periods))

    # fit 1st degree polynomial (linear). If enough points, try degree 2.
    deg = 1 if len(x) < 5 else 2
    coeffs = np.polyfit(x, s.values, deg)
    p = np.poly1d(coeffs)
    pred_vals = p(future_x)
    df_pred = pd.DataFrame({
        'index': future_idx,
        'forecast': pred_vals
    }).set_index('index')
    return df_pred


def compute_insights(df: pd.DataFrame) -> List[str]:
    insights = []
    # Missing values
    miss = df.isna().sum()
    miss = miss[miss > 0]
    if not miss.empty:
        insights.append(f"Missing values detected in columns: {', '.join(miss.index.astype(str))}")
    else:
        insights.append('No missing values detected')
    # Shape
    insights.append(f"Dataset has {df.shape[0]} rows and {df.shape[1]} columns")
    # Top correlations
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] >= 2:
        corr = numeric.corr().abs()
        # find top off-diagonal correlations
        corr_vals = corr.where(~np.eye(corr.shape[0], dtype=bool))
        max_corr = corr_vals.unstack().sort_values(ascending=False).dropna()
        if not max_corr.empty:
            top = max_corr.index[0]
            insights.append(f"Strongest correlation between {top[0]} and {top[1]}: {max_corr.iloc[0]:.2f}")
    # Top N values for object columns
    obj = df.select_dtypes(include=['object', 'category'])
    for c in obj.columns[:3]:
        top_vals = obj[c].value_counts().head(3).index.tolist()
        insights.append(f"Top values for {c}: {', '.join([str(x) for x in top_vals])}")
    return insights


def df_to_excel_bytes(df_dict: dict) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for name, df in df_dict.items():
            df.to_excel(writer, sheet_name=name[:31])
    return output.getvalue()

# ---------------------- Streamlit App ----------------------

st.set_page_config(page_title='Data Analyzer', layout='wide')

if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'

# Sidebar controls
with st.sidebar:
    st.header(t('title'))
    # Language toggle
    lang = st.selectbox(t('language'), options=['English', 'Arabic'])
    st.session_state['lang'] = 'ar' if lang == 'Arabic' else 'en'

    # Theme toggle (simple CSS switch)
    dark = st.checkbox(t('theme'), value=False)
    st.session_state['dark'] = dark

    st.markdown('---')
    st.markdown(t('help'))
    st.caption('• Upload your file (Excel or CSV).\n• Configure pivot and charts.\n• Export results.\n• Forecasting uses a simple trend model (linear/quadratic).')

# Apply simple CSS for dark mode
if st.session_state.get('dark', False):
    st.markdown(
        """
        <style>
        .css-1d391kg {background-color: #0e1117;}
        .stApp {background-color: #0e1117; color: #e6edf3;}
        .big-font {font-size:20px !important; color: #e6edf3}
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown('', unsafe_allow_html=True)

# Main
st.title(t('title'))

col1, col2 = st.columns([1, 3])

with col1:
    uploaded = st.file_uploader(t('upload'), type=['xlsx', 'xls', 'csv'])
    use_sample = st.button(t('use_sample'))
    show_raw = st.checkbox(t('show_data'), value=False)

    if uploaded:
        df = read_file(uploaded)
    elif use_sample:
        # Provide a small sample if user wants quick start
        sample = pd.DataFrame({
            'Date': pd.date_range(end=datetime.today(), periods=12, freq='M'),
            'Category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'Sales': np.random.randint(100, 1000, 12),
            'Quantity': np.random.randint(1, 20, 12),
            'Region': ['North', 'South', 'East', 'West'] * 3
        })
        df = sample
    else:
        df = None

    if df is not None:
        st.success('File loaded' if uploaded else 'Sample data loaded')

with col2:
    if df is None:
        st.info('No data loaded yet — upload an Excel/CSV file to begin or click the sample button.')
    else:
        # Show totals and KPIs
        st.subheader(t('kpis'))
        totals, grand = grand_totals(df)
        kpi_cols = st.columns(4)
        # show first four numeric totals as KPIs
        num_cols = totals.index.tolist()
        for i in range(min(4, len(num_cols))):
            with kpi_cols[i]:
                st.metric(label=num_cols[i], value=f"{totals[num_cols[i]]:.2f}")
        st.markdown(f"**{t('grand_total')}** {grand:.2f}")

        # Stats summary
        st.subheader(t('stats_summary'))
        summary = stats_summary(df)
        if not summary.empty:
            st.dataframe(summary)
        else:
            st.info('No numeric columns to summarize')

        # Insights
        st.subheader(t('insights'))
        insights = compute_insights(df)
        for i in insights:
            st.write('- ', i)

        # Pivot table configuration
        st.subheader(t('pivot_table'))
        all_cols = df.columns.tolist()
        row_field = st.multiselect(t('row_field'), options=all_cols, default=[all_cols[0]] if all_cols else [])
        col_field = st.selectbox(t('column_field'), options=[''] + all_cols, index=0)
        column_field = col_field if col_field != '' else None
        agg_type = st.selectbox(t('agg_type'), options=['sum', 'mean', 'median', 'count', 'min', 'max', 'std'], index=0)
        value_column = st.selectbox(t('value_column'), options=[''] + all_cols, index=0)
        value_col = value_column if value_column != '' else None
        if st.button(t('generate_pivot')):
            pivot = generate_pivot(df, rows=row_field, cols=[column_field] if column_field else None, values=value_col, aggfunc=agg_type)
            if pivot is not None:
                st.dataframe(pivot)
                # allow download
                tosave = { 'pivot': pivot.reset_index() }
                b = df_to_excel_bytes(tosave)
                st.download_button(label=t('download_excel'), data=b, file_name='pivot_table.xlsx')

        # Charts & visuals
        st.subheader(t('charts'))
        chart_type = st.selectbox(t('chart_type'), options=['Line', 'Bar', 'Area', 'Pie', 'Box', 'Scatter', 'Heatmap'])
        x_axis = st.selectbox(t('select_x'), options=[''] + all_cols, index=0)
        y_axis = st.selectbox('Y axis (value)', options=[''] + all_cols, index=0)
        do_plot = st.button('Plot')
        if do_plot:
            if x_axis == '' and chart_type not in ['Pie', 'Heatmap']:
                st.warning('Please select X axis')
            else:
                try:
                    fig = None
                    if chart_type == 'Line':
                        fig = px.line(df, x=x_axis, y=y_axis)
                    elif chart_type == 'Bar':
                        fig = px.bar(df, x=x_axis, y=y_axis)
                    elif chart_type == 'Area':
                        fig = px.area(df, x=x_axis, y=y_axis)
                    elif chart_type == 'Pie':
                        if y_axis == '':
                            st.warning('Select a value column for Pie')
                        else:
                            fig = px.pie(df, names=x_axis if x_axis else df.columns[0], values=y_axis)
                    elif chart_type == 'Box':
                        fig = px.box(df, x=x_axis if x_axis else None, y=y_axis)
                    elif chart_type == 'Scatter':
                        fig = px.scatter(df, x=x_axis, y=y_axis)
                    elif chart_type == 'Heatmap':
                        num = df.select_dtypes(include=[np.number])
                        if num.shape[1] < 2:
                            st.warning('Need at least two numeric columns for heatmap')
                        else:
                            corr = num.corr()
                            fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, zmin=-1, zmax=1))
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f'Could not create chart: {e}')

        # Forecasting simple
        st.subheader(t('forecasting'))
        index_col = st.selectbox('Select time index column (optional)', options=[''] + all_cols, index=0)
        forecast_col = st.selectbox('Select numeric column to forecast', options=[''] + all_cols, index=0)
        periods = st.number_input(t('forecast_periods'), min_value=1, max_value=365, value=12)
        if st.button('Run Forecast'):
            if forecast_col == '':
                st.warning('Select a numeric column to forecast')
            else:
                series = df[forecast_col]
                if index_col and index_col in df.columns:
                    try:
                        df_local = df.copy()
                        df_local[index_col] = pd.to_datetime(df_local[index_col], errors='coerce')
                        df_local = df_local.set_index(index_col)
                        series = df_local[forecast_col]
                    except Exception as e:
                        st.warning(f'Could not set index: {e}')
                pred = forecast_series(series, periods=int(periods))
                if pred.empty:
                    st.info('Not enough data to forecast')
                else:
                    st.line_chart(pd.concat([series.rename('actual'), pred['forecast']], axis=0))
                    st.dataframe(pred)

        # Missing data & correlations
        st.subheader(t('missing_values'))
        miss = df.isna().sum()
        st.dataframe(miss[miss > 0])

        st.subheader(t('correlations'))
        num = df.select_dtypes(include=[np.number])
        if num.shape[1] >= 2:
            corr = num.corr()
            st.dataframe(corr)
        else:
            st.info('Not enough numeric columns to compute correlations')

        # Data preview
        if show_raw:
            st.subheader('Raw Data')
            st.dataframe(df)

        # Export the loaded dataframe entirely
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='data')
        buffer.seek(0)
        st.download_button(label=t('download_sample'), data=buffer, file_name='exported_data.xlsx')

# Footer / small instructions
st.markdown('---')
st.caption('This app generates pivot tables, KPIs, charts, simple forecasts and insights.\nSave this file to GitHub and run with `streamlit run streamlit_data_dashboard.py`.')
