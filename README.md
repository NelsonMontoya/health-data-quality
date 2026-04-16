# 🛡️ Global Health Data Quality & Observability Framework

This project is a **Data Integrity Engine** designed to audit, validate, and visualize global health indicators from the World Bank API. It transforms raw, potentially unreliable data into high-confidence business insights using a multi-layered QA and Data Engineering approach.

## 🚀 The Problem it Solves
Data-driven organizations often suffer from "Data Drift" or "Silent Failures" where API sources change formats or provide incomplete data. This framework acts as a **Data Quality Firewall**, ensuring that only records meeting strict integrity standards reach the end-user dashboard.

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **Data Validation:** Pydantic (Schema enforcement & Business Logic)
* **Visualization:** Streamlit & Plotly (Real-time Observability)
* **Testing & Automation:** Pytest (SLA & Performance Benchmarking)
* **CI/CD:** GitHub Actions (Automated Quality Gates)

## 🏗️ Architecture: The 4 Layers of Quality

1.  **Dynamic Ingestion Layer:** Uses an API Client to discover countries and indicators on the fly, avoiding hardcoded dependencies.
2.  **Validation Layer (Pydantic):** Enforces data contracts. It detects anomalies like future dates, negative values, or type mismatches before processing.
3.  **Observability Layer (Streamlit):** A professional dashboard that displays a **Data Health Score**—a KPI that measures the percentage of valid data received.
4.  **Automated Quality Gates:** Pytest suites that monitor **SLAs**. 
    * *Performance SLA:* API response must be < 1.5s.
    * *Completeness SLA:* Data source must be at least 70% complete.

## 📊 Real-World Insight: The "Brazil Case"
During automated testing, this framework successfully identified a **Data Completeness failure** in Brazil's health expenditure records (48% vs. required 70%). This demonstrates the system's ability to protect downstream analytics from significant bias and missing values.

## ⚙️ Setup & Execution

1. **Clone and Setup Environment:**
   ```bash
   git clone <your-repo-url>
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt