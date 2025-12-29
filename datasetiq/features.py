"""
Feature engineering helpers and lightweight insights for DataSetIQ time series.

All helpers are client-side (Pandas) so they work without new API endpoints.
"""

from typing import Iterable, List, Optional, Sequence, Tuple, Union

import pandas as pd

from .client import get

SeriesLike = Union[str, pd.DataFrame, pd.Series]


def _apply_impute(df: pd.DataFrame, strategy: str) -> pd.DataFrame:
    """Apply simple imputation strategies."""
    if strategy == "none":
        return df
    
    out = df.copy()
    if "ffill" in strategy:
        out = out.ffill()
    if "bfill" in strategy:
        out = out.bfill()
    if "median" in strategy:
        medians = out.median(numeric_only=True)
        out = out.fillna(medians)
    return out


def _coerce_to_dataframe(
    series: SeriesLike,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Tuple[pd.DataFrame, str]:
    """
    Accept a series ID (string), DataFrame, or Series and return a normalized DataFrame.
    Ensures there is a 'value' column and a datetime index.
    """
    series_name = "series"
    if isinstance(series, str):
        df = get(series, start=start, end=end)
        series_name = series
    elif isinstance(series, pd.DataFrame):
        df = series.copy()
        if "value" not in df.columns and df.shape[1] == 1:
            df = df.rename(columns={df.columns[0]: "value"})
    elif isinstance(series, pd.Series):
        df = series.to_frame(name="value").copy()
    else:
        raise TypeError("series must be a series ID (str), DataFrame, or Series")
    
    if "value" not in df.columns:
        raise ValueError("DataFrame must include a 'value' column or a single unnamed column")
    
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    
    df = df.sort_index()
    if start:
        df = df[df.index >= pd.to_datetime(start)]
    if end:
        df = df[df.index <= pd.to_datetime(end)]
    
    return df, series_name


def add_features(
    series: SeriesLike,
    *,
    lags: Sequence[int] = (1, 3, 12),
    windows: Sequence[int] = (3, 6, 12),
    include: Optional[Iterable[str]] = None,
    dropna: bool = False,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Generate common modeling features for a single time series.
    
    Args:
        series: Series ID (str), DataFrame with 'value', or Series
        lags: Which lag periods to add (e.g., 1, 3, 12)
        windows: Rolling window sizes to add (mean/std)
        include: Which feature families to include; default = all
                 Options: 'mom', 'yoy', 'lags', 'rolling_mean', 'rolling_std', 'zscore'
        dropna: Drop rows with any NaNs after feature creation
        start/end: Optional date filters (YYYY-MM-DD)
    
    Returns:
        DataFrame with base 'value' plus engineered feature columns.
    """
    df, _ = _coerce_to_dataframe(series, start=start, end=end)
    features = set(include) if include else {
        "mom",
        "yoy",
        "lags",
        "rolling_mean",
        "rolling_std",
        "zscore",
    }
    
    base = df.copy()
    
    if "mom" in features:
        base["value_mom_pct"] = base["value"].pct_change() * 100
    if "yoy" in features:
        base["value_yoy_pct"] = base["value"].pct_change(periods=12) * 100
    if "lags" in features:
        for lag in lags:
            base[f"value_lag_{lag}"] = base["value"].shift(lag)
    if "rolling_mean" in features:
        for window in windows:
            base[f"value_rollmean_{window}"] = base["value"].rolling(window).mean()
    if "rolling_std" in features:
        for window in windows:
            base[f"value_rollstd_{window}"] = base["value"].rolling(window).std()
    if "zscore" in features:
        std = base["value"].std()
        base["value_zscore"] = (base["value"] - base["value"].mean()) / std if std else pd.NA
    
    if dropna:
        base = base.dropna()
    
    return base


def get_insight(
    series: SeriesLike,
    *,
    window: Optional[str] = "1y",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> dict:
    """
    Return a lightweight insight summary for a time series.
    
    Args:
        series: Series ID (str), DataFrame with 'value', or Series
        window: Optional lookback window (e.g., '6m', '1y'); None = full history
        start/end: Optional date filters
    
    Returns:
        Dict containing summary text and key metrics.
    """
    df, series_name = _coerce_to_dataframe(series, start=start, end=end)
    if df.empty:
        return {"series": series_name, "summary": "No data available"}
    
    df = df.copy()
    if window:
        try:
            unit = window[-1].lower()
            value = int(window[:-1])
            if unit == "y":
                cutoff = df.index.max() - pd.DateOffset(years=value)
            elif unit == "m":
                cutoff = df.index.max() - pd.DateOffset(months=value)
            elif unit == "d":
                cutoff = df.index.max() - pd.DateOffset(days=value)
            else:
                cutoff = None
            if cutoff is not None:
                df = df[df.index >= cutoff]
        except Exception:
            # If parsing fails, use full history
            pass
    
    latest_date = df.index.max()
    latest_value = df.loc[latest_date, "value"]
    prev_value = df["value"].iloc[-2] if len(df) > 1 else None
    yoy_ref = df["value"].shift(12).iloc[-1] if len(df) > 12 else None
    
    mom_change_pct = None
    yoy_change_pct = None
    
    if prev_value not in (None, 0) and not pd.isna(prev_value):
        mom_change_pct = (latest_value - prev_value) / prev_value * 100
    if yoy_ref not in (None, 0) and not pd.isna(yoy_ref):
        yoy_change_pct = (latest_value - yoy_ref) / yoy_ref * 100
    
    volatility = float(df["value"].std()) if len(df) > 2 else None
    trend_slope = df["value"].diff().mean()
    trend = "upward" if trend_slope and trend_slope > 0 else "downward" if trend_slope and trend_slope < 0 else "flat"
    
    parts: List[str] = []
    parts.append(f"{series_name}: latest {latest_value:.2f} on {latest_date.date()}")
    if mom_change_pct is not None:
        parts.append(f"{mom_change_pct:+.2f}% vs prior")
    if yoy_change_pct is not None:
        parts.append(f"{yoy_change_pct:+.2f}% YoY")
    parts.append(f"trend {trend}")
    if volatility is not None:
        parts.append(f"volatility (std) {volatility:.2f}")
    
    return {
        "series": series_name,
        "latest_date": latest_date,
        "latest_value": latest_value,
        "mom_change_pct": mom_change_pct,
        "yoy_change_pct": yoy_change_pct,
        "volatility": volatility,
        "trend": trend,
        "window": window,
        "summary": " | ".join(parts),
    }


def get_ml_ready(
    series_ids: Sequence[str],
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    align: str = "inner",
    impute: str = "ffill+median",
    features: Union[str, None] = "default",
    lags: Sequence[int] = (1, 3, 12),
    windows: Sequence[int] = (3, 6, 12),
    dropna: bool = False,
) -> pd.DataFrame:
    """
    Fetch multiple series, align them on date, optionally impute gaps, and add features.
    
    Args:
        series_ids: List of series IDs to fetch
        start/end: Optional date filters
        align: How to align dates: 'inner' (intersection) or 'outer' (union)
        impute: Imputation strategy: 'ffill+median', 'ffill', 'median', or 'none'
        features: 'default' to add basic features per series, None to skip
        lags/windows: Passed to feature generation when features enabled
        dropna: Drop rows with any NaNs after processing
    
    Returns:
        DataFrame with aligned base columns and optional engineered features.
    """
    join_how = "inner" if align == "inner" else "outer"
    frames = []
    for series_id in series_ids:
        df = get(series_id, start=start, end=end).copy()
        df = df.rename(columns={"value": series_id})
        frames.append(df[[series_id]])
    
    if not frames:
        return pd.DataFrame()
    
    combined = pd.concat(frames, axis=1, join=join_how).sort_index()
    
    # Imputation on base columns
    combined = _apply_impute(combined, impute)
    
    # Feature generation per base column
    base_columns = list(series_ids)
    if features:
        for col in base_columns:
            series = combined[col]
            combined[f"{col}_mom_pct"] = series.pct_change() * 100
            combined[f"{col}_yoy_pct"] = series.pct_change(periods=12) * 100
            for lag in lags:
                combined[f"{col}_lag_{lag}"] = series.shift(lag)
            for window in windows:
                combined[f"{col}_rollmean_{window}"] = series.rolling(window).mean()
                combined[f"{col}_rollstd_{window}"] = series.rolling(window).std()
            std = series.std()
            combined[f"{col}_zscore"] = (series - series.mean()) / std if std else pd.NA
    
    # Imputation again to fill feature NaNs (from pct_change/rolling/lag)
    combined = _apply_impute(combined, impute)
    
    if dropna:
        combined = combined.dropna()
    
    return combined
