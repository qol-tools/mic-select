"""Factory for creating extension result items"""
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ..commands.switch_microphone_command import SwitchMicrophoneCommand
from ..audio.models import AudioSource


class ItemFactory:
    """Factory for creating extension result items"""
    
    ICON_PATH = "icon.png"
    MAX_DESCRIPTION_LENGTH = 50
    
    def create_source_item(self, source: AudioSource) -> ExtensionResultItem:
        """Create an item for an audio source"""
        command = SwitchMicrophoneCommand(source.id)
        script = command.execute()
        
        notification = (
            f" && (notify-send 'Microphone Changed' "
            f"'Switched to: {source.name[:self.MAX_DESCRIPTION_LENGTH]}' "
            f"--expire-time=1500 2>/dev/null || true)"
        )
        
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name=source.name,
            description="Set as default microphone",
            on_enter=RunScriptAction(script + notification, None)
        )
    
    def create_no_sources_item(self) -> ExtensionResultItem:
        """Create item when no sources are found"""
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name="No microphones found",
            description="Make sure PulseAudio/PipeWire is running",
            on_enter=None
        )
    
    def create_no_match_item(self, total_count: int) -> ExtensionResultItem:
        """Create item when query doesn't match any sources"""
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name="No matching sources",
            description=f"Found {total_count} source(s) total",
            on_enter=None
        )
    
    def create_error_item(self, message: str = "") -> ExtensionResultItem:
        """Create error item"""
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name="Error",
            description=message,
            on_enter=None
        )
