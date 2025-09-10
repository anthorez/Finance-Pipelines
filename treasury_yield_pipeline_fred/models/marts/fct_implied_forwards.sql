MODEL (
    name default.fct_implied_forwards,
    kind FULL
);

WITH yield_data AS (
    SELECT
        dt,
        y_2y,
        y_10y,
        -- Get 5Y yield (interpolated between 2Y and 10Y)
        ROUND(y_2y + (y_10y - y_2y) * (5.0 - 2.0) / (10.0 - 2.0), 2) AS y_5y
    FROM default.fct_daily_yields
)
SELECT
    dt,
    y_2y,
    y_5y,
    y_10y,
    -- Calculate 5Y5Y forward rate
    -- Formula: ((1 + r10)^10 / (1 + r5)^5)^(1/5) - 1
    -- Simplified approximation: 2 * r10 - r5
    ROUND(2 * y_10y - y_5y, 2) AS forward_5y5y,
    -- Calculate 2Y8Y forward (2Y rate, 8 years forward)
    -- Approximation: (10 * r10 - 2 * r2) / 8
    ROUND((10 * y_10y - 2 * y_2y) / 8.0, 2) AS forward_2y8y
FROM yield_data
ORDER BY dt
