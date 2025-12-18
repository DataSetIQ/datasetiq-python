# Contributing to DataSetIQ Python Client

Thank you for considering contributing to the DataSetIQ Python client!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DataSetIQ/datasetiq-python.git
   cd datasetiq-python
   ```

2. **Install in editable mode with dev dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests:**
   ```bash
   pytest
   ```

## Code Style

- We use **Black** for code formatting
- We use **Ruff** for linting
- Run before committing:
  ```bash
  black datasetiq tests examples
  ruff check datasetiq tests examples
  ```

## Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use `responses` library for HTTP mocking
- Run tests with coverage:
  ```bash
  pytest --cov=datasetiq --cov-report=html
  ```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Commit with clear messages
7. Push and create a Pull Request

## Reporting Issues

- Use GitHub Issues
- Include Python version, OS, and library version
- Provide minimal reproduction example
- Include full error traceback

## Questions?

Contact us at support@datasetiq.com or open a GitHub Discussion.
