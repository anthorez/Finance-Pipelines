#!/usr/bin/env python3
"""
Fetch Treasury yield data from FRED API.
Saves to data/raw/yield_curve.csv
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from fredapi import Fred

def fetch_treasury_yields():
    """Fetch 2Y, 10Y, and 30Y Treasury yields from FRED."""
    
    # Get API key from environment
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        print("Error: FRED_API_KEY environment variable not set")
        print("Get a free key at: https://fred.stlouisfed.org/")
        sys.exit(1)
    
    # Initialize FRED client
    fred = Fred(api_key=api_key)
    
    # Series IDs for Treasury yields
    series_mapping = {
        'DGS2': 'y_2y',   # 2-Year Treasury
        'DGS10': 'y_10y', # 10-Year Treasury
        'DGS30': 'y_30y'  # 30-Year Treasury
    }
    
    start_date = '1990-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Fetching Treasury yields from {start_date} to {end_date}...")
    
    # Fetch each series
    dfs = []
    for fred_id, col_name in series_mapping.items():
        print(f"  Fetching {fred_id} ({col_name})...")
        series = fred.get_series(fred_id, start_date, end_date)
        df = pd.DataFrame(series, columns=[col_name])
        df.index.name = 'dt'
        dfs.append(df)
    
    # Combine all series
    combined = pd.concat(dfs, axis=1)
    combined = combined.reset_index()
    
    # Handle missing values (forward fill then back fill)
    combined = combined.ffill().bfill()
    
    # Create output directory if needed
    output_dir = Path('data/raw')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    output_path = output_dir / 'yield_curve.csv'
    combined.to_csv(output_path, index=False)
    
    print(f"✓ Saved {len(combined)} rows to {output_path}")
    print(f"  Date range: {combined['dt'].min()} to {combined['dt'].max()}")
    print(f"  Columns: {', '.join(combined.columns)}")

if __name__ == '__main__':
    fetch_treasury_yields()
