"""Handler for keyword query events"""
from typing import List
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction

from ..services.microphone_service import MicrophoneService
from ..commands.switch_microphone_command import SwitchMicrophoneCommand
from ..factories.item_factory import ItemFactory


class KeywordQueryHandler(EventListener):
    """Handles keyword query events"""
    
    def __init__(self, service: MicrophoneService = None):
        self.service = service or MicrophoneService()
        self.item_factory = ItemFactory()
    
    def on_event(self, event: KeywordQueryEvent, extension) -> RenderResultListAction:
        """Handle keyword query event"""
        query = event.get_argument() or ""
        sources = self.service.list_sources(query)
        
        items = self._build_items(sources, query)
        return RenderResultListAction(items)
    
    def _build_items(self, sources: List, query: str) -> List[ExtensionResultItem]:
        """Build extension result items from sources"""
        if not sources:
            return [self.item_factory.create_no_sources_item()]
        
        if query:
            return self._build_filtered_items(sources, query)
        else:
            return self._build_all_items(sources)
    
    def _build_filtered_items(self, sources: List, query: str) -> List[ExtensionResultItem]:
        """Build items for filtered sources"""
        filtered = [src for src in sources if src.matches_query(query)]
        
        if filtered:
            return [
                self.item_factory.create_source_item(src)
                for src in filtered[:10]
            ]
        else:
            return [self.item_factory.create_no_match_item(len(sources))]
    
    def _build_all_items(self, sources: List) -> List[ExtensionResultItem]:
        """Build items for all sources"""
        return [
            self.item_factory.create_source_item(src)
            for src in sources[:10]
        ]
