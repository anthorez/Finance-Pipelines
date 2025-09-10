#!/usr/bin/env python3
"""
Plot 10Y-2Y Treasury spread.
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_spread():
    """Create spread visualization."""
    
    # Connect to DuckDB
    con = duckdb.connect('data/warehouse.duckdb')
    con.sql("SET schema 'default';")
    
    # Fetch data
    df = con.sql("""
        SELECT dt, spread_10y_2y
        FROM fct_spreads
        WHERE dt >= '2000-01-01'
        ORDER BY dt
    """).df()
    
    con.close()
    
    # Convert date column
    df['dt'] = pd.to_datetime(df['dt'])
    
    # Create plot
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot spread
    ax.plot(df['dt'], df['spread_10y_2y'], linewidth=1.5, color='darkblue', alpha=0.8)
    
    # Add zero line
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    
    # Fill areas
    ax.fill_between(df['dt'], 0, df['spread_10y_2y'], 
                    where=(df['spread_10y_2y'] >= 0), 
                    color='green', alpha=0.2, label='Normal')
    ax.fill_between(df['dt'], 0, df['spread_10y_2y'], 
                    where=(df['spread_10y_2y'] < 0), 
                    color='red', alpha=0.2, label='Inverted')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Spread (bps)', fontsize=12)
    ax.set_title('10Y-2Y Treasury Spread', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('reports/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'spread_10y_2y.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved plot to {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_spread()
