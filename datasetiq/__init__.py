"""
DataSetIQ Python Client — Official SDK for the Modern Economic Data Platform

Get started:
    >>> import datasetiq as iq
    >>> iq.set_api_key("your-key-here")  # Get free key at datasetiq.com/dashboard/api-keys
    >>> df = iq.get("fred-cpi")
    >>> print(df.head())

Features:
    - 40M+ economic time series
    - Pandas-ready DataFrames
    - Intelligent caching
    - Automatic retry logic
    - Free tier available

Links:
    - Homepage: https://www.datasetiq.com
    - API Keys: https://www.datasetiq.com/dashboard/api-keys
    - Documentation: https://www.datasetiq.com/docs
    - Pricing: https://www.datasetiq.com/pricing
"""

__version__ = "0.1.2"

# Public API exports
from .client import get, search
from .config import configure, set_api_key
from .cache import clear as clear_cache, get_cache_size

# Exception exports (for type checking)
from .exceptions import (
    AuthenticationError,
    DataSetIQError,
    ForbiddenError,
    IngestionPendingError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ServiceError,
    ValidationError,
)

__all__ = [
    # Core functions
    "get",
    "search",
    "configure",
    "set_api_key",
    # Cache management
    "clear_cache",
    "get_cache_size",
    # Exceptions
    "DataSetIQError",
    "AuthenticationError",
    "ForbiddenError",
    "RateLimitError",
    "QuotaExceededError",
    "NotFoundError",
    "ValidationError",
    "ServiceError",
    "IngestionPendingError",
]
