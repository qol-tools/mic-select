#!/usr/bin/env bash

echo "Uninstalling Raycast extension..."

rm -rf "$HOME/Library/Application Support/com.raycast.macos/extensions/select-mic" 2>/dev/null
rm -rf "$HOME/.config/raycast/extensions/select-mic" 2>/dev/null

find "$HOME/.raycast-scripts" -name "mic-switcher" -o -name "select-mic" 2>/dev/null | while read dir; do
    rm -rf "$dir"
done

killall "Raycast" 2>/dev/null || true

echo "✓ Uninstalled. Restart Raycast to complete."
