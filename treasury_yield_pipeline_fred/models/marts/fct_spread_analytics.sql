MODEL (
    name default.fct_spread_analytics,
    kind FULL
);

WITH spread_changes AS (
    SELECT
        dt,
        spread_10y_2y,
        spread_10y_2y - LAG(spread_10y_2y, 1) OVER (ORDER BY dt) AS daily_change,
        spread_10y_2y - LAG(spread_10y_2y, 5) OVER (ORDER BY dt) AS weekly_change,
        spread_10y_2y - LAG(spread_10y_2y, 21) OVER (ORDER BY dt) AS monthly_change
    FROM default.fct_daily_yields
)
SELECT
    dt,
    spread_10y_2y,
    daily_change,
    weekly_change,
    monthly_change,
    -- Rolling volatility (30-day)
    ROUND(STDDEV(daily_change) OVER (
        ORDER BY dt 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS volatility_30d,
    -- Z-score (how many std devs from mean)
    ROUND((spread_10y_2y - AVG(spread_10y_2y) OVER (
        ORDER BY dt 
        ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
    )) / NULLIF(STDDEV(spread_10y_2y) OVER (
        ORDER BY dt 
        ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
    ), 0), 2) AS z_score_1y
FROM spread_changes
ORDER BY dt
