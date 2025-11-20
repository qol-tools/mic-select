#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MACOS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

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
pip3 install -r "$PROJECT_ROOT/requirements.txt" >/dev/null 2>&1 || true

echo "Compiling aggregate mic tool..."
cd "$MACOS_DIR"
if gcc -o aggregate-mic aggregate-mic.c -framework CoreAudio -framework CoreFoundation 2>/dev/null; then
    chmod +x aggregate-mic
    echo "✓ Aggregate mic tool compiled"
else
    echo "⚠️  Aggregate mic tool compilation failed"
fi

cp "$SCRIPT_DIR/raycast_cli.py.template" "$SCRIPT_DIR/raycast_cli.py"
chmod +x "$SCRIPT_DIR/raycast_cli.py"

echo "Building Raycast extension..."
cd "$SCRIPT_DIR"
npm install --silent
npm run build

RAYCAST_EXT_DIR="$HOME/.config/raycast/extensions/select-mic"
if [ -d "$RAYCAST_EXT_DIR" ]; then
    cp "$SCRIPT_DIR/raycast_cli.py" "$RAYCAST_EXT_DIR/"
    cp -r "$PROJECT_ROOT/lib" "$RAYCAST_EXT_DIR/"
fi

npx ray develop > /dev/null 2>&1 &
DEV_PID=$!
sleep 3
kill $DEV_PID 2>/dev/null || true

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
