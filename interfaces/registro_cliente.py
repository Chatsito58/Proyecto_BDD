from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from interfaces.componentes.ctk_scrollable_combobox import CTkScrollableComboBox
from utils import mostrar_error, mostrar_notificacion
from logica.clientes import crear_cliente, DatosClienteInvalidos


class VentanaCrearCliente(tk.Toplevel):
    """Ventana para registrar un nuevo cliente."""

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("Crear cliente")
        self.configure(bg="#2a2a2a")
        self.geometry("360x580")
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
            ("Documento:", "documento"),
            ("Nombre:", "nombre"),
            ("Teléfono:", "telefono"),
            ("Dirección:", "direccion"),
            ("Correo:", "correo"),
            ("Contraseña:", "pass"),
            ("ID Licencia:", "id_licencia"),
            ("ID Tipo Documento:", "id_tipo_documento"),
            ("ID Tipo Cliente:", "id_tipo_cliente"),
            ("Código Postal:", "id_codigo_postal"),
        ]
        self.entradas: dict[str, ttk.Entry] = {}
        for etiqueta, clave in campos:
            ttk.Label(marco, text=etiqueta).pack(anchor="w", pady=(0, 2))
            entry = ttk.Entry(marco, show="*" if clave == "pass" else None)
            entry.pack(fill="x", pady=5)
            self.entradas[clave] = entry

        ttk.Button(marco, text="💾 Registrar", command=self._registrar).pack(pady=15)

    def _registrar(self) -> None:
        documento = self.entradas["documento"].get().strip()
        nombre = self.entradas["nombre"].get().strip()
        telefono = self.entradas["telefono"].get().strip()
        direccion = self.entradas["direccion"].get().strip()
        correo = self.entradas["correo"].get().strip()
        contrasena = self.entradas["pass"].get()
        id_licencia = self.entradas["id_licencia"].get().strip()
        id_tipo_documento = self.entradas["id_tipo_documento"].get().strip()
        id_tipo_cliente = self.entradas["id_tipo_cliente"].get().strip()
        id_codigo_postal = self.entradas["id_codigo_postal"].get().strip()

        try:
            crear_cliente(
                documento,
                nombre,
                telefono,
                direccion,
                correo,
                contrasena,
                id_licencia,
                id_tipo_documento,
                id_tipo_cliente,
                id_codigo_postal,
            )
            mostrar_notificacion("Éxito", "Cliente creado correctamente")
            self.destroy()
        except DatosClienteInvalidos as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:  # pragma: no cover - conexion errors vary
            mostrar_error(exc)
