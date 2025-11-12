# Mic Switcher - Ulauncher Extension

Quickly switch microphone input using PipeWire/PulseAudio from Ulauncher.

## Installation

```bash
chmod +x install.sh
./install.sh
```

Or:
```bash
make install
make reload
```

## Usage

1. Open Ulauncher (`Ctrl + Space`)
2. Type `mic `
3. Select microphone and press Enter

## Requirements

- Ulauncher
- PulseAudio or PipeWire (`pactl`)

## Testing

```bash
make test
```

See `TESTING.md` for details.
