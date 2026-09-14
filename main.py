"""
Extractor de Recibos a Excel
Entry point: launches the GUI, shows the first-run wizard if needed.
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _ensure_src_on_path() -> None:
    """Allow running as a script (python main.py) or as a frozen exe."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    if not (base / "src").exists():
        base = Path(__file__).resolve().parent
    sys.path.insert(0, str(base))


def _show_error(title: str, message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        print(f"[ERROR] {title}: {message}")


def main() -> int:
    try:
        _ensure_src_on_path()

        from src.core import mappings as mappings_module
        from src.installer import tesseract_installer
        from src.gui.main_window import MainWindow
        from src.gui.wizard import TesseractWizard
        import customtkinter as ctk

    except Exception as e:
        msg = (
            "Faltan dependencias para iniciar la aplicación.\n\n"
            f"Detalle: {e}\n\n"
            "Ejecutá: pip install -r requirements.txt\n\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        _show_error("Dependencias faltantes", msg)
        return 1

    settings = mappings_module.load_settings()

    app = MainWindow()

    needs_wizard = settings.get("first_run", True) and not tesseract_installer.is_tesseract_installed()

    if needs_wizard:
        def on_wizard_done():
            app.deiconify()
            app.lift()
            app.focus_force()

        app.withdraw()
        wizard = TesseractWizard(app, on_complete=on_wizard_done)
        wizard.protocol("WM_DELETE_WINDOW", lambda: None)
    else:
        app.lift()
        app.focus_force()

    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
