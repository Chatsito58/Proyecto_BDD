from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class CTkScrollableComboBox(ctk.CTkFrame):
    """Simple scrollable ComboBox using ``ttk.Combobox`` internally."""

    def __init__(
        self,
        master: tk.Misc | None = None,
        values: list[str] | None = None,
        command: callable | None = None,
        width: int = 140,
        height: int = 28,
        **kwargs,
    ) -> None:
        super().__init__(
            master, width=width, height=height, fg_color="transparent", **kwargs
        )
        self._command = command
        self._var = tk.StringVar()
        self._box = ttk.Combobox(
            self,
            textvariable=self._var,
            values=values or [],
            state="readonly",
            height=height,
        )
        self._box.pack(fill="both", expand=True)
        if command is not None:
            self._box.bind("<<ComboboxSelected>>", self._callback)

    # ------------------------------------------------------------------
    def _callback(self, _event: tk.Event) -> None:
        if self._command is not None:
            self._command(self._var.get())

    # Proxy common widget methods
    def get(self) -> str:
        return self._var.get()

    def set(self, value: str) -> None:
        self._var.set(value)

    def bind(
        self,
        sequence: str | None = None,
        func: callable | None = None,
        add: bool | None = None,
    ) -> str:
        return self._box.bind(sequence, func, add=add)

    def configure(self, require_redraw: bool | None = None, **kwargs) -> None:  # type: ignore[override]
        if "values" in kwargs:
            self._box["values"] = kwargs.pop("values")
        if "command" in kwargs:
            if self._command is not None:
                self._box.unbind("<<ComboboxSelected>>")
            self._command = kwargs.pop("command")
            if self._command is not None:
                self._box.bind("<<ComboboxSelected>>", self._callback)
        self._box.configure(**kwargs)
        super().configure(require_redraw=require_redraw)
