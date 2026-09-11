# COVID-19 Analysis

End-to-end COVID-19 data cleaning, exploratory analysis, visualization, and SQL practice project using the CSV files in `data/`.

## Run the pipeline

```powershell
python src/covid_analysis.py
```

The script reads `data/day_wise.csv` and `data/country_wise_latest.csv`, converts dates and numeric columns, removes duplicate rows, adds derived metrics, validates the result, and writes:

- `data/cleaned/day_wise_clean.csv`
- `data/cleaned/country_wise_clean.csv`
- `outputs/eda_summary.json`
- `outputs/top_10_countries.csv`
- `outputs/regional_summary.csv`
- `outputs/figures/global_trend.png`
- `outputs/figures/top_countries.png`
- `outputs/figures/regional_cases.png`

Derived columns are `Active Cases`, `Death Rate`, `Recovery Rate`, and `Active Rate`. Rates are percentages and are protected against division by zero.

## Dataset checks

The supplied primary files contain 188 daily records and 187 country records. The initial profile found no missing values or exact duplicate rows. The pipeline still performs duplicate removal and validation so the workflow remains useful if the source files change.

Validation checks include required columns, valid dates, unique dates/countries, non-negative core counts, and the active-case formula:

`Active Cases = Confirmed - Deaths - Recovered`

## Verified insights from this dataset

- Date coverage: `2020-01-22` to `2020-07-27`.
- Latest snapshot contains `16,480,485` confirmed cases, `654,036` deaths, `9,468,087` recoveries, and `6,358,362` active cases.
- The highest daily new-case value is `282,756` on `2020-07-23`.
- The country with the highest confirmed count is `US`.
- `Yemen` has the highest calculated death rate in the country snapshot; interpret rates alongside case volume because small denominators can produce extreme percentages.

## SQL analysis

`sql/schema.sql` defines SQLite-compatible tables for the cleaned files. Import the two cleaned CSVs into those tables, then run `sql/analysis_queries.sql`. The query file includes:

- latest global snapshot and top-country queries
- WHO-region aggregation
- seven-day moving average
- regional country ranking with window functions
- above-average case burden versus below-average recovery rate
- day-over-day confirmed-case change using `LAG`

The other source CSVs remain available for extensions such as county-level US analysis or grouped date-region analysis.
