#!/usr/bin/env bash
# macOS (Raycast) installation script

set -e

SCRIPTS_DIR="$HOME/.raycast-scripts/mic-switcher"

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
pip3 install -r requirements.txt >/dev/null 2>&1 || true

# Create scripts directory
mkdir -p "$SCRIPTS_DIR"

# Copy everything to scripts directory
echo "Installing Raycast scripts..."
rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' . "$SCRIPTS_DIR/"

echo ""
echo "✓ Scripts installed to: $SCRIPTS_DIR"
echo ""
echo "Add this directory to Raycast:"
echo "  1. Open Raycast → Settings (⌘,)"
echo "  2. Go to Extensions → Script Commands"
echo "  3. Click 'Add Directories'"
echo "  4. Select: $SCRIPTS_DIR/raycast-scripts"
echo ""
echo "Then type 'List Microphones' or 'Switch Microphone' in Raycast!"
echo ""
