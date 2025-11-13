import logging
import subprocess
import shutil
from typing import Optional
from src.domain.audio_source import AudioSource, AudioSourceList

logger = logging.getLogger(__name__)


class MacOSAudioClient:
    
    def __init__(self, timeout: float = 0.5, set_source_timeout: float = 1.0):
        self.timeout = timeout
        self.set_source_timeout = set_source_timeout
        self._switch_audio_source_path = self._find_switch_audio_source()
        
        if not self._switch_audio_source_path:
            raise RuntimeError(
                "SwitchAudioSource not found. Install via: brew install switchaudio-osx"
            )
    
    def _find_switch_audio_source(self) -> Optional[str]:
        paths = [
            "/usr/local/bin/SwitchAudioSource",
            "/opt/homebrew/bin/SwitchAudioSource",
            shutil.which("SwitchAudioSource"),
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def list_sources(self) -> AudioSourceList:
        try:
            result = subprocess.run(
                [self._switch_audio_source_path, "-a", "-t", "input"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                logger.warning(
                    f"SwitchAudioSource list failed with return code {result.returncode}: {result.stderr}"
                )
                return AudioSourceList([])
            
            if not result.stdout:
                logger.debug("No audio sources found")
                return AudioSourceList([])
            
            sources = []
            for idx, line in enumerate(result.stdout.splitlines()):
                source_name = line.strip()
                if source_name:
                    sources.append(AudioSource(name=source_name, index=idx))
            
            return AudioSourceList(sources)
        except subprocess.TimeoutExpired:
            logger.warning("Timeout while listing audio sources")
            return AudioSourceList([])
        except Exception as e:
            logger.error(f"Error listing audio sources: {e}", exc_info=True)
            return AudioSourceList([])
    
    def set_default_source(self, source_name: str) -> None:
        try:
            result = subprocess.run(
                [self._switch_audio_source_path, "-s", source_name, "-t", "input"],
                capture_output=True,
                text=True,
                timeout=self.set_source_timeout
            )
            
            if result.returncode != 0:
                logger.warning(
                    f"Failed to set default source '{source_name}': {result.stderr}"
                )
                raise RuntimeError(
                    f"Failed to switch audio source: {result.stderr.strip() or 'Unknown error'}"
                )
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout setting default source '{source_name}'")
            raise RuntimeError(f"Timeout while switching audio source")
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Error setting default source '{source_name}': {e}", exc_info=True)
            raise RuntimeError(f"Error switching audio source: {e}")
    
    def move_streams_to_source(self, source_name: str) -> None:
        logger.debug(f"move_streams_to_source called for '{source_name}' (no-op on macOS)")
        pass
