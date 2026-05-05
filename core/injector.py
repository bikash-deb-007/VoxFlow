import sys
import time
import threading
import pyperclip
from pynput.keyboard import Key, Controller


_kb = Controller()


def type_text(text: str) -> None:
    try:
        old_clip = pyperclip.paste()
    except Exception:
        old_clip = ""

    pyperclip.copy(text)
    time.sleep(0.05)

    paste_mod = Key.cmd if sys.platform == "darwin" else Key.ctrl_l
    with _kb.pressed(paste_mod):
        _kb.tap("v")

    def _restore():
        time.sleep(0.5)
        try:
            pyperclip.copy(old_clip)
        except Exception:
            pass

    threading.Thread(target=_restore, daemon=True).start()
