# Mic Switcher

Quick microphone switcher for macOS (Raycast) and Linux (Ulauncher).

## Install

```bash
make install
```

## Use

Type `mic` in Raycast/Ulauncher to list and switch microphones.

### For Teams/Zoom

Apps like Teams and Zoom often ignore system defaults. To force them to follow your mic switches:

1. **Create an Aggregate Device** (one-time setup):
   - Open Audio MIDI Setup (`/Applications/Utilities/Audio MIDI Setup.app`)
   - Click `+` → "Create Aggregate Device"
   - Name it `Aggregate Device`
   - Add all your mics (check the "Use" boxes)

2. **Set Teams/Zoom to use it**:
   - Teams → Settings → Devices → Microphone → `Aggregate Device`
   - Zoom → Settings → Audio → Microphone → `Aggregate Device`

3. **Switch mics normally**:
   - Type `mic` in Raycast → select any mic
   - The aggregate device updates automatically
   - Teams/Zoom follow instantly

## Uninstall

```bash
make uninstall
```
