MODEL (
    name default.agg_monthly_yields,
    kind FULL
);

SELECT
    DATE_TRUNC('month', dt) AS month,
    COUNT(*) AS trading_days,
    -- Average yields
    ROUND(AVG(y_2y), 2) AS avg_y_2y,
    ROUND(AVG(y_10y), 2) AS avg_y_10y,
    ROUND(AVG(y_30y), 2) AS avg_y_30y,
    -- Min/Max yields
    ROUND(MIN(y_2y), 2) AS min_y_2y,
    ROUND(MAX(y_2y), 2) AS max_y_2y,
    ROUND(MIN(y_10y), 2) AS min_y_10y,
    ROUND(MAX(y_10y), 2) AS max_y_10y,
    -- Spread metrics
    ROUND(AVG(spread_10y_2y), 2) AS avg_spread_10y_2y,
    ROUND(STDDEV(spread_10y_2y), 2) AS std_spread_10y_2y
FROM default.fct_daily_yields
GROUP BY DATE_TRUNC('month', dt)
ORDER BY month
