from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from ttkthemes import ThemedTk

from conexion.conexion import ConexionBD


class VentanaReservaCliente(ThemedTk):
    """Interfaz para que el cliente gestione sus reservas."""

    def __init__(self, id_cliente: int) -> None:
        super().__init__(theme="arc")
        self.title("🚗 Reservas")
        self.configure(bg="#f4f6f9")
        self.geometry("420x460")
        self.id_cliente = id_cliente
        self.conexion = ConexionBD()
        self._configurar_estilo()
        self._build_ui()
        self._cargar_datos()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("TLabel", font=("Segoe UI", 11))

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=10)
        marco.pack(fill="both", expand=True)

        ttk.Label(
            marco,
            text="🚗 Crear nueva reserva",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(marco, text="Vehículo:").pack(anchor="w")
        self.combo_vehiculo = ttk.Combobox(marco, state="readonly")
        self.combo_vehiculo.pack(fill="x", pady=5)

        ttk.Label(marco, text="Fecha inicio (YYYY-MM-DD):").pack(anchor="w")
        self.entry_inicio = ttk.Entry(marco)
        self.entry_inicio.pack(fill="x", pady=5)

        ttk.Label(marco, text="Fecha fin (YYYY-MM-DD):").pack(anchor="w")
        self.entry_fin = ttk.Entry(marco)
        self.entry_fin.pack(fill="x", pady=5)

        ttk.Label(marco, text="Medio de pago:").pack(anchor="w")
        self.combo_medio = ttk.Combobox(marco, state="readonly")
        self.combo_medio.pack(fill="x", pady=5)

        ttk.Label(marco, text="Abono inicial:").pack(anchor="w")
        self.entry_abono = ttk.Entry(marco)
        self.entry_abono.pack(fill="x", pady=5)

        ttk.Button(marco, text="📝 Reservar", command=self._reservar).pack(
            fill="x", pady=10
        )
        ttk.Separator(marco).pack(fill="x", pady=10)
        ttk.Button(marco, text="💰 Hacer otro abono", command=self._abrir_abono).pack(
            fill="x"
        )
        ttk.Button(marco, text="Cerrar sesión", command=self._logout).pack(
            fill="x", pady=(20, 0)
        )

    def _cargar_datos(self) -> None:
        consulta_vehiculos = (
            "SELECT v.placa, ma.nombre_marca, v.modelo, tv.tarifa_dia "
            "FROM Vehiculo v "
            "JOIN Marca_vehiculo ma ON v.id_marca=ma.id_marca "
            "JOIN Tipo_vehiculo tv ON v.id_tipo_vehiculo=tv.id_tipo "
            "JOIN Estado_vehiculo ev ON v.id_estado_vehiculo=ev.id_estado "
            "WHERE LOWER(ev.descripcion)='disponible'"
        )
        try:
            filas = self.conexion.ejecutar(consulta_vehiculos)
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar vehículos:\n{exc}")
            filas = []
        self.vehiculos_info: dict[str, tuple[str, float]] = {}
        opciones = []
        for placa, marca, modelo, tarifa in filas:
            texto = f"{placa} - {marca} {modelo}"
            opciones.append(texto)
            self.vehiculos_info[texto] = (placa, float(tarifa))
        self.combo_vehiculo["values"] = opciones

        try:
            medios = self.conexion.ejecutar("SELECT id_medio_pago, descripcion FROM Medio_pago")
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar medios de pago:\n{exc}")
            medios = []
        self.medios_info: dict[str, int] = {}
        self.combo_medio["values"] = [desc for _id, desc in medios]
        for _id, desc in medios:
            self.medios_info[desc] = int(_id)

    # ----------------------------
    def _validar_fechas(self, ini: str, fin: str) -> tuple[datetime, datetime] | None:
        try:
            fecha_ini = datetime.strptime(ini, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fin, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fechas incorrecto")
            return None
        if fecha_fin < fecha_ini:
            messagebox.showerror(
                "Error", "La fecha de fin debe ser posterior a la de inicio"
            )
            return None
        return fecha_ini, fecha_fin

    def _reservar(self) -> None:
        vehiculo = self.combo_vehiculo.get()
        medio = self.combo_medio.get()
        abono = self.entry_abono.get().strip()
        if not vehiculo or not medio or not abono:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        fechas = self._validar_fechas(self.entry_inicio.get().strip(), self.entry_fin.get().strip())
        if fechas is None:
            return
        fecha_ini, fecha_fin = fechas
        try:
            abono_val = float(abono)
        except ValueError:
            messagebox.showerror("Error", "El abono debe ser numérico")
            return

        placa, tarifa = self.vehiculos_info.get(vehiculo, (None, 0))
        if not placa:
            messagebox.showerror("Error", "Vehículo inválido")
            return
        dias = (fecha_fin - fecha_ini).days + 1
        total_pago = dias * tarifa
        restante = total_pago
        if abono_val < restante * 0.3:
            messagebox.showerror(
                "Error", "Cada abono debe ser mínimo el 30% del valor restante"
            )
            return
        restante -= abono_val
        query_reserva = (
            "INSERT INTO reserva "
            "(id_cliente, id_vehiculo, fecha_inicio, fecha_fin, fecha_reserva, estado_reserva, medio_pago, total_pago) "
            "VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s)"
        )
        query_abono = (
            "INSERT INTO abono_reserva (id_reserva, monto_abono, fecha_abono, medio_pago) "
            "VALUES (LAST_INSERT_ID(), %s, NOW(), %s)"
        )
        try:
            self.conexion.ejecutar(
                query_reserva,
                (
                    self.id_cliente,
                    placa,
                    fecha_ini.strftime("%Y-%m-%d"),
                    fecha_fin.strftime("%Y-%m-%d"),
                    "pendiente",
                    self.medios_info[medio],
                    total_pago,
                ),
            )
            self.conexion.ejecutar(
                query_abono,
                (
                    abono_val,
                    self.medios_info[medio],
                ),
            )
            messagebox.showinfo("Éxito", "Reserva registrada correctamente")
            self.entry_abono.delete(0, tk.END)
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror("Error", f"No se pudo registrar la reserva:\n{exc}")

    # ----------------------------
    def _abrir_abono(self) -> None:
        VentanaAbono(self, self.id_cliente, self.conexion, self.medios_info)

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()


class VentanaAbono(tk.Toplevel):
    """Ventana para registrar abonos adicionales."""

    def __init__(self, master: tk.Misc, id_cliente: int, conexion: ConexionBD, medios: dict[str, int]) -> None:
        super().__init__(master)
        self.title("💰 Registrar abono")
        self.configure(bg="#f4f6f9")
        self.geometry("420x300")
        self.id_cliente = id_cliente
        self.conexion = conexion
        self.medios = medios
        self._configurar_estilo()
        self._build_ui()
        self._cargar_reservas()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("arc")
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("TLabel", font=("Segoe UI", 11))

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=10)
        marco.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(marco, columns=("id", "restante"), show="headings")
        self.tree.heading("id", text="Reserva")
        self.tree.heading("restante", text="Saldo restante")
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("restante", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=5)

        ttk.Label(marco, text="Medio de pago:").pack(anchor="w")
        self.combo_medio = ttk.Combobox(marco, state="readonly")
        self.combo_medio.pack(fill="x", pady=5)
        self.combo_medio["values"] = list(self.medios.keys())

        ttk.Label(marco, text="Monto a abonar:").pack(anchor="w")
        self.entry_monto = ttk.Entry(marco)
        self.entry_monto.pack(fill="x", pady=5)

        ttk.Button(marco, text="Registrar abono", command=self._registrar).pack(pady=10)

    def _cargar_reservas(self) -> None:
        query = (
            "SELECT r.id_reserva, r.total_pago, "
            "COALESCE(SUM(a.monto_abono),0) AS pagado "
            "FROM reserva r "
            "LEFT JOIN abono_reserva a ON r.id_reserva=a.id_reserva "
            "WHERE r.id_cliente=%s AND r.estado_reserva='pendiente' "
            "GROUP BY r.id_reserva, r.total_pago"
        )
        try:
            filas = self.conexion.ejecutar(query, (self.id_cliente,))
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar reservas:\n{exc}")
            filas = []
        self.reservas_restante: dict[str, float] = {}
        self.tree.delete(*self.tree.get_children())
        for id_reserva, total, pagado in filas:
            restante = float(total) - float(pagado)
            self.tree.insert("", tk.END, values=(id_reserva, f"{restante:.2f}"))
            self.reservas_restante[str(id_reserva)] = restante

    def _registrar(self) -> None:
        seleccion = self.tree.focus()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione una reserva")
            return
        id_reserva = self.tree.item(seleccion)["values"][0]
        restante = self.reservas_restante.get(str(id_reserva), 0)
        monto_str = self.entry_monto.get().strip()
        medio = self.combo_medio.get()
        if not monto_str or not medio:
            messagebox.showerror("Error", "Debe ingresar el monto y medio de pago")
            return
        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
            return
        if monto < restante * 0.3:
            messagebox.showerror(
                "Error", "Cada abono debe ser mínimo el 30% del saldo restante"
            )
            return
        query = (
            "INSERT INTO abono_reserva (id_reserva, monto_abono, fecha_abono, medio_pago) "
            "VALUES (%s, %s, NOW(), %s)"
        )
        try:
            self.conexion.ejecutar(query, (id_reserva, monto, self.medios[medio]))
            messagebox.showinfo("Éxito", "Abono registrado")
            self.entry_monto.delete(0, tk.END)
            self._cargar_reservas()
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo registrar el abono:\n{exc}")

