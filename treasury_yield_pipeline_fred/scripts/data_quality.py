#!/usr/bin/env python3
"""
Data quality checks for the Treasury yield pipeline.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

import click
import duckdb
import pandas as pd

@click.command()
@click.option('--db', default='data/warehouse.duckdb', help='Path to DuckDB database')
@click.option('--freshness-days', default=7, type=int, help='Max days old for freshness check')
def run_quality_checks(db, freshness_days):
    """Run data quality checks on the warehouse."""
    
    if not Path(db).exists():
        print(f"Error: Database not found at {db}")
        sys.exit(1)
    
    con = duckdb.connect(db)
    con.sql("SET schema 'default';")
    
    print("Running data quality checks...")
    errors = []
    
    # Check 1: Table exists and has data
    try:
        result = con.sql("SELECT COUNT(*) as cnt FROM fct_daily_yields").fetchone()
        row_count = result[0]
        if row_count == 0:
            errors.append("fct_daily_yields is empty")
        else:
            print(f"✓ Row count: {row_count:,} rows")
    except Exception as e:
        errors.append(f"Cannot query fct_daily_yields: {e}")
    
    # Check 2: Date range
    try:
        result = con.sql("""
            SELECT MIN(dt) as min_dt, MAX(dt) as max_dt 
            FROM fct_daily_yields
        """).fetchone()
        min_date, max_date = result
        print(f"✓ Date range: {min_date} to {max_date}")
        
        # Check freshness
        max_date_dt = pd.to_datetime(max_date)
        freshness_threshold = datetime.now() - timedelta(days=freshness_days)
        if max_date_dt < freshness_threshold:
            errors.append(f"Data is stale. Latest date {max_date} is older than {freshness_days} days")
    except Exception as e:
        errors.append(f"Cannot check date range: {e}")
    
    # Check 3: No nulls in key columns
    try:
        result = con.sql("""
            SELECT 
                SUM(CASE WHEN dt IS NULL THEN 1 ELSE 0 END) as null_dates,
                SUM(CASE WHEN y_2y IS NULL THEN 1 ELSE 0 END) as null_2y,
                SUM(CASE WHEN y_10y IS NULL THEN 1 ELSE 0 END) as null_10y,
                SUM(CASE WHEN y_30y IS NULL THEN 1 ELSE 0 END) as null_30y
            FROM fct_daily_yields
        """).fetchone()
        
        null_counts = dict(zip(['dates', '2y', '10y', '30y'], result))
        if any(v > 0 for v in null_counts.values()):
            errors.append(f"Found null values: {null_counts}")
        else:
            print("✓ No null values in key columns")
    except Exception as e:
        errors.append(f"Cannot check for nulls: {e}")
    
    # Check 4: No duplicate dates
    try:
        result = con.sql("""
            SELECT COUNT(*) as dup_count
            FROM (
                SELECT dt, COUNT(*) as cnt
                FROM fct_daily_yields
                GROUP BY dt
                HAVING COUNT(*) > 1
            )
        """).fetchone()
        
        dup_count = result[0]
        if dup_count > 0:
            errors.append(f"Found {dup_count} duplicate dates")
        else:
            print("✓ No duplicate dates")
    except Exception as e:
        errors.append(f"Cannot check for duplicates: {e}")
    
    # Check 5: No future dates
    try:
        today = datetime.now().date()
        result = con.sql(f"""
            SELECT COUNT(*) as future_count
            FROM fct_daily_yields
            WHERE dt > '{today}'
        """).fetchone()
        
        future_count = result[0]
        if future_count > 0:
            errors.append(f"Found {future_count} rows with future dates")
        else:
            print("✓ No future dates")
    except Exception as e:
        errors.append(f"Cannot check for future dates: {e}")
    
    # Check 6: Spreads table consistency
    try:
        result = con.sql("""
            SELECT COUNT(*) as cnt FROM fct_spreads
        """).fetchone()
        spread_count = result[0]
        if spread_count == 0:
            errors.append("fct_spreads is empty")
        else:
            print(f"✓ Spread calculations: {spread_count:,} rows")
    except Exception as e:
        errors.append(f"Cannot query fct_spreads: {e}")
    
    con.close()
    
    # Report results
    if errors:
        print("\n❌ Quality check failures:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ Data quality checks passed.")

if __name__ == '__main__':
    run_quality_checks()
