# Sales_Insights_and_Forecasting.py
# Streamlit app tailored for the uploaded Excel `مبيعات (1).xlsx`.
# Updated: Forecasting shows real future dates and a confidence band.

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import xlsxwriter


# ✨ Footer (Dark mode friendly)
# ---------------------------------------------------------------
st.markdown(
    """
    <hr style="margin-top:50px; margin-bottom:10px; border:1px solid #444;">
    <div style='text-align: center; color: #aaa; font-size: 14px;'>
        Created by <b style='color:#00BFFF;'>Sameh Sobhy Attia</b>
    </div>
    """,
    unsafe_allow_html=True
)

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

def t(key: str) -> str:
    lang = st.session_state.get('lang', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# ---------------- Helper functions ----------------

def read_file(uploaded_file):
    """Read and clean Excel/CSV files with smart header detection."""
    if uploaded_file is None:
        return None

    name = uploaded_file.name.lower()

    # Try to read as Excel, then fallback to CSV
    try:
        if name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None, encoding='utf-8', engine='python')
        else:
            df = pd.read_excel(uploaded_file, header=None, engine='openpyxl')
    except Exception:
        try:
            df = pd.read_csv(uploaded_file, header=None, encoding='utf-8', engine='python')
        except Exception:
            st.error("⚠️ Could not read file. Please upload a valid Excel or CSV file.")
            return None

    # Drop completely empty rows and columns
    df = df.dropna(how='all').dropna(axis=1, how='all')

    # Detect header row: pick the row with the most non-null values
    header_row = df.notna().sum(axis=1).idxmax()
    # If header row looks like 'Unnamed' or numeric index, try to find first row with string values
    header_values = df.iloc[header_row].astype(str).str.strip()
    if all(header_values.str.contains('^Unnamed', na=False)) or header_values.isnull().all():
        # fallback: find first row with >50% non-empty
        header_row = None
        for i in range(len(df)):
            if df.iloc[i].notna().mean() > 0.5:
                header_row = i
                break
        if header_row is None:
            header_row = 0

    df.columns = df.iloc[header_row].astype(str).str.strip()
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Clean column names: replace Unnamed or blanks with Column_i
    df.columns = [
        col if (isinstance(col, str) and col.strip() != "" and not col.strip().startswith("Unnamed"))
        else f"Column_{i}"
        for i, col in enumerate(df.columns)
    ]

    # Drop empty rows after cleaning
    df = df.dropna(how="all").reset_index(drop=True)

    # Try converting numeric columns (safe)
    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c], errors='ignore')
        except Exception:
            pass

    # Drop duplicated columns by name keeping first occurrence
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

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

def df_to_excel_bytes(sheets: dict):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        for name, df_sheet in sheets.items():
            try:
                safe = str(name)[:31]
                df_sheet.to_excel(writer, sheet_name=safe, index=False)
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
            'مبيعات': pd.date_range(end=pd.Timestamp.today(), periods=24, freq='M'),
            'Category': ['A', 'B', 'C'] * 8,
            'Sales': np.random.randint(100, 1000, 24),
            'Quantity': np.random.randint(1, 50, 24),
            'Profit': np.random.randint(-50, 300, 24)
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
        date_col = st.selectbox(t('date_column'), options=[''] + all_cols, index=all_cols.index(default_date)+1 if default_date else 0)
        date_col = date_col if date_col != '' else None

        numeric_cols = st.multiselect(t('kpi_selection'), options=all_cols, default=[c for c in all_cols if pd.api.types.is_numeric_dtype(df[c])][:3])

        # Totals and KPIs
        # ---------------------------------------------------------------
        # 🧮 Totals and KPIs (Global totals + Selected totals)
        # ---------------------------------------------------------------
        st.subheader("🔹 " + t('total_everything') + " — جميع الأعمدة الرقمية")
        
        # --- Global Totals (all numeric columns) ---
        totals_dict_all, grand_all = grand_totals(df)
        kpi_cols_display = list(totals_dict_all.keys())[:4]
        kpi_cols = st.columns(len(kpi_cols_display) if kpi_cols_display else 1)
        for i, k in enumerate(kpi_cols_display):
            kpi_cols[i].metric(k, f"{totals_dict_all[k]:,.2f}")
        st.markdown(f"**{t('grand_total')}:** {grand_all:,.2f}")
        
        st.markdown("---")
        
        # --- Selected Totals (based only on selected numeric columns) ---
        st.subheader("🔸 المجموع للأعمدة المحددة فقط")
        
        if numeric_cols:
            selected_df = df[numeric_cols].select_dtypes(include=[np.number])
            totals_dict = selected_df.sum(numeric_only=True).to_dict()
            grand = selected_df.sum(numeric_only=True).sum()
        
            kpi_cols = st.columns(len(totals_dict) if totals_dict else 1)
            for i, (col, val) in enumerate(totals_dict.items()):
                kpi_cols[i].metric(col, f"{val:,.2f}")
        
            st.markdown(f"**الإجمالي الكلي للأعمدة المحددة:** {grand:,.2f}")
        else:
            st.info("⚠️ لم يتم تحديد أي أعمدة رقمية لحساب المجموع.")


        # Stats summary
        st.subheader(t('stats_summary'))
        stat = stats_summary(df)
        if not stat.empty:
            st.dataframe(stat)
        else:
            st.info('No numeric columns for statistics')

        # Insights
        # =====================================
        # 🤖 Automated Insights (Smart Summary + Table + Chart)
        # =====================================
        import pandas as pd
        import numpy as np
        import streamlit as st
        import plotly.express as px
        
        st.header("🤖 Automated Insights")
        
        try:
            # --- Initialize safe list ---
            insights = []
        
            # --- Helper function to find columns (Arabic or English) ---
            def safe_find(df, possible_names):
                for name in possible_names:
                    for col in df.columns:
                        if str(col).strip().lower() == str(name).strip().lower():
                            return col
                return None
        
            # --- Detect key columns dynamically ---
            revenue_col = safe_find(df, ["القيمة بعد الضريبة", "صافي المبيعات", "الإيرادات", "revenue", "total revenue"])
            discount_col = safe_find(df, ["الخصومات", "خصم", "discount", "total discount"])
            tax_col = safe_find(df, ["الضريبة", "ضريبة الصنف", "tax", "total tax"])
            qty_col = safe_find(df, ["الكمية", "كمية كرتون", "quantity", "total quantity"])
            branch_col = safe_find(df, ["الفرع", "branch"])
            salesman_col = safe_find(df, ["اسم المندوب", "مندوب", "salesman"])
            product_col = safe_find(df, ["اسم الصنف", "الصنف", "product"])
        
            # --- Prepare summary dictionary ---
            insights_dict = {}
        
            # --- Calculate totals ---
            if revenue_col in df.columns:
                total_revenue = df[revenue_col].sum()
                insights_dict["Total Revenue"] = f"{total_revenue:,.2f}"
                insights.append(f"💰 Total Revenue: {total_revenue:,.2f}")
        
            if discount_col in df.columns:
                total_discount = df[discount_col].sum()
                insights_dict["Total Discounts"] = f"{total_discount:,.2f}"
                insights.append(f"🎯 Total Discounts: {total_discount:,.2f}")
        
            if tax_col in df.columns:
                total_tax = df[tax_col].sum()
                insights_dict["Total Tax"] = f"{total_tax:,.2f}"
                insights.append(f"💸 Total Tax: {total_tax:,.2f}")
        
            if qty_col in df.columns:
                total_qty = df[qty_col].sum()
                insights_dict["Total Quantity"] = f"{total_qty:,.2f}"
                insights.append(f"📦 Total Quantity: {total_qty:,.2f}")
        
            # --- Find top categories ---
            if branch_col in df.columns and revenue_col in df.columns:
                top_branch = df.groupby(branch_col)[revenue_col].sum().idxmax()
                insights_dict["Top Branch by Revenue"] = str(top_branch)
                insights.append(f"🏢 Top Branch by Revenue: {top_branch}")
        
            if salesman_col in df.columns and revenue_col in df.columns:
                top_salesman = df.groupby(salesman_col)[revenue_col].sum().idxmax()
                insights_dict["Top Salesman"] = str(top_salesman)
                insights.append(f"🧍‍♂️ Top Salesman: {top_salesman}")
        
            if product_col in df.columns and revenue_col in df.columns:
                top_product = df.groupby(product_col)[revenue_col].sum().idxmax()
                insights_dict["Top Product"] = str(top_product)
                insights.append(f"🛒 Top Product: {top_product}")
        
            # --- Optional correlation check (for numeric relationships) ---
            num = df.select_dtypes(include=[np.number])
            if num.shape[1] >= 2:
                corr = num.corr().abs()
                corr_unstack = corr.where(~np.eye(corr.shape[0], dtype=bool)).unstack().dropna()
                if not corr_unstack.empty:
                    top_pair = corr_unstack.sort_values(ascending=False).index[0]
                    top_val = corr_unstack.sort_values(ascending=False).iloc[0]
                    insights.append(f"📈 Strongest correlation between **{top_pair[0]}** and **{top_pair[1]}**: {top_val:.2f}")
        
            # --- Display the results ---
            st.markdown("### 📊 Summary of Key Metrics")
            col1, col2 = st.columns([1.3, 2])
        
            # --- Left: Table of metrics ---
            with col1:
                if insights_dict:
                    insights_df = pd.DataFrame(list(insights_dict.items()), columns=["Metric", "Value"])
                    st.table(insights_df)
                else:
                    st.info("⚠️ لم يتم العثور على بيانات كافية لإنشاء التحليل التلقائي.")
        
            # --- Right: Textual insights ---
            with col2:
                st.markdown("### 💡 Key Observations")
                for ins in insights:
                    st.write("- ", ins)
        
            # --- Chart: Revenue by Branch (if available) ---
            if revenue_col and branch_col:
                st.markdown("### 🏢 Revenue by Branch")
                fig = px.bar(
                    df.groupby(branch_col)[revenue_col].sum().reset_index(),
                    x=branch_col,
                    y=revenue_col,
                    title="Branch Performance",
                    color=branch_col,
                    text_auto=".2s"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"⚠️ Error generating insights: {e}")

            
        
            
        


    

        # Charts & visuals
        # ---------------------------------------------------------------
        # 📊 Charts & Visuals (allow multiple X and Y selections)
        # ---------------------------------------------------------------
        st.markdown('---')
        st.subheader(t('charts'))
        
        chart_cols = df.columns.tolist()
        chart_type = st.selectbox(t('chart_type'), options=['Line', 'Bar', 'Area', 'Scatter', 'Box', 'Pie', 'Heatmap'])
        
        # 🔹 Multi-selection for X and Y
        x_axes = st.multiselect("🧭 " + t('x_axis'), options=chart_cols, default=[chart_cols[0]] if chart_cols else [])
        y_axes = st.multiselect("📈 " + t('y_axis'), options=chart_cols, default=[chart_cols[1]] if len(chart_cols) > 1 else [])
        
        if st.button(t('plot')):
            try:
                fig = None
        
                if chart_type in ['Line', 'Bar', 'Area', 'Scatter']:
                    if not x_axes or not y_axes:
                        st.warning('يرجى اختيار عمود واحد على الأقل للمحور السيني والمحور الصادي.')
                    else:
                        for y_col in y_axes:
                            if chart_type == 'Line':
                                fig = px.line(df, x=x_axes[0], y=y_col, title=f"{chart_type} Chart - {y_col}")
                            elif chart_type == 'Bar':
                                fig = px.bar(df, x=x_axes[0], y=y_col, title=f"{chart_type} Chart - {y_col}")
                            elif chart_type == 'Area':
                                fig = px.area(df, x=x_axes[0], y=y_col, title=f"{chart_type} Chart - {y_col}")
                            elif chart_type == 'Scatter':
                                fig = px.scatter(df, x=x_axes[0], y=y_col, title=f"{chart_type} Chart - {y_col}")
                            st.plotly_chart(fig, use_container_width=True)
        
                elif chart_type == 'Box':
                    if not y_axes:
                        st.warning('يرجى اختيار عمود واحد على الأقل للمحور الصادي.')
                    else:
                        fig = px.box(df, y=y_axes)
                        st.plotly_chart(fig, use_container_width=True)
        
                elif chart_type == 'Pie':
                    if not y_axes:
                        st.warning('يرجى اختيار عمود للقيم.')
                    else:
                        for y_col in y_axes:
                            names = x_axes[0] if x_axes else df.columns[0]
                            fig = px.pie(df, names=names, values=y_col, title=f"مخطط دائري: {y_col}")
                            st.plotly_chart(fig, use_container_width=True)
        
                elif chart_type == 'Heatmap':
                    num = df.select_dtypes(include=[np.number])
                    if num.shape[1] < 2:
                        st.warning('تحتاج على الأقل إلى عمودين رقميين لرسم خريطة حرارية.')
                    else:
                        corr = num.corr()
                        import plotly.graph_objects as go
                        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, zmin=-1, zmax=1))
                        fig.update_layout(title="خريطة الارتباط الحرارية")
                        st.plotly_chart(fig, use_container_width=True)
        
            except Exception as e:
                st.error(f"تعذر إنشاء المخطط: {e}")

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

        # Forecasting (with real future dates + confidence band)
        st.markdown('---')
        st.subheader(t('forecasting'))
        fc_col = st.selectbox(t('forecast_column'), options=[''] + all_cols, index=0)
        fc_periods = st.number_input(t('forecast_periods'), min_value=1, max_value=365, value=12)
        st.write("🔮 " + ("اضغط تشغيل التنبؤ بعد اختيار العمود والفترات" if st.session_state.get('lang', 'en') == 'ar' else "Select column & periods then press Run Forecast"))
        if st.button(t('run_forecast')):
            if fc_col == '':
                st.warning('Select a numeric column to forecast')
            else:
                try:
                    # Prepare data
                    tmp = df[[date_col, fc_col]].copy() if date_col else None
                    if date_col and tmp is not None:
                        tmp[date_col] = pd.to_datetime(tmp[date_col], errors='coerce')
                        tmp = tmp.dropna(subset=[date_col, fc_col])
                        # Aggregate by date (mean) to remove duplicates, then set index
                        tmp = tmp.groupby(date_col, as_index=False)[fc_col].mean().sort_values(date_col)
                        tmp_series = tmp.set_index(date_col)[fc_col]
                        # ensure unique index
                        tmp_series = tmp_series[~tmp_series.index.duplicated(keep='first')]

                        if tmp_series.shape[0] < 3:
                            st.warning('Not enough unique dated observations to forecast (need >= 3).')
                        else:
                            # Fit polynomial trend (degree 1 or 2)
                            n = tmp_series.shape[0]
                            deg = 1 if n < 6 else 2
                            x = np.arange(n)
                            coeffs = np.polyfit(x, tmp_series.values, deg)
                            model = np.poly1d(coeffs)

                            # Residuals -> estimate sigma for confidence band
                            fitted = model(x)
                            resid = tmp_series.values - fitted
                            resid_std = np.nanstd(resid)

                            # Infer frequency for future dates
                            try:
                                freq = pd.infer_freq(tmp_series.index)
                                if freq is None:
                                    # fallback: if index spacing irregular pick daily
                                    freq = 'D'
                            except Exception:
                                freq = 'D'

                            last = tmp_series.index.max()
                            future_index = pd.date_range(start=last + pd.Timedelta(1, unit='D'), periods=int(fc_periods), freq=freq)

                            future_x = np.arange(n, n + int(fc_periods))
                            preds = model(future_x)

                            # Confidence band (approximate) using residual std
                            ci = 1.96 * resid_std
                            lower = preds - ci
                            upper = preds + ci

                            # Build forecast DataFrame with dates and bands
                            forecast_df = pd.DataFrame({
                                date_col: future_index,
                                'forecast': preds,
                                'lower': lower,
                                'upper': upper
                            })

                            # Plot: actual + forecast + confidence band
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=tmp_series.index, y=tmp_series.values,
                                                     mode='lines', name=('البيانات الفعلية' if st.session_state.get('lang','en')=='ar' else 'Actual'),
                                                     line=dict(color='blue')))
                            fig.add_trace(go.Scatter(x=forecast_df[date_col], y=forecast_df['forecast'],
                                                     mode='lines', name=('التنبؤ' if st.session_state.get('lang','en')=='ar' else 'Forecast'),
                                                     line=dict(dash='dash', color='red', width=3)))
                            # Confidence band (fill between upper and lower)
                            fig.add_trace(go.Scatter(
                                x=list(forecast_df[date_col]) + list(forecast_df[date_col][::-1]),
                                y=list(forecast_df['upper']) + list(forecast_df['lower'][::-1]),
                                fill='toself',
                                fillcolor='rgba(255,0,0,0.15)',
                                line=dict(color='rgba(255,255,255,0)'),
                                hoverinfo="skip",
                                showlegend=True,
                                name=('Confidence Interval' if st.session_state.get('lang','en')=='en' else 'نطاق الثقة')
                            ))
                            fig.update_layout(title=f"{fc_col} - Forecast", xaxis_title=date_col, yaxis_title=fc_col)
                            st.plotly_chart(fig, use_container_width=True)
                            st.subheader(('Forecast Table' if st.session_state.get('lang','en')=='en' else 'جدول التنبؤ'))
                            st.dataframe(forecast_df.reset_index(drop=True))
                    else:
                        # No date column provided: forecast on index sequence
                        series = df[fc_col].dropna().astype(float)
                        if series.shape[0] < 3:
                            st.warning('Not enough data to forecast.')
                        else:
                            n = series.shape[0]
                            deg = 1 if n < 6 else 2
                            x = np.arange(n)
                            coeffs = np.polyfit(x, series.values, deg)
                            model = np.poly1d(coeffs)
                            fitted = model(x)
                            resid = series.values - fitted
                            resid_std = np.nanstd(resid)
                            future_x = np.arange(n, n + int(fc_periods))
                            preds = model(future_x)
                            ci = 1.96 * resid_std
                            lower = preds - ci
                            upper = preds + ci
                            # Build forecast with numeric index
                            forecast_df = pd.DataFrame({
                                'index': future_x,
                                'forecast': preds,
                                'lower': lower,
                                'upper': upper
                            })
                            # Plot actual + forecast
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=x, y=series.values, mode='lines', name='Actual'))
                            fig.add_trace(go.Scatter(x=future_x, y=preds, mode='lines', name='Forecast', line=dict(dash='dash', color='red', width=3)))
                            fig.add_trace(go.Scatter(
                                x=list(future_x) + list(future_x[::-1]),
                                y=list(upper) + list(lower[::-1]),
                                fill='toself',
                                fillcolor='rgba(255,0,0,0.15)',
                                line=dict(color='rgba(255,255,255,0)'),
                                hoverinfo="skip",
                                showlegend=True,
                                name=('Confidence Interval' if st.session_state.get('lang','en')=='en' else 'نطاق الثقة')
                            ))
                            st.plotly_chart(fig, use_container_width=True)
                            st.dataframe(forecast_df)
                except Exception as e:
                    st.error(f'Forecasting failed: {e}')

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

