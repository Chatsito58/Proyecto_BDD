from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash
from utils.validations import validar_correo


class VentanaCrearCliente(tk.Toplevel):
    """Ventana para registrar un nuevo cliente."""

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("Crear cliente")
        self.configure(bg="#f4f6f9")
        self.geometry("340x420")
        self.conexion = ConexionBD()
        self._configurar_estilo()
        self._build_ui()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("arc")
        estilo.configure("TLabel", font=("Segoe UI", 11))
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=20)
        marco.pack(fill="both", expand=True)

        campos = [
            ("Nombre:", "nombre"),
            ("Documento:", "documento"),
            ("Correo:", "correo"),
            ("Contraseña:", "pass"),
        ]
        self.entradas: dict[str, ttk.Entry] = {}
        for etiqueta, clave in campos:
            ttk.Label(marco, text=etiqueta).pack(anchor="w", pady=(0, 2))
            entry = ttk.Entry(marco, show="*" if clave == "pass" else None)
            entry.pack(fill="x", pady=5)
            self.entradas[clave] = entry

        ttk.Button(marco, text="💾 Registrar", command=self._registrar).pack(pady=15)

    def _registrar(self) -> None:
        nombre = self.entradas["nombre"].get().strip()
        documento = self.entradas["documento"].get().strip()
        correo = self.entradas["correo"].get().strip()
        contrasena = self.entradas["pass"].get()

        if not nombre or not documento or not correo or not contrasena:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        if not validar_correo(correo):
            messagebox.showerror("Error", "Correo no válido")
            return

        query = (
            "INSERT INTO Cliente (nombre, documento, correo, contrasena) "
            "VALUES (%s, %s, %s, %s)"
        )
        hashed = sha256_hash(contrasena)
        try:
            self.conexion.ejecutar(query, (nombre, documento, correo, hashed))
            messagebox.showinfo("Éxito", "Cliente creado correctamente")
            self.destroy()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror("Error", f"No se pudo crear el cliente: {exc}")
