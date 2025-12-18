"""
Disk-based caching with TTL support.

Cache location: appdirs.user_cache_dir("datasetiq")
Keying strategy: SHA256 hash of request parameters
Storage format: Pickle (data + timestamp tuple)
"""

import hashlib
import os
import pickle
import time
from pathlib import Path
from typing import Any, Optional

import appdirs


def _get_cache_dir() -> Path:
    """Get the cache directory path, creating it if necessary."""
    cache_dir = Path(appdirs.user_cache_dir("datasetiq"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _generate_key(input_string: str) -> str:
    """
    Generate a cache key from input parameters.
    
    Args:
        input_string: String to hash (e.g., "base_url|endpoint|series_id|start|end")
    
    Returns:
        SHA256 hex digest
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


def get(key: str, ttl: int) -> Optional[Any]:
    """
    Retrieve cached data if it exists and hasn't expired.
    
    Args:
        key: Cache key (will be hashed)
        ttl: Time-to-live in seconds
    
    Returns:
        Cached data if valid, None otherwise
    """
    cache_dir = _get_cache_dir()
    cache_key = _generate_key(key)
    cache_file = cache_dir / f"{cache_key}.pkl"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, "rb") as f:
            data, saved_at = pickle.load(f)
        
        # Check if expired
        age = time.time() - saved_at
        if age > ttl:
            # Expired, remove file
            cache_file.unlink()
            return None
        
        return data
    except (pickle.PickleError, OSError, ValueError):
        # Corrupted cache file, remove it
        try:
            cache_file.unlink()
        except OSError:
            pass
        return None


def set(key: str, data: Any) -> None:
    """
    Store data in cache with current timestamp.
    
    Args:
        key: Cache key (will be hashed)
        data: Data to cache (must be pickle-able)
    """
    cache_dir = _get_cache_dir()
    cache_key = _generate_key(key)
    cache_file = cache_dir / f"{cache_key}.pkl"
    
    try:
        with open(cache_file, "wb") as f:
            pickle.dump((data, time.time()), f, protocol=pickle.HIGHEST_PROTOCOL)
    except (pickle.PickleError, OSError):
        # Silently fail if caching doesn't work
        pass


def clear() -> int:
    """
    Clear all cached data.
    
    Returns:
        Number of files deleted
    """
    cache_dir = _get_cache_dir()
    count = 0
    
    for cache_file in cache_dir.glob("*.pkl"):
        try:
            cache_file.unlink()
            count += 1
        except OSError:
            pass
    
    return count


def get_cache_size() -> tuple[int, int]:
    """
    Get cache statistics.
    
    Returns:
        (file_count, total_bytes) tuple
    """
    cache_dir = _get_cache_dir()
    files = list(cache_dir.glob("*.pkl"))
    total_size = sum(f.stat().st_size for f in files if f.exists())
    return len(files), total_size
