import streamlit as st
import pandas as pd
import plotly.express as px
from app.client import WorldBankClient
from app.models import HealthData, Country

# Configuración de la página
st.set_page_config(page_title="Data Quality Monitor", layout="wide", page_icon="🛡️")

st.title("🛡️ Global Health Data Quality Monitor")
st.markdown("""
Esta plataforma audita en tiempo real la integridad de los datos de salud del **Banco Mundial**, 
asegurando que cumplan con los estándares de gobernanza antes de su visualización.
""")

client = WorldBankClient()

# --- FASE 1: DISCOVERY (Numeral 2) ---
@st.cache_data(ttl=3600) # Guardamos la lista por 1 hora para ser eficientes
def get_sidebar_data():
    raw_countries = client.get_countries_list()
    # Limpiamos los datos usando nuestro modelo de Pydantic
    return [Country.from_api(c) for c in raw_countries if c['region']['value'] != 'Aggregates']

countries = get_sidebar_data()
country_map = {c.name: c.id for c in countries}

# Sidebar
st.sidebar.header("Configuración de Auditoría")
selected_country_name = st.sidebar.selectbox("Selecciona un País:", list(country_map.keys()))
selected_iso = country_map[selected_name := selected_country_name]

# --- FASE 2: INGESTA Y AUDITORÍA (Numeral 3) ---
if st.button("🚀 Iniciar Auditoría de Datos"):
    with st.spinner(f"Analizando integridad para {selected_name}..."):
        raw_records = client.fetch_health_indicator(selected_iso)
        
        if not raw_records:
            st.error("No se encontraron datos para este país.")
        else:
            valid_data = []
            anomalies = []

            for r in raw_records:
                try:
                    # Pasamos cada registro por el "Firewall" de Pydantic
                    clean_record = HealthData(
                        countryiso3code=r['countryiso3code'],
                        date=r['date'],
                        value=r['value'],
                        indicator_value=r['indicator']['value']
                    )
                    valid_data.append(clean_record.model_dump())
                except Exception as e:
                    anomalies.append({"Año": r['date'], "Detalle_Error": str(e)})

            # --- FASE 3: MÉTRICAS DE NIVEL MASTER ---
            total = len(raw_records)
            health_score = (len(valid_data) / total) * 100
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Data Health Score", f"{health_score:.1f}%", delta="Calidad de Datos")
            c2.metric("Registros Totales", total)
            c3.metric("Anomalías Detectadas", len(anomalies))

            if anomalies:
                st.warning("🚨 Se detectaron fallos de integridad en la fuente de datos:")
                st.table(pd.DataFrame(anomalies))

            if valid_data:
                df = pd.DataFrame(valid_data)
                
                # Visualización de Tendencias
                st.subheader(f"Análisis Validado: Gasto en Salud en {selected_name}")
                fig = px.line(df, x="year", y="value", title="Evolución % del PIB", markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Raw Data con Pydantic aplicado
                st.write("Datos que pasaron la auditoría:", df)