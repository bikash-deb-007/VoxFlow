# VoxFlow 🎙️

**Local voice-to-text for Windows — speak anywhere, text appears at your cursor.**

VoxFlow runs entirely on your machine using [OpenAI Whisper](https://github.com/openai/whisper). No cloud, no subscription, no internet required after setup. Hold a hotkey, speak, release — your words are typed wherever your cursor is.

> Inspired by WhisperFlow (macOS). VoxFlow brings the same idea to Windows.

---

## Features

- **100% local** — Whisper runs on your CPU, nothing leaves your machine
- **Works everywhere** — browser, Notepad, Word, chat apps, code editors — anywhere you can type
- **System tray app** — sits quietly in the taskbar, no terminal needed after launch
- **Visual feedback** — tray icon changes colour + floating "Recording…" indicator
- **Settings UI** — change model, language, and hotkey without touching any files
- **Multi-language** — auto-detects language, or lock to English, Hindi, Bengali, and more

---

## Requirements

| Requirement | Minimum |
|---|---|
| OS | Windows 10 / 11 |
| Python | 3.10 or newer |
| Microphone | Any (built-in or external) |
| RAM | 2 GB free (4 GB recommended for `small` model) |
| Disk | ~150 MB for `base` model (downloaded on first run) |

---

## Installation

### Step 1 — Install Python

Download Python 3.10+ from [python.org](https://www.python.org/downloads/).  
During install, **check "Add Python to PATH"**.

### Step 2 — Download VoxFlow

Click the green **Code** button on this page → **Download ZIP** → extract it anywhere.

Or if you have Git:
```
git clone https://github.com/bikash-deb-007/VoxFlow.git
cd VoxFlow
```

### Step 3 — Install dependencies

Open a terminal in the VoxFlow folder and run:
```
pip install -r requirements.txt
```

This installs Whisper, audio libraries, and the tray icon. Takes 1–3 minutes.

### Step 4 — Run VoxFlow

Double-click **VoxFlow.bat**, or run:
```
python voxflow.py
```

The first run downloads the Whisper model (~150 MB). After that it loads in seconds.

---

## How to use

1. **Look for the microphone icon** in your system tray (bottom-right, near the clock)
2. **Click inside any text field** — browser address bar, chat, document, anything
3. **Hold `Ctrl + Space`** and speak
4. **Release** — your speech is transcribed and typed at the cursor

That's it.

### Tray icon colours

| Colour | Meaning |
|---|---|
| Purple | Idle, ready |
| Red | Recording |
| Orange | Transcribing (processing) |

---

## Settings

Right-click the tray icon → **Settings**

| Setting | Options | Default |
|---|---|---|
| Whisper model | tiny, base, small, medium | base |
| Language | Auto-detect, English, Hindi, Bengali, … | Auto-detect |
| Modifier key | ctrl, alt, shift | ctrl |
| Trigger key | space, or any letter | space |

### Which model should I pick?

| Model | Speed | Accuracy | RAM needed |
|---|---|---|---|
| `tiny` | Very fast | Lower | ~1 GB |
| `base` | Fast | Good | ~1 GB |
| `small` | Medium | Better | ~2 GB |
| `medium` | Slower | Best | ~4 GB |

Start with **`base`** — it's the best balance for everyday use.

> After changing the model, restart VoxFlow for the change to take effect.

---

## Project structure

```
VoxFlow/
├── voxflow.py          # Entry point — assembles and runs the app
├── core/
│   ├── config.py       # Load/save settings (config.json)
│   ├── recorder.py     # Microphone audio capture
│   ├── transcriber.py  # Whisper model wrapper
│   ├── injector.py     # Types text at cursor via clipboard paste
│   └── hotkey.py       # Global hotkey listener (pynput)
├── ui/
│   ├── tray.py         # System tray icon (3 states)
│   ├── overlay.py      # Floating "Recording…" indicator
│   └── settings_win.py # Settings window (tkinter)
├── VoxFlow.bat         # Windows launcher (double-click to run)
├── requirements.txt    # Python dependencies
└── config.json         # Your saved settings (auto-created on first run)
```

---

## Troubleshooting

**Tray icon doesn't appear**  
Make sure `pystray` and `Pillow` installed correctly:
```
pip install pystray Pillow
```

**"No module named whisper"**  
```
pip install openai-whisper
```

**Hotkey not working in some apps**  
Some apps (games, admin tools) block global hotkeys. Try running VoxFlow as administrator: right-click `VoxFlow.bat` → Run as administrator.

**Microphone not detected**  
Check that your mic is set as the default recording device in Windows Sound Settings.

**Transcription is slow**  
Switch to the `tiny` model in Settings. Transcription speed depends on your CPU.

**Text pastes in the wrong place**  
The app pastes at wherever the cursor was when you released the hotkey. Click the text field first, then hold the hotkey.

---

## Tech stack

- [OpenAI Whisper](https://github.com/openai/whisper) — local speech recognition
- [sounddevice](https://python-sounddevice.readthedocs.io/) — microphone audio capture
- [pynput](https://pynput.readthedocs.io/) — global hotkey listener
- [pystray](https://pystray.readthedocs.io/) — system tray icon
- [Pillow](https://pillow.readthedocs.io/) — tray icon rendering
- [tkinter](https://docs.python.org/3/library/tkinter.html) — settings window (built into Python)

---

## License

MIT — do whatever you want with it.
