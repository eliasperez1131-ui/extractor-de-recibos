from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import List


SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
ZIP_EXTENSIONS = {".zip"}


@dataclass
class InputItem:
    path: Path
    display_name: str
    kind: str
    is_zip: bool = False

    def __str__(self) -> str:
        return f"{self.display_name} ({self.kind})"


def scan_path(path: str | Path) -> List[InputItem]:
    """Scan a folder or a single file. ZIPs are flattened into their contents."""
    path = Path(path)
    if not path.exists():
        return []

    items: List[InputItem] = []
    if path.is_file():
        items.extend(_wrap_single(path))
        return items

    if path.is_dir():
        for entry in sorted(path.rglob("*")):
            if entry.is_file():
                if entry.suffix.lower() in ZIP_EXTENSIONS:
                    items.extend(_unwrap_zip(entry))
                elif entry.suffix.lower() in SUPPORTED_EXTENSIONS:
                    items.append(InputItem(
                        path=entry,
                        display_name=str(entry.relative_to(path)),
                        kind=_detect_kind(entry),
                    ))

    return items


def _wrap_single(file_path: Path) -> List[InputItem]:
    if file_path.suffix.lower() in ZIP_EXTENSIONS:
        return _unwrap_zip(file_path)
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return []
    return [InputItem(
        path=file_path,
        display_name=file_path.name,
        kind=_detect_kind(file_path),
    )]


def _unwrap_zip(zip_path: Path) -> List[InputItem]:
    items: List[InputItem] = []
    try:
        with zipfile.ZipFile(str(zip_path), "r") as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue
                inner = Path(name)
                if inner.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                items.append(InputItem(
                    path=zip_path,
                    display_name=f"{zip_path.name}::{name}",
                    kind=_detect_kind(inner),
                    is_zip=True,
                ))
    except (zipfile.BadZipFile, OSError):
        pass
    return items


def _detect_kind(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return "PDF"
    if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
        return "Imagen"
    return "Desconocido"


def extract_zip_member(zip_path: Path, member_name: str, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / Path(member_name).name
    with zipfile.ZipFile(str(zip_path), "r") as zf:
        with zf.open(member_name) as src, open(out_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
    return out_path


class TempDirectory:
    """Context manager that creates a temp dir and cleans it up."""

    def __init__(self, prefix: str = "extractor_"):
        self.prefix = prefix
        self.path: Path = None  # type: ignore

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix=self.prefix))
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.path and self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)
