"""Configuration settings for the extension."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Extension configuration."""
    pactl_timeout: float = 0.3
    set_source_timeout: float = 0.5
    move_stream_timeout: float = 0.5
    max_sources_display: int = 10
    notification_expire_time: int = 800
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.pactl_timeout <= 0:
            raise ValueError("pactl_timeout must be greater than 0")
        if self.set_source_timeout <= 0:
            raise ValueError("set_source_timeout must be greater than 0")
        if self.move_stream_timeout <= 0:
            raise ValueError("move_stream_timeout must be greater than 0")
        if self.max_sources_display < 1:
            raise ValueError("max_sources_display must be at least 1")
        if self.notification_expire_time < 0:
            raise ValueError("notification_expire_time must be non-negative")
