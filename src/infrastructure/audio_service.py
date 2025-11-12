"""Infrastructure layer for audio system interactions."""
import subprocess
from typing import Protocol, List
from src.domain.audio_source import AudioSource, AudioSourceList


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
    
    def __init__(self, timeout: float = 0.15):
        self.timeout = timeout
    
    def list_sources(self) -> AudioSourceList:
        """List audio input sources."""
        try:
            cmd = f"timeout {self.timeout} pactl list short sources 2>/dev/null"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout + 0.05
            )
            
            if result.returncode != 0 or not result.stdout:
                return AudioSourceList([])
            
            sources = []
            for idx, line in enumerate(result.stdout.splitlines()):
                parts = line.split("\t")
                if len(parts) >= 2:
                    source_name = parts[1].strip()
                    if source_name:
                        sources.append(AudioSource(name=source_name, index=idx))
            
            return AudioSourceList(sources).filter_monitors()
        except Exception:
            return AudioSourceList([])
    
    def set_default_source(self, source_name: str) -> None:
        """Set default audio input source."""
        subprocess.run(
            f"pactl set-default-source '{source_name}'",
            shell=True,
            check=False,
            timeout=0.5
        )
    
    def move_streams_to_source(self, source_name: str) -> None:
        """Move all active input streams to source."""
        script = f"""for stream_id in $(pactl list short source-outputs 2>/dev/null | cut -f1); do
    if [ -n "$stream_id" ] && [ "$stream_id" -eq "$stream_id" ] 2>/dev/null; then
        pactl move-source-output "$stream_id" '{source_name}' 2>&1 || true
    fi
done"""
        subprocess.run(script, shell=True, timeout=1.0, check=False)
