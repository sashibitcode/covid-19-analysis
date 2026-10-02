from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"


def load_and_clean_worldometer() -> pd.DataFrame:
    """Loads and standardizes Worldometer country-level epidemiological metrics."""
    df = pd.read_csv(DATA_DIR / "worldometer_data.csv")

    numeric_cols = [
        "Population", "TotalCases", "NewCases", "TotalDeaths", "NewDeaths",
        "TotalRecovered", "NewRecovered", "ActiveCases", "Serious,Critical",
        "Tot Cases/1M pop", "Deaths/1M pop", "TotalTests", "Tests/1M pop"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Derived epidemiological metrics
    df["Case_Fatality_Rate"] = np.where(
        df["TotalCases"] > 0,
        (df["TotalDeaths"] / df["TotalCases"] * 100).round(2),
        0.0
    )
    df["Recovery_Rate"] = np.where(
        df["TotalCases"] > 0,
        (df["TotalRecovered"] / df["TotalCases"] * 100).round(2),
        0.0
    )
    df["Critical_Patient_Ratio"] = np.where(
        df["ActiveCases"] > 0,
        (df["Serious,Critical"] / df["ActiveCases"] * 100).round(2),
        0.0
    )
    df["Tests_Per_Case"] = np.where(
        df["TotalCases"] > 0,
        (df["TotalTests"] / df["TotalCases"]).round(1),
        0.0
    )
    df["Testing_Rate_Pct"] = np.where(
        df["Population"] > 0,
        (df["TotalTests"] / df["Population"] * 100).round(2),
        0.0
    )

    return df


def calculate_testing_vs_mortality(worldometer_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates correlation and comparison table between testing intensity and mortality."""
    # Filter countries with meaningful population and cases (>1000 cases)
    filtered = worldometer_df[worldometer_df["TotalCases"] >= 1000].copy()

    # Categorize testing intensity
    filtered["Testing_Tier"] = pd.qcut(
        filtered["Tests/1M pop"].rank(method="first"),
        q=4,
        labels=["Low Testing", "Moderate Testing", "High Testing", "Very High Testing"]
    )

    cols = [
        "Country/Region", "Continent", "WHO Region", "Population",
        "TotalCases", "TotalDeaths", "TotalRecovered", "ActiveCases",
        "Tot Cases/1M pop", "Deaths/1M pop", "Tests/1M pop",
        "Case_Fatality_Rate", "Recovery_Rate", "Critical_Patient_Ratio",
        "Tests_Per_Case", "Testing_Tier"
    ]
    return filtered[cols].sort_values("TotalCases", ascending=False).reset_index(drop=True)


def calculate_country_wave_peaks(min_cases: int = 50000) -> pd.DataFrame:
    """Identifies epidemic wave peaks and 7-day rolling trends using full_grouped daily series."""
    df = pd.read_csv(DATA_DIR / "full_grouped.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values(["Country/Region", "Date"]).reset_index(drop=True)

    # Compute 7-day rolling average per country
    df["New_Cases_7d_MA"] = (
        df.groupby("Country/Region")["New cases"]
        .rolling(window=7, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
        .round(1)
    )

    df["New_Deaths_7d_MA"] = (
        df.groupby("Country/Region")["New deaths"]
        .rolling(window=7, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
        .round(1)
    )

    # Filter to countries with significant case counts
    latest_totals = df.groupby("Country/Region")["Confirmed"].max()
    qualifying_countries = latest_totals[latest_totals >= min_cases].index.tolist()

    peak_records = []
    for country in qualifying_countries:
        c_df = df[df["Country/Region"] == country]
        max_idx = c_df["New_Cases_7d_MA"].idxmax()
        peak_row = c_df.loc[max_idx]
        total_cases = int(c_df["Confirmed"].max())
        total_deaths = int(c_df["Deaths"].max())

        peak_records.append({
            "Country/Region": country,
            "WHO Region": peak_row["WHO Region"],
            "Total_Confirmed": total_cases,
            "Total_Deaths": total_deaths,
            "Peak_Date": peak_row["Date"].strftime("%Y-%m-%d"),
            "Peak_7d_Avg_Cases": float(peak_row["New_Cases_7d_MA"]),
            "Peak_Daily_Cases": int(peak_row["New cases"]),
            "Latest_7d_Avg_Cases": float(c_df.iloc[-1]["New_Cases_7d_MA"]),
            "Trajectory": "Surging" if c_df.iloc[-1]["New_Cases_7d_MA"] >= 0.85 * peak_row["New_Cases_7d_MA"] else "Declining"
        })

    peaks_df = pd.DataFrame(peak_records).sort_values("Total_Confirmed", ascending=False).reset_index(drop=True)
    return peaks_df


def calculate_regional_benchmarks(worldometer_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates WHO regional summary benchmarks."""
    regional = (
        worldometer_df.groupby("WHO Region")
        .agg(
            Countries=("Country/Region", "count"),
            Total_Population=("Population", "sum"),
            Total_Confirmed=("TotalCases", "sum"),
            Total_Deaths=("TotalDeaths", "sum"),
            Total_Recovered=("TotalRecovered", "sum"),
            Total_Active=("ActiveCases", "sum"),
            Critical_Cases=("Serious,Critical", "sum"),
            Total_Tests=("TotalTests", "sum"),
        )
        .reset_index()
    )

    regional["Overall_CFR"] = (regional["Total_Deaths"] / regional["Total_Confirmed"] * 100).round(2)
    regional["Overall_Recovery_Rate"] = (regional["Total_Recovered"] / regional["Total_Confirmed"] * 100).round(2)
    regional["Cases_Per_Million"] = (
        regional["Total_Confirmed"] / (regional["Total_Population"] / 1_000_000)
    ).round(1)
    regional["Deaths_Per_Million"] = (
        regional["Total_Deaths"] / (regional["Total_Population"] / 1_000_000)
    ).round(1)

    return regional.sort_values("Total_Confirmed", ascending=False).reset_index(drop=True)


def run_advanced_pipeline() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    worldometer = load_and_clean_worldometer()
    testing_mortality = calculate_testing_vs_mortality(worldometer)
    wave_peaks = calculate_country_wave_peaks(min_cases=50000)
    regional_benchmarks = calculate_regional_benchmarks(worldometer)

    testing_mortality.to_csv(OUTPUT_DIR / "testing_vs_mortality.csv", index=False)
    wave_peaks.to_csv(OUTPUT_DIR / "country_wave_peaks.csv", index=False)
    regional_benchmarks.to_csv(OUTPUT_DIR / "regional_benchmarks.csv", index=False)

    summary = {
        "total_countries_analyzed": len(worldometer),
        "qualifying_wave_peak_countries": len(wave_peaks),
        "regions_covered": len(regional_benchmarks),
        "global_total_cases": int(worldometer["TotalCases"].sum()),
        "global_total_deaths": int(worldometer["TotalDeaths"].sum()),
        "global_tests_conducted": int(worldometer["TotalTests"].sum()),
    }

    print("Advanced Metrics Pipeline Completed:")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    run_advanced_pipeline()
