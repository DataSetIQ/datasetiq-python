"""
Basic example: Fetching and plotting economic data with DataSetIQ

This example demonstrates:
- Setting up API authentication
- Fetching time series data
- Basic data manipulation
- Visualization
"""

import datasetiq as iq
import matplotlib.pyplot as plt

# Set your API key (get one free at datasetiq.com/dashboard/api-keys)
iq.set_api_key("your-api-key-here")

# Fetch Consumer Price Index data
print("Fetching CPI data...")
cpi = iq.get("fred-cpi", start="2010-01-01")

print(f"Loaded {len(cpi)} observations")
print(f"Date range: {cpi.index.min()} to {cpi.index.max()}")
print(f"\nFirst 5 rows:")
print(cpi.head())

# Calculate year-over-year inflation rate
cpi['yoy_inflation'] = cpi['value'].pct_change(periods=12) * 100

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# CPI level
ax1.plot(cpi.index, cpi['value'], linewidth=2)
ax1.set_title("Consumer Price Index (CPI)", fontsize=14, fontweight='bold')
ax1.set_ylabel("Index Value")
ax1.grid(True, alpha=0.3)

# YoY inflation rate
ax2.plot(cpi.index, cpi['yoy_inflation'], color='red', linewidth=2)
ax2.axhline(y=2.0, color='gray', linestyle='--', label='2% Target')
ax2.set_title("Year-over-Year Inflation Rate", fontsize=14, fontweight='bold')
ax2.set_ylabel("Inflation Rate (%)")
ax2.set_xlabel("Date")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("cpi_analysis.png", dpi=300, bbox_inches='tight')
print("\n✅ Chart saved as 'cpi_analysis.png'")

# Show statistics
print(f"\nInflation Statistics (since 2010):")
print(f"Average: {cpi['yoy_inflation'].mean():.2f}%")
print(f"Min: {cpi['yoy_inflation'].min():.2f}% ({cpi['yoy_inflation'].idxmin().date()})")
print(f"Max: {cpi['yoy_inflation'].max():.2f}% ({cpi['yoy_inflation'].idxmax().date()})")
print(f"Current: {cpi['yoy_inflation'].iloc[-1]:.2f}%")
