import sys
import json
import logging
from lib.infrastructure.audio_router_daemon import AudioRouterDaemon

logger = logging.getLogger(__name__)


def daemon_start_command() -> None:
    """Start the audio router daemon."""
    daemon = AudioRouterDaemon()
    
    if daemon.is_running():
        output_error("Daemon is already running", 1)
        return

    pid = os.fork()
    if pid > 0:
        print(json.dumps({"success": True, "message": "Daemon started", "pid": pid}))
        sys.exit(0)

    import os
    os.setsid()
    daemon.start_routing()


def daemon_stop_command() -> None:
    """Stop the audio router daemon."""
    daemon = AudioRouterDaemon()
    
    if not daemon.is_running():
        output_error("Daemon is not running", 1)
        return
    
    daemon.stop_routing()
    print(json.dumps({"success": True, "message": "Daemon stopped"}))


def daemon_status_command() -> None:
    """Check daemon status."""
    daemon = AudioRouterDaemon()
    running = daemon.is_running()
    
    status = {
        "running": running,
        "source": daemon.current_source if running else None
    }
    
    print(json.dumps(status))


def output_error(message: str, exit_code: int) -> None:
    """Output error message as JSON."""
    error_output = {"error": message}
    print(json.dumps(error_output))
    sys.exit(exit_code)
