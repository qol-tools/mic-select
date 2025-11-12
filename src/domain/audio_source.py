"""Domain model for audio sources."""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AudioSource:
    """Represents an audio input source."""
    name: str
    index: int
    
    def is_monitor(self) -> bool:
        """Check if this is a monitor source."""
        return "monitor" in self.name.lower()
    
    def matches_query(self, query: str) -> bool:
        """Check if source name matches search query."""
        return query.lower() in self.name.lower()


@dataclass(frozen=True)
class AudioSourceList:
    """Collection of audio sources."""
    sources: List[AudioSource]
    
    def filter_monitors(self) -> "AudioSourceList":
        """Return sources excluding monitors."""
        filtered = [s for s in self.sources if not s.is_monitor()]
        return AudioSourceList(filtered)
    
    def filter_by_query(self, query: str) -> "AudioSourceList":
        """Filter sources matching query."""
        if not query:
            return self
        filtered = [s for s in self.sources if s.matches_query(query)]
        return AudioSourceList(filtered)
    
    def limit(self, max_count: int) -> "AudioSourceList":
        """Limit number of sources."""
        limited = self.sources[:max_count]
        return AudioSourceList(limited)
    
    def is_empty(self) -> bool:
        """Check if list is empty."""
        return len(self.sources) == 0
