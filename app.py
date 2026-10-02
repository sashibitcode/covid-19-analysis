"""
COVID-19 Global Analytics & Epidemiological Intelligence Dashboard
Interactive Streamlit Web Application
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CLEAN_DIR = DATA_DIR / "cleaned"
OUTPUT_DIR = ROOT / "outputs"
DB_PATH = ROOT / "covid_analysis.db"

st.set_page_config(
    page_title="COVID-19 Global Analytics Hub",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        color: white;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; }
    .metric-val { font-size: 1.8rem; font-weight: bold; margin-top: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_datasets():
    # 1. Day-wise clean
    day_df = pd.read_csv(CLEAN_DIR / "day_wise_clean.csv")
    day_df["Date"] = pd.to_datetime(day_df["Date"])

    # 2. Country-wise clean
    country_df = pd.read_csv(CLEAN_DIR / "country_wise_clean.csv")

    # 3. Worldometer data
    worldometer_path = DATA_DIR / "worldometer_data.csv"
    worldometer_df = pd.read_csv(worldometer_path) if worldometer_path.exists() else pd.DataFrame()

    # 4. Full grouped daily series
    full_path = DATA_DIR / "full_grouped.csv"
    full_df = pd.read_csv(full_path) if full_path.exists() else pd.DataFrame()
    if not full_df.empty:
        full_df["Date"] = pd.to_datetime(full_df["Date"])

    return day_df, country_df, worldometer_df, full_df


day_df, country_df, worldometer_df, full_df = load_datasets()

# Sidebar controls
st.sidebar.title("🦠 COVID-19 Analytics")
st.sidebar.markdown("**Global Pandemic Tracking & Epidemiological Intelligence Platform**")
st.sidebar.markdown("---")

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(day_df["Date"].min(), day_df["Date"].max()),
    min_value=day_df["Date"].min(),
    max_value=day_df["Date"].max()
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_day = day_df[(day_df["Date"] >= start_date) & (day_df["Date"] <= end_date)]
else:
    filtered_day = day_df

latest_record = filtered_day.iloc[-1] if not filtered_day.empty else day_df.iloc[-1]

# Header Metrics
st.title("🌐 COVID-19 Global Pandemic Intelligence Hub")
st.caption(f"Data period: {day_df['Date'].min().strftime('%B %d, %Y')} – {day_df['Date'].max().strftime('%B %d, %Y')} | 187 Countries tracked")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #3b82f6;">
        <div class="metric-title">Total Confirmed</div>
        <div class="metric-val">{int(latest_record['Confirmed']):,}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #ef4444;">
        <div class="metric-title">Total Deaths</div>
        <div class="metric-val">{int(latest_record['Deaths']):,}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #10b981;">
        <div class="metric-title">Total Recovered</div>
        <div class="metric-val">{int(latest_record['Recovered']):,}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #f59e0b;">
        <div class="metric-title">Active Cases</div>
        <div class="metric-val">{int(latest_record['Active Cases']):,}</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    cfr = (latest_record['Deaths'] / latest_record['Confirmed'] * 100) if latest_record['Confirmed'] > 0 else 0
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #8b5cf6;">
        <div class="metric-title">Case Fatality Rate</div>
        <div class="metric-val">{cfr:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Global Pandemic Pulse",
    "🌍 Country Trajectories & Waves",
    "🧪 Testing & Clinical Severity",
    "🏛️ WHO Regional Comparison",
    "⚡ Interactive SQL Engine"
])

# ----------------- TAB 1: Global Pulse -----------------
with tab1:
    st.subheader("Global Cumulative Infection & Outcome Trajectory")
    col_t1a, col_t1b = st.columns([2, 1])

    with col_t1a:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(filtered_day["Date"], filtered_day["Confirmed"] / 1e6, label="Confirmed", color="#3b82f6", linewidth=2.5)
        ax.plot(filtered_day["Date"], filtered_day["Recovered"] / 1e6, label="Recovered", color="#10b981", linewidth=2)
        ax.plot(filtered_day["Date"], filtered_day["Active Cases"] / 1e6, label="Active", color="#f59e0b", linewidth=2)
        ax.plot(filtered_day["Date"], filtered_day["Deaths"] / 1e6, label="Deaths", color="#ef4444", linewidth=2)
        ax.set_ylabel("Cases (Millions)")
        ax.set_xlabel("Date")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        st.pyplot(fig)
        plt.close()

    with col_t1b:
        st.markdown("#### Outcome Distribution Snapshot")
        rec_pct = (latest_record['Recovered'] / latest_record['Confirmed']) * 100
        act_pct = (latest_record['Active Cases'] / latest_record['Confirmed']) * 100
        dea_pct = (latest_record['Deaths'] / latest_record['Confirmed']) * 100

        fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
        ax_pie.pie(
            [rec_pct, act_pct, dea_pct],
            labels=[f"Recovered ({rec_pct:.1f}%)", f"Active ({act_pct:.1f}%)", f"Deaths ({dea_pct:.1f}%)"],
            colors=["#10b981", "#f59e0b", "#ef4444"],
            startangle=140,
            wedgeprops=dict(width=0.4, edgecolor='w')
        )
        st.pyplot(fig_pie)
        plt.close()

    st.subheader("Daily Global New Cases with 7-Day Moving Average")
    fig_daily, ax_daily = plt.subplots(figsize=(12, 4))
    ma7 = filtered_day["New cases"].rolling(7, min_periods=1).mean()
    ax_daily.bar(filtered_day["Date"], filtered_day["New cases"], color="#cbd5e1", alpha=0.6, label="Daily Reported Cases")
    ax_daily.plot(filtered_day["Date"], ma7, color="#dc2626", linewidth=2.5, label="7-Day Moving Average")
    ax_daily.set_ylabel("New Daily Cases")
    ax_daily.grid(True, linestyle="--", alpha=0.5)
    ax_daily.legend()
    st.pyplot(fig_daily)
    plt.close()

# ----------------- TAB 2: Country Trajectories -----------------
with tab2:
    st.subheader("Multi-Country Epidemic Curve Comparison")
    if not full_df.empty:
        all_countries = sorted(full_df["Country/Region"].unique().tolist())
        selected_countries = st.multiselect(
            "Select Countries to Compare (7-Day Rolling Moving Average)",
            options=all_countries,
            default=["US", "Brazil", "India", "Russia", "United Kingdom", "South Africa"]
        )

        if selected_countries:
            c_data = full_df[full_df["Country/Region"].isin(selected_countries)].copy()
            c_data = c_data.sort_values(["Country/Region", "Date"])
            c_data["7d_MA"] = (
                c_data.groupby("Country/Region")["New cases"]
                .rolling(7, min_periods=1)
                .mean()
                .reset_index(drop=True)
            )

            fig_ct, ax_ct = plt.subplots(figsize=(11, 5.5))
            for country in selected_countries:
                subset = c_data[c_data["Country/Region"] == country]
                ax_ct.plot(subset["Date"], subset["7d_MA"], label=country, linewidth=2.2)

            ax_ct.set_title("7-Day Rolling Moving Average of New Daily Cases", fontsize=13, fontweight="bold")
            ax_ct.set_xlabel("Date")
            ax_ct.set_ylabel("Daily Cases (7D MA)")
            ax_ct.legend(loc="upper left")
            ax_ct.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig_ct)
            plt.close()

        st.markdown("#### Country Snapshot Rankings")
        st.dataframe(
            country_df[["Country/Region", "Confirmed", "Deaths", "Recovered", "Active Cases", "Death Rate", "Recovery Rate", "WHO Region"]]
            .sort_values("Confirmed", ascending=False)
            .reset_index(drop=True),
            use_container_width=True
        )

# ----------------- TAB 3: Testing & Clinical Severity -----------------
with tab3:
    st.subheader("Diagnostic Testing Penetration vs. Case Detection")
    if not worldometer_df.empty:
        w_df = worldometer_df[(worldometer_df["Tests/1M pop"] > 0) & (worldometer_df["Tot Cases/1M pop"] > 0)].copy()

        fig_sc, ax_sc = plt.subplots(figsize=(10, 5.5))
        scatter = ax_sc.scatter(
            w_df["Tests/1M pop"],
            w_df["Tot Cases/1M pop"],
            c=np.log10(w_df["TotalCases"].clip(lower=1)),
            cmap="viridis",
            alpha=0.75,
            edgecolors="none",
            s=80
        )
        ax_sc.set_xscale("log")
        ax_sc.set_yscale("log")
        ax_sc.set_xlabel("Diagnostic Tests conducted per 1M Population (Log Scale)")
        ax_sc.set_ylabel("Total Confirmed Cases per 1M Population (Log Scale)")
        cbar = plt.colorbar(scatter, ax=ax_sc)
        cbar.set_label("Log10(Total Confirmed Cases)")
        ax_sc.grid(True, which="both", linestyle="--", alpha=0.5)
        st.pyplot(fig_sc)
        plt.close()

        col_t3a, col_t3b = st.columns(2)
        with col_t3a:
            st.markdown("#### Top 10 Nations by Serious & Critical ICU Patients")
            top_crit = w_df.sort_values("Serious,Critical", ascending=False).head(10)
            fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
            ax_bar.barh(top_crit["Country/Region"], top_crit["Serious,Critical"], color="#e11d48")
            ax_bar.invert_yaxis()
            ax_bar.set_xlabel("Serious / Critical Patients")
            st.pyplot(fig_bar)
            plt.close()

        with col_t3b:
            st.markdown("#### Highest Case Fatality Rates (Min 10,000 Cases)")
            high_cfr = (
                w_df[w_df["TotalCases"] >= 10000]
                .assign(CFR=lambda x: (x["TotalDeaths"] / x["TotalCases"] * 100).round(2))
                .sort_values("CFR", ascending=False)
                .head(10)[["Country/Region", "TotalCases", "TotalDeaths", "CFR"]]
            )
            st.dataframe(high_cfr, use_container_width=True)

# ----------------- TAB 4: WHO Regional Analysis -----------------
with tab4:
    st.subheader("WHO Regional Epidemiological Comparison")
    reg_summary = (
        country_df.groupby("WHO Region")
        .agg(
            Total_Confirmed=("Confirmed", "sum"),
            Total_Deaths=("Deaths", "sum"),
            Total_Recovered=("Recovered", "sum"),
            Active_Cases=("Active Cases", "sum"),
            Countries=("Country/Region", "count")
        )
        .reset_index()
    )
    reg_summary["CFR (%)"] = (reg_summary["Total_Deaths"] / reg_summary["Total_Confirmed"] * 100).round(2)
    reg_summary["Recovery Rate (%)"] = (reg_summary["Total_Recovered"] / reg_summary["Total_Confirmed"] * 100).round(2)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        fig_r1, ax_r1 = plt.subplots(figsize=(7, 4.5))
        sorted_reg = reg_summary.sort_values("Total_Confirmed", ascending=True)
        ax_r1.barh(sorted_reg["WHO Region"], sorted_reg["Total_Confirmed"] / 1e6, color="#0284c7")
        ax_r1.set_xlabel("Confirmed Cases (Millions)")
        ax_r1.set_title("Confirmed Cases by WHO Region", fontsize=12, fontweight="bold")
        st.pyplot(fig_r1)
        plt.close()

    with col_r2:
        fig_r2, ax_r2 = plt.subplots(figsize=(7, 4.5))
        ax_r2.barh(sorted_reg["WHO Region"], sorted_reg["CFR (%)"], color="#dc2626")
        ax_r2.set_xlabel("Case Fatality Rate (%)")
        ax_r2.set_title("Case Fatality Rate by WHO Region", fontsize=12, fontweight="bold")
        st.pyplot(fig_r2)
        plt.close()

    st.dataframe(reg_summary.sort_values("Total_Confirmed", ascending=False), use_container_width=True)

# ----------------- TAB 5: Live SQL Engine -----------------
with tab5:
    st.subheader("⚡ Live SQL Analytics Query Console")
    st.markdown("Execute queries directly on SQLite database (`covid_analysis.db`) containing `day_wise_clean`, `country_wise_clean`, `worldometer_data`, and `full_grouped` tables.")

    preset_queries = {
        "Global Latest Snapshot": "SELECT Date, Confirmed, Deaths, Recovered, [Active Cases], [Death Rate], [Recovery Rate] FROM day_wise_clean ORDER BY Date DESC LIMIT 1;",
        "Top 10 Countries by Total Cases": "SELECT [Country/Region], Confirmed, Deaths, Recovered, [Active Cases], [Death Rate] FROM country_wise_clean ORDER BY Confirmed DESC LIMIT 10;",
        "7-Day Moving Average of Global Cases": "SELECT Date, [New cases], ROUND(AVG([New cases]) OVER (ORDER BY Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) as [7D_MA] FROM day_wise_clean ORDER BY Date DESC LIMIT 20;",
        "Regional Recovery & Mortality Benchmark": "SELECT [WHO Region], SUM(Confirmed) as TotalCases, SUM(Deaths) as TotalDeaths, ROUND(SUM(Deaths)*100.0/SUM(Confirmed), 2) as CFR_Pct FROM country_wise_clean GROUP BY [WHO Region] ORDER BY TotalCases DESC;",
        "High Burden & Low Recovery Countries": "SELECT [Country/Region], Confirmed, [Recovery Rate], [Death Rate] FROM country_wise_clean WHERE Confirmed > (SELECT AVG(Confirmed) FROM country_wise_clean) AND [Recovery Rate] < (SELECT AVG([Recovery Rate]) FROM country_wise_clean) ORDER BY Confirmed DESC LIMIT 15;"
    }

    selected_preset = st.selectbox("Select a Preset SQL Query or write your own below:", list(preset_queries.keys()))
    query_text = st.text_area("SQL Query Editor", value=preset_queries[selected_preset], height=120)

    if st.button("▶ Run SQL Query", type="primary"):
        if not DB_PATH.exists():
            from sql.build_sqlite_db import build_database
            build_database()

        try:
            conn = sqlite3.connect(DB_PATH)
            result_df = pd.read_sql_query(query_text, conn)
            conn.close()

            st.success(f"Query returned {len(result_df)} rows.")
            st.dataframe(result_df, use_container_width=True)

            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Query Result as CSV", data=csv, file_name="covid_sql_query_result.csv", mime="text/csv")
        except Exception as err:
            st.error(f"SQL Execution Error: {err}")
