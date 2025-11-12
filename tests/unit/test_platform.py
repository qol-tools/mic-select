"""Unit tests for platform detection."""
import sys
from unittest.mock import patch, MagicMock

import pytest

from src.config import Config


class TestDetectPlatform:
    """Tests for detect_platform function."""

    def test_detect_platform_linux(self):
        """Test platform detection for Linux."""
        from src.infrastructure.platform import detect_platform
        
        with patch("sys.platform", "linux"):
            result = detect_platform()
            assert result == "linux"

    def test_detect_platform_darwin(self):
        """Test platform detection for macOS."""
        from src.infrastructure.platform import detect_platform
        
        with patch("sys.platform", "darwin"):
            result = detect_platform()
            assert result == "darwin"

    def test_detect_platform_unknown(self):
        """Test platform detection for unknown platform."""
        from src.infrastructure.platform import detect_platform
        
        with patch("sys.platform", "win32"):
            result = detect_platform()
            assert result == "unknown"


class TestGetAudioClient:
    """Tests for get_audio_client function."""

    @patch("sys.platform", "linux")
    @patch("src.infrastructure.platform.detect_platform")
    def test_get_audio_client_linux(self, mock_detect):
        """Test getting audio client on Linux."""
        mock_detect.return_value = "linux"
        
        from src.infrastructure.platform import get_audio_client
        from src.infrastructure.audio_service import PactlClient
        
        config = Config()
        client = get_audio_client(config)
        
        assert isinstance(client, PactlClient)

    @patch("sys.platform", "darwin")
    @patch("src.infrastructure.platform.detect_platform")
    @patch("src.infrastructure.macos_audio_service.shutil.which")
    def test_get_audio_client_darwin(self, mock_which, mock_detect):
        """Test getting audio client on macOS."""
        mock_detect.return_value = "darwin"
        mock_which.return_value = "/usr/local/bin/SwitchAudioSource"
        
        from src.infrastructure.platform import get_audio_client
        from src.infrastructure.macos_audio_service import MacOSAudioClient
        
        config = Config()
        client = get_audio_client(config)
        
        assert isinstance(client, MacOSAudioClient)

    @patch("sys.platform", "win32")
    @patch("src.infrastructure.platform.detect_platform")
    def test_get_audio_client_unsupported(self, mock_detect):
        """Test getting audio client on unsupported platform."""
        mock_detect.return_value = "unknown"
        
        from src.infrastructure.platform import get_audio_client
        
        config = Config()
        
        with pytest.raises(RuntimeError, match="Unsupported platform"):
            get_audio_client(config)

    @patch("sys.platform", "darwin")
    @patch("src.infrastructure.platform.detect_platform")
    @patch("src.infrastructure.macos_audio_service.shutil.which")
    def test_get_audio_client_darwin_missing_tool(self, mock_which, mock_detect):
        """Test getting audio client on macOS when SwitchAudioSource is missing."""
        mock_detect.return_value = "darwin"
        mock_which.return_value = None
        
        from src.infrastructure.platform import get_audio_client
        
        config = Config()
        
        with pytest.raises(RuntimeError, match="SwitchAudioSource not found"):
            get_audio_client(config)
