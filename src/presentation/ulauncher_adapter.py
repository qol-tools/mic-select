"""Ulauncher extension adapter."""
from typing import List
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction

from src.application.list_sources_use_case import ListSourcesUseCase
from src.application.switch_source_use_case import SwitchSourceUseCase
from src.domain.audio_source import AudioSourceList


class MicSwitcherPresenter:
    """Presents microphone switching options to Ulauncher."""
    
    def __init__(
        self,
        list_use_case: ListSourcesUseCase,
        switch_use_case: SwitchSourceUseCase
    ):
        self._list_use_case = list_use_case
        self._switch_use_case = switch_use_case
    
    def create_switch_command(self, source_name: str) -> str:
        """Create command script to switch source."""
        # Generate script that executes the switch
        return f"""pactl set-default-source '{source_name}' 2>&1 && \
for stream_id in $(pactl list short source-outputs 2>/dev/null | cut -f1); do
    if [ -n "$stream_id" ]; then
        pactl move-source-output "$stream_id" '{source_name}' 2>&1 || true
    fi
done && (notify-send 'Microphone Changed' 'Switched to: {source_name[:50]}' --expire-time=1500 2>/dev/null || true)"""
    
    def present_sources(self, query: str) -> RenderResultListAction:
        """Present sources as Ulauncher items."""
        sources = self._list_use_case.execute(query=query, limit=10)
        
        items = []
        
        if sources.is_empty():
            items.append(
                ExtensionResultItem(
                    icon="icon.png",
                    name="No microphones found",
                    description="Make sure PulseAudio/PipeWire is running",
                    on_enter=None
                )
            )
        else:
            for source in sources.sources:
                items.append(
                    ExtensionResultItem(
                        icon="icon.png",
                        name=source.name,
                        description="Set as default microphone",
                        on_enter=RunScriptAction(
                            self.create_switch_command(source.name),
                            None
                        ),
                    )
                )
            
            # If query provided but no matches
            if query and len(items) == 0:
                items.append(
                    ExtensionResultItem(
                        icon="icon.png",
                        name="No matching sources",
                        description=f"Found {len(sources.sources)} source(s) total",
                        on_enter=None
                    )
                )
        
        if not items:
            items.append(
                ExtensionResultItem(
                    icon="icon.png",
                    name="Error",
                    description="",
                    on_enter=None
                )
            )
        
        return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):
    """Handles keyword query events from Ulauncher."""
    
    def __init__(self, presenter: MicSwitcherPresenter):
        self._presenter = presenter
    
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        return self._presenter.present_sources(query)


class MicSwitcherExtension(Extension):
    """Ulauncher extension for microphone switching."""
    
    def __init__(self, presenter: MicSwitcherPresenter):
        super(MicSwitcherExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener(presenter))
