# Treasury Yield Pipeline with SQLMesh & DuckDB

A data pipeline for analyzing US Treasury yields, spreads, and market dynamics SQLMesh & DuckDB

## Project Overview

This pipeline automatically fetches, transforms, and analyzes US Treasury yield data to provide insights into:
- **Yield curve dynamics** - Understanding interest rate environments
- **Spread analysis** - Detecting inversions and recession signals
- **Volatility patterns** - Risk assessment and market stress indicators
- **Forward rates** - Market expectations of future interest rates

### Why This Matters

Treasury yields are fundamental to finance:
- **Economic Indicators**: Yield curve inversions historically predict recessions
- **Risk-Free Rate**: Foundation for pricing all other financial assets
- **Market Sentiment**: Reflects inflation expectations and growth outlook
- **Policy Insights**: Federal Reserve monetary policy transmission

## Architecture

```
FRED API → CSV → SQLMesh/DuckDB → Analytics → Visualizations
```

- **Data Source**: Federal Reserve Economic Data (FRED) API
- **Orchestration**: SQLMesh for declarative data transformations
- **Storage**: DuckDB for local analytical database
- **Analytics**: 8 specialized models for different analytical views
- **Visualization**: Python/Matplotlib for charts and insights

## Prerequisites

- **Python 3.11** (recommended) or 3.12
- **macOS/Linux** (Windows WSL works too)
- **Git**
- **~500MB disk space**
- **FRED API Key** (free from https://fred.stlouisfed.org/)

## Quick Start (First Time Setup)

### Step 1: Clone and Enter Directory

```bash
# If using the setup script
mkdir treasury_yield_pipeline_fred
cd treasury_yield_pipeline_fred

# Run the setup script to create all files
bash setup_treasury_pipeline.sh
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> **Note**: If you see DuckDB compilation errors, ensure you're using Python 3.11 or 3.12

### Step 3: Configure FRED API Access

```bash
# Get your free API key from: https://fred.stlouisfed.org/
export FRED_API_KEY="your_actual_key_here"

# Optional: Add to .env file for persistence
echo "FRED_API_KEY=your_actual_key_here" > .env
```

### Step 4: Fetch Raw Data

```bash
python scripts/fetch_fred_yields.py
```

**Expected Output:**
```
Fetching Treasury yields from 1990-01-01 to 2025-01-10...
  Fetching DGS2 (y_2y)...
  Fetching DGS10 (y_10y)...
  Fetching DGS30 (y_30y)...
✓ Saved 8,658 rows to data/raw/yield_curve.csv
```

This downloads 35+ years of daily yield data for 2-year, 10-year, and 30-year Treasury bonds.

### Step 5: Run the Data Pipeline

```bash
# Clean state (recommended for first run)
rm -rf .sqlmesh/
rm -f data/warehouse.duckdb

# Execute the pipeline
sqlmesh plan --auto-apply prod
```

**Expected Output:**
```
Models:
└── Added:
    ├── default.stg_treasury_yields
    ├── default.fct_daily_yields
    ├── default.fct_spreads
    ├── default.fct_curve_geometry
    └── [4 more models...]

[1/1] default.stg_treasury_yields    [full refresh]    0.04s
[1/1] default.fct_daily_yields       [full refresh]    0.02s
... 
✔ Model batches executed
```

### Step 6: Verify Data Quality

```bash
python scripts/data_quality.py --db data/warehouse.duckdb --freshness-days 7
```

**Expected Output:**
```
Running data quality checks...
✓ Row count: 8,658 rows
✓ Date range: 1990-01-02 to 2025-01-10
✓ No null values in key columns
✓ No duplicate dates
✓ No future dates
✓ Spread calculations: 8,658 rows

✅ Data quality checks passed.
```

### Step 7: Generate Visualizations

```bash
# Create all visualizations
python scripts/plot_yields.py
python scripts/plot_spread.py
python scripts/plot_spread_volatility.py
python scripts/plot_forwards.py
```

**Output files in `reports/figures/`:**
- `yields.png` - Historical yield trends with recession overlays
- `spread_10y_2y.png` - Spread analysis with inversion highlighting
- `spread_volatility_30d.png` - Rolling volatility metrics
- `implied_forwards.png` - Forward rate expectations

## Data Models Explained

### 1. **stg_treasury_yields** (Staging Layer)
**Purpose**: Clean entry point for raw data
```sql
-- Ingests CSV, enforces data types, removes nulls
FROM read_csv_auto('data/raw/yield_curve.csv')
```
**Value**: Ensures data quality from the start, standardizes formats

### 2. **fct_daily_yields** (Core Fact Table)
**Purpose**: Central source of truth with calculated spreads
```sql
-- Adds: spread_10y_2y, spread_30y_10y, curve_slope
```
**Value**: 
- Monitor yield curve steepness/inversion
- Recession indicator (negative 10Y-2Y spread)
- One-stop shop for yield analysis

### 3. **fct_spreads** (Spread Analysis)
**Purpose**: Deep dive into term structure dynamics
```sql
-- Adds: curve_regime (Inverted/Flat/Normal/Steep)
-- Rolling averages: 30-day, 90-day
```
**Value**:
- Regime detection for strategy shifts
- Smoothed trends for signal generation
- Historical context for current spreads

### 4. **fct_curve_geometry** (Advanced Metrics)
**Purpose**: Decompose yield curve into level, slope, and curvature
```sql
-- Level: Average yield across curve
-- Slope: Long-term minus short-term
-- Curvature: Butterfly spread (2×10Y - 2Y - 30Y)
```
**Value**:
- **Level**: Overall interest rate environment
- **Slope**: Growth and inflation expectations
- **Curvature**: Relative value opportunities
- Percentile ranks for historical context

### 5. **agg_monthly_yields** (Time Aggregations)
**Purpose**: Monthly summaries for reporting
```sql
-- Monthly averages, min/max, volatility
```
**Value**:
- Executive dashboards
- Trend analysis without daily noise
- Volatility regime identification

### 6. **fct_spread_analytics** (Risk Metrics)
**Purpose**: Volatility and z-score calculations
```sql
-- 30-day rolling volatility
-- 1-year z-scores
-- Daily/weekly/monthly changes
```
**Value**:
- **Volatility**: Market stress indicator
- **Z-scores**: Identify extreme conditions
- **Change metrics**: Momentum signals

### 7. **fct_10y_breakouts** (Technical Analysis)
**Purpose**: Trading signals and technical indicators
```sql
-- 50-day and 200-day moving averages
-- 52-week highs/lows
-- Trend signals (Bullish/Bearish/Neutral)
```
**Value**:
- Systematic trading strategies
- Support/resistance levels
- Trend following signals

### 8. **fct_implied_forwards** (Forward Rates)
**Purpose**: Extract market expectations
```sql
-- 5Y5Y forward rate (5-year rate, 5 years forward)
-- 2Y8Y forward rate
```
**Value**:
- Long-term inflation expectations
- Central bank credibility assessment
- Term premium analysis

## Query Examples

### Check Current Yield Levels
```sql
-- Connect to DuckDB and query
duckdb data/warehouse.duckdb

SET schema = 'default';

SELECT dt, y_2y, y_10y, y_30y, spread_10y_2y
FROM fct_daily_yields
ORDER BY dt DESC
LIMIT 5;
```

### Find Yield Curve Inversions
```sql
SELECT dt, spread_10y_2y
FROM fct_spreads  
WHERE spread_10y_2y < 0
  AND dt >= '2020-01-01'
ORDER BY dt;
```

### Analyze Volatility Regimes
```sql
SELECT 
    DATE_TRUNC('month', dt) as month,
    AVG(volatility_30d) as avg_vol,
    MAX(volatility_30d) as max_vol
FROM fct_spread_analytics
WHERE dt >= '2020-01-01'
GROUP BY DATE_TRUNC('month', dt)
ORDER BY avg_vol DESC
LIMIT 10;
```

## Troubleshooting

### Issue: "FRED_API_KEY environment variable not set"
**Solution**: 
```bash
export FRED_API_KEY="your_key_here"
```

### Issue: "No models are ready to run"
**Solution**: Clear SQLMesh state
```bash
rm -rf .sqlmesh/
sqlmesh plan --auto-apply prod
```

### Issue: SQLMesh version mismatch
**Solution**: 
```bash
sqlmesh migrate
```

### Issue: DuckDB compilation errors
**Solution**: Use Python 3.11 or 3.12 (not 3.13)

### Issue: "Table not found" errors
**Solution**: Ensure you've run the pipeline first
```bash
sqlmesh plan --auto-apply prod
```

## Use Cases

### 1. **Recession Forecasting**
- Monitor 10Y-2Y spread inversions
- Analyze inversion depth and duration
- Compare to historical recession periods

### 2. **Portfolio Risk Management**
- Track volatility regimes
- Identify flight-to-quality episodes
- Duration and convexity positioning

### 3. **Fed Policy Analysis**
- Forward rate movements
- Curve shape changes around FOMC meetings
- Terminal rate expectations

### 4. **Relative Value Trading**
- Butterfly trades using curvature metrics
- Mean reversion strategies on z-scores
- Curve steepeners/flatteners

### 5. **Macro Research**
- Long-term yield trends
- International yield comparisons
- Inflation expectation extraction

## Daily Updates

To update with latest data:
```bash
# Fetch new data
python scripts/fetch_fred_yields.py

# Re-run pipeline
sqlmesh run --ignore-cron prod

# Regenerate visualizations
python scripts/plot_yields.py
```

Consider scheduling with cron:
```bash
# Add to crontab (runs at 6 PM ET on weekdays)
0 18 * * 1-5 cd /path/to/project && ./update_pipeline.sh
```

## Resources

- **FRED API Documentation**: https://fred.stlouisfed.org/docs/api/
- **SQLMesh Documentation**: https://sqlmesh.com/
- **DuckDB Documentation**: https://duckdb.org/
- **Treasury Direct**: https://www.treasurydirect.gov/