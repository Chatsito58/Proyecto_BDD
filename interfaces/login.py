import tkinter as tk
from tkinter import messagebox

from logica.auth import Autenticador


class LoginApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Inicio de sesión')
        self.geometry('300x180')
        self.autenticador = Autenticador()
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self, text='Correo:').pack(pady=5)
        self.entry_correo = tk.Entry(self)
        self.entry_correo.pack(fill='x', padx=20)

        tk.Label(self, text='Contraseña:').pack(pady=5)
        self.entry_pass = tk.Entry(self, show='*')
        self.entry_pass.pack(fill='x', padx=20)

        tk.Button(self, text='Ingresar', command=self._ingresar).pack(pady=10)
        tk.Button(self, text='Crear cliente', command=self._abrir_registro).pack(pady=5)

    def _ingresar(self) -> None:
        correo = self.entry_correo.get().strip()
        password = self.entry_pass.get()
        rol = self.autenticador.autenticar(correo, password)
        if not rol:
            messagebox.showerror('Error', 'Credenciales inválidas')
            return
        self.destroy()
        if rol == 'cliente':
            from interfaces.cliente import ClienteApp
            ClienteApp().mainloop()
        elif rol == 'empleado':
            from interfaces.empleado import EmpleadoApp
            EmpleadoApp().mainloop()
        elif rol == 'gerente':
            from interfaces.gerente import GerenteApp
            GerenteApp().mainloop()
        elif rol == 'admin':
            from interfaces.admin import AdminApp
            AdminApp().mainloop()
        else:
            messagebox.showerror('Error', 'Rol desconocido')

    def _abrir_registro(self) -> None:
        from interfaces.registro_cliente import RegistroClienteApp
        RegistroClienteApp(self)
