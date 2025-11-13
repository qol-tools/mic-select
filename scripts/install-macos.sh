#!/usr/bin/env bash
set -e

echo "Installing for macOS (Raycast)..."

if ! command -v brew >/dev/null 2>&1; then
    echo "Error: Homebrew not found. Install from https://brew.sh"
    exit 1
fi

if ! brew list switchaudio-osx >/dev/null 2>&1; then
    echo "Installing switchaudio-osx..."
    brew install switchaudio-osx
else
    echo "✓ switchaudio-osx installed"
fi

echo "Installing Python dependencies..."
pip3 install -r requirements.txt >/dev/null 2>&1 || true

mkdir -p macos/raycast/lib
rsync -a src/ macos/raycast/lib/src/
rsync -a macos/cli/src/ macos/raycast/lib/macos/cli/src/

cp macos/raycast/raycast_cli.py.template macos/raycast/raycast_cli.py
chmod +x macos/raycast/raycast_cli.py

echo "Building Raycast extension..."
cd macos/raycast
npm install --silent
npm run build
cd ../..

RAYCAST_EXT_DIR="$HOME/.config/raycast/extensions/select-mic"
if [ -d "$RAYCAST_EXT_DIR" ]; then
    cp macos/raycast/raycast_cli.py "$RAYCAST_EXT_DIR/"
    cp -r macos/raycast/lib "$RAYCAST_EXT_DIR/"
fi

echo "Activating in Raycast..."
cd macos/raycast
npx ray develop > /dev/null 2>&1 &
DEV_PID=$!
cd ../..

sleep 3
kill $DEV_PID 2>/dev/null || true

echo "✓ Installed! Type 'mic' in Raycast to use."
