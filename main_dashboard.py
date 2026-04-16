import streamlit as st
import pandas as pd
import plotly.express as px
from app.client import WorldBankClient
from app.models import HealthData

st.title("🛡️ Data Quality Monitor")
client = WorldBankClient()

# Discovery dinámico
countries = client.get_countries_list()
option = st.selectbox("País:", [c['name'] for c in countries if c['region']['value'] != 'Aggregates'])
iso = [c['id'] for c in countries if c['name'] == option][0]

if st.button("Auditar"):
    raw = client.fetch_health_indicator(iso)
    clean = []
    for r in raw:
        try:
            val = HealthData(date=r['date'], value=r['value'])
            clean.append(val.model_dump())
        except: continue
    
    df = pd.DataFrame(clean)
    st.metric("Health Score", f"{(len(clean)/len(raw))*100:.1f}%")
    st.plotly_chart(px.line(df, x="year", y="value"))