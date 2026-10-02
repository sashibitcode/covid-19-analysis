"""
Unit test suite for COVID-19 Analysis pipeline and metrics engine.
"""

from __future__ import annotations

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from src.covid_analysis import clean_day_wise, clean_country_wise, validate
from src.advanced_metrics import (
    load_and_clean_worldometer,
    calculate_testing_vs_mortality,
    calculate_country_wave_peaks,
    calculate_regional_benchmarks
)
from sql.build_sqlite_db import build_database, extract_queries

ROOT = Path(__file__).resolve().parents[1]


class TestCovidAnalysisPipeline(unittest.TestCase):

    def test_clean_day_wise_structure_and_invariants(self):
        df = clean_day_wise()
        self.assertFalse(df.empty)
        self.assertIn("Date", df.columns)
        self.assertIn("Active Cases", df.columns)
        self.assertIn("Death Rate", df.columns)
        self.assertIn("Recovery Rate", df.columns)

        # Check Active Cases invariant: Confirmed - Deaths - Recovered
        expected_active = df["Confirmed"] - df["Deaths"] - df["Recovered"]
        pd.testing.assert_series_equal(df["Active Cases"], expected_active, check_names=False)

        # Ensure dates are chronological
        self.assertTrue(df["Date"].is_monotonic_increasing)

    def test_clean_country_wise_uniqueness_and_ranges(self):
        df = clean_country_wise()
        self.assertFalse(df.empty)
        # Ensure no duplicate countries
        self.assertEqual(df["Country/Region"].nunique(), len(df))
        # Ensure rates are non-negative
        self.assertTrue((df["Death Rate"] >= 0).all())
        self.assertTrue((df["Recovery Rate"] >= 0).all())

    def test_validation_function_passes(self):
        day = clean_day_wise()
        country = clean_country_wise()
        try:
            validate(day, country)
        except AssertionError as e:
            self.fail(f"validate() raised AssertionError unexpectedly: {e}")

    def test_advanced_worldometer_metrics(self):
        df = load_and_clean_worldometer()
        self.assertFalse(df.empty)
        self.assertIn("Case_Fatality_Rate", df.columns)
        self.assertIn("Recovery_Rate", df.columns)
        self.assertIn("Critical_Patient_Ratio", df.columns)
        self.assertIn("Tests_Per_Case", df.columns)

        # Test CFR bounded between 0% and 100%
        valid_cfr = df[df["TotalCases"] > 0]["Case_Fatality_Rate"]
        self.assertTrue((valid_cfr >= 0).all() and (valid_cfr <= 100).all())

    def test_country_wave_peaks_detection(self):
        peaks = calculate_country_wave_peaks(min_cases=50000)
        self.assertFalse(peaks.empty)
        self.assertIn("Peak_Date", peaks.columns)
        self.assertIn("Peak_7d_Avg_Cases", peaks.columns)
        self.assertIn("Trajectory", peaks.columns)
        self.assertTrue(set(peaks["Trajectory"].unique()).issubset({"Surging", "Declining"}))

    def test_regional_benchmarks_aggregation(self):
        worldometer = load_and_clean_worldometer()
        reg = calculate_regional_benchmarks(worldometer)
        self.assertGreaterEqual(len(reg), 5)
        self.assertIn("Overall_CFR", reg.columns)
        self.assertIn("Cases_Per_Million", reg.columns)
        self.assertTrue((reg["Total_Confirmed"] > 0).all())

    def test_sqlite_builder_and_query_extraction(self):
        conn = build_database()
        cursor = conn.cursor()

        # Check table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        self.assertIn("day_wise_clean", tables)
        self.assertIn("country_wise_clean", tables)

        # Check a sample query
        cursor.execute("SELECT COUNT(*) FROM day_wise_clean;")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0)
        conn.close()


if __name__ == "__main__":
    unittest.main()
