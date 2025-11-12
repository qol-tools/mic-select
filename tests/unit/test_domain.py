"""Unit tests for domain models."""
import pytest

from src.domain.audio_source import AudioSource, AudioSourceList


class TestAudioSource:
    """Tests for AudioSource domain model."""

    def test_is_monitor_detects_monitor_source(self):
        """Test detection of monitor sources (case-insensitive)."""
        monitor_source = AudioSource(name="alsa_output.monitor", index=0)
        monitor_upper = AudioSource(name="alsa_output.MONITOR", index=1)
        regular_source = AudioSource(name="alsa_input.microphone", index=2)

        assert monitor_source.is_monitor()
        assert monitor_upper.is_monitor()
        assert not regular_source.is_monitor()

    def test_matches_query(self):
        """Test query matching (case-insensitive)."""
        source = AudioSource(name="alsa_input.usb-Microphone", index=0)

        assert source.matches_query("usb")
        assert source.matches_query("USB")
        assert source.matches_query("Microphone")
        assert not source.matches_query("bluetooth")


class TestAudioSourceList:
    """Tests for AudioSourceList domain model."""

    def test_filter_monitors(self):
        """Test filtering out monitor sources."""
        sources = [
            AudioSource(name="alsa_input.microphone", index=0),
            AudioSource(name="alsa_output.monitor", index=1),
            AudioSource(name="alsa_input.webcam", index=2),
        ]
        source_list = AudioSourceList(sources)

        filtered = source_list.filter_monitors()

        assert len(filtered.sources) == 2
        assert all("monitor" not in s.name.lower() for s in filtered.sources)

    def test_filter_by_query(self):
        """Test filtering sources by query."""
        sources = [
            AudioSource(name="alsa_input.usb-Microphone", index=0),
            AudioSource(name="alsa_input.pci-Speakers", index=1),
            AudioSource(name="alsa_input.usb-Webcam", index=2),
        ]
        source_list = AudioSourceList(sources)

        filtered = source_list.filter_by_query("usb")

        assert len(filtered.sources) == 2
        assert all("usb" in s.name.lower() for s in filtered.sources)

    def test_filter_by_query_empty_returns_all(self):
        """Test that empty query returns all sources."""
        sources = [
            AudioSource(name="source1", index=0),
            AudioSource(name="source2", index=1),
        ]
        source_list = AudioSourceList(sources)

        filtered = source_list.filter_by_query("")

        assert len(filtered.sources) == 2

    def test_limit(self):
        """Test limiting number of sources."""
        sources = [
            AudioSource(name=f"source{i}", index=i) for i in range(10)
        ]
        source_list = AudioSourceList(sources)

        limited = source_list.limit(3)

        assert len(limited.sources) == 3
        assert limited.sources[0].name == "source0"
        assert limited.sources[2].name == "source2"

    def test_is_empty(self):
        """Test checking if list is empty."""
        empty_list = AudioSourceList([])
        non_empty_list = AudioSourceList([AudioSource(name="test", index=0)])

        assert empty_list.is_empty()
        assert not non_empty_list.is_empty()

    def test_chaining_filters(self):
        """Test chaining multiple filter operations."""
        sources = [
            AudioSource(name="alsa_input.usb-Microphone", index=0),
            AudioSource(name="alsa_output.usb-Monitor", index=1),
            AudioSource(name="alsa_input.usb-Webcam", index=2),
            AudioSource(name="alsa_input.pci-Speakers", index=3),
        ]
        source_list = AudioSourceList(sources)

        result = (
            source_list.filter_monitors()
            .filter_by_query("usb")
            .limit(1)
        )

        assert len(result.sources) == 1
        assert "usb" in result.sources[0].name.lower()
        assert "monitor" not in result.sources[0].name.lower()
