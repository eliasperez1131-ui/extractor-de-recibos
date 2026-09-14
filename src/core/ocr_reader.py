from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional

import pytesseract
from PIL import Image


def configure_tesseract(tesseract_path: Optional[str] = None) -> str:
    """Configure the path to tesseract.exe. Returns the resolved path."""
    if tesseract_path and Path(tesseract_path).exists():
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        return tesseract_path

    bundled = _get_bundled_tesseract_path()
    if bundled and Path(bundled).exists():
        pytesseract.pytesseract.tesseract_cmd = bundled
        return bundled

    system = shutil.which("tesseract")
    if system:
        pytesseract.pytesseract.tesseract_cmd = system
        return system

    raise FileNotFoundError(
        "Tesseract no está instalado. Ejecuta el asistente de instalación."
    )


def _get_bundled_tesseract_path() -> Optional[str]:
    """Locate tesseract in the user's AppData folder (installed by wizard)."""
    if sys.platform != "win32":
        return None
    appdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    candidates = [
        os.path.join(appdata, "ExtractorRecibos", "tesseract", "tesseract.exe"),
        os.path.join(appdata, "ExtractorRecibos", "tesseract", "Tesseract-OCR", "tesseract.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def ocr_image(image_path: str | Path, lang: str = "spa+eng+por") -> str:
    """Run OCR on a single image file."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
    try:
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img, lang=lang)
        return _clean_ocr_text(text)
    except Exception as e:
        raise RuntimeError(f"Error OCR en {image_path.name}: {e}")


def ocr_pdf_pages(pdf_path: str | Path, lang: str = "spa+eng+por", dpi: int = 300) -> str:
    """Convert PDF pages to images and run OCR on each."""
    try:
        import pymupdf
    except ImportError:
        raise RuntimeError("PyMuPDF (pymupdf) es necesario para OCR de PDFs escaneados.")

    pdf_path = Path(pdf_path)
    doc = pymupdf.open(str(pdf_path))
    text_parts: List[str] = []
    try:
        for page_index, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img, lang=lang)
            if page_text.strip():
                text_parts.append(f"--- Página {page_index + 1} ---\n{page_text}")
    finally:
        doc.close()

    full = "\n".join(text_parts)
    return _clean_ocr_text(full)


def _clean_ocr_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    cleaned = "\n".join(lines)
    return cleaned.strip()


def detect_tesseract_languages() -> List[str]:
    """Return available tesseract language codes."""
    try:
        langs = pytesseract.get_languages(config="")
        return [l for l in langs if l not in ("osd",)]
    except Exception:
        return ["eng"]
