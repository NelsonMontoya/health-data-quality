import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os
import re
from datetime import datetime
from app.client import WorldBankClient
from app.models import HealthData
from app.database import AuditDatabase
from app.reports import ExecutiveReport
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# 1. Configuración Profesional de la Interfaz
st.set_page_config(
    page_title="Strategic Data Hub & Auditor", 
    layout="wide", 
    page_icon="🛡️"
)

# Inicialización de componentes
client = WorldBankClient()
db = AuditDatabase()

# 2. Diccionario Estratégico de Indicadores (KPIs)
INDICATORS = {
    "GDP Growth (Annual %)": "NY.GDP.MKTP.KD.ZG",
    "Inflation (Annual %)": "FP.CPI.TOTL.ZG",
    "Unemployment Rate (%)": "SL.UEM.TOTL.ZS",
    "GDP per capita (US$)": "NY.GDP.PCAP.CD",
    "Life Expectancy (Years)": "SP.DYN.LE00.IN",
    "Health Expenditure (%)": "SH.XPD.CHEX.GD.ZS",
    "CO2 Emissions (Metric tons)": "EN.ATM.CO2E.PC",
    "Renewable Energy (%)": "EG.FEC.RNEW.ZS",
    "Internet Usage (%)": "IT.NET.USER.ZS",
    "Education Expenditure (%)": "SE.XPD.TOTL.GD.ZS"
}

# --- CONFIGURACIÓN DE BARRA LATERAL (GLOBAL) ---
st.sidebar.header("Global Configuration")

# Selector de Indicador y País
selected_topic = st.sidebar.selectbox("Global Indicator:", list(INDICATORS.keys()))
indicator_code = INDICATORS[selected_topic]

@st.cache_data(ttl=3600)
def load_countries():
    raw = client.get_countries_list()
    return [c for c in raw if c['region']['value'] != 'Aggregates']

countries_data = load_countries()
country_options = {c['name']: c['id'] for c in countries_data} if countries_data else {}
selected_country = st.sidebar.selectbox("Target Country:", list(country_options.keys()))
selected_iso = country_options.get(selected_country)

# 3. Navegación por Pestañas
tab_audit, tab_history, tab_correlation, tab_forecast = st.tabs([
    "📊 Live Data Audit", "📜 Audit History", "🔗 Correlation", "🔮 Predictive Forecast"
])

# --- PESTAÑA 1: AUDITORÍA Y FIREWALL ---
with tab_audit:
    st.title("🛡️ Strategic Data Quality Firewall")
    st.info(f"Auditing: {selected_topic} for {selected_country}")
    
    if st.button("Execute Production Audit") and selected_iso:
        with st.spinner("Processing..."):
            raw_records = client.fetch_indicator(selected_iso, indicator_code)
            if raw_records:
                valid, anomalies = [], []
                for r in raw_records:
                    try:
                        # El Firewall de Pydantic valida cada registro
                        point = HealthData(date=r['date'], value=r['value'])
                        valid.append(point.model_dump())
                    except Exception as e:
                        # Captura de errores estructurales
                        anomalies.append({"Year": r.get('date'), "Error": str(e)})

                # Cálculo de Health Score (penaliza nulos y anomalías)
                populated_count = len([v for v in valid if v['value'] is not None])
                health_score = (populated_count / len(raw_records)) * 100 if raw_records else 0
                
                # Persistencia en DuckDB
                db.save_audit(selected_country, selected_topic, health_score, len(raw_records), len(anomalies))
                st.toast("Audit saved to Database", icon="💾")

                # Métricas Principales
                c1, c2, c3 = st.columns(3)
                c1.metric("Health Score", f"{health_score:.1f}%", delta="PASS" if health_score >= 80 else "FAIL")
                c2.metric("Total Records", len(raw_records))
                c3.metric("Structural Anomalies", len(anomalies), delta_color="inverse")

                # Visualización de Tendencia Validada
                if valid:
                    df_p = pd.DataFrame(valid)
                    fig = px.line(df_p, x="year", y="value", markers=True, template="plotly_white")
                    st.plotly_chart(fig, width='stretch', config={'responsive': True})

                # --- MODIFICACIÓN: LOG DETALLADO DE ANOMALÍAS ---
                st.divider()
                if anomalies:
                    st.warning(f"Detected {len(anomalies)} structural anomalies in the data contract.")
                    with st.expander("🔍 View Detailed Anomaly Log"):
                        st.table(anomalies)
                else:
                    st.success("No structural anomalies detected. Data contract is valid.")

# --- PESTAÑA 2: HISTORIAL ---
with tab_history:
    st.header("📜 Historical Quality Audit Logs")
    history_df = db.get_history()
    if not history_df.empty:
        st.dataframe(history_df, width='stretch')
        fig_hist = px.bar(history_df, x="timestamp", y="health_score", color="country_name", template="plotly_white")
        st.plotly_chart(fig_hist, width='stretch', config={'responsive': True})
    else:
        st.info("No audit history found.")

# --- PESTAÑA 3: CORRELACIÓN ---
with tab_correlation:
    st.header("🔗 Multi-Indicator Correlation")
    st.write(f"Comparing **{selected_topic}** (X) vs another indicator (Y)")
    other_topic = st.selectbox("Select Indicator Y:", list(INDICATORS.keys()))

    if st.button("Calculate Correlation") and selected_iso:
        if selected_topic != other_topic:
            d1 = client.fetch_indicator(selected_iso, indicator_code)
            d2 = client.fetch_indicator(selected_iso, INDICATORS[other_topic])
            if d1 and d2:
                df1 = pd.DataFrame(d1)[['date', 'value']].rename(columns={'value': selected_topic})
                df2 = pd.DataFrame(d2)[['date', 'value']].rename(columns={'value': other_topic})
                combined = pd.merge(df1, df2, on='date').dropna()
                if len(combined) > 5:
                    r_val = combined[selected_topic].astype(float).corr(combined[other_topic].astype(float))
                    st.metric("Pearson Correlation (r)", f"{r_val:.2f}")
                    fig = px.scatter(combined, x=selected_topic, y=other_topic, trendline="ols", template="plotly_white")
                    st.plotly_chart(fig, width='stretch', config={'responsive': True})

# --- PESTAÑA 4: PREDICCIÓN Y REPORTE PDF ---
with tab_forecast:
    st.header("🔮 Advanced Predictive Analytics")
    col_f1, col_f2 = st.columns(2)
    horizon = col_f1.slider("Forecast Horizon (Years):", 1, 15, 5)
    degree = col_f2.slider("Curve Complexity (Degree):", 1, 3, 2)

    if st.button("Generate Forecast & Export PDF") and selected_iso:
        with st.spinner("Executing Prediction Model..."):
            raw_data = client.fetch_indicator(selected_iso, indicator_code)
            if raw_data:
                df = pd.DataFrame(raw_data).dropna(subset=['value'])
                df['year'] = df['date'].astype(int)
                df['value'] = df['value'].astype(float)
                
                if len(df) > 10:
                    # Modelado ML
                    X, y = df[['year']].values, df['value'].values
                    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
                    model.fit(X, y)

                    # Predicción
                    fut_y = np.array(range(df['year'].max()+1, df['year'].max()+horizon+1)).reshape(-1, 1)
                    preds = model.predict(fut_y)

                    # Gráfico
                    df_h = pd.DataFrame({'year': df['year'], 'value': df['value'], 'type': 'Historical'})
                    df_f = pd.DataFrame({'year': fut_y.flatten(), 'value': preds, 'type': 'Forecast'})
                    full_df = pd.concat([df_h, df_f])
                    
                    fig_f = px.line(full_df, x="year", y="value", color="type", markers=True, 
                                 title=f"Forecast: {selected_topic} ({selected_country})", template="plotly_white")
                    st.plotly_chart(fig_f, width='stretch', config={'responsive': True})

                    # --- CAPTURA DE IMAGEN PARA PDF (Kaleido 1.0.0+) ---
                    img_path = f"chart_{selected_iso}.png"
                    try:
                        fig_f.write_image(img_path)
                    except Exception as e:
                        st.error(f"Image Export Failed: {e}")
                        img_path = None

                    # Generar PDF
                    h_score = (len(df) / len(raw_data)) * 100
                    trend = "UPWARD" if preds[-1] > y[-1] else "DOWNWARD"
                    summary = {
                        "country": selected_country, "indicator": selected_topic,
                        "health_score": h_score, "degree": degree,
                        "forecast_insight": f"A {trend} trend is projected."
                    }

                    report = ExecutiveReport()
                    pdf_out = report.generate(summary, img_path)
                    
                    st.divider()
                    st.download_button(
                        label="📥 Download Executive PDF Report",
                        data=bytes(pdf_out),
                        file_name=f"Executive_Report_{selected_country}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Limpieza
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)
                else:
                    st.warning("Insufficient data points for forecasting.")