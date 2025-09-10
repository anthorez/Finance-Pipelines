MODEL (
    name default.fct_daily_yields,
    kind FULL
);

SELECT
    dt,
    y_2y,
    y_10y,
    y_30y,
    -- Add calculated metrics
    ROUND(y_10y - y_2y, 2) AS spread_10y_2y,
    ROUND(y_30y - y_10y, 2) AS spread_30y_10y,
    ROUND(y_30y - y_2y, 2) AS spread_30y_2y,
    -- Curve slope metric
    ROUND((y_30y - y_2y) / 28.0, 3) AS curve_slope
FROM default.stg_treasury_yields
ORDER BY dt
