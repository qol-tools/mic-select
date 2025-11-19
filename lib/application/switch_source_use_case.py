"""Use case for switching audio source."""
import logging
from lib.infrastructure.audio_service import AudioSystemClient

logger = logging.getLogger(__name__)


class SwitchSourceUseCase:
    """Use case for switching to a different audio source."""
    
    def __init__(self, audio_client: AudioSystemClient):
        self._audio_client = audio_client
    
    def execute(self, source_name: str) -> None:
        """
        Switch to a different audio source.
        
        Args:
            source_name: Name of the source to switch to
            
        Raises:
            ValueError: If source_name is empty
        """
        if not source_name or not source_name.strip():
            raise ValueError("Source name cannot be empty")
        
        logger.info(f"Switching to audio source: {source_name}")
        self._audio_client.set_default_source(source_name)
        self._audio_client.move_streams_to_source(source_name)
