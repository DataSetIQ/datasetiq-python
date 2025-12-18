# DataSetIQ Python Client

**Official Python SDK for [DataSetIQ](https://www.datasetiq.com) — The Modern Economic Data Platform**

[![PyPI version](https://img.shields.io/pypi/v/datasetiq.svg)](https://pypi.org/project/datasetiq/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/datasetiq.svg)](https://pypi.org/project/datasetiq/)
[![GitHub](https://img.shields.io/github/stars/DataSetIQ/datasetiq-python?style=social)](https://github.com/DataSetIQ/datasetiq-python)

---

## 🚀 Features

- **40M+ Time Series**: Access FRED, BLS, Census, World Bank, IMF, OECD, and more
- **Pandas-Ready**: Returns clean DataFrames with date index
- **Intelligent Caching**: Disk-based caching with TTL (24h default)
- **Automatic Retries**: Exponential backoff with `Retry-After` support
- **Free Tier**: 25 requests/minute + 25 AI insights/month
- **Type-Safe Errors**: Helpful exception messages with upgrade paths

---

## 📦 Installation

```bash
pip install datasetiq
```

**Requirements**: Python 3.9+

---

## 🔑 Quick Start

### 1. Get Your Free API Key

Visit [datasetiq.com/dashboard/api-keys](https://www.datasetiq.com/dashboard/api-keys) to create a free account and generate your API key.

### 2. Fetch Economic Data

```python
import datasetiq as iq

# Set your API key
iq.set_api_key("diq_your_key_here")

# Get time series data as a Pandas DataFrame
df = iq.get("fred-cpi")
print(df.head())
```

**Output:**
```
            value
date             
1947-01-01  21.48
1947-02-01  21.62
1947-03-01  22.00
1947-04-01  22.00
1947-05-01  21.95
```

### 3. Plot It

```python
import matplotlib.pyplot as plt

df['value'].plot(title="Consumer Price Index", figsize=(12, 6))
plt.ylabel("CPI")
plt.show()
```

---

## 📖 API Reference

### Core Functions

#### `get(series_id, start=None, end=None, dropna=False)`

Fetch time series data as a Pandas DataFrame.

**Parameters:**
- `series_id` (str): Series identifier (e.g., `"fred-cpi"`, `"bls-unemployment"`)
- `start` (str, optional): Start date in `YYYY-MM-DD` format
- `end` (str, optional): End date in `YYYY-MM-DD` format
- `dropna` (bool): Drop rows with NaN values (default: `False`)

**Returns:** `pd.DataFrame` with date index and `value` column

**Example:**
```python
# Get recent data
df = iq.get("fred-gdp", start="2020-01-01", end="2023-12-31")

# Preserve data gaps (default)
df = iq.get("fred-cpi", dropna=False)

# Drop missing values
df = iq.get("fred-cpi", dropna=True)
```

---

#### `search(query, limit=10, offset=0)`

Search for datasets by keyword.

**Parameters:**
- `query` (str): Search term (searches titles, descriptions, IDs)
- `limit` (int): Max results to return (default: `10`, max: `10`)
- `offset` (int): Pagination offset (default: `0`)

**Returns:** `pd.DataFrame` with columns: `id`, `slug`, `title`, `description`, `provider`, `frequency`, `start_date`, `end_date`, `last_updated`

**Example:**
```python
results = iq.search("unemployment rate")
print(results[["id", "title", "provider"]])

# Output:
#              id                          title provider
# 0  fred-unrate        Unemployment Rate (U.S.)     FRED
# 1  bls-lns14000000  Labor Force: Unemployed       BLS
```

---

### Configuration

#### `set_api_key(api_key)`

Set your DataSetIQ API key.

```python
iq.set_api_key("diq_your_key_here")
```

---

#### `configure(**options)`

Customize client behavior.

**Options:**
- `api_key` (str): Your API key
- `base_url` (str): API base URL (default: `https://www.datasetiq.com/api/public`)
- `timeout` (tuple): `(connect_timeout, read_timeout)` in seconds (default: `(3.05, 30)`)
- `max_retries` (int): Max retry attempts (default: `3`)
- `max_retry_sleep` (int): Cap total backoff time in seconds (default: `20`)
- `anon_max_pages` (int): Safety limit for anonymous pagination (default: `200`)
- `data_cache_ttl` (int): Cache TTL for time series data in seconds (default: `86400` / 24h)
- `search_cache_ttl` (int): Cache TTL for search results in seconds (default: `900` / 15m)
- `enable_cache` (bool): Enable/disable disk caching (default: `True`)

**Example:**
```python
iq.configure(
    api_key="diq_your_key_here",
    max_retries=5,
    data_cache_ttl=3600,  # 1 hour cache
    enable_cache=True
)
```

---

### Cache Management

#### `clear_cache()`

Clear all cached data.

```python
count = iq.clear_cache()
print(f"Cleared {count} cached files")
```

#### `get_cache_size()`

Get cache statistics.

```python
file_count, total_bytes = iq.get_cache_size()
print(f"Cache: {file_count} files, {total_bytes / 1024 / 1024:.2f} MB")
```

---

## 🔐 Authentication Modes

### Authenticated Mode (Recommended)

**With API Key:**
- ✅ Full CSV exports (all observations)
- ✅ Higher rate limits (25-500 RPM based on plan)
- ✅ Access to AI insights and premium features
- ✅ Date filtering support

```python
iq.set_api_key("diq_your_key_here")
df = iq.get("fred-cpi")  # Full dataset
```

### Anonymous Mode

**Without API Key:**
- ⚠️ Returns **latest 100 observations** only (most recent data)
- ⚠️ Lower rate limits (5 RPM)
- ⚠️ Metadata-only for some datasets
- ⚠️ No date filtering support

```python
# No API key set
df = iq.get("fred-cpi")  # Latest 100 observations only
print(df.tail())  # Most recent data points
```

---

## 🛡️ Error Handling

All errors include helpful marketing messages to guide you toward solutions.

### Authentication Required (401)

```python
try:
    df = iq.get("fred-cpi")
except iq.AuthenticationError as e:
    print(e)
    # Output:
    # [UNAUTHORIZED] Authentication required
    #
    # 🔑 GET YOUR FREE API KEY:
    #    → https://www.datasetiq.com/dashboard/api-keys
    # ...
```

### Rate Limit Exceeded (429)

```python
try:
    df = iq.get("fred-cpi")
except iq.RateLimitError as e:
    print(e)
    # Output:
    # [RATE_LIMITED] Rate limit exceeded: 26/25 requests this minute
    #
    # ⚡ RATE LIMIT REACHED:
    #    26/25 requests this minute
    #
    # 🚀 INCREASE YOUR LIMITS:
    #    → https://www.datasetiq.com/pricing
    # ...
```

### Quota Exceeded (429)

```python
try:
    # Generate 26th basic insight on free plan
    pass
except iq.QuotaExceededError as e:
    print(e.metric)  # "insight_basic"
    print(e.current)  # 26
    print(e.limit)  # 25
```

### Series Not Found (404)

```python
try:
    df = iq.get("invalid-series-id")
except iq.NotFoundError as e:
    print(e)
    # Output:
    # [NOT_FOUND] Series not found
    #
    # 🔍 SERIES NOT FOUND
    #
    # 💡 TIP: Search for series first:
    #    import datasetiq as iq
    #    results = iq.search('unemployment rate')
    # ...
```

---

## 📊 Advanced Examples

### Comparing Multiple Series

```python
import datasetiq as iq
import pandas as pd

# Fetch multiple series
cpi = iq.get("fred-cpi", start="2020-01-01")
gdp = iq.get("fred-gdp", start="2020-01-01")

# Merge on date
df = pd.merge(
    cpi.rename(columns={"value": "CPI"}),
    gdp.rename(columns={"value": "GDP"}),
    left_index=True,
    right_index=True,
    how="outer"
)

print(df.head())
```

### Calculate Year-over-Year Change

```python
df = iq.get("fred-cpi", start="2015-01-01")

# Calculate YoY % change
df['yoy_change'] = df['value'].pct_change(periods=12) * 100

print(df.tail())
```

### Export to Excel

```python
df = iq.get("fred-gdp")
df.to_excel("gdp_data.xlsx")
```

---

## 🧪 Development

### Setup

```bash
git clone https://github.com/DataSetIQ/datasetiq-python.git
cd datasetiq-python
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black datasetiq tests
ruff check datasetiq tests
```

---

## 🛡️ Stability & API Guarantees

**Current Status: Beta (0.x versions)**

- **Breaking changes** may occur between minor versions (e.g., 0.1.x → 0.2.x)
- **Core functions** (`get()`, `set_api_key()`) are stable and tested
- **v1.0 release** will follow semantic versioning with backward compatibility guarantees
- Subscribe to [GitHub releases](https://github.com/DataSetIQ/datasetiq-python/releases) for updates

---

## 🗺️ Roadmap

- [ ] Add `get_insight()` for AI-generated analysis
- [ ] Support batch requests: `iq.get_many(["fred-cpi", "fred-gdp"])`
- [ ] Async support: `await iq.get_async("fred-cpi")`
- [ ] Streaming for large datasets
- [ ] Jupyter notebook integration (progress bars)

---

## 📚 Resources

- **Homepage**: [datasetiq.com](https://www.datasetiq.com)
- **API Keys**: [datasetiq.com/dashboard/api-keys](https://www.datasetiq.com/dashboard/api-keys)
- **Documentation**: [datasetiq.com/docs](https://www.datasetiq.com/docs)
- **Pricing**: [datasetiq.com/pricing](https://www.datasetiq.com/pricing)
- **GitHub**: [github.com/DataSetIQ/datasetiq-python](https://github.com/DataSetIQ/datasetiq-python)
- **Support**: [support@datasetiq.com](mailto:support@datasetiq.com)

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

**Made with ❤️ by [DataSetIQ](https://www.datasetiq.com)**
