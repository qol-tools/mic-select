"""Pytest configuration and shared fixtures."""
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

sys.modules['ulauncher'] = MagicMock()
sys.modules['ulauncher.api'] = MagicMock()
sys.modules['ulauncher.api.client'] = MagicMock()
sys.modules['ulauncher.api.client.Extension'] = MagicMock()
sys.modules['ulauncher.api.client.EventListener'] = MagicMock()
sys.modules['ulauncher.api.shared'] = MagicMock()
sys.modules['ulauncher.api.shared.event'] = MagicMock()
sys.modules['ulauncher.api.shared.item'] = MagicMock()
sys.modules['ulauncher.api.shared.item.ExtensionResultItem'] = MagicMock()
sys.modules['ulauncher.api.shared.action'] = MagicMock()
sys.modules['ulauncher.api.shared.action.RunScriptAction'] = MagicMock()
sys.modules['ulauncher.api.shared.action.RenderResultListAction'] = MagicMock()


@pytest.fixture
def mock_pactl_output():
    """Fixture providing sample pactl output."""
    return (
        "0\talsa_input.pci-0000_00_1f.3.analog-stereo\tPipeWire\n"
        "1\talsa_input.usb-ME6S-00.mono-fallback\tPipeWire\n"
        "2\talsa_output.pci-0000_00_1f.3.iec958-stereo.monitor\tPipeWire\n"
    )


@pytest.fixture
def sample_source_names():
    """Fixture providing sample source names."""
    return [
        "alsa_input.pci-0000_00_1f.3.analog-stereo",
        "alsa_input.usb-ME6S-00.mono-fallback",
        "alsa_input.usb-Webcam-00.mono-fallback",
    ]


def pytest_configure(config):
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


def pytest_collection_modifyitems(config, items):
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


@pytest.fixture
def pactl_available():
    """Check if pactl is available on the system."""
    try:
        result = subprocess.run(
            ["which", "pactl"],
            capture_output=True,
            timeout=1,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.fixture
def skip_if_no_pactl(pactl_available):
    """Skip test if pactl is not available."""
    if not pactl_available:
        pytest.skip("pactl not available on this system")
