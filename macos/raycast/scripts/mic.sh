#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title mic
# @raycast.mode fullOutput
# @raycast.packageName System

# Optional parameters:
# @raycast.icon 🎤

# Documentation:
# @raycast.description List and switch microphones
# @raycast.author KMRH47
# @raycast.argument1 { "type": "text", "placeholder": "Mic name (leave empty to list)", "optional": true }

# Get script directory and find Python CLI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
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

# If argument provided, switch to that mic, otherwise list all
if [ -n "$1" ]; then
    "$PYTHON" "$CLI_PATH" switch --name "$1"
else
    "$PYTHON" "$CLI_PATH" list --limit 50
fi
