#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title List Microphones
# @raycast.mode fullOutput
# @raycast.packageName Audio

# Optional parameters:
# @raycast.icon 🎤

# Documentation:
# @raycast.description List all available microphones
# @raycast.author KMRH47

# Get script directory and find Python CLI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLI_PATH="$PROJECT_ROOT/macos/cli/mic_cli.py"

# Check if CLI exists
if [ ! -f "$CLI_PATH" ]; then
    echo "Error: CLI not found at $CLI_PATH"
    exit 1
fi

# Find Python
PYTHON=""
for p in /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    if [ -x "$p" ]; then
        PYTHON="$p"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: Python 3 not found"
    exit 1
fi

# List microphones
"$PYTHON" "$CLI_PATH" list --limit 50
