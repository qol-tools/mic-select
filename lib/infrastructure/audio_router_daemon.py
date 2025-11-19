import subprocess
import logging
import signal
import sys
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioRouterDaemon:
    """Routes real microphone to BlackHole virtual device."""
    
    def __init__(self, virtual_device: str = "BlackHole 2ch"):
        self.virtual_device = virtual_device
        self.current_source: Optional[str] = None
        self.router_process: Optional[subprocess.Popen] = None
        self.pidfile = Path.home() / ".mic-select-daemon.pid"
        
    def start_routing(self, source_name: str) -> None:
        """Start routing from source to virtual device."""
        if self.router_process:
            self.stop_routing()
        
        try:
            cmd = [
                "sox",
                "-t", "coreaudio", source_name,
                "-t", "coreaudio", self.virtual_device,
                "rate", "48000"
            ]
            
            self.router_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            
            self.current_source = source_name
            self.pidfile.write_text(str(self.router_process.pid))
            
            logger.info(f"Started routing: {source_name} -> {self.virtual_device}")
            
        except Exception as e:
            logger.error(f"Failed to start routing: {e}")
            raise
    
    def stop_routing(self) -> None:
        """Stop current audio routing."""
        if self.router_process:
            try:
                self.router_process.terminate()
                self.router_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.router_process.kill()
            except Exception as e:
                logger.debug(f"Error stopping router: {e}")
            finally:
                self.router_process = None
                self.current_source = None
                
                if self.pidfile.exists():
                    self.pidfile.unlink()
    
    def switch_source(self, new_source: str) -> None:
        """Switch routing to new source."""
        logger.info(f"Switching from {self.current_source} to {new_source}")
        self.start_routing(new_source)
    
    def is_running(self) -> bool:
        """Check if daemon is running."""
        if not self.pidfile.exists():
            return False
        
        try:
            pid = int(self.pidfile.read_text().strip())
            subprocess.run(["kill", "-0", str(pid)], check=True, capture_output=True)
            return True
        except (ValueError, subprocess.CalledProcessError):
            return False
    
    def cleanup(self, signum=None, frame=None):
        """Cleanup on exit."""
        logger.info("Shutting down audio router daemon")
        self.stop_routing()
        sys.exit(0)


def main():
    """Run daemon in foreground."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    daemon = AudioRouterDaemon()

    signal.signal(signal.SIGTERM, daemon.cleanup)
    signal.signal(signal.SIGINT, daemon.cleanup)

    try:
        result = subprocess.run(
            ["SwitchAudioSource", "-t", "input", "-c"],
            capture_output=True,
            text=True,
            check=True
        )
        initial_source = result.stdout.strip()
        
        logger.info(f"Starting daemon with source: {initial_source}")
        daemon.start_routing(initial_source)

        daemon.router_process.wait()
        
    except KeyboardInterrupt:
        daemon.cleanup()
    except Exception as e:
        logger.error(f"Daemon error: {e}")
        daemon.cleanup()


if __name__ == "__main__":
    main()
