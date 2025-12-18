# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-17

### Added
- Initial public release
- `get()` function for fetching time series data
- `search()` function for dataset discovery
- `configure()` for client configuration
- `set_api_key()` helper function
- Disk-based caching with TTL
- Automatic retry logic with exponential backoff
- Typed exceptions with marketing messages
- Support for authenticated (CSV) and anonymous (paginated JSON) modes
- Date filtering with `start` and `end` parameters
- NaN handling with `dropna` parameter
- Comprehensive test suite
- Documentation and examples

### Features
- TCP connection reuse via `requests.Session`
- Respects `Retry-After` headers
- Pagination safety valve (max 200 pages for anonymous)
- SHA256-based cache keying
- Type-safe error handling

[0.1.0]: https://github.com/DataSetIQ/datasetiq-python/releases/tag/v0.1.0
