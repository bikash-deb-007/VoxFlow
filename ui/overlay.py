import threading
import tkinter as tk


class RecordingOverlay:
    """Small floating indicator shown while recording."""

    def __init__(self):
        self._root: tk.Tk | None = None
        self._thread: threading.Thread | None = None
        self._visible = False

    def show(self) -> None:
        if self._visible:
            return
        self._visible = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def hide(self) -> None:
        self._visible = False
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass
            self._root = None

    def _run(self) -> None:
        self._root = tk.Tk()
        root = self._root

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.88)
        root.configure(bg="#1a1a1a")
        root.resizable(False, False)

        w, h = 160, 44
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{sw - w - 24}+{sh - h - 72}")

        canvas = tk.Canvas(root, width=w, height=h, bg="#1a1a1a", highlightthickness=0)
        canvas.pack()

        dot = canvas.create_oval(14, 15, 28, 29, fill="#ff4466", outline="")
        label = canvas.create_text(40, 22, anchor="w", text="Recording...", fill="#e8e8f0", font=("Segoe UI", 11))

        def _pulse(scale: float = 1.0, growing: bool = True):
            if not self._visible:
                return
            next_scale = scale + 0.05 if growing else scale - 0.05
            next_growing = growing if (0.8 < next_scale < 1.3) else not growing
            r = int(7 * next_scale)
            cx, cy = 21, 22
            canvas.coords(dot, cx - r, cy - r, cx + r, cy + r)
            root.after(60, lambda: _pulse(next_scale, next_growing))

        _pulse()
        root.mainloop()
