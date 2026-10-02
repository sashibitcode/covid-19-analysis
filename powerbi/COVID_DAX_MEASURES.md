# Power BI Data Modeling & DAX Measures Guide

This document defines the dimensional modeling strategy, star schema architecture, and production-ready **DAX (Data Analysis Expressions)** measures for building high-performance executive dashboards in **Power BI**.

---

## 🏛️ Data Architecture & Star Schema

```
                     ┌──────────────────────┐
                     │     Dim_Date         │
                     │  Date, Year, Month,  │
                     │  Week, DayOfWeek     │
                     └──────────┬───────────┘
                                │ 1:N
                                ▼
┌───────────────────┐    ┌───────────────────────────┐    ┌─────────────────────┐
│  Dim_WHORegion    ├───►│     Fact_DailyCases       │◄───┤    Dim_Country      │
│  WHO_Region_ID,   │ 1:N│  Date, Country, Confirmed,│ 1:N│  Country, Continent,│
│  Region_Name      │    │  Deaths, Recovered, Active│    │  Population         │
└───────────────────┘    └───────────────────────────┘    └──────────┬──────────┘
                                                                     │ 1:1
                                                                     ▼
                                                          ┌─────────────────────┐
                                                          │ Fact_CountrySnapshot│
                                                          │ Country, Tests, CFR │
                                                          │ Critical, 1Wk_Change│
                                                          └─────────────────────┘
```

---

## 📐 Core Aggregation Measures

### 1. Total Confirmed Cases
```dax
Total Confirmed = 
SUM('Fact_DailyCases'[Confirmed])
```

### 2. Total Deaths
```dax
Total Deaths = 
SUM('Fact_DailyCases'[Deaths])
```

### 3. Total Recoveries
```dax
Total Recoveries = 
SUM('Fact_DailyCases'[Recovered])
```

### 4. Active Cases
```dax
Active Cases = 
[Total Confirmed] - [Total Deaths] - [Total Recoveries]
```

### 5. Daily New Cases
```dax
Daily New Cases = 
SUM('Fact_DailyCases'[New cases])
```

---

## 📊 Rate & Outcome Measures

### 6. Case Fatality Rate (CFR %)
```dax
Case Fatality Rate % = 
DIVIDE([Total Deaths], [Total Confirmed], 0) * 100
```

### 7. Recovery Rate (%)
```dax
Recovery Rate % = 
DIVIDE([Total Recoveries], [Total Confirmed], 0) * 100
```

### 8. Active Case Proportion (%)
```dax
Active Rate % = 
DIVIDE([Active Cases], [Total Confirmed], 0) * 100
```

### 9. Critical Patient Burden (%)
```dax
Critical Burden % = 
DIVIDE(
    SUM('Fact_CountrySnapshot'[Serious,Critical]),
    [Active Cases],
    0
) * 100
```

---

## ⏱️ Time-Intelligence & Rolling Average Measures

### 10. 7-Day Moving Average of New Cases
```dax
New Cases 7D MA = 
AVERAGEX(
    DATESINPERIOD(
        'Dim_Date'[Date],
        LASTDATE('Dim_Date'[Date]),
        -7,
        DAY
    ),
    [Daily New Cases]
)
```

### 11. 14-Day Moving Average of Daily Deaths
```dax
New Deaths 14D MA = 
AVERAGEX(
    DATESINPERIOD(
        'Dim_Date'[Date],
        LASTDATE('Dim_Date'[Date]),
        -14,
        DAY
    ),
    SUM('Fact_DailyCases'[New deaths])
)
```

### 12. Week-over-Week (WoW) Confirmed Growth %
```dax
WoW Confirmed Growth % = 
VAR CurrentWeek = [Total Confirmed]
VAR PreviousWeek = 
    CALCULATE(
        [Total Confirmed],
        DATEADD('Dim_Date'[Date], -7, DAY)
    )
RETURN
    DIVIDE(CurrentWeek - PreviousWeek, PreviousWeek, 0) * 100
```

---

## 🏆 Ranking & Segmentation Measures

### 13. Country Rank within WHO Region
```dax
Rank in WHO Region = 
IF(
    HASONEVALUE('Dim_Country'[Country/Region]),
    RANKX(
        ALLEXCEPT('Dim_Country', 'Dim_WHORegion'[Region_Name]),
        [Total Confirmed],
        ,
        DESC,
        Dense
    )
)
```

### 14. Testing Penetration Category
```dax
Testing Penetration Tier = 
VAR TestsPerMillion = MAX('Fact_CountrySnapshot'[Tests/1M pop])
RETURN
    SWITCH(
        TRUE(),
        TestsPerMillion >= 200000, "Tier 1: High Coverage (>=200k/1M)",
        TestsPerMillion >= 100000, "Tier 2: Moderate Coverage (100k-200k/1M)",
        TestsPerMillion >= 25000,  "Tier 3: Emerging Coverage (25k-100k/1M)",
        "Tier 4: Low Coverage (<25k/1M)"
    )
```

### 15. CFR Severity Benchmark
```dax
CFR Severity Benchmark = 
SWITCH(
    TRUE(),
    [Case Fatality Rate %] >= 8.0, "Critical Severity (>=8%)",
    [Case Fatality Rate %] >= 4.0, "High Severity (4-8%)",
    [Case Fatality Rate %] >= 2.0, "Moderate Severity (2-4%)",
    "Low Severity (<2%)"
)
```

---

## 🖥️ Recommended Visual Layouts
1. **Executive KPI Ribbon**: Total Confirmed, Active Cases, Total Recovered, Case Fatality Rate (CFR %).
2. **Global Infection Curve**: Line chart with `New Cases 7D MA` and `New Deaths 14D MA`.
3. **Regional Decomposition**: Treemap of WHO Regions with drill-down to countries.
4. **Diagnostic Correlation Matrix**: Scatter chart with `Tests/1M pop` (X-axis) vs. `Tot Cases/1M pop` (Y-axis) with bubble size = `Total Confirmed`.
