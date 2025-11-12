"""Unit tests for CLI interface."""
import json
import sys
from unittest.mock import MagicMock, patch
from io import StringIO

import pytest

from src.dependency_injection.container import Container
from src.domain.audio_source import AudioSource, AudioSourceList


class TestListCommand:
    """Tests for list_command function."""

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_list_command_success(self, mock_exit, mock_stdout):
        """Test successful list command execution."""
        from src.presentation.cli import list_command

        container = MagicMock()
        mock_use_case = MagicMock()
        container.list_sources_use_case.return_value = mock_use_case
        mock_use_case.execute.return_value = AudioSourceList([
            AudioSource(name="Microphone 1", index=0),
            AudioSource(name="Microphone 2", index=1),
        ])

        list_command(container, query="", limit=10)

        output = mock_stdout.getvalue()
        data = json.loads(output)

        assert "sources" in data
        assert len(data["sources"]) == 2
        assert data["sources"][0]["name"] == "Microphone 1"
        assert data["sources"][0]["index"] == 0
        mock_exit.assert_called_once_with(0)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_list_command_with_query(self, mock_exit, mock_stdout):
        """Test list command with query filter."""
        from src.presentation.cli import list_command
        
        container = MagicMock()
        mock_use_case = MagicMock()
        container.list_sources_use_case.return_value = mock_use_case
        mock_use_case.execute.return_value = AudioSourceList([
            AudioSource(name="USB Microphone", index=0),
        ])
        
        list_command(container, query="USB", limit=10)
        
        mock_use_case.execute.assert_called_once_with(query="USB", limit=10)
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert len(data["sources"]) == 1
        assert data["sources"][0]["name"] == "USB Microphone"

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_list_command_error(self, mock_exit, mock_stdout):
        """Test list command error handling."""
        from src.presentation.cli import list_command
        
        container = MagicMock()
        mock_use_case = MagicMock()
        container.list_sources_use_case.return_value = mock_use_case
        mock_use_case.execute.side_effect = ValueError("Invalid limit")
        
        list_command(container, query="", limit=-1)
        
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert "error" in data
        assert "Invalid limit" in data["error"]
        mock_exit.assert_called_once_with(1)


class TestSwitchCommand:
    """Tests for switch_command function."""

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_switch_command_success(self, mock_exit, mock_stdout):
        """Test successful switch command execution."""
        from src.presentation.cli import switch_command
        
        container = MagicMock()
        mock_use_case = MagicMock()
        container.switch_source_use_case.return_value = mock_use_case
        
        switch_command(container, name="USB Microphone")
        
        mock_use_case.execute.assert_called_once_with("USB Microphone")
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert data["success"] is True
        assert "USB Microphone" in data["message"]
        mock_exit.assert_called_once_with(0)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_switch_command_empty_name(self, mock_exit, mock_stdout):
        """Test switch command with empty name."""
        from src.presentation.cli import switch_command
        
        container = MagicMock()
        
        switch_command(container, name="")
        
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert "error" in data
        assert "cannot be empty" in data["error"].lower()
        mock_exit.assert_called_once_with(1)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_switch_command_runtime_error(self, mock_exit, mock_stdout):
        """Test switch command with runtime error."""
        from src.presentation.cli import switch_command
        
        container = MagicMock()
        mock_use_case = MagicMock()
        container.switch_source_use_case.return_value = mock_use_case
        mock_use_case.execute.side_effect = RuntimeError("Source not found")
        
        switch_command(container, name="Non-existent")
        
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert "error" in data
        assert "Source not found" in data["error"]
        mock_exit.assert_called_once_with(1)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_switch_command_value_error(self, mock_exit, mock_stdout):
        """Test switch command with value error."""
        from src.presentation.cli import switch_command
        
        container = MagicMock()
        mock_use_case = MagicMock()
        container.switch_source_use_case.return_value = mock_use_case
        mock_use_case.execute.side_effect = ValueError("Invalid source name")
        
        switch_command(container, name="   ")
        
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert "error" in data
        mock_exit.assert_called_once_with(1)


class TestOutputJson:
    """Tests for output_json function."""

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_output_json_success(self, mock_exit, mock_stdout):
        """Test JSON output function."""
        from src.presentation.cli import output_json
        
        data = {"test": "value", "number": 42}
        output_json(data, exit_code=0)
        
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        
        assert parsed == data
        mock_exit.assert_called_once_with(0)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.exit")
    def test_output_json_error(self, mock_exit, mock_stdout):
        """Test JSON error output."""
        from src.presentation.cli import output_error
        
        output_error("Test error message", exit_code=1)
        
        output = mock_stdout.getvalue()
        data = json.loads(output)
        
        assert "error" in data
        assert data["error"] == "Test error message"
        mock_exit.assert_called_once_with(1)
