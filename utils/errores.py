from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


def mostrar_error(error: Exception) -> None:
    """Log and show an error using a messagebox."""
    logging.error("%s", error)
    messagebox.showerror("Error", str(error))


def mostrar_notificacion(titulo: str, mensaje: str) -> None:
    """Display a small centered CTkToplevel with a message."""
    top = ctk.CTkToplevel()
    top.title(titulo)
    top.resizable(False, False)
    label = ctk.CTkLabel(top, text=mensaje, font=("Segoe UI", 12))
    label.pack(padx=20, pady=20)

    top.update_idletasks()
    x = (top.winfo_screenwidth() // 2) - (top.winfo_width() // 2)
    y = (top.winfo_screenheight() // 2) - (top.winfo_height() // 2)
    top.geometry(f"+{x}+{y}")
    top.after(4000, top.destroy)
    top.grab_set()
    top.focus_force()
