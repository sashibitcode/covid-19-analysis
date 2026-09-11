# COVID-19 Analysis

An end-to-end data analysis project covering COVID-19 data cleaning, validation, exploratory analysis, visualization, and SQL reporting.

## Overview

This project transforms raw COVID-19 CSV datasets into analysis-ready tables and decision-friendly outputs. The workflow focuses on global trends, country comparisons, regional summaries, case outcomes, and daily changes over time.

## Analysis Workflow

1. Read the daily and country-level source datasets.
2. Normalize dates and numeric fields.
3. Remove duplicate records and validate required fields.
4. Create derived measures for active cases and outcome rates.
5. Generate country, regional, and time-series analysis outputs.
6. Export cleaned data, summary files, and charts.
7. Run basic and advanced SQL queries against the cleaned tables.

## Run the Analysis

From the project root:

```powershell
python src/covid_analysis.py
```

The pipeline reads `data/day_wise.csv` and `data/country_wise_latest.csv` and writes refreshed outputs to `data/cleaned/` and `outputs/`.

## Key Metrics

- `Active Cases = Confirmed - Deaths - Recovered`
- `Death Rate = Deaths / Confirmed * 100`
- `Recovery Rate = Recovered / Confirmed * 100`
- `Active Rate = Active Cases / Confirmed * 100`

Rates are calculated safely for zero-case records and rounded to two decimal places.

## Project Structure

```text
covid-19-analysis/
|-- data/
|   |-- cleaned/                 # Pipeline-generated analysis tables
|   |-- day_wise.csv             # Global daily time series
|   |-- country_wise_latest.csv  # Country-level latest snapshot
|   `-- ...                      # Additional source datasets
|-- outputs/
|   |-- figures/                 # Generated charts
|   |-- eda_summary.json         # Key analysis findings
|   |-- regional_summary.csv     # WHO-region aggregation
|   `-- top_10_countries.csv     # Highest confirmed case counts
|-- sql/
|   |-- schema.sql               # Cleaned-table definitions
|   `-- analysis_queries.sql     # Basic and advanced SQL analysis
|-- src/
|   `-- covid_analysis.py        # Cleaning, EDA, visualization, validation
`-- README.md
```

## Generated Outputs

The pipeline produces:

- Cleaned daily and country-level CSV files.
- Global confirmed, death, recovery, and active-case trend chart.
- Top 10 countries by confirmed cases chart.
- WHO-region confirmed-case comparison chart.
- Regional and top-country summary tables.
- A JSON summary containing the main verified findings.

## Data Quality Validation

The pipeline validates:

- Required columns and parseable dates.
- Unique daily dates and country names.
- Non-negative confirmed, death, and recovery counts.
- Duplicate removal at the row and country levels.
- Correct active-case calculations.

The source profile contains 188 daily records and 187 countries, with no initial missing values or exact duplicate rows in the primary datasets.

## Verified Findings

- **Coverage:** January 22, 2020 to July 27, 2020.
- **Latest snapshot:** 16,480,485 confirmed cases, 654,036 deaths, 9,468,087 recoveries, and 6,358,362 active cases.
- **Peak daily increase:** 282,756 new cases on July 23, 2020.
- **Highest confirmed count:** United States (`US`).
- **Highest calculated death rate:** Yemen in the country snapshot. Small case counts can produce unusually high rates, so this metric should be interpreted with case volume.

## SQL Analysis

The SQL layer is designed for SQLite-compatible workflows. Use [sql/schema.sql](sql/schema.sql) to define tables for the cleaned files, then run [sql/analysis_queries.sql](sql/analysis_queries.sql).

Included analyses cover:

- Latest global snapshot and top countries.
- WHO-region aggregation.
- Seven-day moving average of new cases.
- Country ranking within each WHO region.
- High case burden versus below-average recovery rate.
- Day-over-day confirmed-case change using `LAG`.

## Source Data

The repository also includes grouped, worldometer, and US county-level datasets for future extensions such as county comparisons, regional time series, and location-specific analysis.
