from __future__ import annotations

import os
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List, Optional

import customtkinter as ctk
from PIL import Image

from ..core.input_loader import InputItem, scan_path
from ..core.excel_writer import write_excel
from ..core import mappings as mappings_module
from ..core.locale_detector import LocaleInfo
from ..workers import Processor
from .widgets import (
    COLORS, Card, ScrollableLog, make_label,
    make_primary_button, make_success_button, make_danger_button, make_secondary_button,
    set_button_active,
)


APP_TITLE = "Extractor de Recibos a Excel"
APP_NAME = "Extractor de Recibos a Excel v1.0.4"
APP_VERSION = "v1.0.4"
DEFAULT_OUTPUT = "recibos_extraidos.xlsx"


def _find_logo_path() -> Optional[Path]:
    """Locate the logo PNG (works both in dev and inside a PyInstaller bundle)."""
    candidates: List[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "assets" / "icon.png")
    candidates.append(Path(__file__).resolve().parent.parent.parent / "assets" / "icon.png")
    candidates.append(Path.cwd() / "assets" / "icon.png")
    for c in candidates:
        if c.exists():
            return c
    return None


def _tk_icon_photo(logo_path: Path):
    """Build a tk.PhotoImage from the PNG for the window icon."""
    try:
        import tkinter as tk
        return tk.PhotoImage(file=str(logo_path))
    except Exception:
        return None


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)
        self.geometry("1300x820")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_light"])
        self._cards: List = []

        logo_path = _find_logo_path()
        if logo_path:
            try:
                self._logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(40, 40),
                )
                self.iconphoto(False, _tk_icon_photo(logo_path))
            except Exception:
                self._logo_image = None
        else:
            self._logo_image = None

        self.settings = mappings_module.load_settings()
        self._processor: Optional[Processor] = None
        self._processing_thread: Optional[threading.Thread] = None
        self._processing = False
        self._last_columns: List[str] = []
        self._last_rows: List[dict] = []
        self._last_locale: Optional[LocaleInfo] = None
        self._last_summary: dict = {}
        self._last_output_path: Optional[Path] = None

        self._build_ui()
        self._refresh_files_list()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=72)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        if getattr(self, "_logo_image", None):
            logo_lbl = ctk.CTkLabel(header, image=self._logo_image, text="")
            logo_lbl.pack(side="left", padx=(16, 8), pady=14)

        title_lbl = make_label(
            header, APP_TITLE,
            size=20, weight="bold", color="#FFFFFF",
        )
        title_lbl.pack(side="left", padx=(4, 20), pady=14)

        subtitle_lbl = make_label(
            header, APP_VERSION,
            size=11, color="#C9D6E5",
        )
        subtitle_lbl.pack(side="left", padx=(0, 8), pady=14)

        self.theme_btn = ctk.CTkButton(
            header, text="Claro", width=110, height=36,
            fg_color="#FFFFFF",
            hover_color="#F0F4F8",
            text_color=COLORS["primary"],
            border_width=1,
            border_color="#FFFFFF",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="right", padx=20, pady=14)

        body = ctk.CTkFrame(self, fg_color=COLORS["bg_light"])
        body.pack(fill="both", expand=True, padx=12, pady=12)

        body.grid_columnconfigure(0, weight=2, uniform="col1")
        body.grid_columnconfigure(1, weight=3, uniform="col1")
        body.grid_rowconfigure(0, weight=1)

        # Left column: input + config
        left = ctk.CTkFrame(body, fg_color=COLORS["bg_light"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._build_input_card(left)
        self._build_config_card(left)
        self._build_actions_card(left)

        # Right column: log + progress
        right = ctk.CTkFrame(body, fg_color=COLORS["bg_light"])
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self._build_files_card(right)
        self._build_progress_card(right)
        self._build_log_card(right)

        self._apply_theme_to_widgets()
        self._update_theme_button()

        self.locale_lbl = make_label(
            header, "Locale: detectando...",
            size=12, color="#E0E8F0",
        )
        self.locale_lbl.pack(side="right", padx=8, pady=14)

    def _build_input_card(self, parent) -> None:
        card = Card(parent)
        card.pack(fill="x", pady=(0, 8))
        self._cards.append(card)

        make_label(card, "1. Archivos de entrada", size=14, weight="bold").pack(
            anchor="w", padx=16, pady=(12, 8),
        )

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=12, pady=(0, 12))

        make_primary_button(
            btns, "📂 Carpeta", command=self._on_add_folder, width=110,
        ).pack(side="left", padx=3, pady=4)

        make_primary_button(
            btns, "🗜️ ZIPs", command=self._on_add_zip, width=80,
        ).pack(side="left", padx=3, pady=4)

        make_primary_button(
            btns, "📄 Archivos", command=self._on_add_files, width=100,
        ).pack(side="left", padx=3, pady=4)

        make_secondary_button(
            btns, "🗑️ Limpiar", command=self._on_clear_files, width=90,
        ).pack(side="left", padx=3, pady=4)

    def _build_config_card(self, parent) -> None:
        card = Card(parent)
        card.pack(fill="x", pady=(0, 8))
        self._cards.append(card)

        make_label(card, "2. Configuración", size=14, weight="bold").pack(
            anchor="w", padx=16, pady=(12, 8),
        )

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(0, 6))

        make_label(row1, "OCR:", size=11).pack(side="left", padx=(4, 4))
        self.ocr_var = ctk.StringVar(value=self.settings.get("ocr_lang", "spa+eng+por"))
        ocr_menu = ctk.CTkOptionMenu(
            row1, variable=self.ocr_var,
            values=["spa", "spa+eng", "spa+eng+por", "eng", "por"],
            width=130,
        )
        ocr_menu.pack(side="left", padx=2)

        make_label(row1, "Workers:", size=11).pack(side="left", padx=(8, 4))
        cpu = os.cpu_count() or 4
        self.workers_var = ctk.StringVar(value=str(self.settings.get("max_workers") or (cpu - 1)))
        ctk.CTkOptionMenu(
            row1, variable=self.workers_var,
            values=["1", "2", str(cpu - 1), str(cpu), str(cpu * 2)],
            width=70,
        ).pack(side="left", padx=2)

        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(0, 12))

        make_label(row2, "Excel:", size=11).pack(side="left", padx=(4, 4))
        self.output_var = ctk.StringVar(value=str(Path.cwd() / DEFAULT_OUTPUT))
        out_entry = ctk.CTkEntry(row2, textvariable=self.output_var)
        out_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        make_primary_button(
            row2, "...", command=self._on_choose_output, width=36,
        ).pack(side="left")

    def _build_actions_card(self, parent) -> None:
        card = Card(parent)
        card.pack(fill="x", pady=(0, 8))
        self._cards.append(card)

        make_label(card, "3. Acciones", size=14, weight="bold").pack(
            anchor="w", padx=16, pady=(12, 8),
        )

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(0, 6))

        self.process_btn = make_success_button(
            row1, "▶️ Procesar", command=self._on_process, width=130,
        )
        self.process_btn.pack(side="left", padx=3, pady=4)

        self.cancel_btn = make_danger_button(
            row1, "⏹️ Cancelar", command=lambda: None, width=110,
        )
        self.cancel_btn.pack(side="left", padx=3, pady=4)

        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(0, 12))

        self.preview_btn = make_primary_button(
            row2, "👁️ Vista previa", command=lambda: None, width=130,
        )
        self.preview_btn.pack(side="left", padx=3, pady=4)

        self.open_excel_btn = make_primary_button(
            row2, "📊 Abrir Excel", command=lambda: None, width=130,
        )
        self.open_excel_btn.pack(side="left", padx=3, pady=4)

    def _build_files_card(self, parent) -> None:
        card = Card(parent)
        card.pack(fill="both", expand=False, pady=(0, 8), ipady=4)
        self._cards.append(card)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 4))

        make_label(top, "4. Archivos detectados", size=14, weight="bold").pack(side="left")

        self.files_count_lbl = make_label(top, "0 archivos", size=12, color=COLORS["text_muted"])
        self.files_count_lbl.pack(side="right")

        self.files_listbox = ctk.CTkTextbox(card, height=120, font=ctk.CTkFont(family="Consolas", size=11))
        self.files_listbox.pack(fill="both", expand=False, padx=16, pady=(0, 12))
        self.files_listbox.configure(state="disabled")

    def _build_progress_card(self, parent) -> None:
        card = Card(parent)
        card.pack(fill="x", pady=(0, 8))
        self._cards.append(card)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, 6))

        make_label(top, "5. Progreso", size=14, weight="bold").pack(side="left")

        self.progress_text_lbl = make_label(top, "0/0", size=12, color=COLORS["text_muted"])
        self.progress_text_lbl.pack(side="right")

        self.progress = ctk.CTkProgressBar(inner, height=14, corner_radius=7)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(0, 4))

        self.eta_lbl = make_label(inner, "", size=11, color=COLORS["text_muted"])
        self.eta_lbl.pack(anchor="w")

    def _build_log_card(self, parent) -> None:
        card = Card(parent)
        card.pack(fill="both", expand=True, pady=(0, 0))
        self._cards.append(card)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 4))

        make_label(top, "6. Registro de actividad", size=14, weight="bold").pack(side="left")

        make_primary_button(
            top, "💾 Guardar log", command=self._on_save_log,
            width=130, height=32,
        ).pack(side="right")

        self.log_text = ScrollableLog(card)
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    # ── Actions ────────────────────────────────────────────────────────────

    def _on_add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta con recibos")
        if not folder:
            return
        items = scan_path(folder)
        if not items:
            messagebox.showwarning("Sin archivos", "No se encontraron PDFs ni imágenes.")
            return
        for item in items:
            self._add_item(item)

    def _on_add_zip(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Seleccionar archivos ZIP",
            filetypes=[("Archivos ZIP", "*.zip"), ("Todos", "*.*")],
        )
        if not paths:
            return
        added = 0
        for p in paths:
            items = scan_path(p)
            for item in items:
                self._add_item(item)
                added += 1
        if added == 0:
            messagebox.showwarning("Sin contenido", "Los ZIP no contienen PDFs ni imágenes.")

    def _on_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("PDFs e imágenes", "*.pdf *.png *.jpg *.jpeg *.tif *.tiff *.bmp *.webp"),
                ("Todos", "*.*"),
            ],
        )
        if not paths:
            return
        for p in paths:
            items = scan_path(p)
            for item in items:
                self._add_item(item)

    def _on_clear_files(self) -> None:
        self._items = []
        self._refresh_files_list()

    def _add_item(self, item: InputItem) -> None:
        if not hasattr(self, "_items") or self._items is None:
            self._items = []
        if any(i.display_name == item.display_name for i in self._items):
            return
        self._items.append(item)
        self._refresh_files_list()

    def _refresh_files_list(self) -> None:
        if not hasattr(self, "_items"):
            self._items = []
        self.files_listbox.configure(state="normal")
        self.files_listbox.delete("1.0", "end")
        for it in self._items:
            self.files_listbox.insert("end", f"  • {it.display_name}  [{it.kind}]\n")
        self.files_listbox.configure(state="disabled")
        self.files_count_lbl.configure(text=f"{len(self._items)} archivo(s)")

    def _on_choose_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Guardar Excel como...",
            defaultextension=".xlsx",
            initialfile=DEFAULT_OUTPUT,
            filetypes=[("Excel", "*.xlsx")],
        )
        if path:
            self.output_var.set(path)

    def _toggle_theme(self) -> None:
        current = ctk.get_appearance_mode()
        new_mode = "light" if current.lower() == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.settings["theme"] = new_mode
        mappings_module.save_settings(self.settings)
        self._update_theme_button()
        self._apply_theme_to_widgets()

    def _update_theme_button(self) -> None:
        if not getattr(self, "theme_btn", None):
            return
        mode = ctk.get_appearance_mode().lower()
        if mode == "dark":
            self.theme_btn.configure(text="☀️ Claro")
            self.theme_btn.configure(fg_color="#FFFFFF")
            self.theme_btn.configure(text_color=COLORS["primary"])
            self.theme_btn.configure(border_color="#FFFFFF")
        else:
            self.theme_btn.configure(text="🌙 Oscuro")
            self.theme_btn.configure(fg_color="#FFFFFF")
            self.theme_btn.configure(text_color=COLORS["primary"])
            self.theme_btn.configure(border_color="#FFFFFF")

    def _apply_theme_to_widgets(self) -> None:
        mode = ctk.get_appearance_mode().lower()
        is_dark = mode == "dark"
        bg = COLORS["bg_dark"] if is_dark else COLORS["bg_light"]
        card_bg = COLORS["card_dark"] if is_dark else COLORS["card_light"]
        border = COLORS["border_dark"] if is_dark else COLORS["border_light"]
        text = COLORS["text_dark"] if is_dark else COLORS["text_light"]
        text_muted = COLORS["text_muted_dark"] if is_dark else COLORS["text_muted_light"]
        try:
            self.configure(fg_color=bg)
        except Exception:
            pass
        for card in getattr(self, "_cards", []):
            try:
                card.configure(fg_color=card_bg, border_color=border)
            except Exception:
                pass

    def _on_process(self) -> None:
        if self._processing:
            return
        if not hasattr(self, "_items") or not self._items:
            messagebox.showwarning("Sin archivos", "Agregá al menos un archivo.")
            return
        out_path = self.output_var.get().strip()
        if not out_path:
            messagebox.showwarning("Sin salida", "Indicá la ruta del Excel de salida.")
            return
        if not out_path.lower().endswith(".xlsx"):
            out_path += ".xlsx"
            self.output_var.set(out_path)

        ocr_lang = self.ocr_var.get()
        try:
            max_workers = int(self.workers_var.get())
        except ValueError:
            max_workers = max(1, (os.cpu_count() or 4) - 1)

        self.settings["ocr_lang"] = ocr_lang
        self.settings["max_workers"] = max_workers
        mappings_module.save_settings(self.settings)

        self._set_processing_state(True)
        self._clear_log()
        self._append_log(f"═══ Nueva ejecución {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ═══")
        self._append_log(f"Enviando {len(self._items)} archivo(s) a procesar...")

        self._processor = Processor(
            items=list(self._items),
            ocr_lang=ocr_lang,
            max_workers=max_workers,
            progress_callback=self._on_progress,
            log_callback=lambda m: self.after(0, lambda mm=m: self._append_log(mm)),
            cancel_check=lambda: False,
        )

        self._processing_start = time.time()
        self._processing_thread = threading.Thread(target=self._run_processor, daemon=True)
        self._processing_thread.start()
        self._start_progress_watchdog()

    def _run_processor(self) -> None:
        try:
            result = self._processor.run()
            self._last_columns = result["columns"]
            self._last_rows = result["rows"]
            self._last_locale = result["locale"]
            self._last_summary = result["summary"]

            self.after(0, lambda: self._on_processing_finished(result))
        except FileNotFoundError as e:
            self.after(0, lambda: self._on_processing_error(str(e)))
        except Exception as e:
            self.after(0, lambda: self._on_processing_error(f"{e}"))
        finally:
            self._processing = False

    def _on_progress(self, completed: int, total: int, result) -> None:
        def update():
            pct = completed / total if total else 0
            self.progress.set(pct)
            self.progress_text_lbl.configure(text=f"{completed}/{total} ({int(pct * 100)}%)")
            if total > 0:
                elapsed = time.time() - getattr(self, "_processing_start", time.time())
                rate = completed / elapsed if elapsed > 0 else 0
                if rate > 0 and completed < total:
                    eta = (total - completed) / rate
                    self.eta_lbl.configure(text=f"Procesando {completed} de {total} - ETA: {int(eta)}s")
                else:
                    self.eta_lbl.configure(text=f"Procesando {completed} de {total}...")
        self.after(0, update)

    def _start_progress_watchdog(self) -> None:
        """Update the eta label every 2s while processing (so user sees activity)."""
        if not getattr(self, "_processing", False):
            return
        try:
            elapsed = time.time() - getattr(self, "_processing_start", time.time())
            current_text = self.eta_lbl.cget("text") or ""
            if not current_text.startswith("Procesando") or "Procesando 0 de" in current_text:
                self.eta_lbl.configure(text=f"Procesando... ({int(elapsed)}s)")
        except Exception:
            pass
        self.after(2000, self._start_progress_watchdog)

    def _on_processing_finished(self, result: dict) -> None:
        out_path = Path(self.output_var.get().strip())
        try:
            locale_dict = result["locale"].to_dict() if result["locale"] else None
            saved = write_excel(
                out_path,
                result["columns"],
                result["rows"],
                locale_info=locale_dict,
                summary=result["summary"],
            )
            self._last_output_path = saved
            self._append_log(f"✓ Excel generado: {saved}")
            self._append_log(f"✓ {len(result['rows'])} filas x {len(result['columns'])} columnas")
            set_button_active(self.open_excel_btn, self._on_open_excel)
            set_button_active(self.preview_btn, self._on_preview)
            set_button_active(self.process_btn, self._on_process)
            set_button_active(self.cancel_btn, None)
            self.progress.set(1.0)
            self.progress_text_lbl.configure(
                text=f"✓ {result['summary']['processed']} archivos procesados"
            )
            self.eta_lbl.configure(text="")
            if result["locale"]:
                self.locale_lbl.configure(
                    text=f"Locale: {result['locale'].country} ({result['locale'].code}) • {result['locale'].currency}"
                )
            self._set_processing_state(False)
            messagebox.showinfo(
                "Completado",
                f"Excel generado con éxito:\n{saved}\n\n"
                f"Filas: {len(result['rows'])}\n"
                f"Columnas: {len(result['columns'])}",
            )
        except Exception as e:
            self._on_processing_error(f"Error guardando Excel: {e}")

    def _on_processing_error(self, message: str) -> None:
        self._append_log(f"✗ ERROR: {message}")
        self._set_processing_state(False)
        self.progress.set(0)
        self.progress_text_lbl.configure(text="Error")
        self.eta_lbl.configure(text="")
        messagebox.showerror("Error", message)

    def _on_cancel(self) -> None:
        if self._processor:
            self._processor.cancel()
            self._append_log("⚠ Cancelación solicitada...")
            set_button_active(self.cancel_btn, None)

    def _set_processing_state(self, busy: bool) -> None:
        self._processing = busy
        if busy:
            set_button_active(self.process_btn, None)
            set_button_active(self.cancel_btn, self._on_cancel)
            self.progress.set(0)
            self.progress_text_lbl.configure(text="0/0 (0%)")
            self.eta_lbl.configure(text="Iniciando...")
            set_button_active(self.preview_btn, None)
            set_button_active(self.open_excel_btn, None)
            self.update_idletasks()
        else:
            set_button_active(self.process_btn, self._on_process)
            set_button_active(self.cancel_btn, None)
            self.eta_lbl.configure(text="")

    # ── Log / preview helpers ──────────────────────────────────────────────

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _append_log(self, text: str) -> None:
        self.log_text.append(text)

    def _on_save_log(self) -> None:
        if not hasattr(self, "_items"):
            return
        path = filedialog.asksaveasfilename(
            title="Guardar log",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", "end"))
            messagebox.showinfo("Log guardado", f"Log guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el log: {e}")

    def _on_preview(self) -> None:
        if not self._last_rows or not self._last_columns:
            messagebox.showinfo("Sin datos", "Todavía no hay datos para previsualizar.")
            return
        PreviewWindow(self, self._last_columns, self._last_rows)

    def _on_open_excel(self) -> None:
        if not self._last_output_path or not self._last_output_path.exists():
            messagebox.showwarning("Sin archivo", "El Excel aún no fue generado.")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(str(self._last_output_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(self._last_output_path)], check=False)
            else:
                subprocess.run(["xdg-open", str(self._last_output_path)], check=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")


class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, columns: List[str], rows: List[dict]):
        super().__init__(parent)
        self.title("Vista previa de datos")
        self.geometry("1000x600")
        self.configure(fg_color=COLORS["bg"])
        self.transient(parent)

        make_label(self, f"{len(rows)} archivo(s) x {len(columns)} columna(s)",
                   size=14, weight="bold").pack(padx=16, pady=(14, 8), anchor="w")

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["card"])
        scroll_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        header_row = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary"])
        header_row.pack(fill="x")
        for i, col in enumerate(columns):
            lbl = ctk.CTkLabel(
                header_row, text=str(col),
                width=140, anchor="w", padx=8, pady=8,
                font=ctk.CTkFont(weight="bold", size=11),
                text_color="#FFFFFF",
            )
            lbl.grid(row=0, column=i, sticky="w")

        max_show = min(50, len(rows))
        for r_idx, row in enumerate(rows[:max_show], start=1):
            row_frame = ctk.CTkFrame(
                scroll_frame,
                fg_color="#F9F9F9" if r_idx % 2 == 0 else "#FFFFFF",
            )
            row_frame.pack(fill="x")
            for c_idx, col in enumerate(columns):
                val = str(row.get(col, ""))[:50]
                lbl = ctk.CTkLabel(
                    row_frame, text=val,
                    width=140, anchor="w", padx=8, pady=6,
                    font=ctk.CTkFont(size=11), text_color=COLORS["text"],
                )
                lbl.grid(row=0, column=c_idx, sticky="w")

        if len(rows) > max_show:
            make_label(
                self, f"Mostrando primeras {max_show} filas de {len(rows)}.",
                size=11, color=COLORS["text_muted"],
            ).pack(pady=(0, 12))
