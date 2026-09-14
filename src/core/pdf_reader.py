from __future__ import annotations

import re
from pathlib import Path
from typing import List

import pdfplumber
import pymupdf as fitz  # PyMuPDF (pymupdf package)


_TEXT_THRESHOLD = 50


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract text from a PDF using digital text layer (pdfplumber + PyMuPDF fallback)."""
    pdf_path = Path(pdf_path)
    text_parts: List[str] = []

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
    except Exception:
        text_parts = []

    if not text_parts:
        try:
            doc = fitz.open(str(pdf_path))
            for page in doc:
                text_parts.append(page.get_text("text") or "")
            doc.close()
        except Exception:
            pass

    full_text = "\n".join(text_parts).strip()

    if len(full_text) < _TEXT_THRESHOLD:
        return ""

    full_text = _clean_text(full_text)
    return full_text


def is_scanned_pdf(pdf_path: str | Path) -> bool:
    """Return True if the PDF has no usable text layer (likely scanned)."""
    return extract_text_from_pdf(pdf_path) == ""


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)


def get_pdf_page_count(pdf_path: str | Path) -> int:
    try:
        doc = fitz.open(str(pdf_path))
        n = doc.page_count
        doc.close()
        return n
    except Exception:
        return 0
