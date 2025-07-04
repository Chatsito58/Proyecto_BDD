from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from Consulta import MySQLApp
from redundancia import GestorRedundancia
from utils import cancel_pending_after, safe_bg_error_handler


class VentanaAdmin(tk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("arc")
        except Exception:
            pass
        self.report_callback_exception = safe_bg_error_handler
        self._after_ids: list[str] = []
        self.title("🛠️ Panel del Administrador")
        self.configure(bg="#2a2a2a")
        self.geometry("340x220")
        self.ventana_consulta: tk.Toplevel | None = None
        self.btn_sql: ttk.Button | None = None
        self._configurar_estilo()
        self._build_ui()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("TLabel", font=("Segoe UI", 11))

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=20)
        marco.pack(expand=True)

        ttk.Label(marco, text="🛠️ Panel del Administrador", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        self.btn_sql = ttk.Button(marco, text="Abrir consultas SQL", command=self._abrir_sql)
        self.btn_sql.pack(fill="x", pady=5)
        ttk.Button(marco, text="Cerrar sesión", command=self._logout).pack(fill="x", pady=(15, 0))

    def _abrir_sql(self) -> None:
        if self.ventana_consulta and self.ventana_consulta.winfo_exists():
            self.ventana_consulta.focus()
            return

        self.ventana_consulta = tk.Toplevel(self)
        self.btn_sql.config(state=tk.DISABLED)
        MySQLApp(self.ventana_consulta, GestorRedundancia())
        self.ventana_consulta.protocol("WM_DELETE_WINDOW", self._cerrar_consulta)

    def _logout(self) -> None:
        if self.ventana_consulta and self.ventana_consulta.winfo_exists():
            self.ventana_consulta.destroy()
        cancel_pending_after(self)
        self.destroy()
        if self.master is not None:
            self.master.deiconify()

    def _cerrar_consulta(self) -> None:
        if self.ventana_consulta:
            self.ventana_consulta.destroy()
            self.ventana_consulta = None
            self.btn_sql.config(state=tk.NORMAL)
