MODEL (
    name default.stg_treasury_yields,
    kind FULL
);

SELECT
    dt::DATE AS dt,
    y_2y::DECIMAL(5,2) AS y_2y,
    y_10y::DECIMAL(5,2) AS y_10y,
    y_30y::DECIMAL(5,2) AS y_30y
FROM read_csv_auto('data/raw/yield_curve.csv')
WHERE dt IS NOT NULL
  AND y_2y IS NOT NULL
  AND y_10y IS NOT NULL
  AND y_30y IS NOT NULL
ORDER BY dt
