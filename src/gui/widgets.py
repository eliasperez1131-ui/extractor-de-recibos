from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk


COLORS = {
    "primary": "#1F4E78",
    "primary_hover": "#2A5F8A",
    "success": "#2E7D32",
    "success_hover": "#388E3C",
    "danger": "#C62828",
    "danger_hover": "#D32F2F",
    "warning": "#F57C00",
    "warning_hover": "#FB8C00",
    "bg_light": "#F5F7FA",
    "bg_dark": "#1E1E1E",
    "card_light": "#FFFFFF",
    "card_dark": "#2D2D2D",
    "border_light": "#E0E0E0",
    "border_dark": "#3A3A3A",
    "text_light": "#212121",
    "text_dark": "#E8E8E8",
    "text_muted_light": "#616161",
    "text_muted_dark": "#B0B0B0",
    "accent": "#1976D2",
    "bg": "#F5F7FA",
    "card": "#FFFFFF",
    "border": "#E0E0E0",
    "text": "#212121",
    "text_muted": "#616161",
}


def _make_button(parent, text: str, command: Optional[Callable], kind: str, **kwargs) -> ctk.CTkButton:
    """Internal: create a CTkButton with full-color palette per kind.

    `kind` must be one of: primary, success, danger, warning, secondary.
    """
    palette = {
        "primary": (COLORS["primary"], COLORS["primary_hover"]),
        "success": (COLORS["success"], COLORS["success_hover"]),
        "danger": (COLORS["danger"], COLORS["danger_hover"]),
        "warning": (COLORS["warning"], COLORS["warning_hover"]),
        "secondary": ("#6C757D", "#5A6268"),
    }
    fg, hover = palette[kind]
    defaults = dict(
        fg_color=fg,
        hover_color=hover,
        text_color="#FFFFFF",
        corner_radius=8,
        height=40,
        font=ctk.CTkFont(size=13, weight="bold"),
        border_width=0,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **defaults)


def make_primary_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    return _make_button(parent, text, command, "primary", **kwargs)


def make_success_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    return _make_button(parent, text, command, "success", **kwargs)


def make_danger_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    return _make_button(parent, text, command, "danger", **kwargs)


def make_warning_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    return _make_button(parent, text, command, "warning", **kwargs)


def make_secondary_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    """Neutral gray button for secondary actions (e.g., Limpiar)."""
    return _make_button(parent, text, command, "secondary", **kwargs)


def set_button_active(btn: ctk.CTkButton, command: Optional[Callable]) -> None:
    """Enable/disable a button by attaching/detaching its command (keeps colors)."""
    try:
        btn.configure(command=command if command is not None else lambda: None)
    except Exception:
        pass


def make_label(parent, text: str, size: int = 12, weight: str = "normal",
               color: Optional[str] = None, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=size, weight=weight),
        text_color=color or COLORS["text_light"],
        **kwargs,
    )


class Card(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["card_light"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border_light"],
            **kwargs,
        )


class ScrollableLog(ctk.CTkTextbox):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            **kwargs,
        )
        self.configure(state="disabled")

    def append(self, text: str) -> None:
        self.configure(state="normal")
        self.insert("end", text + "\n")
        self.see("end")
        self.configure(state="disabled")
