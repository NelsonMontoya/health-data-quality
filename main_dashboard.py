import streamlit as st
import pandas as pd
import plotly.express as px
from app.client import WorldBankClient
from app.models import HealthData

# 1. Professional Page Configuration
st.set_page_config(
    page_title="Global Health Data Quality Monitor", 
    layout="wide", 
    page_icon="🛡️"
)

# Initialize API Client
client = WorldBankClient()

st.title("🛡️ Global Health Data Quality Monitor")
st.markdown("""
This platform operates as a **Data Quality Firewall**, classifying incoming telemetry into 
validated records, missing data, and technical anomalies before visual analysis.
""")

# 2. Discovery Phase: Dynamic API Loading
@st.cache_data(ttl=3600)
def load_countries():
    """Fetches and filters the list of available countries from the API."""
    try:
        raw_countries = client.get_countries_list()
        return [c for c in raw_countries if c['region']['value'] != 'Aggregates']
    except Exception as e:
        st.error(f"API Connection Error during discovery: {e}")
        return []

countries_data = load_countries()
if not countries_data:
    st.error("Could not load country list. Please check your internet connection.")
    country_options = {}
else:
    country_options = {c['name']: c['id'] for c in countries_data}

st.sidebar.header("Audit Parameters")
selected_name = st.sidebar.selectbox("Select a Country:", list(country_options.keys())) if country_options else None
selected_iso = country_options.get(selected_name) if selected_name else None

# 3. Audit, Classification, and Visualization Phase
if st.button("Execute Quality Audit") and selected_iso:
    with st.spinner(f"Analyzing data integrity for {selected_name}..."):
        raw_records = client.fetch_health_indicator(selected_iso)
        
        if not raw_records:
            st.error("🔌 **Network Timeout or No Data**: The World Bank server is unreachable. Please try again.")
        else:
            valid_records = []  
            anomalies = []       
            null_records = []    
            
            for r in raw_records:
                try:
                    # Pydantic model validation
                    audit_point = HealthData(date=r['date'], value=r['value'])
                    valid_records.append(audit_point.model_dump())
                    
                    if r['value'] is None:
                        null_records.append({"Year": r['date'], "Status": "Missing (Null)"})
                except Exception as e:
                    anomalies.append({
                        "Year": r.get('date'), 
                        "Technical_Error": str(e),
                        "Original_Value": r.get('value')
                    })
            
            # --- STRICT 80% THRESHOLD LOGIC ---
            total = len(raw_records)
            well_populated = [r for r in valid_records if r['value'] is not None]
            health_score = (len(well_populated) / total) * 100 if total > 0 else 0
            
            # Traffic Light Logic
            if health_score >= 80:
                status_msg = "✅ PASS: High Quality Data"
                status_color = "normal"
            else:
                status_msg = "❌ FAIL: Below 80% Threshold"
                status_color = "inverse" # Turns Red

            # Key Performance Indicators
            c1, c2, c3 = st.columns(3)
            c1.metric("Data Health Score", f"{health_score:.1f}%", delta=status_msg, delta_color=status_color)
            c2.metric("Total Records Analyzed", total)
            c3.metric("Rule Anomalies", len(anomalies), delta="In Quarantine", delta_color="inverse")
            
            if health_score < 80:
                st.error(f"### ⚠️ Quality Gate Alert: {health_score:.1f}%")
                st.write("This dataset does not meet the **80% corporate integrity threshold**. Visualizations may be misleading.")

            # Trend Visualization
            if well_populated:
                df_plot = pd.DataFrame(well_populated)
                st.subheader(f"Validated Trend Analysis: {selected_name}")
                fig = px.line(
                    df_plot, x="year", y="value", markers=True,
                    labels={"year": "Year", "value": "Health Expenditure (% of GDP)"},
                    template="plotly_white"
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Insufficient data quality to generate visual trends.")

            # --- TRANSPARENCY & AUDIT SECTION ---
            st.divider()
            st.subheader("📋 Technical Audit Report")
            
            col_a, col_b = st.columns(2)
            with col_a:
                with st.expander("✅ View Validated Dataset"):
                    if valid_records:
                        st.dataframe(pd.DataFrame(valid_records), width='stretch')
                    else:
                        st.write("No records passed validation.")

            with col_b:
                with st.expander("⚠️ View Quarantine (Technical Anomalies)"):
                    if anomalies:
                        st.warning("These records violate defined integrity rules.")
                        st.table(pd.DataFrame(anomalies))
                    else:
                        st.success("No schema failures detected.")

            with st.expander("ℹ️ Completeness Analysis (Missing Data)"):
                if null_records:
                    st.info(f"Identified {len(null_records)} years with null values.")
                    st.dataframe(pd.DataFrame(null_records), width='stretch')
                else:
                    st.success("Complete historical series.")