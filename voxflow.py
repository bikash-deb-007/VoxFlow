import sys
import os
import signal
import threading

sys.path.insert(0, os.path.dirname(__file__))

from core import config
from core.recorder import Recorder
from core.transcriber import Transcriber
from core.injector import type_text
from core.hotkey import HotkeyListener
from ui.tray import TrayApp
from ui.overlay import RecordingOverlay
from ui.settings_win import SettingsWindow


class VoxFlow:
    def __init__(self):
        self._cfg = config.load()
        self._recorder = Recorder(sample_rate=self._cfg["sample_rate"])
        self._transcriber = Transcriber(
            model_name=self._cfg["model"],
            language=self._cfg["language"],
        )
        self._overlay = RecordingOverlay()
        self._settings = SettingsWindow(on_save_callback=self._on_settings_saved)
        self._tray = TrayApp(
            on_quit=self._quit,
            on_settings=self._settings.open,
            on_toggle_recording=self._on_hotkey_start,
        )
        self._hotkey = HotkeyListener(
            modifier=self._cfg["hotkey_modifier"],
            trigger=self._cfg["hotkey_trigger"],
            on_start=self._on_hotkey_start,
            on_stop=self._on_hotkey_stop,
        )

    def _on_hotkey_start(self) -> None:
        if self._recorder.is_recording:
            return
        self._tray.set_recording()
        self._overlay.show()
        self._recorder.start()

    def _on_hotkey_stop(self) -> None:
        self._overlay.hide()
        self._tray.set_transcribing()
        audio = self._recorder.stop()

        if audio is None:
            self._tray.set_idle()
            return

        try:
            text, lang = self._transcriber.transcribe(audio)
        except Exception as e:
            print(f"[VoxFlow] Transcription error: {e}")
            self._tray.set_idle()
            return

        if not text:
            self._tray.set_idle()
            return

        print(f"[VoxFlow] [{lang}] {text}")
        type_text(text)
        self._tray.set_idle()

    def _on_settings_saved(self, new_cfg: dict) -> None:
        self._cfg = new_cfg
        self._hotkey.reconfigure(new_cfg["hotkey_modifier"], new_cfg["hotkey_trigger"])

    def _quit(self) -> None:
        self._hotkey.stop()
        self._overlay.hide()
        self._tray.stop()
        sys.exit(0)

    def run(self) -> None:
        print("╔══════════════════════════════════════╗")
        print("║  VoxFlow — Local Voice-to-Text        ║")
        print("╠══════════════════════════════════════╣")
        mod = self._cfg["hotkey_modifier"]
        trig = self._cfg["hotkey_trigger"]
        print(f"║  Model  : {self._cfg['model']:<27}║")
        print(f"║  Hotkey : {mod}+{trig:<25}║")
        print("╚══════════════════════════════════════╝")

        print("[VoxFlow] Loading Whisper model...")
        self._transcriber.load()
        print("[VoxFlow] Model ready.")

        self._hotkey.start()
        print(f"[VoxFlow] Hold {mod}+{trig} anywhere to speak.")
        print("[VoxFlow] Right-click tray icon → Settings or Quit.\n")

        signal.signal(signal.SIGINT, lambda s, f: self._quit())
        self._tray.run()


if __name__ == "__main__":
    VoxFlow().run()
