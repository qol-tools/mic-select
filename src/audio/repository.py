"""Repository pattern for audio source data access"""
import subprocess
from typing import List, Optional
from .models import AudioSource, SourceOutput


class AudioSourceRepository:
    """Repository for accessing audio sources"""
    
    def __init__(self, timeout: float = 0.15):
        self.timeout = timeout
    
    def list_sources(self) -> List[AudioSource]:
        """List all available audio input sources"""
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
                return []
            
            sources = []
            for line in result.stdout.splitlines():
                if "monitor" in line.lower():
                    continue
                
                parts = line.split("\t")
                if len(parts) >= 2:
                    source_id = parts[1].strip()
                    if source_id:
                        sources.append(AudioSource(
                            id=source_id,
                            name=source_id,
                            description=parts[2].strip() if len(parts) > 2 else None
                        ))
            
            return sources
        except Exception:
            return []
    
    def get_default_source(self) -> Optional[str]:
        """Get the current default source name"""
        try:
            result = subprocess.run(
                "pactl get-default-source",
                shell=True,
                capture_output=True,
                text=True,
                timeout=0.1
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None


class SourceOutputRepository:
    """Repository for accessing source outputs (active streams)"""
    
    def __init__(self, timeout: float = 0.1):
        self.timeout = timeout
    
    def list_active_outputs(self) -> List[SourceOutput]:
        """List all active source outputs"""
        try:
            result = subprocess.run(
                "pactl list short source-outputs 2>/dev/null",
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0 or not result.stdout:
                return []
            
            outputs = []
            for line in result.stdout.splitlines():
                parts = line.split("\t")
                if parts:
                    stream_id = parts[0].strip()
                    if stream_id.isdigit():
                        source_name = parts[1].strip() if len(parts) > 1 else ""
                        app_name = parts[2].strip() if len(parts) > 2 else None
                        outputs.append(SourceOutput(
                            id=int(stream_id),
                            source_name=source_name,
                            application=app_name
                        ))
            
            return outputs
        except Exception:
            return []
