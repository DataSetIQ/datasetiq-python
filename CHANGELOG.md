# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2025-12-17

### Fixed
- **Anonymous users now receive latest 100 observations** instead of oldest 100
- Backend API updated to fetch most recent data for non-authenticated requests  
- Updated documentation to clarify anonymous mode returns latest data only

### Changed
- Improved README to explain anonymous vs authenticated data access patterns

## [0.1.0] - 2025-12-17

### Added
- Initial release of DataSetIQ Python client
- Core `get()` function for fetching time series data
- `search()` function for dataset discovery
- Intelligent disk-based caching with TTL
- Automatic retry logic with exponential backoff
- Support for authenticated (CSV) and anonymous (JSON) modes
- Comprehensive error handling with marketing-embedded messages
- Date filtering support (start/end parameters)
- Configuration management via `configure()` and `set_api_key()`
- Cache management: `clear_cache()` and `get_cache_size()`
- Full pandas DataFrame integration with date index
- Example scripts (basic and advanced)
- Complete documentation and guides

### Features
- 40M+ economic time series from FRED, BLS, Census, World Bank, and more
- Free tier: 25 requests/minute + 25 AI insights/month
- Smart NaN detection and handling
- Connection pooling for performance
- `Retry-After` header support
- Metadata-only dataset detection
- Cross-platform cache directory management
