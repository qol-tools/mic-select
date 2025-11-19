"""Use case for listing audio sources."""
from lib.domain.audio_source import AudioSourceList
from lib.infrastructure.audio_service import AudioSystemClient


class ListSourcesUseCase:
    """Use case for listing and filtering audio sources."""
    
    def __init__(self, audio_client: AudioSystemClient):
        self._audio_client = audio_client
    
    def execute(self, query: str = "", limit: int = 10) -> AudioSourceList:
        """
        List audio sources, optionally filtered by query.
        
        Args:
            query: Optional search query to filter sources
            limit: Maximum number of sources to return (must be > 0)
            
        Returns:
            Filtered and limited list of audio sources
            
        Raises:
            ValueError: If limit is less than 1
        """
        if limit < 1:
            raise ValueError("limit must be greater than 0")
        
        sources = self._audio_client.list_sources()
        
        if query:
            sources = sources.filter_by_query(query)
        
        return sources.limit(limit)
