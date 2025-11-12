#!/bin/bash
set -e

EXTENSION_DIR="$HOME/.local/share/ulauncher/extensions/mic-switcher.kmrh47"
ICON_URL="https://cdn-icons-png.flaticon.com/512/107/107831.png"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Mic Switcher extension..."

# Create extension directory and copy files
mkdir -p "$EXTENSION_DIR"
cp "$SCRIPT_DIR/manifest.json" "$SCRIPT_DIR/main.py" "$EXTENSION_DIR/"
cp -r "$SCRIPT_DIR/src" "$EXTENSION_DIR/"

# Download icon if missing
if [ ! -f "$EXTENSION_DIR/icon.png" ]; then
    wget -q -O "$EXTENSION_DIR/icon.png" "$ICON_URL" 2>/dev/null || true
fi

echo "Installation complete! Restart Ulauncher: killall ulauncher && ulauncher &"
