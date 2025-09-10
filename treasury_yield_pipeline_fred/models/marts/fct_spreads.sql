MODEL (
    name default.fct_spreads,
    kind FULL
);

SELECT
    dt,
    spread_10y_2y,
    spread_30y_10y,
    spread_30y_2y,
    -- Add spread analysis
    CASE 
        WHEN spread_10y_2y < 0 THEN 'Inverted'
        WHEN spread_10y_2y < 50 THEN 'Flat'
        WHEN spread_10y_2y < 150 THEN 'Normal'
        ELSE 'Steep'
    END AS curve_regime,
    -- Rolling metrics
    AVG(spread_10y_2y) OVER (
        ORDER BY dt 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS spread_10y_2y_ma30,
    AVG(spread_10y_2y) OVER (
        ORDER BY dt 
        ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
    ) AS spread_10y_2y_ma90
FROM default.fct_daily_yields
ORDER BY dt
