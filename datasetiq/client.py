"""
Core client logic for DataSetIQ API.

Handles:
- Session management with TCP reuse
- Retry logic with exponential backoff
- CSV vs JSON path selection
- Robust NaN handling
- Error translation to marketing messages
"""

import io
import time
from typing import Optional
from importlib.metadata import version

import pandas as pd
import requests

from . import cache
from .config import get_config
from .exceptions import (
    AuthenticationError,
    ForbiddenError,
    IngestionPendingError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ServiceError,
    ValidationError,
)


# Module-level session for TCP connection reuse
_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get or create the module-level session."""
    global _session
    if _session is None:
        _session = requests.Session()
        # Set default headers
        try:
            pkg_version = version("datasetiq")
        except Exception:
            pkg_version = "unknown"
        
        _session.headers.update({
            "User-Agent": f"datasetiq-python/{pkg_version}",
            "Accept-Encoding": "gzip",
        })
    return _session


def _handle_error_response(response: requests.Response) -> None:
    """
    Convert HTTP errors to typed exceptions with marketing messages.
    
    Args:
        response: Failed response object
    
    Raises:
        Appropriate DataSetIQError subclass
    """
    status_code = response.status_code
    
    # Try to parse error JSON
    try:
        error_data = response.json()
        error = error_data.get("error", {})
        code = error.get("code", "UNKNOWN")
        message = error.get("message", response.text or "Unknown error")
        details = error.get("details", {})
    except Exception:
        code = "UNKNOWN"
        message = response.text or f"HTTP {status_code}"
        details = {}
    
    # Map to typed exceptions
    if status_code == 401:
        raise AuthenticationError(message)
    
    elif status_code == 403:
        raise ForbiddenError(message)
    
    elif status_code == 404:
        raise NotFoundError(message)
    
    elif status_code == 400:
        raise ValidationError(message)
    
    elif status_code == 202:
        raise IngestionPendingError(message)
    
    elif status_code == 429:
        # Distinguish between rate limit and quota
        if code == "QUOTA_EXCEEDED":
            raise QuotaExceededError(
                metric=details.get("metric", "unknown"),
                current=details.get("current", 0),
                limit=details.get("limit", 0),
                message=message,
            )
        else:
            raise RateLimitError(
                message=message,
                limit=details.get("limit"),
                current=details.get("current"),
                reset_epoch_sec=details.get("resetEpochSec"),
            )
    
    elif status_code >= 500:
        raise ServiceError(status_code, code, message)
    
    else:
        # Unknown error
        raise ServiceError(status_code, code, message)


def _make_request_with_retry(
    method: str,
    url: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
) -> requests.Response:
    """
    Make HTTP request with retry logic.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full URL
        headers: Request headers
        params: Query parameters
    
    Returns:
        Successful response object
    
    Raises:
        DataSetIQError on failure
    """
    config = get_config()
    session = _get_session()
    
    total_sleep = 0
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            response = session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=config.timeout,
            )
            
            # Success
            if response.status_code < 400:
                return response
            
            # Check if we should retry
            should_retry = response.status_code in (429, 502, 503, 504)
            
            if not should_retry or attempt == config.max_retries:
                # Final attempt or non-retryable error
                _handle_error_response(response)
            
            # Calculate backoff
            retry_after = None
            if "Retry-After" in response.headers:
                try:
                    retry_after = int(response.headers["Retry-After"])
                except ValueError:
                    pass
            
            if retry_after is None:
                # Exponential backoff: 1s, 2s, 4s, 8s...
                retry_after = min(2 ** attempt, 10)
            
            # Respect max_retry_sleep cap
            if total_sleep + retry_after > config.max_retry_sleep:
                # Would exceed cap, make final attempt
                _handle_error_response(response)
            
            time.sleep(retry_after)
            total_sleep += retry_after
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            
            if attempt == config.max_retries:
                raise ServiceError(
                    503,
                    "CONNECTION_ERROR",
                    f"Failed to connect after {config.max_retries} retries: {str(e)}",
                )
            
            # Exponential backoff for connection errors
            backoff = min(2 ** attempt, 10)
            if total_sleep + backoff > config.max_retry_sleep:
                break
            
            time.sleep(backoff)
            total_sleep += backoff
    
    # Should not reach here, but handle it
    if last_exception:
        raise ServiceError(503, "CONNECTION_ERROR", str(last_exception))
    raise ServiceError(503, "MAX_RETRIES", "Maximum retries exceeded")


def _parse_csv_to_dataframe(csv_text: str, dropna: bool = False) -> pd.DataFrame:
    """
    Parse CSV text into a clean DataFrame.
    
    Args:
        csv_text: Raw CSV string
        dropna: Whether to drop rows with NaN values
    
    Returns:
        Pandas DataFrame with date index
    """
    # Parse CSV with aggressive NaN detection
    df = pd.read_csv(
        io.StringIO(csv_text),
        na_values=[".", "NA", "N/A", "null", "", "nan", "NaN"],
    )
    
    # Convert value column to numeric (coerce errors to NaN)
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    # Parse date and set as index
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
    
    # Optionally drop NaN values
    if dropna and "value" in df.columns:
        df = df.dropna(subset=["value"])
    
    return df


def _parse_json_to_dataframe(data: list, dropna: bool = False) -> pd.DataFrame:
    """
    Parse JSON observations into a DataFrame.
    
    Args:
        data: List of {date, value} dicts
        dropna: Whether to drop rows with NaN values
    
    Returns:
        Pandas DataFrame with date index
    """
    if not data:
        # Return empty DataFrame with correct structure
        return pd.DataFrame(columns=["value"]).astype({"value": float})
    
    df = pd.DataFrame(data)
    
    # Convert value to numeric
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    # Parse date and set as index
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
    
    # Optionally drop NaN values
    if dropna and "value" in df.columns:
        df = df.dropna(subset=["value"])
    
    return df


def get(
    series_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    dropna: bool = False,
) -> pd.DataFrame:
    """
    Fetch time series data as a Pandas DataFrame.
    
    Args:
        series_id: Series identifier (e.g., "fred-cpi", "bls-unemployment")
        start: Start date in YYYY-MM-DD format (optional)
        end: End date in YYYY-MM-DD format (optional)
        dropna: Drop rows with NaN values (default: False, preserves data gaps)
    
    Returns:
        Pandas DataFrame with date index and 'value' column
    
    Raises:
        AuthenticationError: API key required
        NotFoundError: Series not found
        RateLimitError: Rate limit exceeded
        QuotaExceededError: Monthly quota exceeded
        ValidationError: Invalid parameters
        ServiceError: Server error
    
    Example:
        >>> import datasetiq as iq
        >>> df = iq.get("fred-cpi")
        >>> print(df.head())
                    value
        date
        1947-01-01   21.48
        1947-02-01   21.62
        ...
        
        >>> # With date filtering
        >>> df = iq.get("fred-cpi", start="2020-01-01", end="2023-12-31")
    """
    config = get_config()
    
    # Generate cache key
    cache_key = f"{config.base_url}|get|{series_id}|{start}|{end}|{dropna}"
    
    # Check cache
    if config.enable_cache:
        cached = cache.get(cache_key, config.data_cache_ttl)
        if cached is not None:
            return cached
    
    # Prepare headers
    headers = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    # Prepare query params
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    # Choose path: CSV (auth) or JSON (anon)
    if config.api_key:
        # Path A: Authenticated CSV export
        url = f"{config.base_url}/series/{series_id}/csv"
        response = _make_request_with_retry("GET", url, headers=headers, params=params)
        df = _parse_csv_to_dataframe(response.text, dropna=dropna)
    else:
        # Path B: Anonymous paginated JSON
        url = f"{config.base_url}/series/{series_id}/data"
        params["limit"] = 100  # Anonymous limit
        
        all_data = []
        page_count = 0
        cursor = None
        
        while True:
            if cursor:
                params["cursor"] = cursor
            
            response = _make_request_with_retry("GET", url, headers=headers, params=params)
            result = response.json()
            
            # Handle special statuses
            if result.get("status") in ("metadata_only", "ingestion_pending"):
                # Return empty DataFrame with message
                message = result.get("message", "No data available")
                print(f"⚠️  {message}")
                return pd.DataFrame(columns=["value"]).astype({"value": float})
            
            data = result.get("data", [])
            all_data.extend(data)
            
            # Check pagination
            cursor = result.get("nextCursor")
            has_more = result.get("hasMore", False)
            
            if not has_more or not cursor:
                break
            
            # Safety valve: prevent infinite loops
            page_count += 1
            if page_count >= config.anon_max_pages:
                raise RateLimitError(
                    message=f"Series too large for anonymous mode (>{config.anon_max_pages * 100} observations). "
                    "Set an API key for full CSV export: iq.set_api_key('your-key')",
                )
        
        df = _parse_json_to_dataframe(all_data, dropna=dropna)
    
    # Cache result
    if config.enable_cache:
        cache.set(cache_key, df)
    
    return df


def search(
    query: str,
    limit: int = 10,
    offset: int = 0,
) -> pd.DataFrame:
    """
    Search for datasets by keyword.
    
    Args:
        query: Search query (searches titles, descriptions, IDs)
        limit: Maximum results to return (default: 10, max: 10)
        offset: Pagination offset (default: 0)
    
    Returns:
        DataFrame with columns: id, slug, title, description, provider,
        frequency, start_date, end_date, last_updated
    
    Example:
        >>> import datasetiq as iq
        >>> results = iq.search("unemployment rate")
        >>> print(results[["id", "title"]])
    """
    config = get_config()
    
    # Generate cache key
    cache_key = f"{config.base_url}|search|{query}|{limit}|{offset}"
    
    # Check cache
    if config.enable_cache:
        cached = cache.get(cache_key, config.search_cache_ttl)
        if cached is not None:
            return cached
    
    # Prepare headers
    headers = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    # Make request
    url = f"{config.base_url}/search"
    params = {"q": query, "limit": min(limit, 10), "offset": offset}
    
    response = _make_request_with_retry("GET", url, headers=headers, params=params)
    result = response.json()
    
    results = result.get("results", [])
    df = pd.DataFrame(results) if results else pd.DataFrame()
    
    # Cache result
    if config.enable_cache:
        cache.set(cache_key, df)
    
    return df
