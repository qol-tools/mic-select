#!/usr/bin/env bash
# macOS (Raycast) installation script

set -e

RAYCAST_EXT_DIR="$HOME/Library/Application Support/com.raycast.macos/extensions"
RAYCAST_TARGET="$RAYCAST_EXT_DIR/select-mic"

echo "Installing for macOS (Raycast)..."

# Check for Homebrew
if ! command -v brew >/dev/null 2>&1; then
    echo "Error: Homebrew not found. Install from https://brew.sh"
    exit 1
fi

# Install switchaudio-osx
if ! brew list switchaudio-osx >/dev/null 2>&1; then
    echo "Installing switchaudio-osx via Homebrew..."
    brew install switchaudio-osx
else
    echo "✓ switchaudio-osx already installed"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt >/dev/null 2>&1 || echo "Warning: Failed to install Python dependencies"

# Build extension
echo "Building Raycast extension..."
cd macos/raycast
npm install --silent
npm run build
cd ../..

# Create installation directory
mkdir -p "$RAYCAST_EXT_DIR"

# Remove old installation if exists
if [ -d "$RAYCAST_TARGET" ] || [ -L "$RAYCAST_TARGET" ]; then
    rm -rf "$RAYCAST_TARGET"
fi

# Copy required Python source to extension directory
mkdir -p macos/raycast/lib
rsync -a src/ macos/raycast/lib/src/
rsync -a macos/cli/src/ macos/raycast/lib/macos/cli/src/

# Copy CLI wrapper template
cp macos/raycast/raycast_cli.py.template macos/raycast/raycast_cli.py
chmod +x macos/raycast/raycast_cli.py

echo ""
echo "✓ Extension built!"
echo ""
echo "Activating in Raycast..."
cd macos/raycast
npx ray develop > /dev/null 2>&1 &
DEV_PID=$!
cd ../..

sleep 3
kill $DEV_PID 2>/dev/null

echo ""
echo "✓ Extension activated in Raycast (free tier)"
echo "  Open Raycast and type 'mic' to use it"
echo ""
