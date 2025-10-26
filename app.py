# Sales_Insights_and_Forecasting.py
# Streamlit app tailored for the uploaded Excel `مبيعات (1).xlsx`.
# Features:
# - Upload Excel / CSV
# - Manual selection of date column (default attempts 'مبيعات')
# - Manual selection of numeric columns (KPIs) and more selections for pivot
# - Total of everything (sum of all numeric columns)
# - Extended KPIs, statistics summary (count, mean, median, max, min, std)
# - Pivot table configuration (multi row, multi column, aggregation types)
# - Multiple charts (plotly): line, bar, area, pie, box, scatter, heatmap
# - Simple trend forecasting (linear/quadratic) for any numeric column
# - Insights (missing values, top values, correlations)
# - Language toggle (Arabic / English)
# - Dark / Light mode
# - Export: Excel summary, HTML report
# Save as: Sales_Insights_and_Forecasting.py
# Run: streamlit run Sales_Insights_and_Forecasting.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import io
import base64




# ---------------- Translations ----------------
TRANSLATIONS = {
    'en': {
        'title': 'Sales Insights & Forecasting',
        'upload': 'Upload Excel or CSV file',
        'load_sample': 'Load sample data',
        'total_everything': 'Total of everything (sum of numeric columns)',
        'grand_total': 'Grand total',
        'kpi_selection': 'Select KPI / Numeric columns (for totals, KPIs, forecasting)',
        'date_column': 'Select date column (for time series & forecasting)',
        'pivot_config': 'Pivot Table Configuration',
        'row_field': 'Row Field (Group By) — select one or more',
        'col_field': 'Column Field (Optional)',
        'agg_type': 'Aggregation Type',
        'value_col': 'Value Column (for pivot)',
        'generate_pivot': 'Generate Pivot Table',
        'stats_summary': 'Statistics Summary (count, mean, median, max, min, std)',
        'charts': 'Charts & Visuals',
        'chart_type': 'Chart Type',
        'x_axis': 'X axis',
        'y_axis': 'Y axis',
        'plot': 'Plot',
        'forecasting': 'Simple Forecasting (trend)',
        'forecast_column': 'Select numeric column to forecast',
        'forecast_periods': 'Forecast periods (steps)',
        'run_forecast': 'Run Forecast',
        'insights': 'Automated Insights',
        'missing_values': 'Missing values by column',
        'correlations': 'Correlation matrix (numeric)',
        'download_excel': 'Download Excel summary',
        'download_html': 'Download HTML report',
        'language': 'Language',
        'theme': 'Dark Mode',
        'show_data': 'Show raw data',
        'download_pivot': 'Download Pivot as Excel',
    },
    'ar': {
        'title': 'تحليلات ومؤشرات المبيعات والتنبؤ',
        'upload': 'رفع ملف Excel أو CSV',
        'load_sample': 'تحميل بيانات العينة',
        'total_everything': 'مجموع كل شيء (مجموع الأعمدة الرقمية)',
        'grand_total': 'المجموع الكلي',
        'kpi_selection': 'اختر أعمدة رقمية (للكل، مؤشرات، والتنبؤ)',
        'date_column': 'اختر عمود التاريخ (للسلاسل الزمنية والتنبؤ)',
        'pivot_config': 'إعداد الجدول المحوري',
        'row_field': 'حقل الصف (تجميع حسب) — اختر واحدًا أو أكثر',
        'col_field': 'حقل العمود (اختياري)',
        'agg_type': 'نوع التجميع',
        'value_col': 'عمود القيمة (للمحور)',
        'generate_pivot': 'إنشاء جدول محوري',
        'stats_summary': 'ملخص الإحصائيات (العدد، المتوسط، الوسيط، الأعلى، الأدنى، الانحراف)',
        'charts': 'المخططات والمرئيات',
        'chart_type': 'نوع المخطط',
        'x_axis': 'المحور السيني',
        'y_axis': 'المحور الصادي',
        'plot': 'ارسم',
        'forecasting': 'التنبؤ البسيط (الاتجاه)',
        'forecast_column': 'اختر العمود الرقمي للتنبؤ',
        'forecast_periods': 'فترات التنبؤ (خطوات)',
        'run_forecast': 'تشغيل التنبؤ',
        'insights': 'رؤى تلقائية',
        'missing_values': 'القيم المفقودة حسب العمود',
        'correlations': 'مصفوفة الارتباط (الرقمية)',
        'download_excel': 'تحميل ملخص Excel',
        'download_html': 'تحميل تقرير HTML',
        'language': 'اللغة',
        'theme': 'الوضع الداكن',
        'show_data': 'عرض البيانات الخام',
        'download_pivot': 'تحميل الجدول المحوري كـ Excel',
    }
}

# ---------------- Helpers ----------------

def t(key: str) -> str:
    lang = st.session_state.get('lang', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


def read_file(uploaded_file):
    """Smart file reader that auto-detects header row and cleans up Unnamed columns."""
    if uploaded_file is None:
        return None

    name = uploaded_file.name.lower()

    # Read Excel or CSV without assuming header
    if name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None, encoding='utf-8', engine='python')
    else:
        df = pd.read_excel(uploaded_file, header=None, engine='openpyxl')

    # Drop completely empty rows and columns
    df = df.dropna(how='all').dropna(axis=1, how='all')

    # Detect header row: the one with the most non-null values
    header_row = df.notna().sum(axis=1).idxmax()
    df.columns = df.iloc[header_row].astype(str).str.strip()
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Clean columns: replace Unnamed or empty with generated names
    df.columns = [
        c if (isinstance(c, str) and not c.strip().startswith("Unnamed") and c.strip() != "")
        else f"Column_{i}"
        for i, c in enumerate(df.columns)
    ]

    # Drop empty rows after header assignment
    df = df.dropna(how="all")

    # Try to convert numeric columns safely
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df



def grand_totals(df: pd.DataFrame):
    numeric = df.select_dtypes(include=[np.number])
    totals = numeric.sum(numeric_only=True)
    grand = totals.sum()
    return totals.to_dict(), grand


def stats_summary(df: pd.DataFrame):
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] == 0:
        return pd.DataFrame()
    summary = numeric.agg(['count', 'mean', 'median', 'max', 'min', 'std']).transpose()
    summary = summary.rename(columns={'std': 'dev'})
    return summary


def generate_pivot(df, rows, cols, values, aggfunc):
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
        pvt = pd.pivot_table(df, index=rows if rows else None, columns=cols if cols else None,
                             values=values if values else None, aggfunc=func, margins=True)
        return pvt
    except Exception as e:
        st.error(f"Pivot error: {e}")
        return None


def simple_forecast(series: pd.Series, periods: int = 12):
    s = series.dropna()
    if s.empty or len(s) < 3:
        return pd.DataFrame()
    idx = np.arange(len(s))
    deg = 1 if len(s) < 6 else 2
    coeffs = np.polyfit(idx, s.values, deg)
    p = np.poly1d(coeffs)
    future_idx = np.arange(len(s), len(s) + periods)
    preds = p(future_idx)
    return pd.DataFrame({'forecast': preds}, index=future_idx)


def df_to_excel_bytes(sheets: dict):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        for name, df in sheets.items():
            try:
                safe = str(name)[:31]
                df.to_excel(writer, sheet_name=safe, index=False)
            except Exception:
                pass
    out.seek(0)
    return out


def create_html_report(df: pd.DataFrame, insights: list):
    html = '<html><head><meta charset="utf-8"><title>Report</title></head><body>'
    html += f'<h1>{t("title")}</h1>'
    html += f'<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>'
    html += f'<h2>Dataset</h2><p>Rows: {df.shape[0]} | Columns: {df.shape[1]}</p>'
    html += '<h3>Insights</h3><ul>'
    for ins in insights:
        html += f'<li>{ins}</li>'
    html += '</ul>'
    html += '</body></html>'
    return html.encode('utf-8')

# ---------------- Streamlit App ----------------
st.set_page_config(page_title='Sales Insights', layout='wide')

if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'

with st.sidebar:
    st.header(t('title'))
    lang = st.selectbox(t('language'), options=['English', 'Arabic'])
    st.session_state['lang'] = 'ar' if lang == 'Arabic' else 'en'
    dark = st.checkbox(t('theme'))

if dark:
    st.markdown("""
    <style>
    .stApp { background-color: #0f1724; color: #e6edf3; }
    </style>
    """, unsafe_allow_html=True)

st.title(t('title'))

col1, col2 = st.columns([1, 3])

with col1:
    uploaded = st.file_uploader(t('upload'), type=['xlsx', 'xls', 'csv'])
    load_sample = st.button(t('load_sample'))
    show_raw = st.checkbox(t('show_data'))

    if uploaded:
        df = read_file(uploaded)
    elif load_sample:
        df = pd.DataFrame({
            'مبيعات': pd.date_range(end=pd.Timestamp.today(), periods=12, freq='M'),
            'Category': ['A', 'B', 'C'] * 4,
            'Sales': np.random.randint(100, 1000, 12),
            'Quantity': np.random.randint(1, 50, 12),
            'Profit': np.random.randint(-50, 300, 12)
        })
    else:
        df = None

with col2:
    if df is None:
        st.info('No data loaded — upload your Excel/CSV (e.g., the provided مبيعات file).')
    else:
        st.success('Data loaded')
        # Manual selections
        all_cols = df.columns.tolist()
        st.subheader('Configuration')
        st.markdown('Choose the columns manually (date & numeric KPIs).')
        default_date = 'مبيعات' if 'مبيعات' in all_cols else None
        date_col = st.selectbox(t('date_column'), options=[''] + all_cols, index=all_cols.index(default_date) + 1 if default_date else 0)
        date_col = date_col if date_col != '' else None

        numeric_cols = st.multiselect(t('kpi_selection'), options=all_cols, default=[c for c in all_cols if pd.api.types.is_numeric_dtype(df[c])][:3])

        # Totals and KPIs
        st.subheader(t('total_everything'))
        totals_dict, grand = grand_totals(df)
        # Show top numeric totals as metrics
        kpi_cols_display = list(totals_dict.keys())[:4]
        kpi_cols = st.columns(len(kpi_cols_display) if kpi_cols_display else 1)
        for i, k in enumerate(kpi_cols_display):
            kpi_cols[i].metric(k, f"{totals_dict[k]:,.2f}")
        st.markdown(f"**{t('grand_total')}:** {grand:,.2f}")

        # Stats summary
        st.subheader(t('stats_summary'))
        stat = stats_summary(df)
        if not stat.empty:
            st.dataframe(stat)
        else:
            st.info('No numeric columns for statistics')

        # Insights
        st.subheader(t('insights'))
        insights = []
        miss = df.isna().sum()
        if miss.sum() > 0:
            insights.append('Missing values exist in: ' + ', '.join(miss[miss>0].index.astype(str)))
        else:
            insights.append('No missing values detected')
        insights.append(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        # top categorical values
        obj_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for c in obj_cols[:3]:
            vals = df[c].value_counts().head(3).index.tolist()
            insights.append(f"Top values for {c}: {', '.join([str(v) for v in vals])}")
        num = df.select_dtypes(include=[np.number])
        if num.shape[1] >= 2:
            corr = num.corr().abs()
            top_pairs = corr.unstack().sort_values(ascending=False).drop_duplicates()
            # attempt to add one strong correlation
            for (a, b), v in top_pairs.items():
                if a != b:
                    insights.append(f"Correlation between {a} and {b}: {v:.2f}")
                    break
        for ins in insights:
            st.write('- ', ins)

        # Charts & visuals
        st.markdown('---')
        st.subheader(t('charts'))
        chart_cols = df.columns.tolist()
        chart_type = st.selectbox(t('chart_type'), options=['Line', 'Bar', 'Area', 'Pie', 'Box', 'Scatter', 'Heatmap'])
        x_axis = st.selectbox(t('x_axis'), options=[''] + chart_cols, index=0)
        y_axis = st.selectbox(t('y_axis'), options=[''] + chart_cols, index=0)
        if st.button(t('plot')):
            try:
                fig = None
                if chart_type == 'Line':
                    if x_axis == '' or y_axis == '':
                        st.warning('Select X and Y for line chart')
                    else:
                        fig = px.line(df, x=x_axis, y=y_axis)
                elif chart_type == 'Bar':
                    if x_axis == '' or y_axis == '':
                        st.warning('Select X and Y for bar chart')
                    else:
                        fig = px.bar(df, x=x_axis, y=y_axis)
                elif chart_type == 'Area':
                    if x_axis == '' or y_axis == '':
                        st.warning('Select X and Y for area chart')
                    else:
                        fig = px.area(df, x=x_axis, y=y_axis)
                elif chart_type == 'Pie':
                    if y_axis == '':
                        st.warning('Select a value column for pie chart')
                    else:
                        names = x_axis if x_axis != '' else df.columns[0]
                        fig = px.pie(df, names=names, values=y_axis)
                elif chart_type == 'Box':
                    if y_axis == '':
                        st.warning('Select Y for box plot')
                    else:
                        fig = px.box(df, y=y_axis)
                elif chart_type == 'Scatter':
                    if x_axis == '' or y_axis == '':
                        st.warning('Select X and Y for scatter')
                    else:
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
                st.error(f"Could not create chart: {e}")

        # Pivot table configuration
        st.markdown('---')
        st.subheader(t('pivot_config'))
        pivot_rows = st.multiselect(t('row_field'), options=all_cols, default=[all_cols[0]] if all_cols else [])
        pivot_cols = st.multiselect(t('col_field'), options=all_cols)
        pivot_value = st.selectbox(t('value_col'), options=[''] + all_cols, index=0)
        pivot_agg = st.selectbox(t('agg_type'), options=['sum', 'mean', 'median', 'count', 'min', 'max', 'std'], index=0)
        if st.button(t('generate_pivot')):
            pvt = generate_pivot(df, rows=pivot_rows, cols=pivot_cols if pivot_cols else None, values=pivot_value if pivot_value != '' else None, aggfunc=pivot_agg)
            if pvt is not None:
                st.dataframe(pvt)
                # allow download
                excel_bytes = df_to_excel_bytes({'pivot': pvt.reset_index()})
                st.download_button(t('download_pivot'), data=excel_bytes, file_name='pivot_table.xlsx')

        # Forecasting
        st.markdown('---')
        st.subheader(t('forecasting'))
        # manual selection enforced
        fc_col = st.selectbox(t('forecast_column'), options=[''] + all_cols, index=0)
        fc_periods = st.number_input(t('forecast_periods'), min_value=1, max_value=365, value=12)
        if st.button(t('run_forecast')):
            if fc_col == '':
                st.warning('Select a numeric column to forecast')
            else:
                if date_col:
                    try:
                        tmp = df[[date_col, fc_col]].copy()
                        tmp[date_col] = pd.to_datetime(tmp[date_col], errors='coerce', infer_datetime_format=True)
                        tmp = tmp.dropna(subset=[date_col])
                        tmp = tmp.sort_values(date_col)
                        # aggregate by date if duplicates
                        tmp_agg = tmp.groupby(date_col)[fc_col].sum()
                        pred = simple_forecast(tmp_agg, periods=int(fc_periods))
                        if pred.empty:
                            st.info('Not enough data to forecast')
                        else:
                            # attempt to create a datetime index for future based on median diff
                            if isinstance(tmp_agg.index[0], (pd.Timestamp, datetime)):
                                diffs = np.diff(tmp_agg.index.astype('int64') // 10**9)
                                median = int(np.median(diffs)) if len(diffs) > 0 else 86400
                                last = tmp_agg.index.max()
                                future_dates = [last + pd.to_timedelta(median * (i+1), unit='s') for i in range(len(pred))]
                                pred.index = future_dates
                                combined = pd.concat([tmp_agg.rename('actual'), pred['forecast']], axis=1)
                                st.line_chart(combined)
                                st.dataframe(pred.head(50))
                            else:
                                st.line_chart(pd.concat([tmp_agg.rename('actual'), pred['forecast']], axis=0))
                                st.dataframe(pred.head(50))
                    except Exception as e:
                        st.error(f'Forecasting failed: {e}')
                else:
                    # no date column: forecast on index sequence
                    series = df[fc_col]
                    pred = simple_forecast(series, periods=int(fc_periods))
                    if pred.empty:
                        st.info('Not enough data to forecast')
                    else:
                        st.line_chart(pd.concat([series.rename('actual'), pred['forecast']], axis=0))
                        st.dataframe(pred.head(50))

        # Missing values & correlations
        st.markdown('---')
        st.subheader(t('missing_values'))
        miss = df.isna().sum()
        st.dataframe(miss[miss>0])

        st.subheader(t('correlations'))
        num_df = df.select_dtypes(include=[np.number])
        if num_df.shape[1] >= 2:
            st.dataframe(num_df.corr())
        else:
            st.info('Not enough numeric columns for correlations')

        # Export reports
        st.markdown('---')
        st.subheader('Exports & Reports')
        if st.button(t('download_excel')):
            try:
                sheets = {'Raw': df.copy(), 'Stats': stat.reset_index() if not stat.empty else pd.DataFrame()}
                excel_io = df_to_excel_bytes(sheets)
                fname = f"sales_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                st.download_button('Download Excel', data=excel_io, file_name=fname)
            except Exception as e:
                st.error(f'Export failed: {e}')

        if st.button(t('download_html')):
            try:
                html_b = create_html_report(df, insights)
                fname = f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                st.download_button('Download HTML report', data=html_b, file_name=fname, mime='text/html')
            except Exception as e:
                st.error(f'HTML export failed: {e}')

        if show_raw:
            st.markdown('---')
            st.subheader('Raw Data')
            st.dataframe(df)

# footer
st.markdown('---')
st.caption('Save this script to your GitHub repo and deploy on Streamlit Cloud. Requirements: streamlit, pandas, numpy, plotly, xlsxwriter, openpyxl')
