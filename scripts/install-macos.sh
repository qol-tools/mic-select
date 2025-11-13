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

echo "Compiling aggregate mic tool..."
cd macos
if gcc -o aggregate-mic aggregate-mic.c -framework CoreAudio -framework CoreFoundation 2>/dev/null; then
    chmod +x aggregate-mic
    echo "✓ Aggregate mic tool compiled"
else
    echo "⚠️  Aggregate mic tool compilation failed"
fi
cd ..

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

cd macos/raycast
npx ray develop > /dev/null 2>&1 &
DEV_PID=$!
sleep 3
kill $DEV_PID 2>/dev/null || true
cd ../..

echo ""
echo "✓ Installed"
echo ""
echo "Usage: Type 'mic' in Raycast"
echo ""
echo "For Teams/Zoom:"
echo "  1. Audio MIDI Setup → Create Aggregate Device → Name it 'Aggregate Device'"
echo "  2. Teams/Zoom → Settings → Microphone → 'Aggregate Device'"
echo "  3. Switching mics in Raycast updates the aggregate automatically"
echo ""
