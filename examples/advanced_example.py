"""
Advanced example: Multi-series comparison and correlation analysis

This example demonstrates:
- Searching for datasets
- Fetching multiple time series
- Merging and aligning data
- Correlation analysis
- Advanced visualization
"""

import datasetiq as iq
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure
iq.set_api_key("your-api-key-here")

# Search for related datasets
print("Searching for economic indicators...")
results = iq.search("gdp unemployment inflation")
print(f"\nFound {len(results)} datasets:")
print(results[["id", "title", "provider"]].head(10))

# Fetch key economic indicators
print("\nFetching data...")
series_ids = {
    "GDP": "fred-gdp",
    "Unemployment": "fred-unrate",
    "CPI": "fred-cpi",
    "10Y Treasury": "fred-dgs10",
}

data = {}
for name, series_id in series_ids.items():
    print(f"  - {name}...")
    df = iq.get(series_id, start="2000-01-01")
    data[name] = df.rename(columns={"value": name})

# Merge all series
combined = pd.concat(data.values(), axis=1, join="outer")

# Forward fill to handle different frequencies
combined = combined.ffill()

print(f"\nMerged dataset shape: {combined.shape}")
print(f"Date range: {combined.index.min()} to {combined.index.max()}")

# Resample to quarterly for cleaner correlation
quarterly = combined.resample('Q').last()

# Calculate correlations
print("\nCorrelation Matrix:")
corr_matrix = quarterly.corr()
print(corr_matrix)

# Visualize correlations
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. Heatmap
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True,
    ax=axes[0, 0]
)
axes[0, 0].set_title("Correlation Matrix", fontsize=12, fontweight='bold')

# 2. Unemployment vs GDP Growth
gdp_growth = combined['GDP'].pct_change(periods=4) * 100  # YoY growth
axes[0, 1].scatter(
    gdp_growth,
    combined['Unemployment'],
    alpha=0.5,
    c=combined.index.year,
    cmap='viridis'
)
axes[0, 1].set_xlabel("GDP Growth (YoY %)")
axes[0, 1].set_ylabel("Unemployment Rate (%)")
axes[0, 1].set_title("GDP Growth vs Unemployment", fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)

# 3. Inflation vs Interest Rates
inflation = combined['CPI'].pct_change(periods=12) * 100
axes[1, 0].scatter(
    inflation,
    combined['10Y Treasury'],
    alpha=0.5,
    c=combined.index.year,
    cmap='plasma'
)
axes[1, 0].set_xlabel("CPI Inflation (YoY %)")
axes[1, 0].set_ylabel("10Y Treasury Yield (%)")
axes[1, 0].set_title("Inflation vs Interest Rates", fontsize=12, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3)

# 4. Time series overlay (normalized)
normalized = (quarterly - quarterly.mean()) / quarterly.std()
for col in normalized.columns:
    axes[1, 1].plot(normalized.index, normalized[col], label=col, linewidth=1.5)
axes[1, 1].set_title("Normalized Time Series", fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel("Standard Deviations from Mean")
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("economic_indicators_analysis.png", dpi=300, bbox_inches='tight')
print("\n✅ Chart saved as 'economic_indicators_analysis.png'")

# Export to Excel
with pd.ExcelWriter("economic_data.xlsx") as writer:
    combined.to_excel(writer, sheet_name="Daily Data")
    quarterly.to_excel(writer, sheet_name="Quarterly Data")
    corr_matrix.to_excel(writer, sheet_name="Correlations")

print("✅ Data exported to 'economic_data.xlsx'")

# Cache statistics
file_count, total_bytes = iq.get_cache_size()
print(f"\nCache: {file_count} files, {total_bytes / 1024 / 1024:.2f} MB")
