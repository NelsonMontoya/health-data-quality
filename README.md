# 🛡️ Strategic Data Quality Hub & Predictive Auditor

This project is a high-performance **Data Intelligence Platform** designed to audit, validate, and forecast global indicators from the World Bank API. It transforms raw, potentially unreliable data into high-confidence executive insights through a multi-layered Data Engineering and Machine Learning approach.

## 🚀 The Core Innovation: The Data Quality Firewall
In modern data environments, "Silent Failures" and "Data Drift" can lead to catastrophic business decisions. This framework acts as a **Data Quality Firewall**, enforcing a strict **80% Integrity Gate**. If a dataset fails to meet this threshold of completeness, it is flagged as **REJECTED**, protecting downstream analytics from significant bias.

---

## 🏗️ Evolution of the Framework: Key Development Steps

### Step 2: Statistical Correlation Engine
The platform has evolved from simple data fetching to identifying complex relationships between global KPIs.
* **Pearson Correlation:** Implements real-time calculation of the $r$ coefficient to measure the strength and direction of relationships between indicators (e.g., GDP vs. Education Expenditure).
* **Diagnostic Analytics:** Uses **Ordinary Least Squares (OLS)** through `statsmodels` to provide a trendline that helps verify if two variables move in harmony or opposition.

### Step 3: Machine Learning (Predictive Analytics)
The "Grand Finale" of the analytical engine is its ability to project the future using non-linear models.
* **Polynomial Regression:** Instead of simple straight lines, the system uses `scikit-learn` to fit curves of degree $n$, capturing the natural fluctuations of economic data.
* **Automated Forecasting:** Users can define a forecast horizon (1-15 years) to visualize where a country is heading by 2030 and beyond, using the equation:
    $$y = \beta_0 + \beta_1 x + \beta_2 x^2 + \dots + \beta_n x^n + \epsilon$$

---
```bash
# Clone the repository
git clone <your-repo-url>
cd health-data-quality

```

# Create and activate a virtual environment
```bash
git clone <your-repo-url>
cd health-data-quality
```

# Install primary dependencies
pip install -r requirements.txt

# Essential for capturing visual trend analysis into PDF
pip install kaleido==0.2.1

# Launch Platform
streamlit run main_dashboard.py

```

## 📋 Project Structure
The repository is organized following professional modularity standards to ensure scalability:

```text
health-data-quality/
├── app/
│   ├── client.py        # Resilient API Client for World Bank data.
│   ├── models.py        # Pydantic validation models (The Quality Firewall).
│   ├── database.py      # Persistence layer using DuckDB (OLAP).
│   └── reports.py       # Executive PDF generation engine (FPDF2).
├── main_dashboard.py    # Main UI Orchestrator (Streamlit).
├── requirements.txt     # System dependencies.
└── README.md            # Project documentation.

