MODEL (
    name default.fct_10y_breakouts,
    kind FULL
);

WITH rolling_stats AS (
    SELECT
        dt,
        y_10y,
        -- 50-day moving average
        AVG(y_10y) OVER (
            ORDER BY dt 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS ma_50,
        -- 200-day moving average  
        AVG(y_10y) OVER (
            ORDER BY dt 
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS ma_200,
        -- 52-week high/low
        MAX(y_10y) OVER (
            ORDER BY dt 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS high_52w,
        MIN(y_10y) OVER (
            ORDER BY dt 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS low_52w
    FROM default.fct_daily_yields
)
SELECT
    dt,
    y_10y,
    ROUND(ma_50, 2) AS ma_50,
    ROUND(ma_200, 2) AS ma_200,
    high_52w,
    low_52w,
    -- Technical signals
    CASE
        WHEN y_10y > ma_50 AND ma_50 > ma_200 THEN 'Bullish'
        WHEN y_10y < ma_50 AND ma_50 < ma_200 THEN 'Bearish'
        ELSE 'Neutral'
    END AS trend_signal,
    -- Position in 52-week range
    ROUND(100.0 * (y_10y - low_52w) / NULLIF(high_52w - low_52w, 0), 1) AS range_pct
FROM rolling_stats
WHERE ma_200 IS NOT NULL
ORDER BY dt
