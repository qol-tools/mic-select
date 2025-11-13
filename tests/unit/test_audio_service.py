"""Unit tests for audio service."""
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.audio_service import PactlClient


class TestPactlClientListSources:
    """Tests for PactlClient.list_sources method."""

    @patch("src.infrastructure.audio_service.subprocess.run")
    def test_list_sources_success(self, mock_run):
        """Test successful source listing and monitor filtering."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "Source #0\n"
                "\tName: alsa_input.pci-0000_00_1f.3.analog-stereo\n"
                "\tDescription: Built-in Audio Analog Stereo\n"
                "Source #1\n"
                "\tName: alsa_output.pci-0000_00_1f.3.iec958-stereo.monitor\n"
                "\tDescription: Monitor of Built-in Audio Digital Stereo\n"
            ),
        )

        client = PactlClient()
        result = client.list_sources()

        assert len(result.sources) == 1
        assert result.sources[0].name == "alsa_input.pci-0000_00_1f.3.analog-stereo"
        assert result.sources[0].description == "Built-in Audio Analog Stereo"
        # Should filter out monitor sources
        for source in result.sources:
            assert "monitor" not in source.name.lower()

    @patch("src.infrastructure.audio_service.subprocess.run")
    def test_list_sources_timeout(self, mock_run):
        """Test handling of timeout exception."""
        mock_run.side_effect = subprocess.TimeoutExpired("pactl", 0.5)

        client = PactlClient()
        result = client.list_sources()

        assert result.sources == []

    @patch("src.infrastructure.audio_service.subprocess.run")
    def test_list_sources_file_not_found(self, mock_run):
        """Test handling of missing pactl command."""
        mock_run.side_effect = FileNotFoundError()

        client = PactlClient()
        result = client.list_sources()

        assert result.sources == []

    @patch("src.infrastructure.audio_service.subprocess.run")
    def test_list_sources_command_failure(self, mock_run):
        """Test handling of command failure or empty output."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        client = PactlClient()
        result = client.list_sources()

        assert result.sources == []


class TestPactlClientSetDefaultSource:
    """Tests for PactlClient.set_default_source method."""

    @patch("src.infrastructure.audio_service.subprocess.run")
    def test_set_default_source(self, mock_run):
        """Test setting default source."""
        client = PactlClient()
        source_name = "alsa_input.test.mono-fallback"

        client.set_default_source(source_name)

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert isinstance(call_args, list)
        assert "pactl" in call_args
        assert "set-default-source" in call_args
        assert source_name in call_args


class TestPactlClientMoveStreams:
    """Tests for PactlClient.move_streams_to_source method."""

    @patch("src.infrastructure.audio_service.subprocess.run")
    def test_move_streams_to_source(self, mock_run):
        """Test moving streams to source."""
        from unittest.mock import MagicMock
        client = PactlClient()
        source_name = "alsa_input.test.mono-fallback"
        
        # Mock first call (list source-outputs) to return empty or valid output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="123\talsa_input.test.mono-fallback\tapplication\n"
        )

        client.move_streams_to_source(source_name)

        # Should be called at least once (list source-outputs)
        assert mock_run.call_count >= 1
        # Check first call is list command
        first_call = mock_run.call_args_list[0][0][0]
        assert isinstance(first_call, list)
        assert "pactl" in first_call
        assert "list" in first_call
        assert "source-outputs" in first_call
