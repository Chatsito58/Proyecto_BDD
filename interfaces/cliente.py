from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
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
        ventana = tk.Toplevel(self)
        ventana.title("Nueva reserva")
        ventana.configure(bg="#f4f6f9")

        ttk.Label(
            ventana, text="Fecha y hora inicio (YYYY-MM-DD HH:MM):"
        ).pack(anchor="w", padx=10, pady=(10, 2))
        entry_inicio = ttk.Entry(ventana)
        entry_inicio.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            ventana, text="Fecha y hora fin (YYYY-MM-DD HH:MM):"
        ).pack(anchor="w", padx=10, pady=(10, 2))
        entry_fin = ttk.Entry(ventana)
        entry_fin.pack(fill="x", padx=10, pady=5)

        ttk.Label(ventana, text="Abono:").pack(anchor="w", padx=10, pady=(10, 2))
        entry_abono = ttk.Entry(ventana)
        entry_abono.pack(fill="x", padx=10, pady=5)

        ttk.Label(ventana, text="Saldo pendiente:").pack(
            anchor="w", padx=10, pady=(10, 2)
        )
        entry_saldo = ttk.Entry(ventana)
        entry_saldo.pack(fill="x", padx=10, pady=5)

        def registrar() -> None:
            inicio = entry_inicio.get().strip()
            fin = entry_fin.get().strip()
            abono = entry_abono.get().strip()
            saldo = entry_saldo.get().strip()
            if not inicio or not fin or not abono or not saldo:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            try:
                fecha_ini = datetime.strptime(inicio, "%Y-%m-%d %H:%M")
                fecha_fin = datetime.strptime(fin, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fechas incorrecto (YYYY-MM-DD HH:MM)"
                )
                return
            if fecha_fin < fecha_ini:
                messagebox.showerror(
                    "Error", "La fecha de fin debe ser posterior a la de inicio"
                )
                return
            try:
                abono_val = float(abono)
                saldo_val = float(saldo)
            except ValueError:
                messagebox.showerror("Error", "Valores num\u00e9ricos inv\u00e1lidos")
                return
            query = (
                "INSERT INTO Reserva_alquiler "
                "(fecha_hora, fecha_hora_entrada, fecha_hora_salida, abono, saldo_pendiente, id_estado_reserva) "
                "VALUES (NOW(), %s, %s, %s, %s, %s)"
            )
            try:
                self.conexion.ejecutar(
                    query,
                    (
                        fecha_ini.strftime("%Y-%m-%d %H:%M:%S"),
                        fecha_fin.strftime("%Y-%m-%d %H:%M:%S"),
                        abono_val,
                        saldo_val,
                        1,  # Estado 'Reservado'
                    ),
                )
                messagebox.showinfo(
                    "Reserva", "Reserva registrada correctamente"
                )
                ventana.destroy()
            except Exception as exc:  # pragma: no cover - depende de la BD
                messagebox.showerror(
                    "Error", f"No se pudo registrar la reserva:\n{exc}"
                )

        ttk.Button(ventana, text="Reservar", command=registrar).pack(
            pady=15
        )

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
