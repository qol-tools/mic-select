"""Unit tests for Ulauncher presenter."""
from unittest.mock import Mock

import pytest

from lib.domain.audio_source import AudioSource, AudioSourceList
from lib.presentation.ulauncher_adapter import MicSwitcherPresenter


@pytest.fixture
def mock_list_use_case():
    """Mock list sources use case."""
    return Mock()


@pytest.fixture
def mock_switch_use_case():
    """Mock switch source use case."""
    return Mock()


@pytest.fixture
def presenter(mock_list_use_case, mock_switch_use_case):
    """Create a presenter with mocked dependencies."""
    return MicSwitcherPresenter(mock_list_use_case, mock_switch_use_case)


class TestMicSwitcherPresenter:
    """Tests for MicSwitcherPresenter."""

    def test_command_builder_creates_valid_script(self):
        """Test that SwitchCommandBuilder creates correct structure."""
        from lib.presentation.ulauncher_adapter import SwitchCommandBuilder

        builder = SwitchCommandBuilder(notification_expire_time=1500)
        source = "alsa_input.test.mono-fallback"
        script = builder.build(source, "Test Microphone")

        assert source in script
        assert "set-default-source" in script
        assert "move-source-output" in script
        assert "source-outputs" in script
        assert "notify-send" in script

    def test_present_sources_empty_list(self, presenter, mock_list_use_case):
        """Test presenting when no sources are found."""
        mock_list_use_case.execute.return_value = AudioSourceList([])

        result = presenter.present_sources("")

        assert result is not None

    def test_present_sources_with_sources(self, presenter, mock_list_use_case):
        """Test presenting with available sources."""
        sources = AudioSourceList([
            AudioSource(name="alsa_input.pci-0000_00_1f.3.analog-stereo", index=0),
            AudioSource(name="alsa_input.usb-ME6S-00.mono-fallback", index=1),
        ])
        mock_list_use_case.execute.return_value = sources

        result = presenter.present_sources("")

        assert result is not None
        mock_list_use_case.execute.assert_called_once()

    def test_present_sources_passes_query_and_limit(self, presenter, mock_list_use_case):
        """Test that query and limit are passed to use case."""
        sources = AudioSourceList([
            AudioSource(name="alsa_input.usb-ME6S-00.mono-fallback", index=0),
        ])
        mock_list_use_case.execute.return_value = sources

        result = presenter.present_sources("usb")

        mock_list_use_case.execute.assert_called_once_with(query="usb", limit=10)
        assert result is not None
