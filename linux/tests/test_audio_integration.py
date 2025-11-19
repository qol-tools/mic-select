"""Integration tests for audio system."""
import subprocess

import pytest

from lib.infrastructure.audio_service import PactlClient
from lib.application.list_sources_use_case import ListSourcesUseCase
from lib.dependency_injection.container import Container


class TestPactlDirectAccess:
    """Tests for direct pactl command access."""

    def test_pactl_command_available(self):
        """Test that pactl command is available and responsive."""
        try:
            result = subprocess.run(
                ["pactl", "list", "short", "sources"],
                capture_output=True,
                text=True,
                timeout=1.0,
            )
            assert result.returncode in [0, 1]
        except FileNotFoundError:
            pytest.skip("pactl not available on this system")
        except subprocess.TimeoutExpired:
            pytest.fail("pactl command timed out - may be hanging")


class TestListSourcesIntegration:
    """Integration tests for listing audio sources."""

    def test_list_sources_with_real_pactl(self):
        """Test list_sources with real pactl command."""
        client = PactlClient()
        use_case = ListSourcesUseCase(client)

        try:
            sources = use_case.execute()

            assert hasattr(sources, "sources")
            assert hasattr(sources, "is_empty")

        except FileNotFoundError:
            pytest.skip("pactl not available on this system")

    def test_list_sources_filters_monitors(self):
        """Test that monitor sources are filtered out."""
        client = PactlClient()
        use_case = ListSourcesUseCase(client)

        try:
            sources = use_case.execute()

            for source in sources.sources:
                assert "monitor" not in source.name.lower()

        except FileNotFoundError:
            pytest.skip("pactl not available on this system")

    def test_list_sources_with_query(self):
        """Test filtering sources by query."""
        client = PactlClient()
        use_case = ListSourcesUseCase(client)

        try:
            all_sources = use_case.execute()

            if not all_sources.is_empty():
                query = all_sources.sources[0].name.split(".")[0]
                filtered = use_case.execute(query=query)

                for source in filtered.sources:
                    assert query.lower() in source.name.lower()

        except FileNotFoundError:
            pytest.skip("pactl not available on this system")


class TestExtensionInitialization:
    """Integration tests for extension initialization."""

    def test_container_creates_all_dependencies(self):
        """Test that container can create all dependencies."""
        container = Container()

        presenter = container.presenter()
        assert presenter is not None

        list_use_case = container.list_sources_use_case()
        assert list_use_case is not None

        switch_use_case = container.switch_source_use_case()
        assert switch_use_case is not None


class TestShellTimeout:
    """Tests for shell timeout command functionality."""

    def test_shell_timeout_works(self):
        """Test that shell timeout command actually works."""
        result = subprocess.run(
            "timeout 0.1 sleep 1",
            shell=True,
            capture_output=True,
            text=True,
            timeout=0.2,
        )

        assert result.returncode != 0, "Command should have been killed"

    def test_pactl_with_timeout_wrapper(self):
        """Test real pactl with timeout wrapper."""
        timeout_check = subprocess.run(
            ["which", "timeout"],
            capture_output=True,
        )
        if timeout_check.returncode != 0:
            pytest.skip("timeout command not available (Linux-only)")

        try:
            cmd = "timeout 0.15 pactl list short sources 2>/dev/null"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=0.3,
            )

            assert result.returncode in [0, 1, 124]

        except FileNotFoundError:
            pytest.skip("pactl not available on this system")
        except subprocess.TimeoutExpired:
            pytest.fail("Python timeout expired - timeout wrapper failed")
