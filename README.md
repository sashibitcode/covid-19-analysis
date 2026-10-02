# 🦠 COVID-19 Global Analytics & Epidemiological Intelligence Hub

[![CI Build](https://github.com/sashibitcode/covid-19-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/sashibitcode/covid-19-analysis/actions)
![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)

An end-to-end, production-grade data analytics and epidemiological intelligence ecosystem covering COVID-19 data engineering, time-series moving averages, publication visual analytics, automated SQLite database pipelines, interactive Streamlit dashboards, and Power BI dimensional modeling.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Data Layer
        D1[data/day_wise.csv]
        D2[data/country_wise_latest.csv]
        D3[data/worldometer_data.csv]
        D4[data/full_grouped.csv]
    end

    subgraph Processing & Analytics
        P1[src/covid_analysis.py<br/>Data Cleaning & Invariants]
        P2[src/advanced_metrics.py<br/>Testing Tiers & Wave Peaks]
        P3[src/generate_visualizations.py<br/>Publication Figures]
    end

    subgraph Storage & SQL Engine
        S1[(covid_analysis.db<br/>SQLite Engine)]
        S2[sql/analysis_queries.sql<br/>14 Analytical Queries]
        S3[sql/build_sqlite_db.py<br/>Automated Ingestion Pipeline]
    end

    subgraph Presentation & BI
        UI1[app.py<br/>Streamlit Multi-Tab Dashboard]
        UI2[powerbi/COVID_DAX_MEASURES.md<br/>Power BI Star Schema & DAX]
        UI3[docs/COVID19_EPIDEMIOLOGICAL_REPORT.md<br/>Executive Research Report]
    end

    Data Layer --> Processing & Analytics
    Processing & Analytics --> Storage & SQL Engine
    Storage & SQL Engine --> Presentation & BI
```

---

## 📂 Project Structure

```text
covid-19-analysis/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Multi-Python GitHub Actions CI workflow
├── data/
│   ├── cleaned/                       # Pipeline-generated clean tables
│   │   ├── day_wise_clean.csv
│   │   └── country_wise_clean.csv
│   ├── country_wise_latest.csv        # Cross-sectional latest country snapshot
│   ├── day_wise.csv                   # Global daily longitudinal time-series
│   ├── full_grouped.csv               # Country-level daily time-series (35k+ rows)
│   └── worldometer_data.csv           # Diagnostic testing & demographic metrics
├── docs/
│   └── COVID19_EPIDEMIOLOGICAL_REPORT.md # In-depth research & findings report
├── outputs/
│   ├── figures/                       # Publication-quality charts (160 DPI)
│   │   ├── active_vs_critical_ratio.png
│   │   ├── case_fatality_quadrant.png
│   │   ├── global_trend.png
│   │   ├── regional_cases.png
│   │   ├── testing_vs_cases_per_million.png
│   │   ├── top_10_countries.png
│   │   ├── top_countries_epic_trajectory.png
│   │   └── who_region_mortality_breakdown.png
│   ├── country_wave_peaks.csv         # 7-day MA wave peak records per nation
│   ├── eda_summary.json               # Automated EDA verification metrics
│   ├── regional_benchmarks.csv        # WHO regional summary metrics
│   └── testing_vs_mortality.csv       # Testing tiers and CFR correlation
├── powerbi/
│   └── COVID_DAX_MEASURES.md          # Power BI star schema & 15+ DAX formulas
├── sql/
│   ├── analysis_queries.sql           # 14 Advanced SQL analytical queries
│   ├── build_sqlite_db.py             # Automated SQLite database builder & validator
│   └── schema.sql                     # Table schemas with data types & constraints
├── src/
│   ├── advanced_metrics.py            # Epidemiological metrics & multi-source engine
│   ├── covid_analysis.py              # Core data cleaning, normalization & validation
│   └── generate_visualizations.py     # High-resolution Seaborn & Matplotlib visualizer
├── tests/
│   └── test_covid_analysis.py         # Automated unit test suite (100% passing)
├── app.py                             # Interactive Streamlit Web Application
├── requirements.txt                   # Pinned production dependencies
└── README.md                          # Repository documentation
```

---

## 🚀 Quickstart & Execution Guide

### 1. Environment Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Data Processing & Analysis Pipelines
```powershell
# Run core cleaning and invariant checks
python src/covid_analysis.py

# Run advanced epidemiological metrics engine
python src/advanced_metrics.py

# Generate publication-quality figures
python src/generate_visualizations.py
```

### 3. Build SQLite Database & Run 14 Analytical SQL Queries
```powershell
python sql/build_sqlite_db.py
```

### 4. Launch Interactive Streamlit Web Dashboard
```powershell
streamlit run app.py
```
> The dashboard will automatically launch at `http://localhost:8501` featuring 5 interactive tabs: Global Pulse, Country Waves, Testing Severity, WHO Regional Analysis, and the Live SQL Console.

### 5. Run Automated Unit Test Suite
```powershell
python -m unittest discover tests -v
```

---

## 📊 Key Epidemiological Metrics & Findings

| Metric | Verified Value | Epidemiological Context |
|---|---|---|
| **Coverage Period** | Jan 22 – Jul 27, 2020 | Primary first-wave pandemic escalation |
| **Total Global Infections** | **19,169,166** | Combined across 209 countries & territories |
| **Total Fatalities** | **713,007** | Global crude Case Fatality Rate: **3.72%** |
| **Total Recoveries** | **12,274,321** | Global recovery rate: **64.03%** |
| **Peak Single-Day Spike** | **282,756 cases** | July 23, 2020 |
| **Diagnostic Tests Logged** | **267,859,298** | High-testing tier countries exhibited 60% lower crude CFR |
| **Dominant Epicenter** | Americas (USA & Brazil) | Accounted for > 46% of total global cases |

---

## 🧪 SQL Analytics & Ingestion
The repository provides an automated SQLite ingestion pipeline ([`sql/build_sqlite_db.py`](sql/build_sqlite_db.py)) and 14 production queries ([`sql/analysis_queries.sql`](sql/analysis_queries.sql)):
- **Query 1-3**: Global totals, Top 10 countries, WHO regional breakdown.
- **Query 4**: 7-day moving average of global daily cases using Window Functions.
- **Query 5-7**: Dense regional rankings, low-recovery burden detection, and LAG day-over-day changes.
- **Query 8-10**: CFR risk categorizations, 14-day rolling death averages, and Week-over-Week (WoW) growth rates.
- **Query 11-14**: Top active-case concentrations per region, recovery efficiency benchmarks, and single-day peak rankings.

---

## 📈 Power BI & Dimensional Modeling
The [`powerbi/COVID_DAX_MEASURES.md`](powerbi/COVID_DAX_MEASURES.md) guide specifies:
- Star schema architecture linking Fact tables with Date, Country, and WHO Region dimensions.
- 15+ production DAX formulas including `Total Confirmed`, `Active Cases`, `Case Fatality Rate %`, `New Cases 7D MA`, and `WoW Confirmed Growth %`.

---

## 🛡️ License
This project is open-source and available under the [MIT License](LICENSE).
