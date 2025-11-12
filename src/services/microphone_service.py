"""Service for microphone switching operations"""
from typing import List
from ..audio.repository import AudioSourceRepository, SourceOutputRepository
from ..audio.models import AudioSource


class MicrophoneService:
    """Service for microphone-related operations"""
    
    def __init__(
        self,
        source_repo: AudioSourceRepository = None,
        output_repo: SourceOutputRepository = None
    ):
        self.source_repo = source_repo or AudioSourceRepository()
        self.output_repo = output_repo or SourceOutputRepository()
    
    def list_sources(self, query: str = "") -> List[AudioSource]:
        """List audio sources, optionally filtered by query"""
        sources = self.source_repo.list_sources()
        
        if not query:
            return sources
        
        return [src for src in sources if src.matches_query(query)]
    
    def get_default_source(self) -> str:
        """Get current default source"""
        return self.source_repo.get_default_source() or ""
