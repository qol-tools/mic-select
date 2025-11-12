"""Audio domain models"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AudioSource:
    """Represents an audio input source"""
    id: str
    name: str
    description: Optional[str] = None
    
    def __str__(self) -> str:
        return self.name
    
    def matches_query(self, query: str) -> bool:
        """Check if source matches search query"""
        if not query:
            return True
        return query.lower() in self.name.lower()


@dataclass(frozen=True)
class SourceOutput:
    """Represents an active source output (stream)"""
    id: int
    source_name: str
    application: Optional[str] = None
