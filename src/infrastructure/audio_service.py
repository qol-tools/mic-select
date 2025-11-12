"""Infrastructure layer for audio system interactions."""
import logging
import subprocess
from typing import Protocol
from src.domain.audio_source import AudioSource, AudioSourceList

logger = logging.getLogger(__name__)


class AudioSystemClient(Protocol):
    """Protocol for audio system client."""
    
    def list_sources(self) -> AudioSourceList:
        """List all audio input sources."""
        ...
    
    def set_default_source(self, source_name: str) -> None:
        """Set default audio input source."""
        ...
    
    def move_streams_to_source(self, source_name: str) -> None:
        """Move all active input streams to source."""
        ...


class PactlClient:
    """PulseAudio/PipeWire client using pactl."""
    
    def __init__(self, timeout: float = 0.15, set_source_timeout: float = 0.5, move_stream_timeout: float = 0.5):
        self.timeout = timeout
        self.set_source_timeout = set_source_timeout
        self.move_stream_timeout = move_stream_timeout
    
    def list_sources(self) -> AudioSourceList:
        """List audio input sources."""
        try:
            result = subprocess.run(
                ["timeout", str(self.timeout), "pactl", "list", "short", "sources"],
                capture_output=True,
                text=True,
                timeout=self.timeout + 0.05
            )
            
            if result.returncode != 0:
                logger.warning(f"pactl list sources failed with return code {result.returncode}: {result.stderr}")
                return AudioSourceList([])
            
            if not result.stdout:
                logger.debug("No audio sources found")
                return AudioSourceList([])
            
            sources = []
            for idx, line in enumerate(result.stdout.splitlines()):
                parts = line.split("\t")
                if len(parts) >= 2:
                    source_name = parts[1].strip()
                    if source_name:
                        sources.append(AudioSource(name=source_name, index=idx))
            
            return AudioSourceList(sources).filter_monitors()
        except subprocess.TimeoutExpired:
            logger.warning("Timeout while listing audio sources")
            return AudioSourceList([])
        except Exception as e:
            logger.error(f"Error listing audio sources: {e}", exc_info=True)
            return AudioSourceList([])
    
    def set_default_source(self, source_name: str) -> None:
        """Set default audio input source."""
        try:
            result = subprocess.run(
                ["pactl", "set-default-source", source_name],
                capture_output=True,
                text=True,
                timeout=self.set_source_timeout
            )
            if result.returncode != 0:
                logger.warning(f"Failed to set default source '{source_name}': {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout setting default source '{source_name}'")
        except Exception as e:
            logger.error(f"Error setting default source '{source_name}': {e}", exc_info=True)
    
    def move_streams_to_source(self, source_name: str) -> None:
        """Move all active input streams to source."""
        try:
            result = subprocess.run(
                ["pactl", "list", "short", "source-outputs"],
                capture_output=True,
                text=True,
                timeout=self.move_stream_timeout,
                check=False
            )
            
            if result.returncode != 0:
                logger.debug(f"No source outputs to move (return code {result.returncode})")
                return
            
            if not result.stdout:
                logger.debug("No active source outputs found")
                return
            
            moved_count = 0
            for line in result.stdout.splitlines():
                parts = line.split("\t")
                if parts and parts[0].strip().isdigit():
                    stream_id = parts[0].strip()
                    move_result = subprocess.run(
                        ["pactl", "move-source-output", stream_id, source_name],
                        capture_output=True,
                        text=True,
                        timeout=self.move_stream_timeout,
                        check=False
                    )
                    if move_result.returncode == 0:
                        moved_count += 1
                    else:
                        logger.debug(f"Failed to move stream {stream_id}: {move_result.stderr}")
            
            logger.debug(f"Moved {moved_count} stream(s) to source '{source_name}'")
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout moving streams to source '{source_name}'")
        except Exception as e:
            logger.error(f"Error moving streams to source '{source_name}': {e}", exc_info=True)
