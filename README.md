# 🛡️ Global Health Data Quality & Observability Framework

This project is a high-performance **Data Integrity Engine** designed to audit, validate, and visualize global health indicators from the World Bank API. It transforms raw, potentially unreliable data into high-confidence business insights using a multi-layered QA and Data Engineering approach.

## 🚀 The Problem it Solves
Data-driven organizations often suffer from "Data Drift" or "Silent Failures" where API sources change formats or provide incomplete data. This framework acts as a **Data Quality Firewall**, ensuring that only records meeting strict integrity standards reach the end-user dashboard.

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **Data Validation:** Pydantic (Schema enforcement & Business Logic)
* **Visualization:** Streamlit & Plotly (Real-time Observability)
* **Testing & Automation:** Pytest (SLA & Performance Benchmarking)
* **CI/CD:** GitHub Actions (Automated Quality Gates)

## 🏗️ Architecture: The 4 Layers of Quality

1.  **Dynamic Ingestion Layer:** Uses a specialized API Client to discover countries and indicators on the fly, avoiding hardcoded dependencies.
2.  **Validation Layer (Pydantic):** Enforces strict data contracts. It detects anomalies like future dates, negative values, or type mismatches before data reaches the storage or visualization layers.
3.  **Observability Layer (Streamlit):** A professional dashboard that displays a **Data Health Score**—a critical KPI that measures the percentage of valid data received from the provider.
4.  **Automated Quality Gates (SLAs):** * *Performance SLA:* Ensures API response is consistently under 1.5 seconds.
    * *Completeness SLA:* Validates that the data source provides at least a 70% threshold of historical records.

## 📊 Real-World Insight: The "Brazil Case"
During automated testing, this framework successfully identified a **Data Completeness failure** in Brazil's health expenditure records (currently at 48% vs. the required 70%). This demonstrates the system's ability to protect downstream analytics from significant bias and missing values.

## ⚙️ Setup & Execution

### 1. Clone and Setup Environment:
```bash
git clone <your-repo-url>
cd health-data-quality
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt