"""Ulauncher extension adapter."""
import shlex
import threading
import subprocess
import logging
from typing import Callable, Optional
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction

from src.application.list_sources_use_case import ListSourcesUseCase
from src.application.switch_source_use_case import SwitchSourceUseCase
from src.domain.audio_source import AudioSourceList

logger = logging.getLogger(__name__)


class DeviceChangeNotifier:
    def __init__(self, callback: Optional[Callable[[], None]] = None):
        self._callback = callback

    def notify(self):
        if not self._callback:
            return

        self._callback()


class PactlSubscribeReader:
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None

    def start(self):
        self._process = subprocess.Popen(
            ["pactl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def read_line(self) -> Optional[str]:
        if not self._process:
            return None

        return self._process.stdout.readline()

    def terminate(self):
        if not self._process:
            return

        self._process.terminate()


class SourceEventDetector:
    def detect(self, line: str) -> bool:
        return "source" in line.lower()


class PulseAudioDeviceMonitor:
    def __init__(
        self,
        notifier: DeviceChangeNotifier,
        reader: PactlSubscribeReader,
        detector: SourceEventDetector,
    ):
        self._notifier = notifier
        self._reader = reader
        self._detector = detector
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

    def start(self):
        if self._running:
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.debug("PulseAudio device monitor started")

    def stop(self):
        self._running = False
        if not self._monitor_thread:
            return

        self._monitor_thread.join(timeout=1)
        logger.debug("PulseAudio device monitor stopped")

    def _monitor_loop(self):
        try:
            self._reader.start()
        except Exception as e:
            logger.warning(f"Failed to monitor devices: {e}")
            return

        while self._running:
            self._process_monitor_line()

        self._reader.terminate()

    def _process_monitor_line(self):
        try:
            line = self._reader.read_line()
        except Exception as e:
            logger.warning(f"Error reading pactl subscribe: {e}")
            self._running = False
            return

        if not line:
            self._running = False
            return

        if not self._detector.detect(line):
            return

        logger.debug(f"Device event detected: {line.strip()}")
        self._notifier.notify()


class SwitchCommandBuilder:
    def __init__(self, notification_expire_time: int):
        self._notification_expire_time = notification_expire_time

    def build(self, source_name: str, display_name: str) -> str:
        escaped_name = shlex.quote(source_name)
        safe_display_name = shlex.quote(display_name[:50] if display_name else source_name)

        return f"""pactl set-default-source {escaped_name} 2>&1 && \
for stream_id in $(pactl list short source-outputs 2>/dev/null | cut -f1); do
    if [ -n "$stream_id" ]; then
        pactl move-source-output "$stream_id" {escaped_name} 2>&1 || true
    fi
done && notify-send 'Microphone Changed' {safe_display_name} --icon=audio-input-microphone --expire-time={self._notification_expire_time}"""


class QuerySanitizer:
    MAX_LENGTH = 100

    def sanitize(self, query: str) -> str:
        return query[:self.MAX_LENGTH] if query else ""


class SourcesItemFactory:
    ICON_PATH = "icon.png"
    DEFAULT_DESCRIPTION = "Set as default microphone"

    def create_source_items(
        self,
        sources: AudioSourceList,
        command_builder: SwitchCommandBuilder,
    ) -> list:
        return [
            ExtensionResultItem(
                icon=self.ICON_PATH,
                name=source.display_name(),
                description=self.DEFAULT_DESCRIPTION,
                on_enter=RunScriptAction(
                    command_builder.build(source.name, source.display_name()),
                    None
                ),
            )
            for source in sources.sources
        ]

    def create_empty_sources_item(self) -> ExtensionResultItem:
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name="No microphones found",
            description="Make sure PulseAudio/PipeWire is running",
            on_enter=None
        )

    def create_no_matches_item(self, total_sources: int) -> ExtensionResultItem:
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name="No matching sources",
            description=f"Found {total_sources} source(s) total",
            on_enter=None
        )

    def create_error_item(self) -> ExtensionResultItem:
        return ExtensionResultItem(
            icon=self.ICON_PATH,
            name="Error",
            description="",
            on_enter=None
        )


class SourcesPresentationStrategy:
    def present(
        self,
        sources: AudioSourceList,
        query: str,
        factory: SourcesItemFactory,
        command_builder: SwitchCommandBuilder,
    ) -> list:
        if sources.is_empty():
            return [factory.create_empty_sources_item()]

        items = factory.create_source_items(sources, command_builder)

        if items:
            return items

        if query:
            return [factory.create_no_matches_item(len(sources.sources))]

        return [factory.create_error_item()]


class MicSwitcherPresenter:
    def __init__(
        self,
        list_use_case: ListSourcesUseCase,
        switch_use_case: SwitchSourceUseCase,
        max_sources: int = 10,
        notification_expire_time: int = 1500,
    ):
        self._list_use_case = list_use_case
        self._switch_use_case = switch_use_case
        self._max_sources = max_sources
        self._notification_expire_time = notification_expire_time

        self._sanitizer = QuerySanitizer()
        self._command_builder = SwitchCommandBuilder(notification_expire_time)
        self._item_factory = SourcesItemFactory()
        self._presentation_strategy = SourcesPresentationStrategy()

        notifier = DeviceChangeNotifier(self._on_device_change)
        reader = PactlSubscribeReader()
        detector = SourceEventDetector()

        self._device_monitor = PulseAudioDeviceMonitor(notifier, reader, detector)
        self._device_monitor.start()

    def _on_device_change(self):
        logger.debug("Device change detected")

    def present_sources(self, query: str) -> RenderResultListAction:
        sanitized_query = self._sanitizer.sanitize(query)
        sources = self._list_use_case.execute(query=sanitized_query, limit=self._max_sources)

        items = self._presentation_strategy.present(
            sources,
            sanitized_query,
            self._item_factory,
            self._command_builder,
        )

        return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):
    def __init__(self, presenter: MicSwitcherPresenter):
        self._presenter = presenter

    def on_event(self, event: KeywordQueryEvent, extension) -> RenderResultListAction:
        query = event.get_argument() or ""
        return self._presenter.present_sources(query)


class MicSwitcherExtension(Extension):
    def __init__(self, presenter: MicSwitcherPresenter):
        super(MicSwitcherExtension, self).__init__()
        self._presenter = presenter
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener(presenter))

    def __del__(self):
        if not hasattr(self, "_presenter"):
            return

        if not self._presenter:
            return

        self._presenter._device_monitor.stop()
