import tkinter as tk


class RecordingOverlay:
    """Small floating indicator shown while recording."""

    def __init__(self, tk_root: tk.Tk):
        self._root = tk_root
        self._win: tk.Toplevel | None = None

    def show(self) -> None:
        self._root.after(0, self._create)

    def hide(self) -> None:
        self._root.after(0, self._destroy)

    def _create(self) -> None:
        if self._win:
            return
        win = tk.Toplevel(self._root)
        self._win = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.88)
        win.configure(bg="#1a1a1a")
        win.resizable(False, False)

        w, h = 160, 44
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{sw - w - 24}+{sh - h - 72}")

        canvas = tk.Canvas(win, width=w, height=h, bg="#1a1a1a", highlightthickness=0)
        canvas.pack()
        dot = canvas.create_oval(14, 15, 28, 29, fill="#ff4466", outline="")
        canvas.create_text(40, 22, anchor="w", text="Recording...", fill="#e8e8f0", font=("Segoe UI", 11))

        def _pulse(scale: float = 1.0, growing: bool = True) -> None:
            if not self._win:
                return
            ns = scale + 0.05 if growing else scale - 0.05
            ng = growing if (0.8 < ns < 1.3) else not growing
            r = int(7 * ns)
            canvas.coords(dot, 21 - r, 22 - r, 21 + r, 22 + r)
            win.after(60, lambda: _pulse(ns, ng))

        _pulse()

    def _destroy(self) -> None:
        if self._win:
            self._win.destroy()
            self._win = None
