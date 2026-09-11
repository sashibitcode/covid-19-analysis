from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CLEAN_DIR = DATA_DIR / "cleaned"
OUTPUT_DIR = ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"


def _numeric_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _add_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    frame["Active Cases"] = frame["Confirmed"] - frame["Deaths"] - frame["Recovered"]
    frame["Death Rate"] = (frame["Deaths"] / frame["Confirmed"].replace(0, pd.NA) * 100).round(2)
    frame["Recovery Rate"] = (frame["Recovered"] / frame["Confirmed"].replace(0, pd.NA) * 100).round(2)
    frame["Active Rate"] = (frame["Active Cases"] / frame["Confirmed"].replace(0, pd.NA) * 100).round(2)
    return frame


def clean_day_wise() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "day_wise.csv")
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    numeric = [column for column in frame.columns if column != "Date"]
    frame = _numeric_columns(frame, numeric).drop_duplicates().sort_values("Date")
    frame = _add_metrics(frame)
    return frame.reset_index(drop=True)


def clean_country_wise() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "country_wise_latest.csv")
    numeric = [column for column in frame.columns if column not in {"Country/Region", "WHO Region"}]
    frame = _numeric_columns(frame, numeric).drop_duplicates(subset=["Country/Region"]).reset_index(drop=True)
    frame = _add_metrics(frame)
    return frame


def make_eda_outputs(day: pd.DataFrame, country: pd.DataFrame) -> dict:
    sns.set_theme(style="whitegrid", palette="colorblind")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    latest = day.iloc[-1]
    global_totals = latest[["Confirmed", "Deaths", "Recovered", "Active Cases"]].to_dict()
    top_cases = country.nlargest(10, "Confirmed")[["Country/Region", "Confirmed", "Deaths", "Recovered"]]
    regional = country.groupby("WHO Region", as_index=False)[["Confirmed", "Deaths", "Recovered"]].sum()
    peak_new_cases = day.loc[day["New cases"].idxmax(), ["Date", "New cases"]].to_dict()
    summary = {
        "date_range": [day["Date"].min().strftime("%Y-%m-%d"), day["Date"].max().strftime("%Y-%m-%d")],
        "latest_date_totals": {key: int(value) for key, value in global_totals.items()},
        "peak_new_cases": {"Date": peak_new_cases["Date"].strftime("%Y-%m-%d"), "New cases": int(peak_new_cases["New cases"])},
        "highest_confirmed_country": str(country.loc[country["Confirmed"].idxmax(), "Country/Region"]),
        "highest_death_rate_country": str(country.loc[country["Death Rate"].idxmax(), "Country/Region"]),
        "countries_in_dataset": int(country["Country/Region"].nunique()),
    }
    top_cases.to_csv(OUTPUT_DIR / "top_10_countries.csv", index=False)
    regional.to_csv(OUTPUT_DIR / "regional_summary.csv", index=False)
    (OUTPUT_DIR / "eda_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    plt.figure(figsize=(12, 6))
    for column, color in [("Confirmed", "#0b7285"), ("Recovered", "#2f9e44"), ("Deaths", "#c92a2a"), ("Active Cases", "#f08c00")]:
        plt.plot(day["Date"], day[column], label=column, linewidth=2)
    plt.title("Global COVID-19 Trend")
    plt.xlabel("Date")
    plt.ylabel("Cases")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "global_trend.png", dpi=160)
    plt.close()

    plot_data = top_cases.sort_values("Confirmed")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=plot_data, x="Confirmed", y="Country/Region", color="#0b7285")
    plt.title("Top 10 Countries by Confirmed Cases")
    plt.xlabel("Confirmed cases")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "top_countries.png", dpi=160)
    plt.close()

    regional_plot = regional.sort_values("Confirmed")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=regional_plot, x="Confirmed", y="WHO Region", color="#f08c00")
    plt.title("Confirmed Cases by WHO Region")
    plt.xlabel("Confirmed cases")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "regional_cases.png", dpi=160)
    plt.close()
    return summary


def validate(day: pd.DataFrame, country: pd.DataFrame) -> None:
    required_day = {"Date", "Confirmed", "Deaths", "Recovered", "Active Cases", "Death Rate", "Recovery Rate"}
    required_country = {"Country/Region", "Confirmed", "Deaths", "Recovered", "Active Cases", "Death Rate", "Recovery Rate"}
    assert required_day.issubset(day.columns)
    assert required_country.issubset(country.columns)
    assert day["Date"].notna().all()
    assert not day.duplicated(subset=["Date"]).any()
    assert not country.duplicated(subset=["Country/Region"]).any()
    assert (day[["Confirmed", "Deaths", "Recovered"]] >= 0).all().all()
    assert (country[["Confirmed", "Deaths", "Recovered"]] >= 0).all().all()
    assert (day["Active Cases"] == day["Confirmed"] - day["Deaths"] - day["Recovered"]).all()
    assert (country["Active Cases"] == country["Confirmed"] - country["Deaths"] - country["Recovered"]).all()


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    day = clean_day_wise()
    country = clean_country_wise()
    validate(day, country)
    day.to_csv(CLEAN_DIR / "day_wise_clean.csv", index=False, date_format="%Y-%m-%d")
    country.to_csv(CLEAN_DIR / "country_wise_clean.csv", index=False)
    summary = make_eda_outputs(day, country)
    print(json.dumps(summary, indent=2))
    print("Validation passed; cleaned CSVs and EDA outputs created.")


if __name__ == "__main__":
    main()
