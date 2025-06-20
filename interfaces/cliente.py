from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from ttkthemes import ThemedTk

from conexion.conexion import ConexionBD


class VentanaCliente(ThemedTk):
    def __init__(self) -> None:
        super().__init__(theme="arc")
        self.title("👤 Panel del Cliente")
        self.configure(bg="#f4f6f9")
        self.geometry("360x300")
        self.conexion = ConexionBD()
        self._configurar_estilo()
        self._build_ui()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("TLabel", font=("Segoe UI", 11))

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=20)
        marco.pack(expand=True)

        ttk.Label(marco, text="👤 Panel del Cliente", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        ttk.Button(marco, text="Ver Reservas", command=self._reservar).pack(fill="x", pady=5)
        ttk.Button(marco, text="Vehículos disponibles", command=self._ver_vehiculos).pack(fill="x", pady=5)
        ttk.Button(marco, text="Tarifas/promociones", command=self._ver_tarifas).pack(fill="x", pady=5)
        ttk.Button(marco, text="Cerrar sesión", command=self._logout).pack(fill="x", pady=(15, 0))

    def _reservar(self) -> None:
        messagebox.showinfo("Reservas", "Función de reserva no implementada")

    def _ver_vehiculos(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT placa, modelo FROM Vehiculo")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudieron obtener los vehículos:\n{exc}")
            return
        self._mostrar_resultados("Vehículos disponibles", ["Placa", "Modelo"], filas)

    def _ver_tarifas(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT descripcion, valor FROM Descuento_alquiler")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudieron obtener las tarifas:\n{exc}")
            return
        self._mostrar_resultados("Tarifas y promociones", ["Descripción", "Valor"], filas)

    def _mostrar_resultados(self, titulo: str, columnas: list[str], filas: list[tuple]) -> None:
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.configure(bg="#f4f6f9")
        tree = ttk.Treeview(ventana, columns=columnas, show="headings")
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        for fila in filas:
            tree.insert("", "end", values=fila)
        tree.pack(expand=True, fill="both", padx=10, pady=10)

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()
