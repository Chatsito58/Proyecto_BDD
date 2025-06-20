from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

from Consulta import MySQLApp
from conexion.conexion import ConexionBD


class VentanaAdmin(ThemedTk):
    def __init__(self) -> None:
        super().__init__(theme="arc")
        self.title("🛠️ Panel del Administrador")
        self.configure(bg="#f4f6f9")
        self.geometry("340x220")
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
        ttk.Button(marco, text="Abrir consultas SQL", command=self._abrir_sql).pack(fill="x", pady=5)
        ttk.Button(marco, text="Cerrar sesión", command=self._logout).pack(fill="x", pady=(15, 0))

    def _abrir_sql(self) -> None:
        root = ThemedTk(theme="arc")
        MySQLApp(root, ConexionBD())
        root.mainloop()

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()
