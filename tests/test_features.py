"""Tests for feature helpers and insights."""

import pandas as pd
import pytest

import datasetiq as iq
from datasetiq import features


def _sample_df():
    idx = pd.date_range("2020-01-01", periods=24, freq="M")
    return pd.DataFrame({"value": range(1, 25)}, index=idx)


def test_add_features_dataframe():
    df = _sample_df()
    result = iq.add_features(df, lags=[1], windows=[3], dropna=False)
    
    assert "value" in result.columns
    assert "value_lag_1" in result.columns
    assert "value_rollmean_3" in result.columns
    assert "value_rollstd_3" in result.columns
    assert "value_yoy_pct" in result.columns
    assert "value_mom_pct" in result.columns
    assert "value_zscore" in result.columns


def test_get_insight_dataframe():
    df = _sample_df()
    insight = iq.get_insight(df, window="1y")
    
    assert insight["series"] == "series"
    assert "summary" in insight
    assert insight["latest_value"] == 24
    assert insight["trend"] in ("upward", "downward", "flat")


def test_get_ml_ready_with_features(monkeypatch):
    df = _sample_df()
    iq.configure(api_key="test-key")
    
    def fake_get(series_id, *args, **kwargs):
        return df.rename(columns={"value": "value"})
    
    monkeypatch.setattr(features, "get", fake_get)
    monkeypatch.setattr(iq, "get", fake_get)
    
    result = iq.get_ml_ready(["series_a", "series_b"], align="inner", impute="median")
    
    # Base columns present
    assert {"series_a", "series_b"}.issubset(set(result.columns))
    # Feature columns present
    assert "series_a_lag_1" in result.columns
    assert "series_b_rollmean_3" in result.columns
    # No NaNs after median fill
    assert result.isna().sum().sum() == 0
