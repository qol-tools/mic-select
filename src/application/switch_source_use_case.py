"""Use case for switching audio source."""
from src.infrastructure.audio_service import AudioSystemClient


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
        
        self._audio_client.set_default_source(source_name)
        self._audio_client.move_streams_to_source(source_name)
