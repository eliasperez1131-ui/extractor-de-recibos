from __future__ import annotations

import hashlib
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Callable, Optional

import requests


TESSERACT_VERSION = "5.3.3.20231005"

_DOWNLOAD_URLS = {
    "win32": {
        "spa": f"https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata",
        "eng": f"https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata",
        "por": f"https://github.com/tesseract-ocr/tessdata_fast/raw/main/por.traineddata",
        "spa.traineddata": f"https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata",
        "eng.traineddata": f"https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata",
        "por.traineddata": f"https://github.com/tesseract-ocr/tessdata_fast/raw/main/por.traineddata",
    }
}

_TESSERACT_WIN_URL = (
    "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-{ver}.exe"
).format(ver=TESSERACT_VERSION)

_FALLBACK_URLS = [
    "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/"
    "tesseract-ocr-w64-setup-5.3.3.20231005.exe",
]


def get_install_dir() -> Path:
    """Directory where Tesseract will be installed (portable, user-scope)."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = Path(base) / "ExtractorRecibos" / "tesseract"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_tesseract_exe_path() -> Path:
    install_dir = get_install_dir()
    if sys.platform == "win32":
        candidate = install_dir / "tesseract.exe"
        if candidate.exists():
            return candidate
        candidate2 = install_dir / "Tesseract-OCR" / "tesseract.exe"
        if candidate2.exists():
            return candidate2
    elif sys.platform == "darwin":
        return install_dir / "bin" / "tesseract"
    else:
        return install_dir / "bin" / "tesseract"
    return candidate


def get_tessdata_dir() -> Path:
    install_dir = get_install_dir()
    if sys.platform == "win32":
        candidates = [install_dir / "tessdata", install_dir / "Tesseract-OCR" / "tessdata"]
        for c in candidates:
            if c.exists():
                return c
        return candidates[0]
    return install_dir / "share" / "tessdata"


def is_tesseract_installed() -> bool:
    try:
        exe = get_tesseract_exe_path()
        if not exe.exists():
            return False
        tessdata = get_tessdata_dir()
        if not tessdata.exists():
            return False
        required = ["spa.traineddata", "eng.traineddata", "por.traineddata"]
        return all((tessdata / r).exists() for r in required)
    except Exception:
        return False


def _download_file(url: str, dest: Path,
                   progress: Optional[Callable[[int, int], None]] = None) -> bool:
    try:
        with requests.get(url, stream=True, timeout=60, allow_redirects=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress:
                            progress(downloaded, total)
        return True
    except Exception as e:
        print(f"[ERROR] Descarga fallida {url}: {e}")
        return False


def _download_tessdata(languages: list[str],
                       progress: Optional[Callable[[int, int, str], None]] = None) -> bool:
    """Download only the .traineddata files (lightweight approach)."""
    if sys.platform != "win32":
        return False

    install_dir = get_install_dir()
    tessdata = install_dir / "tessdata"
    tessdata.mkdir(parents=True, exist_ok=True)

    urls = _DOWNLOAD_URLS.get("win32", {})

    downloaded_ok = True
    for lang in languages:
        url = urls.get(lang) or urls.get(f"{lang}.traineddata")
        if not url:
            continue
        dest = tessdata / f"{lang}.traineddata"
        if dest.exists():
            if progress:
                progress(dest.stat().st_size, dest.stat().st_size, lang)
            continue

        def _cb(d, t, l=lang):
            if progress:
                progress(d, t, l)

        ok = _download_file(url, dest, progress=_cb)
        if not ok:
            downloaded_ok = False

    return downloaded_ok


def _try_portable_tesseract_windows(
        progress: Optional[Callable[[int, int, str], None]] = None) -> bool:
    """Try downloading a minimal portable Tesseract for Windows.

    Strategy: download the official .exe installer (which is small) and extract it
    using 7-Zip-style approach is NOT available, so we fall back to downloading
    just the tessdata files and using the system tesseract.exe if available.
    If neither is available, instruct user to install manually.
    """
    install_dir = get_install_dir()

    tesseract_exe = install_dir / "tesseract.exe"
    if not tesseract_exe.exists():
        if progress:
            progress(0, 1, "Buscando tesseract.exe portable...")
        found = False
        for url in _FALLBACK_URLS:
            installer = install_dir / "tesseract-setup.exe"
            if progress:
                progress(0, 1, f"Descargando instalador...")
            ok = _download_file(url, installer)
            if ok:
                if progress:
                    progress(50, 100, "Instalador descargado")
                if progress:
                    progress(80, 100, "Por favor ejecuta el instalador manualmente")
                found = True
                break
        if not found:
            return False

    langs = ["spa", "eng", "por"]
    if progress:
        progress(0, 1, "Descargando modelos de idioma...")
    ok = _download_tessdata(langs, progress=progress)
    return ok


def install_tesseract(languages: Optional[list[str]] = None,
                      progress: Optional[Callable[[int, int, str], None]] = None) -> bool:
    """Install Tesseract + language data into the user's app folder.

    progress callback signature: (downloaded_bytes, total_bytes, message)
    """
    if is_tesseract_installed():
        if progress:
            progress(100, 100, "Tesseract ya está instalado")
        return True

    if languages is None:
        languages = ["spa", "eng", "por"]

    if sys.platform == "win32":
        return _try_portable_tesseract_windows(progress=progress)
    else:
        if progress:
            progress(0, 100, "Plataforma no soportada para instalación automática")
        return False


def uninstall_tesseract() -> bool:
    install_dir = get_install_dir()
    if install_dir.exists():
        try:
            shutil.rmtree(install_dir)
            return True
        except Exception:
            return False
    return True
