"""Basic smoke tests for DataSetIQ Python client."""

import pytest
import responses
import pandas as pd

import datasetiq as iq


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration and session before each test."""
    # Reset configuration
    iq.configure(
        api_key=None,
        enable_cache=False,
        max_retries=3,
    )
    # Clear the global session to ensure clean state
    import datasetiq.client
    datasetiq.client._session = None
    
    yield
    
    # Cleanup after test
    iq.configure(api_key=None, enable_cache=False)
    datasetiq.client._session = None


def test_import():
    """Test that package imports correctly."""
    assert iq.__version__ == "0.2.0"
    assert hasattr(iq, 'get')
    assert hasattr(iq, 'search')
    assert hasattr(iq, 'add_features')
    assert hasattr(iq, 'get_insight')
    assert hasattr(iq, 'get_ml_ready')
    assert hasattr(iq, 'configure')
    assert hasattr(iq, 'set_api_key')


def test_configure():
    """Test configuration works."""
    iq.configure(
        api_key="test-key",
        max_retries=5,
        data_cache_ttl=3600,
    )
    
    config = iq.config.get_config()
    assert config.api_key == "test-key"
    assert config.max_retries == 5
    assert config.data_cache_ttl == 3600


@responses.activate
def test_authenticated_csv():
    """Test CSV endpoint with auth."""
    iq.configure(api_key="test-key", enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/fred-cpi/csv",
        body="date,value\n2020-01-01,100.5\n2020-02-01,101.2\n",
        status=200,
        content_type="text/csv",
    )
    
    df = iq.get("fred-cpi")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "value" in df.columns
    assert df.iloc[0]["value"] == 100.5


@responses.activate
def test_anonymous_paginated():
    """Test paginated JSON without auth."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/fred-cpi/data",
        json={
            "seriesId": "fred-cpi",
            "data": [
                {"date": "2020-01-01", "value": 100.5},
                {"date": "2020-02-01", "value": 101.2}
            ],
            "nextCursor": None,
            "hasMore": False
        },
        status=200
    )
    
    df = iq.get("fred-cpi")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["value"] == 100.5


@responses.activate
def test_authentication_error():
    """Test 401 raises AuthenticationError."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/data",
        json={"error": {"code": "UNAUTHORIZED", "message": "Auth required"}},
        status=401
    )
    
    with pytest.raises(iq.AuthenticationError):
        iq.get("test")


@responses.activate
def test_search():
    """Test search function."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/search",
        json={
            "results": [
                {
                    "id": "fred-cpi",
                    "slug": "fred-cpi",
                    "title": "CPI",
                    "description": "Consumer Price Index",
                    "provider": "FRED",
                    "frequency": "Monthly",
                    "startDate": "1947-01-01",
                    "endDate": "2023-12-01",
                    "lastUpdated": "2024-01-15"
                }
            ],
            "count": 1,
            "limit": 10,
            "offset": 0
        },
        status=200
    )
    
    results = iq.search("cpi")
    
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 1
    assert results.iloc[0]["id"] == "fred-cpi"
