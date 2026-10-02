import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"


def setup_plotting_theme():
    """Sets a clean, publication-grade visualization style."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        "figure.autolayout": True,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "semibold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 16,
    })


def plot_testing_vs_cases(worldometer_df: pd.DataFrame):
    """Log-scale scatter plot showing testing intensity versus cases per million."""
    df = worldometer_df[(worldometer_df["Tests/1M pop"] > 0) & (worldometer_df["Tot Cases/1M pop"] > 0)].copy()

    plt.figure(figsize=(11, 7))
    palette = sns.color_palette("tab10", n_colors=df["WHO Region"].nunique())
    ax = sns.scatterplot(
        data=df,
        x="Tests/1M pop",
        y="Tot Cases/1M pop",
        hue="WHO Region",
        size="TotalCases",
        sizes=(40, 600),
        palette=palette,
        alpha=0.8,
        edgecolor="black",
        linewidth=0.5
    )

    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.title("Testing Intensity vs. COVID-19 Case Detection per Million Population")
    plt.xlabel("Diagnostic Tests per 1M Population (Log Scale)")
    plt.ylabel("Confirmed Cases per 1M Population (Log Scale)")

    # Annotate prominent outlier countries
    key_countries = ["USA", "India", "Brazil", "Russia", "South Africa", "UK", "Chile", "New Zealand"]
    for _, row in df.iterrows():
        if row["Country/Region"] in key_countries:
            ax.annotate(
                row["Country/Region"],
                (row["Tests/1M pop"], row["Tot Cases/1M pop"]),
                textcoords="offset points",
                xytext=(6, 6),
                fontsize=8,
                fontweight="bold"
            )

    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.savefig(FIGURE_DIR / "testing_vs_cases_per_million.png", dpi=160, bbox_inches="tight")
    plt.close()


def plot_case_fatality_quadrant(worldometer_df: pd.DataFrame):
    """Quadrant analysis comparing Case Fatality Rate vs. Recovery Rate."""
    df = worldometer_df[(worldometer_df["TotalCases"] >= 5000) & (worldometer_df["Recovery_Rate"] > 0)].copy()

    mean_rec = df["Recovery_Rate"].median()
    mean_cfr = df["Case_Fatality_Rate"].median()

    plt.figure(figsize=(10, 6.5))
    ax = sns.scatterplot(
        data=df,
        x="Recovery_Rate",
        y="Case_Fatality_Rate",
        hue="WHO Region",
        size="TotalCases",
        sizes=(40, 500),
        alpha=0.75,
        palette="Set2"
    )

    plt.axvline(mean_rec, color="gray", linestyle="--", linewidth=1.2, label=f"Median Recovery ({mean_rec:.1f}%)")
    plt.axhline(mean_cfr, color="crimson", linestyle="--", linewidth=1.2, label=f"Median CFR ({mean_cfr:.1f}%)")

    # Quadrant annotations
    plt.text(5, df["Case_Fatality_Rate"].max() * 0.9, "High Fatalities / Low Recovery (Vulnerable)", color="darkred", fontweight="bold", fontsize=9)
    plt.text(mean_rec + 5, 1, "High Recovery / Low Fatalities (Resilient)", color="darkgreen", fontweight="bold", fontsize=9)

    plt.title("Epidemiological Quadrant: Recovery Rate vs. Case Fatality Rate (CFR)")
    plt.xlabel("Recovery Rate (%)")
    plt.ylabel("Case Fatality Rate (%)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.savefig(FIGURE_DIR / "case_fatality_quadrant.png", dpi=160, bbox_inches="tight")
    plt.close()


def plot_top_country_trajectories():
    """Plots 7-day rolling average epidemic curve for the top affected countries."""
    df = pd.read_csv(DATA_DIR / "full_grouped.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    # Find top 6 countries by final confirmed cases
    top_countries = (
        df.groupby("Country/Region")["Confirmed"].max()
        .nlargest(6).index.tolist()
    )

    filtered = df[df["Country/Region"].isin(top_countries)].copy()
    filtered = filtered.sort_values(["Country/Region", "Date"])
    filtered["New_Cases_7d_MA"] = (
        filtered.groupby("Country/Region")["New cases"]
        .rolling(7, min_periods=1)
        .mean()
        .reset_index(drop=True)
    )

    plt.figure(figsize=(12, 6.5))
    sns.lineplot(
        data=filtered,
        x="Date",
        y="New_Cases_7d_MA",
        hue="Country/Region",
        linewidth=2.4,
        palette="tab10"
    )

    plt.title("Epidemic Trajectory: 7-Day Rolling Average Daily Cases (Top 6 Countries)")
    plt.xlabel("Date")
    plt.ylabel("New Cases (7-Day Moving Avg)")
    plt.legend(title="Country", loc="upper left")
    plt.savefig(FIGURE_DIR / "top_countries_epic_trajectory.png", dpi=160, bbox_inches="tight")
    plt.close()


def plot_who_region_breakdown(regional_benchmarks_df: pd.DataFrame):
    """Compares confirmed cases and overall CFR per WHO region."""
    df = regional_benchmarks_df.copy().sort_values("Total_Confirmed", ascending=True)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar plot for total confirmed cases
    y_pos = np.arange(len(df))
    bars = ax1.barh(y_pos, df["Total_Confirmed"] / 1_000_000, color="#2b5c8f", height=0.55, label="Total Cases (Millions)")
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df["WHO Region"])
    ax1.set_xlabel("Confirmed Cases (Millions)", color="#2b5c8f")
    ax1.tick_params(axis="x", labelcolor="#2b5c8f")

    # Second axis for Case Fatality Rate
    ax2 = ax1.twiny()
    ax2.plot(df["Overall_CFR"], y_pos, color="#c92a2a", marker="o", linewidth=2.5, markersize=8, label="Case Fatality Rate (%)")
    ax2.set_xlabel("Overall Case Fatality Rate (%)", color="#c92a2a")
    ax2.tick_params(axis="x", labelcolor="#c92a2a")
    ax2.grid(False)

    plt.title("WHO Regional Case Burden vs. Overall Case Fatality Rate", pad=25)
    plt.savefig(FIGURE_DIR / "who_region_mortality_breakdown.png", dpi=160, bbox_inches="tight")
    plt.close()


def plot_active_vs_critical_ratio(worldometer_df: pd.DataFrame):
    """Examines serious/critical cases against active cases in high-case nations."""
    df = worldometer_df[(worldometer_df["ActiveCases"] > 10000) & (worldometer_df["Serious,Critical"] > 0)].copy()
    top_critical = df.sort_values("Serious,Critical", ascending=False).head(12)

    plt.figure(figsize=(11, 6))
    sns.barplot(
        data=top_critical,
        x="Serious,Critical",
        y="Country/Region",
        hue="Country/Region",
        palette="mako",
        legend=False
    )

    for i, v in enumerate(top_critical["Serious,Critical"]):
        plt.text(v + 100, i, f"{int(v):,} ({top_critical.iloc[i]['Critical_Patient_Ratio']:.1f}% active)", va="center", fontsize=9)

    plt.title("Top High-Burden Nations by Serious & Critical ICU Patient Volume")
    plt.xlabel("Critical / Serious Cases Count")
    plt.ylabel("")
    plt.savefig(FIGURE_DIR / "active_vs_critical_ratio.png", dpi=160, bbox_inches="tight")
    plt.close()


def main():
    setup_plotting_theme()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    from src.advanced_metrics import load_and_clean_worldometer, calculate_regional_benchmarks

    worldometer = load_and_clean_worldometer()
    regional = calculate_regional_benchmarks(worldometer)

    print("Generating epidemiological visualizations...")
    plot_testing_vs_cases(worldometer)
    print(" - testing_vs_cases_per_million.png generated")
    plot_case_fatality_quadrant(worldometer)
    print(" - case_fatality_quadrant.png generated")
    plot_top_country_trajectories()
    print(" - top_countries_epic_trajectory.png generated")
    plot_who_region_breakdown(regional)
    print(" - who_region_mortality_breakdown.png generated")
    plot_active_vs_critical_ratio(worldometer)
    print(" - active_vs_critical_ratio.png generated")
    print("All 5 publication-quality figures successfully created!")


if __name__ == "__main__":
    main()
