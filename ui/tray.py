import threading
import pystray
from PIL import Image, ImageDraw
from ui.settings_win import SettingsWindow


def _make_icon(color: str) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Microphone body
    draw.rounded_rectangle([22, 4, 42, 38], radius=10, fill=color)
    # Stand arc (3 lines approximating an arc)
    draw.arc([14, 22, 50, 50], start=0, end=180, fill=color, width=3)
    # Vertical stem
    draw.line([32, 50, 32, 58], fill=color, width=3)
    # Base
    draw.line([22, 58, 42, 58], fill=color, width=3)
    return img


ICON_IDLE = _make_icon("#7c5cfc")
ICON_RECORDING = _make_icon("#ff4466")
ICON_BUSY = _make_icon("#ffaa44")


class TrayApp:
    def __init__(self, on_quit, on_settings, on_toggle_recording):
        self.on_quit = on_quit
        self.on_settings = on_settings
        self.on_toggle_recording = on_toggle_recording
        self._icon: pystray.Icon | None = None
        self._status = "idle"

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("VoxFlow", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", lambda: threading.Thread(target=self.on_settings, daemon=True).start()),
            pystray.MenuItem("Quit", lambda: self.on_quit()),
        )

    def run(self) -> None:
        self._icon = pystray.Icon(
            "VoxFlow",
            ICON_IDLE,
            "VoxFlow — idle\nHold hotkey to record",
            menu=self._build_menu(),
        )
        self._icon.run()

    def set_recording(self) -> None:
        if self._icon:
            self._icon.icon = ICON_RECORDING
            self._icon.title = "VoxFlow — Recording..."

    def set_transcribing(self) -> None:
        if self._icon:
            self._icon.icon = ICON_BUSY
            self._icon.title = "VoxFlow — Transcribing..."

    def set_idle(self) -> None:
        if self._icon:
            self._icon.icon = ICON_IDLE
            self._icon.title = "VoxFlow — idle\nHold hotkey to record"

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
