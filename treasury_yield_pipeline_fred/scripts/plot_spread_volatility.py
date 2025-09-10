#!/usr/bin/env python3
"""
Plot spread volatility (30-day rolling).
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_spread_volatility():
    """Create spread volatility visualization."""
    
    # Connect to DuckDB
    con = duckdb.connect('data/warehouse.duckdb')
    con.sql("SET schema 'default';")
    
    # Fetch data
    df = con.sql("""
        SELECT dt, volatility_30d
        FROM fct_spread_analytics
        WHERE dt >= '2000-01-01'
          AND volatility_30d IS NOT NULL
        ORDER BY dt
    """).df()
    
    con.close()
    
    # Convert date column
    df['dt'] = pd.to_datetime(df['dt'])
    
    # Create plot
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.plot(df['dt'], df['volatility_30d'], linewidth=1.5, color='purple', alpha=0.8)
    
    # Add percentile lines
    p75 = df['volatility_30d'].quantile(0.75)
    p90 = df['volatility_30d'].quantile(0.90)
    
    ax.axhline(y=p75, color='orange', linestyle='--', linewidth=1, alpha=0.5, label=f'75th percentile ({p75:.1f})')
    ax.axhline(y=p90, color='red', linestyle='--', linewidth=1, alpha=0.5, label=f'90th percentile ({p90:.1f})')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('30-Day Volatility (bps)', fontsize=12)
    ax.set_title('10Y-2Y Spread Volatility (30-Day Rolling)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('reports/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'spread_volatility_30d.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved plot to {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_spread_volatility()
