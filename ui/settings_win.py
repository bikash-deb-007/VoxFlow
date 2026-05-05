import threading
import tkinter as tk
from tkinter import ttk, messagebox
from core import config


MODELS = ["tiny", "base", "small", "medium"]
MODIFIERS = ["ctrl", "alt", "shift"]
LANGUAGES = {
    "Auto-detect": None,
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "Arabic": "ar",
    "Portuguese": "pt",
}


class SettingsWindow:
    def __init__(self, on_save_callback=None):
        self.on_save = on_save_callback
        self._win: tk.Tk | None = None
        self._thread: threading.Thread | None = None

    def open(self) -> None:
        if self._win and tk.Toplevel.winfo_exists(self._win):
            self._win.lift()
            return
        self._thread = threading.Thread(target=self._build, daemon=True)
        self._thread.start()

    def _build(self) -> None:
        cfg = config.load()

        win = tk.Tk()
        self._win = win
        win.title("VoxFlow Settings")
        win.resizable(False, False)
        win.configure(bg="#12121a")

        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        w, h = 380, 320
        win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("TLabel", background="#12121a", foreground="#e8e8f0", font=("Segoe UI", 10))
        style.configure("TCombobox", fieldbackground="#1a1a26", background="#1a1a26", foreground="#e8e8f0")
        style.configure("TButton", background="#7c5cfc", foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "#a08aff")])
        style.configure("TCheckbutton", background="#12121a", foreground="#e8e8f0", font=("Segoe UI", 10))

        pad = {"padx": 20, "pady": 6}

        tk.Label(win, text="VoxFlow Settings", bg="#12121a", fg="#a08aff",
                 font=("Segoe UI", 14, "bold")).pack(pady=(18, 10))

        def row(label, widget_factory):
            frame = tk.Frame(win, bg="#12121a")
            frame.pack(fill="x", **pad)
            ttk.Label(frame, text=label, width=18, anchor="w").pack(side="left")
            w = widget_factory(frame)
            w.pack(side="left", fill="x", expand=True)
            return w

        # Whisper model
        model_var = tk.StringVar(value=cfg.get("model", "base"))
        row("Whisper model:", lambda f: ttk.Combobox(f, textvariable=model_var,
            values=MODELS, state="readonly", width=14))

        # Language
        lang_display = {v: k for k, v in LANGUAGES.items()}
        current_lang_label = lang_display.get(cfg.get("language"), "Auto-detect")
        lang_var = tk.StringVar(value=current_lang_label)
        row("Language:", lambda f: ttk.Combobox(f, textvariable=lang_var,
            values=list(LANGUAGES.keys()), state="readonly", width=14))

        # Hotkey modifier
        mod_var = tk.StringVar(value=cfg.get("hotkey_modifier", "ctrl"))
        row("Modifier key:", lambda f: ttk.Combobox(f, textvariable=mod_var,
            values=MODIFIERS, state="readonly", width=14))

        # Hotkey trigger
        trigger_var = tk.StringVar(value=cfg.get("hotkey_trigger", "space"))
        trigger_entry = row("Trigger key:", lambda f: ttk.Entry(f, textvariable=trigger_var, width=16))

        # Notify on paste
        notify_var = tk.BooleanVar(value=cfg.get("notify_on_paste", True))
        frame = tk.Frame(win, bg="#12121a")
        frame.pack(fill="x", padx=20, pady=6)
        ttk.Checkbutton(frame, text="Show notification after paste", variable=notify_var).pack(side="left")

        def _save():
            new_cfg = config.load()
            new_cfg["model"] = model_var.get()
            new_cfg["language"] = LANGUAGES.get(lang_var.get())
            new_cfg["hotkey_modifier"] = mod_var.get()
            new_cfg["hotkey_trigger"] = trigger_var.get().strip() or "space"
            new_cfg["notify_on_paste"] = notify_var.get()
            config.save(new_cfg)
            if self.on_save:
                self.on_save(new_cfg)
            messagebox.showinfo("Saved", "Settings saved. Restart VoxFlow to apply model changes.", parent=win)
            win.destroy()

        btn_frame = tk.Frame(win, bg="#12121a")
        btn_frame.pack(pady=18)
        ttk.Button(btn_frame, text="Save", command=_save, width=12).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy, width=10).pack(side="left", padx=8)

        win.mainloop()
        self._win = None
