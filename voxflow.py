"""
╔══════════════════════════════════════════════════════════╗
║  VoxFlow — System-Wide Voice to Text                     ║
║  Hold Ctrl+Space to speak, release to type anywhere      ║
╚══════════════════════════════════════════════════════════╝

SETUP (one time):
    pip install openai-whisper sounddevice numpy pynput pyperclip

USAGE:
    python voxflow.py

    Hold Ctrl+Space → speak → release → text appears at your cursor.
    Press Ctrl+Q to quit.
"""

import sys
import os
import threading
import tempfile
import time
import queue
import signal
import numpy as np
import sounddevice as sd
import whisper
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller as KbController

# ══════════════════════════════════════════════════════════
# CONFIG — change these to your liking
# ══════════════════════════════════════════════════════════
WHISPER_MODEL = "base"        # tiny | base | small | medium | large
LANGUAGE = None               # None = auto-detect, or "en", "hi", "bn", etc.
SAMPLE_RATE = 16000
HOTKEY_MODIFIER = Key.ctrl_l  # Left Ctrl (change to Key.cmd for Mac)
HOTKEY_TRIGGER = Key.space
QUIT_KEY = "q"                # Ctrl+Q to quit

# ══════════════════════════════════════════════════════════
# CORE APP
# ══════════════════════════════════════════════════════════

class VoxFlow:
    def __init__(self):
        self.recording = False
        self.audio_chunks = []
        self.modifier_held = False
        self.trigger_held = False
        self.model = None
        self.kb_controller = KbController()
        self.stream = None
        self.lock = threading.Lock()
        self.running = True
        
    def load_model(self):
        """Load Whisper model (downloads on first run)."""
        print(f"  Loading Whisper '{WHISPER_MODEL}' model...")
        print(f"  (First run will download the model — be patient)\n")
        self.model = whisper.load_model(WHISPER_MODEL)
        print(f"  ✓ Model loaded and ready!\n")

    def start_recording(self):
        """Start capturing audio from mic."""
        with self.lock:
            if self.recording:
                return
            self.recording = True
            self.audio_chunks = []

        print("  🎤 Recording... (speak now)")

        def audio_callback(indata, frames, time_info, status):
            if self.recording:
                self.audio_chunks.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
            blocksize=1024,
        )
        self.stream.start()

    def stop_recording_and_transcribe(self):
        """Stop recording, transcribe with Whisper, type result."""
        with self.lock:
            if not self.recording:
                return
            self.recording = False

        # Stop audio stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_chunks:
            print("  ⚠ No audio captured.\n")
            return

        print("  ⏳ Transcribing...")

        # Combine audio chunks
        audio = np.concatenate(self.audio_chunks, axis=0).flatten()

        # Skip if too short (< 0.3 seconds)
        if len(audio) < SAMPLE_RATE * 0.3:
            print("  ⚠ Too short, skipped.\n")
            return

        # Transcribe with Whisper
        try:
            result = self.model.transcribe(
                audio,
                language=LANGUAGE,
                fp16=False,  # CPU-safe
            )
            text = result["text"].strip()
        except Exception as e:
            print(f"  ✗ Transcription error: {e}\n")
            return

        if not text:
            print("  ⚠ No speech detected.\n")
            return

        detected_lang = result.get("language", "?")
        print(f"  ✓ [{detected_lang}] \"{text}\"\n")

        # Type the text at current cursor position
        self.type_text(text)

    def type_text(self, text):
        """
        Type text at the current cursor position.
        Uses clipboard paste for reliability with special characters / unicode.
        """
        # Save current clipboard
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        # Copy transcribed text to clipboard
        pyperclip.copy(text)

        # Small delay to ensure focus
        time.sleep(0.05)

        # Paste using Ctrl+V (or Cmd+V on Mac)
        paste_modifier = Key.cmd if sys.platform == "darwin" else Key.ctrl_l
        with self.kb_controller.pressed(paste_modifier):
            self.kb_controller.tap("v")

        # Restore old clipboard after a short delay
        def restore_clipboard():
            time.sleep(0.5)
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass

        threading.Thread(target=restore_clipboard, daemon=True).start()

    def on_key_press(self, key):
        """Handle key press events."""
        if not self.running:
            return False

        if key == HOTKEY_MODIFIER:
            self.modifier_held = True

        if key == HOTKEY_TRIGGER and self.modifier_held:
            if not self.recording:
                threading.Thread(target=self.start_recording, daemon=True).start()

        # Ctrl+Q to quit
        try:
            if self.modifier_held and hasattr(key, 'char') and key.char == QUIT_KEY:
                self.quit()
                return False
        except AttributeError:
            pass

    def on_key_release(self, key):
        """Handle key release events."""
        if key == HOTKEY_MODIFIER:
            self.modifier_held = False
            if self.recording:
                threading.Thread(target=self.stop_recording_and_transcribe, daemon=True).start()

        if key == HOTKEY_TRIGGER:
            self.trigger_held = False
            if self.recording and not self.modifier_held:
                threading.Thread(target=self.stop_recording_and_transcribe, daemon=True).start()

    def quit(self):
        """Clean shutdown."""
        self.running = False
        if self.recording and self.stream:
            self.stream.stop()
            self.stream.close()
        print("\n  👋 VoxFlow stopped. Bye!\n")

    def run(self):
        """Main entry point."""
        print()
        print("  ╔══════════════════════════════════════════╗")
        print("  ║       VoxFlow — Voice to Text            ║")
        print("  ╠══════════════════════════════════════════╣")
        print("  ║  Hold  Ctrl + Space  →  speak            ║")
        print("  ║  Release             →  text is typed     ║")
        print("  ║  Ctrl + Q            →  quit              ║")
        print("  ╚══════════════════════════════════════════╝")
        print()

        # Load model
        self.load_model()

        print("  ─────────────────────────────────────────")
        print("  Ready! Hold Ctrl+Space anywhere to speak.")
        print("  ─────────────────────────────────────────\n")

        # Start global keyboard listener
        with keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release,
        ) as listener:
            listener.join()


# ══════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = VoxFlow()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        app.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
