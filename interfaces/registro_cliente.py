import tkinter as tk
from tkinter import messagebox

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash
from utils.validations import validar_correo


class RegistroClienteApp(tk.Toplevel):
    """Ventana para registrar un nuevo cliente."""

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title('Registro de cliente')
        self.geometry('320x380')
        self.conexion = ConexionBD()
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self, text='Nombre:').pack(pady=5)
        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.pack(fill='x', padx=20)

        tk.Label(self, text='Documento:').pack(pady=5)
        self.entry_documento = tk.Entry(self)
        self.entry_documento.pack(fill='x', padx=20)

        tk.Label(self, text='Tel\u00E9fono:').pack(pady=5)
        self.entry_telefono = tk.Entry(self)
        self.entry_telefono.pack(fill='x', padx=20)

        tk.Label(self, text='Direcci\u00F3n:').pack(pady=5)
        self.entry_direccion = tk.Entry(self)
        self.entry_direccion.pack(fill='x', padx=20)

        tk.Label(self, text='Correo:').pack(pady=5)
        self.entry_correo = tk.Entry(self)
        self.entry_correo.pack(fill='x', padx=20)

        tk.Label(self, text='Contrase\u00F1a:').pack(pady=5)
        self.entry_pass = tk.Entry(self, show='*')
        self.entry_pass.pack(fill='x', padx=20)

        tk.Button(self, text='Registrar', command=self._registrar).pack(pady=15)

    def _registrar(self) -> None:
        nombre = self.entry_nombre.get().strip()
        documento = self.entry_documento.get().strip()
        telefono = self.entry_telefono.get().strip()
        direccion = self.entry_direccion.get().strip()
        correo = self.entry_correo.get().strip()
        contrasena = self.entry_pass.get()

        if not nombre or not documento or not correo or not contrasena:
            messagebox.showerror('Error', 'Nombre, documento, correo y contrase\u00F1a son obligatorios')
            return
        if not validar_correo(correo):
            messagebox.showerror('Error', 'Correo no v\u00E1lido')
            return

        query = (
            'INSERT INTO cliente '
            '(nombre, documento, telefono, direccion, correo, contrasena) '
            'VALUES (%s, %s, %s, %s, %s, %s)'
        )
        hashed = sha256_hash(contrasena)
        try:
            self.conexion.ejecutar(
                query,
                (nombre, documento, telefono, direccion, correo, hashed),
            )
            messagebox.showinfo('\u00C9xito', 'Cliente creado correctamente')
            self.destroy()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror('Error', f'No se pudo crear el cliente: {exc}')
