from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def get_app_data_dir() -> Path:
    """Return the directory where persistent data is stored."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    path = Path(base) / "ExtractorRecibos"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_mappings_path() -> Path:
    return get_app_data_dir() / "field_mappings.json"


def get_settings_path() -> Path:
    return get_app_data_dir() / "settings.json"


def load_mappings() -> Dict:
    path = get_mappings_path()
    if not path.exists():
        return {
            "locale": None,
            "currency": None,
            "columns": {},
            "aliases": {},
            "last_used": None,
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"locale": None, "currency": None, "columns": {}, "aliases": {}, "last_used": None}


def save_mappings(mappings: Dict) -> None:
    mappings["last_used"] = datetime.utcnow().isoformat()
    path = get_mappings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(mappings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] No se pudo guardar mappings: {e}")


def load_settings() -> Dict:
    path = get_settings_path()
    if not path.exists():
        return {
            "ocr_lang": "spa+eng+por",
            "max_workers": None,
            "theme": "system",
            "first_run": True,
            "tesseract_installed": False,
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "ocr_lang": "spa+eng+por",
            "max_workers": None,
            "theme": "system",
            "first_run": True,
            "tesseract_installed": False,
        }


def save_settings(settings: Dict) -> None:
    path = get_settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] No se pudo guardar settings: {e}")
