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
    "bg": "#F5F7FA",
    "card": "#FFFFFF",
    "border": "#E0E0E0",
    "text": "#212121",
    "text_muted": "#616161",
    "accent": "#1976D2",
}


def make_primary_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    defaults = dict(
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        text_color="#FFFFFF",
        corner_radius=8,
        height=36,
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **defaults)


def make_success_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    defaults = dict(
        fg_color=COLORS["success"],
        hover_color=COLORS["success_hover"],
        text_color="#FFFFFF",
        corner_radius=8,
        height=36,
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **defaults)


def make_danger_button(parent, text: str, command: Optional[Callable] = None, **kwargs) -> ctk.CTkButton:
    defaults = dict(
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        text_color="#FFFFFF",
        corner_radius=8,
        height=36,
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **defaults)


def make_label(parent, text: str, size: int = 12, weight: str = "normal",
               color: Optional[str] = None, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=size, weight=weight),
        text_color=color or COLORS["text"],
        **kwargs,
    )


class Card(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
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
