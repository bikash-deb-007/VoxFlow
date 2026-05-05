import threading
from typing import Callable
from pynput import keyboard
from pynput.keyboard import Key


MODIFIER_MAP = {
    "ctrl": Key.ctrl_l,
    "alt": Key.alt_l,
    "shift": Key.shift_l,
}


class HotkeyListener:
    def __init__(
        self,
        modifier: str,
        trigger: str,
        on_start: Callable,
        on_stop: Callable,
    ):
        self.modifier_key = MODIFIER_MAP.get(modifier, Key.ctrl_l)
        self.trigger_char = trigger
        self.on_start = on_start
        self.on_stop = on_stop

        self._modifier_held = False
        self._trigger_held = False
        self._listener: keyboard.Listener | None = None
        self._running = False

    def start(self) -> None:
        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self) -> None:
        self._running = False
        if self._listener:
            self._listener.stop()

    def reconfigure(self, modifier: str, trigger: str) -> None:
        self.stop()
        self.modifier_key = MODIFIER_MAP.get(modifier, Key.ctrl_l)
        self.trigger_char = trigger
        self.start()

    def _on_press(self, key) -> None:
        if not self._running:
            return

        if key == self.modifier_key:
            self._modifier_held = True

        if self._modifier_held and self._matches_trigger(key) and not self._trigger_held:
            self._trigger_held = True
            threading.Thread(target=self.on_start, daemon=True).start()

    def _on_release(self, key) -> None:
        if key == self.modifier_key:
            self._modifier_held = False
            if self._trigger_held:
                self._trigger_held = False
                threading.Thread(target=self.on_stop, daemon=True).start()

        if self._matches_trigger(key) and self._trigger_held:
            self._trigger_held = False
            if not self._modifier_held:
                threading.Thread(target=self.on_stop, daemon=True).start()

    def _matches_trigger(self, key) -> bool:
        trigger = self.trigger_char.lower()
        if trigger == "space":
            return key == Key.space
        try:
            return hasattr(key, "char") and key.char == trigger
        except AttributeError:
            return False
