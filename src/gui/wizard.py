from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from ..installer import tesseract_installer
from ..core import mappings as mappings_module
from .widgets import (
    COLORS, Card, make_label, make_primary_button, make_success_button,
)


class TesseractWizard(ctk.CTkToplevel):
    """First-run wizard: downloads Tesseract + language data with friendly progress."""

    def __init__(self, parent, on_complete: Optional[callable] = None):
        super().__init__(parent)
        self.title("Extractor de Recibos - Instalación inicial")
        self.geometry("640x480")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])

        self.on_complete = on_complete
        self._cancelled = False

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.after(300, self._start_installation)

    def _build_ui(self) -> None:
        outer = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        title = make_label(
            outer,
            "¡Bienvenido a Extractor de Recibos!",
            size=22, weight="bold", color=COLORS["primary"],
        )
        title.pack(pady=(10, 6))

        subtitle = make_label(
            outer,
            "Vamos a instalar el motor OCR para leer tus PDFs escaneados e imágenes.",
            size=13, color=COLORS["text_muted"],
        )
        subtitle.pack(pady=(0, 20))

        info_card = Card(outer)
        info_card.pack(fill="x", padx=10, pady=(0, 16))

        info_text = (
            "• Motor: Tesseract OCR 5.x\n"
            "• Idiomas: Español + Inglés + Portugués (~70 MB)\n"
            "• Ubicación: instalación local (no requiere admin)\n"
            "• Se descarga solo la primera vez"
        )
        lbl = make_label(info_card, info_text, size=12, color=COLORS["text"])
        lbl.pack(padx=18, pady=14, anchor="w")

        self.status_label = make_label(
            outer, "Preparando descarga...", size=13, weight="bold", color=COLORS["text"],
        )
        self.status_label.pack(pady=(4, 6))

        self.progress = ctk.CTkProgressBar(outer, height=14, corner_radius=7)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=10, pady=(0, 6))

        self.detail_label = make_label(
            outer, "", size=11, color=COLORS["text_muted"],
        )
        self.detail_label.pack(pady=(0, 20))

        self.btn_frame = ctk.CTkFrame(outer, fg_color=COLORS["bg"])
        self.btn_frame.pack(fill="x", pady=(4, 0))

        self.skip_btn = make_primary_button(
            self.btn_frame, "Saltar instalación",
            command=self._on_skip,
        )
        self.skip_btn.pack(side="right", padx=4)

        self.install_btn = make_success_button(
            self.btn_frame, "Reintentar",
            command=self._start_installation,
        )
        self.install_btn.pack(side="right", padx=4)
        self.install_btn.pack_forget()

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def _set_detail(self, text: str) -> None:
        self.detail_label.configure(text=text)

    def _start_installation(self) -> None:
        self.install_btn.pack_forget()
        self.skip_btn.configure(state="disabled", text="Instalando...")
        self._cancelled = False

        def progress_cb(downloaded: int, total: int, message: str) -> None:
            if self._cancelled:
                return
            try:
                if total and total > 0:
                    pct = min(downloaded / total, 1.0)
                    self.after(0, lambda: self.progress.set(pct))
                msg = f"{message}  ({downloaded // 1024} KB / {total // 1024} KB)" if total else message
                self.after(0, lambda m=msg: self._set_detail(m))
            except Exception:
                pass

        def worker():
            try:
                ok = tesseract_installer.install_tesseract(progress=progress_cb)
                self.after(0, lambda: self._on_finished(ok))
            except Exception as e:
                self.after(0, lambda: self._on_finished(False, error=str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_finished(self, ok: bool, error: Optional[str] = None) -> None:
        if ok:
            self._set_status("✓ Instalación completa")
            self._set_detail("Tesseract listo. Abriendo aplicación...")
            settings = mappings_module.load_settings()
            settings["tesseract_installed"] = True
            settings["first_run"] = False
            mappings_module.save_settings(settings)
            self.after(1500, self._close_and_open_main)
        else:
            self._set_status("⚠ No se pudo instalar automáticamente")
            msg = (
                f"Error: {error}\n\n"
                "Podés continuar con la app, pero solo se procesarán PDFs con texto.\n"
                "Para habilitar OCR, instalá Tesseract manualmente:\n"
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )
            self._set_detail(msg)
            self.skip_btn.configure(state="normal", text="Continuar sin OCR")
            self.install_btn.pack(side="right", padx=4)

    def _on_skip(self) -> None:
        self._cancelled = True
        settings = mappings_module.load_settings()
        settings["tesseract_installed"] = False
        settings["first_run"] = False
        mappings_module.save_settings(settings)
        self._close_and_open_main()

    def _close_and_open_main(self) -> None:
        if self.on_complete:
            try:
                self.on_complete()
            except Exception as e:
                print(f"[WARN] on_complete callback failed: {e}")
        self.destroy()
