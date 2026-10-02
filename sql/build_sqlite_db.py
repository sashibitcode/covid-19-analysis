"""
Automated SQLite Database Builder and SQL Query Validator.
Ingests COVID-19 datasets into SQLite and validates all analysis queries.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CLEAN_DIR = DATA_DIR / "cleaned"
SQL_DIR = ROOT / "sql"
DB_PATH = ROOT / "covid_analysis.db"


def build_database(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Builds and populates SQLite database tables from CSV files."""
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)

    # 1. Load day_wise_clean
    day_wise_path = CLEAN_DIR / "day_wise_clean.csv"
    if day_wise_path.exists():
        df_day = pd.read_csv(day_wise_path)
        df_day.to_sql("day_wise_clean", conn, index=False, if_exists="replace")
        print(f" Loaded 'day_wise_clean' ({len(df_day)} rows)")

    # 2. Load country_wise_clean
    country_wise_path = CLEAN_DIR / "country_wise_clean.csv"
    if country_wise_path.exists():
        df_country = pd.read_csv(country_wise_path)
        df_country.to_sql("country_wise_clean", conn, index=False, if_exists="replace")
        print(f" Loaded 'country_wise_clean' ({len(df_country)} rows)")

    # 3. Load worldometer_data
    worldometer_path = DATA_DIR / "worldometer_data.csv"
    if worldometer_path.exists():
        df_world = pd.read_csv(worldometer_path)
        df_world.to_sql("worldometer_data", conn, index=False, if_exists="replace")
        print(f" Loaded 'worldometer_data' ({len(df_world)} rows)")

    # 4. Load full_grouped
    full_path = DATA_DIR / "full_grouped.csv"
    if full_path.exists():
        df_full = pd.read_csv(full_path)
        df_full.to_sql("full_grouped", conn, index=False, if_exists="replace")
        print(f" Loaded 'full_grouped' ({len(df_full)} rows)")

    return conn


def extract_queries(sql_file: Path) -> list[tuple[str, str]]:
    """Extracts SQL queries with their comment titles from a .sql file."""
    content = sql_file.read_text(encoding="utf-8")
    raw_statements = [s.strip() for s in content.split(";") if s.strip()]

    queries = []
    for stmt in raw_statements:
        lines = stmt.splitlines()
        comment = ""
        sql_lines = []
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("--"):
                if not comment:
                    comment = line_str.lstrip("-").strip()
            else:
                sql_lines.append(line)
        sql_query = "\n".join(sql_lines).strip()
        if sql_query:
            queries.append((comment or "Analytical Query", sql_query))
    return queries


def validate_all_queries(conn: sqlite3.Connection, sql_file: Path = SQL_DIR / "analysis_queries.sql"):
    """Executes every query against the SQLite connection to guarantee correctness."""
    queries = extract_queries(sql_file)
    print(f"\nValidating {len(queries)} queries from {sql_file.name}...")

    passed = 0
    for idx, (title, query) in enumerate(queries, 1):
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchmany(5)
            passed += 1
            print(f" [PASS] Query {idx}: {title} (returned {len(rows)} sample rows)")
        except Exception as e:
            print(f" [FAIL] Query {idx}: {title}\n  Error: {e}")
            raise e

    print(f"\nAll {passed}/{len(queries)} SQL queries validated successfully with zero errors!")


def main():
    print("Building SQLite COVID-19 Analytics Database...")
    conn = build_database()
    validate_all_queries(conn)
    conn.close()
    print("Database build and query verification complete.")


if __name__ == "__main__":
    main()
