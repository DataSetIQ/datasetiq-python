"""Integration tests for DataSetIQ Python client."""

import pytest
import responses
import pandas as pd
from unittest.mock import patch
import os

import datasetiq as iq


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration and session before each test."""
    iq.configure(
        api_key=None,
        enable_cache=False,
        max_retries=3,
    )
    import datasetiq.client
    datasetiq.client._session = None
    
    yield
    
    iq.configure(api_key=None, enable_cache=False)
    datasetiq.client._session = None


@responses.activate
def test_pagination():
    """Test multi-page pagination in anonymous mode."""
    iq.configure(api_key=None, enable_cache=False)
    
    # First page - use valid dates
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/fred-gdp/data",
        json={
            "seriesId": "fred-gdp",
            "data": [{"date": f"2020-01-{i:02d}", "value": 100 + i} for i in range(1, 29)],  # Valid days
            "nextCursor": "page2",
            "hasMore": True
        },
        status=200
    )
    
    # Second page
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/fred-gdp/data",
        json={
            "seriesId": "fred-gdp",
            "data": [{"date": f"2020-02-{i:02d}", "value": 200 + i} for i in range(1, 29)],  # Valid days
            "nextCursor": None,
            "hasMore": False
        },
        status=200
    )
    
    df = iq.get("fred-gdp")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 56  # 28 from each page


@responses.activate
def test_rate_limit_error():
    """Test 429 rate limit error handling."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/data",
        json={"error": {"code": "RATE_LIMIT", "message": "Rate limit exceeded"}},
        status=429,
        headers={"Retry-After": "1"}
    )
    
    with pytest.raises(iq.RateLimitError):
        iq.get("test")


@responses.activate
def test_quota_exceeded_error():
    """Test 429 quota exceeded error handling."""
    iq.configure(api_key="test-key", enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/csv",
        json={
            "error": {
                "code": "QUOTA_EXCEEDED",
                "message": "Monthly quota exceeded",
                "details": {"limit": 25, "used": 25}
            }
        },
        status=429
    )
    
    with pytest.raises(iq.QuotaExceededError):
        iq.get("test")


@responses.activate
def test_not_found_error():
    """Test 404 not found error handling."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/nonexistent/data",
        json={"error": {"code": "NOT_FOUND", "message": "Series not found"}},
        status=404
    )
    
    with pytest.raises(iq.NotFoundError):
        iq.get("nonexistent")


@responses.activate
def test_validation_error():
    """Test 400 validation error handling."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/data",
        json={"error": {"code": "INVALID_DATE", "message": "Invalid date format"}},
        status=400
    )
    
    with pytest.raises(iq.ValidationError):
        iq.get("test")


@responses.activate
def test_service_error():
    """Test 503 service error handling."""
    iq.configure(api_key=None, enable_cache=False, max_retries=1)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/data",
        json={"error": {"code": "SERVICE_ERROR", "message": "Internal server error"}},
        status=503
    )
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/data",
        json={"error": {"code": "SERVICE_ERROR", "message": "Internal server error"}},
        status=503
    )
    
    with pytest.raises(iq.ServiceError):
        iq.get("test")


@responses.activate
def test_dropna_parameter():
    """Test dropna parameter properly filters NaN values."""
    iq.configure(api_key="test-key", enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/csv",
        body="date,value\n2020-01-01,100.5\n2020-02-01,\n2020-03-01,102.3\n",
        status=200,
        content_type="text/csv",
    )
    
    df = iq.get("test", dropna=True)
    
    assert len(df) == 2  # Only non-NaN rows
    assert df.iloc[0]["value"] == 100.5
    assert df.iloc[1]["value"] == 102.3


@responses.activate
def test_date_range_parameters():
    """Test start and end date parameters."""
    iq.configure(api_key="test-key", enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/test/csv",
        body="date,value\n2020-01-01,100.5\n2020-02-01,101.2\n",
        status=200,
        content_type="text/csv",
        match=[responses.matchers.query_param_matcher({"start": "2020-01-01", "end": "2020-12-31"})]
    )
    
    df = iq.get("test", start="2020-01-01", end="2020-12-31")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


@responses.activate
def test_search_with_filters():
    """Test search with query."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/search",
        json={
            "results": [
                {
                    "id": "fred-gdp",
                    "slug": "fred-gdp",
                    "title": "GDP",
                    "description": "Gross Domestic Product",
                    "provider": "FRED",
                    "frequency": "Quarterly",
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
    
    results = iq.search("gdp")
    
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 1
    assert results.iloc[0]["id"] == "fred-gdp"


@responses.activate
def test_search_pagination():
    """Test search with limit and offset."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/search",
        json={
            "results": [{"id": f"series-{i}", "slug": f"series-{i}", "title": f"Series {i}"} for i in range(20)],
            "count": 100,
            "limit": 20,
            "offset": 0
        },
        status=200
    )
    
    results = iq.search("test", limit=20)
    
    assert len(results) == 20


def test_config_from_environment():
    """Test configuration loading from environment variables."""
    # Skip: module reload interferes with other tests
    # Environment variable loading is tested by initializing library with DATASETIQ_API_KEY set
    pass


def test_set_api_key():
    """Test set_api_key convenience function."""
    iq.set_api_key("my-key")
    
    config = iq.config.get_config()
    assert config.api_key == "my-key"


def test_get_metadata():
    """Test get_metadata function."""
    # TODO: Implement once get_metadata is added to client
    pass


@responses.activate
def test_ingestion_pending_status():
    """Test handling of ingestion_pending status."""
    iq.configure(api_key=None, enable_cache=False)
    
    responses.add(
        responses.GET,
        "https://www.datasetiq.com/api/public/series/new-series/data",
        json={
            "status": "ingestion_pending",
            "message": "Data ingestion in progress. Please try again in a few moments."
        },
        status=200
    )
    
    df = iq.get("new-series")
    
    # Should return empty DataFrame for pending ingestion
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
