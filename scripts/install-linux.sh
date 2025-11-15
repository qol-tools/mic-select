#!/usr/bin/env bash
# Linux (Ulauncher) installation script

set -e

EXTENSION_DIR="$HOME/.local/share/ulauncher/extensions/mic-switcher"
OLD_EXTENSION_DIR="$HOME/.local/share/ulauncher/extensions/mic-switcher.kmrh47"

# Remove old installation
rm -rf "$OLD_EXTENSION_DIR" 2>/dev/null || true

# Create extension directory
mkdir -p "$EXTENSION_DIR"

# Copy files
cp linux/ulauncher/manifest.json main.py "$EXTENSION_DIR/"
cp -r src "$EXTENSION_DIR/"
cp assets/icon.svg "$EXTENSION_DIR/icon.png"

# Restart Ulauncher
pkill -9 ulauncher 2>/dev/null || true
sleep 1
ulauncher >/dev/null 2>&1 &

echo "mic-switcher installed! Open Ulauncher and type 'mic'"
