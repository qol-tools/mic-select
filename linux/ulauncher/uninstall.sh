#!/usr/bin/env bash
# Linux (Ulauncher) uninstallation script

EXTENSION_DIR="$HOME/.local/share/ulauncher/extensions/mic-switcher"
OLD_EXTENSION_DIR="$HOME/.local/share/ulauncher/extensions/mic-switcher.kmrh47"

rm -rf "$EXTENSION_DIR" "$OLD_EXTENSION_DIR"
echo "✓ Ulauncher extension uninstalled"
