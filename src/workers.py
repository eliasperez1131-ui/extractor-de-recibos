from __future__ import annotations

import os
import queue
import shutil
import tempfile
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .core.input_loader import InputItem, TempDirectory, extract_zip_member
from .core.locale_detector import detect_locale, merge_locales, LocaleInfo
from .core.field_detector import detect_fields_in_text, build_master_columns
from .core.ocr_reader import ocr_image, ocr_pdf_pages, configure_tesseract
from .core.pdf_reader import extract_text_from_pdf, is_scanned_pdf
from .core import ocr_reader as ocr_module


@dataclass
class FileResult:
    item: InputItem
    text: str
    fields: Dict[str, str]
    method: str
    error: Optional[str] = None


def _resolve_zip_member(item: InputItem, temp_dir: Path) -> Path:
    if not item.is_zip:
        return item.path
    if "::" not in item.display_name:
        return item.path
    _, member = item.display_name.split("::", 1)
    return extract_zip_member(item.path, member, temp_dir)


def _process_one(item: InputItem, ocr_lang: str, temp_dir_str: str) -> FileResult:
    """Process a single file: extract text via PDF-texto, PDF-OCR or Imagen-OCR."""
    temp_dir = Path(temp_dir_str)
    try:
        try:
            ocr_module.configure_tesseract()
        except Exception:
            pass

        resolved = _resolve_zip_member(item, temp_dir)
        text = ""
        method = "Omitido"
        error = None

        if item.kind == "PDF":
            try:
                text = extract_text_from_pdf(resolved)
                if text and len(text.strip()) >= 20:
                    method = "PDF-texto"
                else:
                    try:
                        text = ocr_pdf_pages(resolved, lang=ocr_lang)
                        method = "PDF-OCR"
                    except Exception as e:
                        method = "PDF-error"
                        error = f"OCR fallo: {e}"
            except Exception as e:
                method = "PDF-error"
                error = str(e)
        elif item.kind == "Imagen":
            try:
                text = ocr_image(resolved, lang=ocr_lang)
                method = "Imagen-OCR"
            except Exception as e:
                method = "Imagen-error"
                error = str(e)
        else:
            method = "Omitido"
            error = f"Tipo no soportado: {item.kind}"

        fields = detect_fields_in_text(text, LocaleInfo(
            code="MX", country="México", currency="MXN", currency_symbol="$",
            tax_label="IVA", tax_id_label="RFC", invoice_label="Factura",
            date_format="DD/MM/YYYY",
        )) if text else {}

        return FileResult(item=item, text=text, fields=fields, method=method, error=error)

    except Exception as e:
        return FileResult(
            item=item,
            text="",
            fields={},
            method="Error",
            error=f"{e}\n{traceback.format_exc()[:500]}",
        )


class ProcessingCancelled(Exception):
    pass


class Processor:
    """Coordinates parallel processing with cancellation support and progress callbacks."""

    def __init__(self, items: List[InputItem], ocr_lang: str = "spa+eng+por",
                 max_workers: Optional[int] = None,
                 progress_callback: Optional[Callable[[int, int, FileResult], None]] = None,
                 log_callback: Optional[Callable[[str], None]] = None,
                 cancel_check: Optional[Callable[[], bool]] = None):
        self.items = items
        self.ocr_lang = ocr_lang
        self.max_workers = max_workers or max(1, (os.cpu_count() or 4) - 1)
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_check = cancel_check
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> Dict:
        """Returns dict with: results, locale, columns, rows, summary."""
        total = len(self.items)
        if total == 0:
            return {
                "results": [],
                "locale": LocaleInfo("MX", "México", "MXN", "$", "IVA", "RFC", "Factura", "DD/MM/YYYY"),
                "columns": ["ARCHIVO", "TIPO", "ESTADO"],
                "rows": [],
                "summary": {"processed": 0, "pdf_text": 0, "pdf_ocr": 0, "image_ocr": 0, "errors": 0},
            }

        results: List[FileResult] = []
        completed_count = 0
        summary = {"processed": 0, "pdf_text": 0, "pdf_ocr": 0, "image_ocr": 0, "errors": 0}

        try:
            configure_tesseract()
            if self.log_callback:
                self.log_callback("Tesseract OK")
        except FileNotFoundError as e:
            if self.log_callback:
                self.log_callback(f"⚠ Tesseract no disponible: {e}")
            if self.log_callback:
                self.log_callback("Solo se procesaran PDFs con texto (sin OCR)")
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"⚠ Error configurando Tesseract: {e}")

        if self.log_callback:
            self.log_callback(f"Iniciando procesamiento con {self.max_workers} workers...")
        if self.log_callback:
            self.log_callback(f"Total de archivos: {total}")

        with TempDirectory(prefix="extractor_run_") as temp_dir:
            executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="extract")
            try:
                future_to_item = {}
                for item in self.items:
                    if self.log_callback:
                        self.log_callback(f"→ Enviando a procesar: {item.display_name}")
                    fut = executor.submit(_process_one, item, self.ocr_lang, str(temp_dir))
                    future_to_item[fut] = item

                if self.log_callback:
                    self.log_callback(f"Todos los archivos enviados al pool. Esperando resultados...")

                last_log_time = time.time()
                for future in as_completed(future_to_item):
                    if self._cancelled or (self.cancel_check and self.cancel_check()):
                        if self.log_callback:
                            self.log_callback("Cancelacion solicitada. Deteniendo...")
                        break

                    try:
                        result = future.result(timeout=300)
                    except Exception as e:
                        item = future_to_item[future]
                        result = FileResult(
                            item=item, text="", fields={},
                            method="Error", error=f"Worker fallo: {e}",
                        )

                    results.append(result)
                    completed_count += 1
                    summary["processed"] += 1

                    if result.method == "PDF-texto":
                        summary["pdf_text"] += 1
                    elif result.method == "PDF-OCR":
                        summary["pdf_ocr"] += 1
                    elif result.method == "Imagen-OCR":
                        summary["image_ocr"] += 1

                    if result.error:
                        summary["errors"] += 1

                    if self.log_callback:
                        status = "OK" if not result.error else "ERROR"
                        self.log_callback(
                            f"[{completed_count}/{total}] {result.item.display_name} -> {result.method} [{status}]"
                            + (f" ({result.error[:80]})" if result.error else "")
                        )

                    if self.progress_callback:
                        self.progress_callback(completed_count, total, result)

                    if self.log_callback and time.time() - last_log_time > 5:
                        self.log_callback(f"Progreso: {completed_count}/{total} archivos completados")
                        last_log_time = time.time()

            finally:
                executor.shutdown(wait=False)

        if completed_count < total and not self._cancelled:
            if self.log_callback:
                self.log_callback(f"⚠ Procesamiento incompleto: {completed_count}/{total}")

        all_texts = [r.text for r in results if r.text]
        locale = detect_locale(all_texts)

        all_fields: List[Dict[str, str]] = []
        for r in results:
            if not r.fields:
                all_fields.append({})
            else:
                all_fields.append(r.fields)

        if self.log_callback:
            self.log_callback("Generando columnas y filas...")

        columns, rows = build_master_columns(all_fields, locale)

        for r, row in zip(results, rows):
            row["ARCHIVO"] = r.item.display_name
            row["TIPO"] = r.method
            row["ESTADO"] = "OK" if not r.error else f"Error: {r.error[:50]}"

        return {
            "results": results,
            "locale": locale,
            "columns": columns,
            "rows": rows,
            "summary": summary,
        }
