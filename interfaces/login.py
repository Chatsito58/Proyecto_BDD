from __future__ import annotations

from tkinter import messagebox, ttk
from ttkthemes import ThemedTk

from logica.auth import Autenticador


class VentanaLogin(ThemedTk):
    """Ventana principal de inicio de sesión."""

    def __init__(self) -> None:
        super().__init__(theme="arc")
        self.title("🔐 Iniciar Sesión")
        self.configure(bg="#f4f6f9")
        self.geometry("320x260")
        self.autenticador = Autenticador()
        self._configurar_estilo()
        self._build_ui()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure("TLabel", font=("Segoe UI", 11))
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

    @staticmethod
    def _normalizar_rol(rol: str) -> str:
        """Mapear variantes comunes de nombres de rol al valor esperado."""
        rol = rol.strip().lower()
        mapping = {
            "administrador": "admin",
            "gerete": "gerente",
            "empleadao": "empleado",
            "ventas": "empleado",
            "mantenimiento": "empleado",
            "operaciones": "empleado",
            "conductor": "empleado",
            "atencion al cliente": "empleado",
        }
        return mapping.get(rol, rol)

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=20)
        marco.pack(expand=True)

        ttk.Label(
            marco,
            text="🔐 Iniciar Sesión",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 15))

        ttk.Label(marco, text="Correo:").pack(anchor="w")
        self.entry_correo = ttk.Entry(marco)
        self.entry_correo.pack(fill="x", pady=5)

        ttk.Label(marco, text="Contraseña:").pack(anchor="w")
        self.entry_pass = ttk.Entry(marco, show="*")
        self.entry_pass.pack(fill="x", pady=5)

        ttk.Button(marco, text="🚪 Iniciar", command=self._ingresar).pack(pady=10, fill="x")

        enlace = ttk.Label(
            marco,
            text="🆕 Crear cuenta de cliente",
            foreground="blue",
            cursor="hand2",
        )
        enlace.pack()
        enlace.bind("<Button-1>", lambda _e: self._abrir_registro())

    def _ingresar(self) -> None:
        correo = self.entry_correo.get().strip()
        password = self.entry_pass.get()
        rol = self.autenticador.autenticar(correo, password)
        if not rol:
            messagebox.showerror("Error", "Credenciales inválidas")
            return

        rol = self._normalizar_rol(rol)
        self.destroy()
        if rol == "cliente":
            from interfaces.cliente import VentanaCliente

            VentanaCliente().mainloop()
        elif rol == "empleado":
            from interfaces.empleado import VentanaEmpleado

            VentanaEmpleado().mainloop()
        elif rol == "gerente":
            from interfaces.gerente import VentanaGerente

            VentanaGerente().mainloop()
        elif rol == "admin":
            from interfaces.admin import VentanaAdmin

            VentanaAdmin().mainloop()
        else:
            messagebox.showerror("Error", "Rol desconocido")

    def _abrir_registro(self) -> None:
        from interfaces.registro_cliente import VentanaCrearCliente

        VentanaCrearCliente(self)
