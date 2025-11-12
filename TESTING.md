# Testing

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## Run Tests

```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-coverage     # With coverage report
```

## Structure

- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Integration tests requiring system access
- `tests/conftest.py` - Shared fixtures and configuration
- `pytest.ini` - Pytest configuration

## Coverage

HTML coverage reports are generated in `htmlcov/` directory.
