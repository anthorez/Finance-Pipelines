MODEL (
    name default.fct_curve_geometry,
    kind FULL
);

WITH curve_metrics AS (
    SELECT
        dt,
        y_2y,
        y_10y,
        y_30y,
        -- Curve level (average yield)
        ROUND((y_2y + y_10y + y_30y) / 3.0, 2) AS curve_level,
        -- Curve slope (long - short)
        ROUND(y_30y - y_2y, 2) AS curve_slope,
        -- Curve curvature (butterfly)
        ROUND(2 * y_10y - y_2y - y_30y, 2) AS curve_curvature
    FROM default.fct_daily_yields
)
SELECT
    dt,
    curve_level,
    curve_slope,
    curve_curvature,
    -- Percentile ranks
    PERCENT_RANK() OVER (ORDER BY curve_level) AS level_percentile,
    PERCENT_RANK() OVER (ORDER BY curve_slope) AS slope_percentile,
    PERCENT_RANK() OVER (ORDER BY curve_curvature) AS curvature_percentile
FROM curve_metrics
ORDER BY dt
