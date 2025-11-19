"""Pytest configuration and shared fixtures for OS-agnostic tests."""
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (may need system access)",
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Automatically mark tests based on their filename."""
    for item in items:
        test_file = str(item.fspath)

        if "integration" in test_file:
            item.add_marker(pytest.mark.integration)
            if not any(mark.name == "slow" for mark in item.iter_markers()):
                if any(
                    keyword in item.name.lower()
                    for keyword in ["performance", "timeout", "slow"]
                ):
                    item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)
