"""Command for switching microphone"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..audio.repository import SourceOutputRepository


class Command(ABC):
    """Base command interface"""
    
    @abstractmethod
    def execute(self) -> str:
        """Execute the command and return script"""
        pass


class SwitchMicrophoneCommand(Command):
    """Command to switch microphone and move active streams"""
    
    def __init__(
        self,
        source_name: str,
        output_repo: Optional[SourceOutputRepository] = None
    ):
        self.source_name = source_name
        self.output_repo = output_repo or SourceOutputRepository()
    
    def execute(self) -> str:
        """Generate script to switch microphone"""
        commands = [
            f"pactl set-default-source '{self.source_name}' 2>&1"
        ]
        
        # Add commands to move active streams
        move_commands = self._generate_move_commands()
        commands.extend(move_commands)
        
        return " && ".join(commands)
    
    def _generate_move_commands(self) -> List[str]:
        """Generate commands to move active streams"""
        # Use a loop that executes at runtime, not generation time
        return [
            f"for stream_id in $(pactl list short source-outputs 2>/dev/null | cut -f1); do",
            f"    if [ -n \"$stream_id\" ] && [ \"$stream_id\" -eq \"$stream_id\" ] 2>/dev/null; then",
            f"        pactl move-source-output \"$stream_id\" '{self.source_name}' 2>&1 || true",
            f"    fi",
            f"done"
        ]
