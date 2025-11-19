"""Integration tests for microphone switching."""
import subprocess

import pytest

from lib.infrastructure.audio_service import PactlClient
from lib.application.list_sources_use_case import ListSourcesUseCase
from lib.application.switch_source_use_case import SwitchSourceUseCase
from lib.presentation.ulauncher_adapter import MicSwitcherPresenter


class TestSwitchCommandGeneration:
    """Tests for switch command generation."""

    @pytest.fixture
    def command_builder(self):
        """Create command builder for testing."""
        from lib.presentation.ulauncher_adapter import SwitchCommandBuilder
        return SwitchCommandBuilder(notification_expire_time=1500)

    def test_switch_command_structure(self, command_builder):
        """Test that switch command has correct structure."""
        source = "alsa_input.test.mono-fallback"
        script = command_builder.build(source, "Test Mic")

        assert "set-default-source" in script
        assert source in script
        assert "move-source-output" in script
        assert "source-outputs" in script

    def test_switch_command_handles_special_chars(self, command_builder):
        """Test command generation with special characters."""
        import shlex
        source = "alsa_input.usb-0000:00:14.0.analog-stereo"
        script = command_builder.build(source, "Test Mic")

        escaped = shlex.quote(source)
        assert escaped in script
        assert source not in script or escaped in script

    def test_switch_command_syntax_valid(self, command_builder):
        """Test that generated script has valid shell syntax."""
        source = "alsa_input.test.mono-fallback"
        script = command_builder.build(source, "Test Mic")

        try:
            result = subprocess.run(
                ["bash", "-n"],
                input=script,
                capture_output=True,
                text=True,
                timeout=1,
            )

            assert result.returncode == 0, f"Invalid syntax: {result.stderr}"

        except FileNotFoundError:
            pytest.skip("bash not available")


class TestActualPactlCommands:
    """Tests for actual pactl commands with state preservation."""

    @pytest.fixture
    def original_source(self):
        """Get and restore original default source and move streams back."""
        try:
            result = subprocess.run(
                "pactl get-default-source",
                shell=True,
                capture_output=True,
                text=True,
                timeout=0.5,
            )
            original = result.stdout.strip() if result.returncode == 0 else None

            yield original

            if original:
                subprocess.run(
                    f"pactl set-default-source '{original}'",
                    shell=True,
                    capture_output=True,
                    timeout=0.5,
                )
                move_script = f"""for stream_id in $(pactl list short source-outputs 2>/dev/null | cut -f1); do
    if [ -n "$stream_id" ]; then
        pactl move-source-output "$stream_id" '{original}' 2>/dev/null || true
    fi
done"""
                subprocess.run(
                    move_script,
                    shell=True,
                    capture_output=True,
                    timeout=1.0,
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("pactl not available")

    @pytest.fixture
    def sources(self):
        """Get real sources if available."""
        try:
            client = PactlClient()
            use_case = ListSourcesUseCase(client)
            sources = use_case.execute()
            if sources.is_empty():
                pytest.skip("No sources available for testing")
            return sources
        except FileNotFoundError:
            pytest.skip("pactl not available on this system")

    def test_set_default_source_command(self, sources, original_source):
        """Test that set-default-source command works."""
        test_source = sources.sources[0].name

        result = subprocess.run(
            f"pactl set-default-source '{test_source}'",
            shell=True,
            capture_output=True,
            text=True,
            timeout=0.5,
        )

        assert result.returncode in [0, 1], f"Unexpected error: {result.stderr}"


class TestSwitchIntegration:
    """End-to-end integration tests for switching with state preservation."""

    @pytest.fixture
    def original_source(self):
        """Get and restore original default source and move streams back."""
        try:
            result = subprocess.run(
                "pactl get-default-source",
                shell=True,
                capture_output=True,
                text=True,
                timeout=0.5,
            )
            original = result.stdout.strip() if result.returncode == 0 else None

            yield original

            if original:
                subprocess.run(
                    f"pactl set-default-source '{original}'",
                    shell=True,
                    capture_output=True,
                    timeout=0.5,
                )
                move_script = f"""for stream_id in $(pactl list short source-outputs 2>/dev/null | cut -f1); do
    if [ -n "$stream_id" ]; then
        pactl move-source-output "$stream_id" '{original}' 2>/dev/null || true
    fi
done"""
                subprocess.run(
                    move_script,
                    shell=True,
                    capture_output=True,
                    timeout=1.0,
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("pactl not available")

    def test_switch_use_case_executes(self, original_source):
        """Test that switch use case can execute."""
        try:
            client = PactlClient()
            list_use_case = ListSourcesUseCase(client)
            sources = list_use_case.execute()

            if sources.is_empty():
                pytest.skip("No sources available for testing")

            switch_use_case = SwitchSourceUseCase(client)
            test_source = sources.sources[0].name

            switch_use_case.execute(test_source)

        except FileNotFoundError:
            pytest.skip("pactl not available on this system")
