#!/usr/bin/env python3
"""
Plot Treasury yields time series.
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_yields():
    """Create yield curve visualization."""
    
    # Connect to DuckDB
    con = duckdb.connect('data/warehouse.duckdb')
    con.sql("SET schema 'default';")
    
    # Fetch data
    df = con.sql("""
        SELECT dt, y_2y, y_10y, y_30y
        FROM fct_daily_yields
        WHERE dt >= '2000-01-01'
        ORDER BY dt
    """).df()
    
    con.close()
    
    # Convert date column
    df['dt'] = pd.to_datetime(df['dt'])
    
    # Create plot
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.plot(df['dt'], df['y_2y'], label='2-Year', linewidth=1.5, alpha=0.8)
    ax.plot(df['dt'], df['y_10y'], label='10-Year', linewidth=1.5, alpha=0.8)
    ax.plot(df['dt'], df['y_30y'], label='30-Year', linewidth=1.5, alpha=0.8)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Yield (%)', fontsize=12)
    ax.set_title('US Treasury Yields Over Time', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Highlight recession periods (simplified)
    recession_periods = [
        ('2001-03-01', '2001-11-01'),  # Dot-com
        ('2007-12-01', '2009-06-01'),  # Great Recession
        ('2020-02-01', '2020-04-01'),  # COVID
    ]
    
    for start, end in recession_periods:
        ax.axvspan(pd.to_datetime(start), pd.to_datetime(end), 
                   alpha=0.2, color='gray', label='Recession' if start == recession_periods[0][0] else '')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('reports/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'yields.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved plot to {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_yields()
