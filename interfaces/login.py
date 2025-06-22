from __future__ import annotations

from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("dark")  # o "light"
ctk.set_default_color_theme("blue")

from logica.auth import Autenticador


class VentanaLogin(ctk.CTk):
    """Ventana principal de inicio de sesión."""

    def __init__(self) -> None:
        super().__init__()
        self.title("🔐 Iniciar Sesión")
        self.geometry("320x260")
        self.configure(fg_color="#2a2a2a")
        self.autenticador = Autenticador()
        self._configurar_estilo()
        self._build_ui()

    def _configurar_estilo(self) -> None:
        # CustomTkinter maneja estilos a través de temas
        pass

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
        marco = ctk.CTkFrame(self)
        marco.pack(expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            marco,
            text="🔐 Iniciar Sesión",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 15))

        ctk.CTkLabel(marco, text="Correo:").pack(anchor="w")
        self.entry_correo = ctk.CTkEntry(marco)
        self.entry_correo.pack(fill="x", pady=5)

        ctk.CTkLabel(marco, text="Contraseña:").pack(anchor="w")
        self.entry_pass = ctk.CTkEntry(marco, show="*")
        self.entry_pass.pack(fill="x", pady=5)

        ctk.CTkButton(marco, text="🚪 Iniciar", command=self._ingresar).pack(pady=10, fill="x")

        enlace = ctk.CTkLabel(
            marco,
            text="🆕 Crear cuenta de cliente",
            text_color="blue",
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

            id_cliente = self.autenticador.obtener_id_cliente(correo)
            if id_cliente is None:
                messagebox.showerror("Error", "Cliente no encontrado")
                return
            VentanaCliente(id_cliente).mainloop()
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
