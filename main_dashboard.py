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

# Inicialización de componentes (Asegúrate de que app.database esté correcto)
client = WorldBankClient()
db = AuditDatabase()

# 2. Diccionario de Indicadores
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

# --- BARRA LATERAL GLOBAL ---
st.sidebar.header("Global Configuration")
# Este indicador actúa como el "Indicador A" para todas las pestañas
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
    "📊 Live Data Audit", "📜 Audit History", "🔗 Correlation Analysis", "🔮 Predictive Forecast"
])

# --- PESTAÑA 1: AUDITORÍA (Genera los datos para el History) ---
with tab_audit:
    st.title("🛡️ Strategic Data Quality Firewall")
    st.info(f"Auditing: {selected_topic} for {selected_country}")
    
    if st.button("Execute Production Audit") and selected_iso:
        with st.spinner("Processing Strategy..."):
            raw_records = client.fetch_indicator(selected_iso, indicator_code)
            if raw_records:
                valid, anomalies = [], []
                for r in raw_records:
                    try:
                        point = HealthData(date=r['date'], value=r['value'])
                        valid.append(point.model_dump())
                    except Exception as e:
                        anomalies.append({"Year": r.get('date'), "Error": str(e)})

                # Cálculo de Health Score
                populated = len([v for v in valid if v['value'] is not None])
                health_score = (populated / len(raw_records)) * 100 if raw_records else 0
                
                # GUARDAR EN DUCKDB (Esto alimenta la pestaña History)
                db.save_audit(selected_country, selected_topic, health_score, len(raw_records), len(anomalies))
                st.success("Audit completed and saved to Database.")

                c1, c2, c3 = st.columns(3)
                c1.metric("Health Score", f"{health_score:.1f}%")
                c2.metric("Total Records", len(raw_records))
                c3.metric("Anomalies", len(anomalies))

                if valid:
                    df_p = pd.DataFrame(valid)
                    fig = px.line(df_p, x="year", y="value", markers=True, template="plotly_white")
                    st.plotly_chart(fig, width='stretch')

# --- PESTAÑA 2: AUDIT HISTORY (Lee de DuckDB) ---
with tab_history:
    st.header("📜 Historical Quality Audit Logs")
    # Forzamos la lectura de la base de datos
    history_df = db.get_history()
    
    if not history_df.empty:
        st.write("Last audits performed:")
        st.dataframe(history_df, width='stretch')
        
        # Gráfico de evolución de calidad
        fig_hist = px.bar(
            history_df, 
            x="timestamp", 
            y="health_score", 
            color="country_name", 
            title="Integrity Evolution over Time",
            template="plotly_white"
        )
        st.plotly_chart(fig_hist, width='stretch')
    else:
        st.info("No audit history found. Run an audit in the first tab to see data here.")

# --- PESTAÑA 3: CORRELATION ANALYSIS ---
with tab_correlation:
    st.header("🔗 Multi-Indicator Correlation")
    st.markdown(f"Analyze the relationship between **{selected_topic}** and a second metric.")
    
    # Selector para el segundo indicador (Indicador B)
    other_topic = st.selectbox("Select Secondary Indicator (Y):", list(INDICATORS.keys()))

    if st.button("Calculate Correlation") and selected_iso:
        if selected_topic == other_topic:
            st.warning("Please select a different indicator to compare.")
        else:
            with st.spinner("Aligning datasets..."):
                # Obtenemos datos de ambos indicadores
                data_a = client.fetch_indicator(selected_iso, indicator_code)
                data_b = client.fetch_indicator(selected_iso, INDICATORS[other_topic])
                
                if data_a and data_b:
                    df_a = pd.DataFrame(data_a)[['date', 'value']].rename(columns={'value': selected_topic})
                    df_b = pd.DataFrame(data_b)[['date', 'value']].rename(columns={'value': other_topic})
                    
                    # Unimos por año (date) y quitamos nulos
                    combined = pd.merge(df_a, df_b, on='date').dropna()
                    
                    # Convertir a numérico para asegurar el cálculo
                    combined[selected_topic] = pd.to_numeric(combined[selected_topic])
                    combined[other_topic] = pd.to_numeric(combined[other_topic])

                    if len(combined) > 5:
                        r_val = combined[selected_topic].corr(combined[other_topic])
                        
                        st.metric("Pearson Correlation (r)", f"{r_val:.2f}")
                        
                        fig_corr = px.scatter(
                            combined, x=selected_topic, y=other_topic, 
                            trendline="ols", 
                            title=f"Correlation Analysis: {selected_country}",
                            template="plotly_white"
                        )
                        st.plotly_chart(fig_corr, width='stretch')
                        
                        with st.expander("View Matched Data"):
                            st.dataframe(combined, width='stretch')
                    else:
                        st.error("Insufficient overlapping data points to calculate correlation.")
                else:
                    st.error("Could not retrieve data for one of the indicators.")

# --- PESTAÑA 4: FORECAST & PDF ---
with tab_forecast:
    st.header("🔮 Advanced Predictive Analytics")
    col_f1, col_f2 = st.columns(2)
    horizon = col_f1.slider("Horizon (Years):", 1, 15, 5)
    degree = col_f2.slider("Complexity:", 1, 3, 2)

    if st.button("Generate Forecast & Export PDF") and selected_iso:
        raw_data = client.fetch_indicator(selected_iso, indicator_code)
        if raw_data:
            df = pd.DataFrame(raw_data).dropna(subset=['value'])
            df['year'] = df['date'].astype(int)
            df['value'] = df['value'].astype(float)
            
            if len(df) > 10:
                X, y = df[['year']].values, df['value'].values
                model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
                model.fit(X, y)
                
                fut_y = np.array(range(df['year'].max()+1, df['year'].max()+horizon+1)).reshape(-1, 1)
                preds = model.predict(fut_y)

                df_h = pd.DataFrame({'year': df['year'], 'value': df['value'], 'type': 'Historical'})
                df_f = pd.DataFrame({'year': fut_y.flatten(), 'value': preds, 'type': 'Forecast'})
                fig_f = px.line(pd.concat([df_h, df_f]), x="year", y="value", color="type", markers=True, template="plotly_white")
                st.plotly_chart(fig_f, width='stretch')

                img_path = f"chart_{selected_iso}.png"
                try:
                    fig_f.write_image(img_path)
                except Exception:
                    img_path = None

                summary = {
                    "country": selected_country, "indicator": selected_topic,
                    "health_score": (len(df)/len(raw_data))*100, "degree": degree,
                    "forecast_insight": f"An {'UPWARD' if preds[-1] > y[-1] else 'DOWNWARD'} trend projected."
                }
                pdf_out = ExecutiveReport().generate(summary, img_path)
                st.download_button("📥 Download Executive PDF", data=bytes(pdf_out), file_name=f"Report_{selected_country}.pdf")
                if img_path and os.path.exists(img_path): os.remove(img_path)