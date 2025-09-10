#!/usr/bin/env python3
"""
Plot implied forward rates.
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_forwards():
    """Create implied forwards visualization."""
    
    # Connect to DuckDB
    con = duckdb.connect('data/warehouse.duckdb')
    con.sql("SET schema 'default';")
    
    # Fetch data
    df = con.sql("""
        SELECT dt, forward_5y5y
        FROM fct_implied_forwards
        WHERE dt >= '2000-01-01'
          AND forward_5y5y IS NOT NULL
        ORDER BY dt
    """).df()
    
    con.close()
    
    # Convert date column
    df['dt'] = pd.to_datetime(df['dt'])
    
    # Create plot
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.plot(df['dt'], df['forward_5y5y'], linewidth=1.5, color='darkgreen', alpha=0.8)
    
    # Add moving average
    df['ma_120'] = df['forward_5y5y'].rolling(window=120, min_periods=1).mean()
    ax.plot(df['dt'], df['ma_120'], linewidth=1, color='red', alpha=0.5, linestyle='--', label='120-Day MA')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Forward Rate (%)', fontsize=12)
    ax.set_title('5Y5Y Implied Forward Rate', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('reports/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'implied_forwards.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved plot to {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_forwards()
