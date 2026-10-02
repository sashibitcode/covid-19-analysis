-- COVID-19 SQL Analytics Suite
-- Load data first using your SQL engine's CSV import command or run sql/build_sqlite_db.py.

-- Query 1: Global totals on the latest available date.
SELECT Date, Confirmed, Deaths, Recovered, "Active Cases", "Death Rate", "Recovery Rate"
FROM day_wise_clean
ORDER BY Date DESC
LIMIT 1;

-- Query 2: Top 10 countries by confirmed cases.
SELECT "Country/Region", Confirmed, Deaths, Recovered, "Active Cases", "Death Rate", "Recovery Rate"
FROM country_wise_clean
ORDER BY Confirmed DESC
LIMIT 10;

-- Query 3: Regions ordered by confirmed cases and mortality.
SELECT "WHO Region", SUM(Confirmed) AS confirmed_cases, SUM(Deaths) AS deaths, SUM(Recovered) AS recoveries
FROM country_wise_clean
GROUP BY "WHO Region"
ORDER BY confirmed_cases DESC;

-- Query 4: Seven-day moving average for global new cases.
SELECT Date, "New cases",
       ROUND(AVG("New cases") OVER (ORDER BY Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS seven_day_avg
FROM day_wise_clean
ORDER BY Date;

-- Query 5: Dense rank countries within each WHO region.
SELECT "WHO Region", "Country/Region", Confirmed,
       DENSE_RANK() OVER (PARTITION BY "WHO Region" ORDER BY Confirmed DESC) AS regional_rank
FROM country_wise_clean
ORDER BY "WHO Region", regional_rank;

-- Query 6: Countries with high case burden and below-average recovery rate.
SELECT "Country/Region", Confirmed, "Recovery Rate", "Death Rate"
FROM country_wise_clean
WHERE Confirmed > (SELECT AVG(Confirmed) FROM country_wise_clean)
  AND "Recovery Rate" < (SELECT AVG("Recovery Rate") FROM country_wise_clean)
ORDER BY Confirmed DESC;

-- Query 7: Day-over-day confirmed-case changes using LAG window function.
SELECT Date, Confirmed,
       Confirmed - LAG(Confirmed) OVER (ORDER BY Date) AS day_over_day_change
FROM day_wise_clean
ORDER BY Date;

-- Query 8: Epidemiological risk classification by Case Fatality Rate (CFR).
SELECT "Country/Region", Confirmed, Deaths, "Death Rate",
       CASE 
           WHEN "Death Rate" >= 8.0 THEN 'Critical CFR (>= 8%)'
           WHEN "Death Rate" >= 4.0 THEN 'High CFR (4% - 8%)'
           WHEN "Death Rate" >= 2.0 THEN 'Moderate CFR (2% - 4%)'
           ELSE 'Low CFR (< 2%)'
       END AS CFR_Risk_Category
FROM country_wise_clean
WHERE Confirmed >= 1000
ORDER BY "Death Rate" DESC;

-- Query 9: 14-day rolling moving average of daily mortality.
SELECT Date, "New deaths",
       ROUND(AVG("New deaths") OVER (ORDER BY Date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 2) AS deaths_14d_ma
FROM day_wise_clean
ORDER BY Date;

-- Query 10: Week-over-week growth rate analysis for top affected nations.
SELECT "Country/Region", Confirmed, "Confirmed last week", "1 week change", "1 week % increase"
FROM country_wise_clean
WHERE Confirmed >= 50000
ORDER BY "1 week % increase" DESC;

-- Query 11: Top 3 countries with highest active case concentration per WHO region.
WITH RankedRegionalActive AS (
    SELECT "WHO Region", "Country/Region", "Active Cases", Confirmed,
           ROW_NUMBER() OVER (PARTITION BY "WHO Region" ORDER BY "Active Cases" DESC) as rank_in_region
    FROM country_wise_clean
)
SELECT "WHO Region", rank_in_region, "Country/Region", "Active Cases", Confirmed
FROM RankedRegionalActive
WHERE rank_in_region <= 3
ORDER BY "WHO Region", rank_in_region;

-- Query 12: Countries with superior recovery efficiency (Recovery Rate > 75% and Confirmed > 10,000).
SELECT "Country/Region", "WHO Region", Confirmed, Recovered, "Recovery Rate", "Death Rate"
FROM country_wise_clean
WHERE Confirmed >= 10000 AND "Recovery Rate" >= 75.0
ORDER BY "Recovery Rate" DESC;

-- Query 13: Top 10 single-day spikes in new global cases.
SELECT Date, "New cases", "New deaths", Confirmed, Deaths
FROM day_wise_clean
ORDER BY "New cases" DESC
LIMIT 10;

-- Query 14: Regional mortality-to-recovery severity index.
SELECT "WHO Region",
       SUM(Confirmed) AS total_cases,
       SUM(Deaths) AS total_deaths,
       SUM(Recovered) AS total_recovered,
       ROUND(SUM(Deaths) * 100.0 / NULLIF(SUM(Confirmed), 0), 2) AS regional_cfr,
       ROUND(SUM(Recovered) * 100.0 / NULLIF(SUM(Confirmed), 0), 2) AS regional_recovery_rate,
       ROUND(SUM(Deaths) * 1.0 / NULLIF(SUM(Recovered), 0), 4) AS death_to_recovery_ratio
FROM country_wise_clean
GROUP BY "WHO Region"
ORDER BY total_cases DESC;
