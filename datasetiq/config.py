"""
Global configuration for DataSetIQ client.

Users can customize behavior via configure() or environment variables.
"""

import os
from typing import Optional

# Sentinel value to distinguish "not provided" from "explicitly None"
_NOT_SET = object()


class Config:
    """Global configuration state."""

    def __init__(self):
        # API Key (from env or set manually)
        self.api_key: Optional[str] = os.environ.get("DATASETIQ_API_KEY")
        
        # Base URL for API
        self.base_url: str = "https://www.datasetiq.com/api/public"
        
        # Timeout (connect, read) in seconds
        self.timeout: tuple = (3.05, 30)
        
        # Retry configuration
        self.max_retries: int = 3
        self.max_retry_sleep: int = 20  # Cap total backoff time
        
        # Anonymous mode pagination safety valve
        self.anon_max_pages: int = 200  # 200 pages × 100 obs = 20K observations max
        
        # Cache TTLs (seconds)
        self.data_cache_ttl: int = 86400  # 24 hours for time series data
        self.search_cache_ttl: int = 900  # 15 minutes for search results
        
        # Enable/disable caching
        self.enable_cache: bool = True


# Global config instance
_config = Config()


def configure(
    api_key: Optional[str] = _NOT_SET,
    base_url: Optional[str] = _NOT_SET,
    timeout: Optional[tuple] = _NOT_SET,
    max_retries: Optional[int] = _NOT_SET,
    max_retry_sleep: Optional[int] = _NOT_SET,
    anon_max_pages: Optional[int] = _NOT_SET,
    data_cache_ttl: Optional[int] = _NOT_SET,
    search_cache_ttl: Optional[int] = _NOT_SET,
    enable_cache: Optional[bool] = _NOT_SET,
) -> None:
    """
    Configure DataSetIQ client settings.
    
    Args:
        api_key: Your DataSetIQ API key
        base_url: API base URL (default: https://www.datasetiq.com/api/public)
        timeout: (connect_timeout, read_timeout) tuple in seconds
        max_retries: Maximum retry attempts for failed requests
        max_retry_sleep: Maximum total sleep time for retries (seconds)
        anon_max_pages: Safety limit for anonymous pagination (default: 200)
        data_cache_ttl: Cache TTL for time series data in seconds (default: 86400)
        search_cache_ttl: Cache TTL for search results in seconds (default: 900)
        enable_cache: Enable/disable disk caching (default: True)
    
    Example:
        >>> import datasetiq as iq
        >>> iq.configure(
        ...     api_key="your-key-here",
        ...     max_retries=5,
        ...     data_cache_ttl=3600  # 1 hour cache
        ... )
    """
    if api_key is not _NOT_SET:
        _config.api_key = api_key
    if base_url is not _NOT_SET:
        if base_url is not None:
            _config.base_url = base_url.rstrip("/")
    if timeout is not _NOT_SET:
        _config.timeout = timeout
    if max_retries is not _NOT_SET:
        _config.max_retries = max_retries
    if max_retry_sleep is not _NOT_SET:
        _config.max_retry_sleep = max_retry_sleep
    if anon_max_pages is not _NOT_SET:
        _config.anon_max_pages = anon_max_pages
    if data_cache_ttl is not _NOT_SET:
        _config.data_cache_ttl = data_cache_ttl
    if search_cache_ttl is not _NOT_SET:
        _config.search_cache_ttl = search_cache_ttl
    if enable_cache is not _NOT_SET:
        _config.enable_cache = enable_cache


def set_api_key(api_key: str) -> None:
    """
    Set your DataSetIQ API key.
    
    Args:
        api_key: Your API key from https://www.datasetiq.com/dashboard/api-keys
    
    Example:
        >>> import datasetiq as iq
        >>> iq.set_api_key("diq_abc123...")
    """
    _config.api_key = api_key


def get_config() -> Config:
    """Get the current configuration instance."""
    return _config
