-- Load data first using your SQL engine's CSV import command and schema.sql.

-- Basic: global totals on the latest available date.
SELECT Date, Confirmed, Deaths, Recovered, "Active Cases", "Death Rate", "Recovery Rate"
FROM day_wise_clean
ORDER BY Date DESC
LIMIT 1;

-- Basic: top 10 countries by confirmed cases.
SELECT "Country/Region", Confirmed, Deaths, Recovered, "Active Cases", "Death Rate", "Recovery Rate"
FROM country_wise_clean
ORDER BY Confirmed DESC
LIMIT 10;

-- Basic: regions ordered by confirmed cases.
SELECT "WHO Region", SUM(Confirmed) AS confirmed_cases, SUM(Deaths) AS deaths, SUM(Recovered) AS recoveries
FROM country_wise_clean
GROUP BY "WHO Region"
ORDER BY confirmed_cases DESC;

-- Advanced: seven-day moving average for new cases.
SELECT Date, "New cases",
       AVG("New cases") OVER (ORDER BY Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS seven_day_avg
FROM day_wise_clean
ORDER BY Date;

-- Advanced: rank countries within each WHO region.
SELECT "WHO Region", "Country/Region", Confirmed,
       DENSE_RANK() OVER (PARTITION BY "WHO Region" ORDER BY Confirmed DESC) AS regional_rank
FROM country_wise_clean
ORDER BY "WHO Region", regional_rank;

-- Advanced: countries with high case burden and below-average recovery rate.
SELECT "Country/Region", Confirmed, "Recovery Rate", "Death Rate"
FROM country_wise_clean
WHERE Confirmed > (SELECT AVG(Confirmed) FROM country_wise_clean)
  AND "Recovery Rate" < (SELECT AVG("Recovery Rate") FROM country_wise_clean)
ORDER BY Confirmed DESC;

-- Advanced: compare each date with the previous day's confirmed total.
SELECT Date, Confirmed,
       Confirmed - LAG(Confirmed) OVER (ORDER BY Date) AS day_over_day_change
FROM day_wise_clean
ORDER BY Date;
