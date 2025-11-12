"""Unit tests for macOS audio service."""
import subprocess
import sys
from unittest.mock import MagicMock, patch, Mock

import pytest

# Skip all tests if not on macOS
pytestmark = pytest.mark.skipif(
    sys.platform != "darwin",
    reason="macOS audio service tests only run on macOS"
)


class TestMacOSAudioClientInit:
    """Tests for MacOSAudioClient initialization."""

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    def test_init_success(self, mock_which):
        """Test successful initialization when SwitchAudioSource is found."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        assert client._switch_audio_source_path == "/usr/local/bin/SwitchAudioSource"

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    def test_init_not_found(self, mock_which):
        """Test initialization failure when SwitchAudioSource is not found."""
        mock_which.return_value = None
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        with pytest.raises(RuntimeError, match="SwitchAudioSource not found"):
            MacOSAudioClient()


class TestMacOSAudioClientListSources:
    """Tests for MacOSAudioClient.list_sources method."""

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_list_sources_success(self, mock_run, mock_which):
        """Test successful source listing."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Built-in Microphone\nUSB Microphone\nExternal Microphone\n"
        )
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        result = client.list_sources()
        
        assert len(result.sources) == 3
        assert result.sources[0].name == "Built-in Microphone"
        assert result.sources[1].name == "USB Microphone"
        assert result.sources[2].name == "External Microphone"

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_list_sources_timeout(self, mock_run, mock_which):
        """Test handling of timeout exception."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.side_effect = subprocess.TimeoutExpired("SwitchAudioSource", 0.5)
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        result = client.list_sources()
        
        assert result.sources == []

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_list_sources_command_failure(self, mock_run, mock_which):
        """Test handling of command failure."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        result = client.list_sources()
        
        assert result.sources == []

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_list_sources_empty_output(self, mock_run, mock_which):
        """Test handling of empty output."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        result = client.list_sources()
        
        assert result.sources == []


class TestMacOSAudioClientSetDefaultSource:
    """Tests for MacOSAudioClient.set_default_source method."""

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_set_default_source_success(self, mock_run, mock_which):
        """Test setting default source successfully."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        client.set_default_source("Built-in Microphone")
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert isinstance(call_args, list)
        assert call_args[0] == "/usr/local/bin/SwitchAudioSource"
        assert "-s" in call_args
        assert "Built-in Microphone" in call_args
        assert "-t" in call_args
        assert "input" in call_args

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_set_default_source_failure(self, mock_run, mock_which):
        """Test handling of set default source failure."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.return_value = MagicMock(returncode=1, stderr="Source not found")
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        
        with pytest.raises(RuntimeError, match="Failed to switch audio source"):
            client.set_default_source("Non-existent Microphone")

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    @patch("src.infrastructure.macos_audio_service.subprocess.run")
    def test_set_default_source_timeout(self, mock_run, mock_which):
        """Test handling of timeout when setting default source."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        mock_run.side_effect = subprocess.TimeoutExpired("SwitchAudioSource", 1.0)
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        
        with pytest.raises(RuntimeError, match="Timeout while switching"):
            client.set_default_source("Built-in Microphone")


class TestMacOSAudioClientMoveStreams:
    """Tests for MacOSAudioClient.move_streams_to_source method."""

    @patch("src.infrastructure.macos_audio_service.shutil.which")
    def test_move_streams_to_source_noop(self, mock_which):
        """Test that move_streams_to_source is a no-op on macOS."""
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        client = MacOSAudioClient()
        # Should not raise any exception
        client.move_streams_to_source("Built-in Microphone")
