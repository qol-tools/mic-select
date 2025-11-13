#!/usr/bin/env python3
"""CLI entry point for mic switcher."""
import argparse
import sys
import logging
from pathlib import Path

# Add project root to path
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.config import Config
from macos.cli.src.dependency_injection.container import Container
from macos.cli.src.presentation.cli import list_command, switch_command, output_error

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s"
)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Mic Switcher CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    list_parser = subparsers.add_parser("list", help="List audio sources")
    list_parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Filter sources by query string"
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of sources to return (default: 10)"
    )

    switch_parser = subparsers.add_parser("switch", help="Switch audio source")
    switch_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the audio source to switch to"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        output_error("No command specified", 1)
        return

    try:
        container = Container()

        if args.command == "list":
            list_command(container, query=args.query, limit=args.limit)
        elif args.command == "switch":
            switch_command(container, name=args.name)
        else:
            output_error(f"Unknown command: {args.command}", 1)
    except KeyboardInterrupt:
        output_error("Interrupted by user", 130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        output_error(f"Unexpected error: {e}", 1)


if __name__ == "__main__":
    main()
