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
        self.geometry("460x560")
        self.id_cliente = id_cliente
        self.conexion = ConexionBD()
        self._configurar_estilo()
        self._build_ui()
        self._cargar_datos()
        self._calcular_total()

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
        self.combo_vehiculo.bind("<<ComboboxSelected>>", lambda _e: self._calcular_total())

        ttk.Label(marco, text="Fecha y hora inicio (YYYY-MM-DD HH:MM):").pack(anchor="w")
        self.entry_inicio = ttk.Entry(marco)
        self.entry_inicio.pack(fill="x", pady=5)
        self.entry_inicio.bind("<FocusOut>", lambda _e: self._calcular_total())

        ttk.Label(marco, text="Fecha y hora fin (YYYY-MM-DD HH:MM):").pack(anchor="w")
        self.entry_fin = ttk.Entry(marco)
        self.entry_fin.pack(fill="x", pady=5)
        self.entry_fin.bind("<FocusOut>", lambda _e: self._calcular_total())

        ttk.Label(marco, text="Medio de pago:").pack(anchor="w")
        self.combo_medio = ttk.Combobox(marco, state="readonly")
        self.combo_medio.pack(fill="x", pady=5)

        ttk.Label(marco, text="Abono inicial:").pack(anchor="w")
        self.entry_abono = ttk.Entry(marco)
        self.entry_abono.pack(fill="x", pady=5)

        self.lbl_total = ttk.Label(marco, text="Total: $0.00")
        self.lbl_total.pack(anchor="w", pady=(5, 0))
        ttk.Label(marco, text="Mínimo debe abonar 30%").pack(anchor="w")
        self.lbl_minimo = ttk.Label(marco, text="Abono mínimo: $0.00")
        self.lbl_minimo.pack(anchor="w")
        

        ttk.Button(marco, text="📝 Reservar", command=self._reservar).pack(
            fill="x", pady=10
        )
        ttk.Button(marco, text="📜 Historial de reservas", command=self._abrir_historial).pack(fill="x")
        ttk.Separator(marco).pack(fill="x", pady=10)
        ttk.Button(marco, text="💰 Hacer otro abono", command=self._abrir_abono).pack(
            fill="x"
        )
        ttk.Label(marco, text="Descuentos disponibles:").pack(anchor="w", pady=(10, 0))
        self.tree_desc = ttk.Treeview(marco, columns=("desc", "valor"), show="headings", height=4)
        self.tree_desc.heading("desc", text="Descripción")
        self.tree_desc.heading("valor", text="Valor")
        self.tree_desc.column("desc", width=200)
        self.tree_desc.column("valor", width=80, anchor="center")
        self.tree_desc.pack(fill="both", expand=False, pady=5)
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

        try:
            descuentos = self.conexion.ejecutar(
                "SELECT descripcion, valor FROM Descuento_alquiler"
            )
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar descuentos:\n{exc}")
            descuentos = []
        self.tree_desc.delete(*self.tree_desc.get_children())
        for desc, val in descuentos:
            self.tree_desc.insert("", tk.END, values=(desc, f"{val}%"))

    # ----------------------------
    def _validar_fechas(
        self, ini: str, fin: str, mostrar_error: bool = True
    ) -> tuple[datetime, datetime] | None:
        try:
            fecha_ini = datetime.strptime(ini, "%Y-%m-%d %H:%M")
            fecha_fin = datetime.strptime(fin, "%Y-%m-%d %H:%M")
        except ValueError:
            if mostrar_error:
                messagebox.showerror(
                    "Error", "Formato de fechas incorrecto (YYYY-MM-DD HH:MM)"
                )
            return None
        if fecha_fin < fecha_ini:
            if mostrar_error:
                messagebox.showerror(
                    "Error", "La fecha de fin debe ser posterior a la de inicio"
                )
            return None
        return fecha_ini, fecha_fin

    def _calcular_total(self) -> None:
        vehiculo = self.combo_vehiculo.get()
        fechas = self._validar_fechas(
            self.entry_inicio.get().strip(),
            self.entry_fin.get().strip(),
            mostrar_error=False,
        )
        if not vehiculo or fechas is None:
            self.lbl_total.config(text="Total: $0.00")
            self.lbl_minimo.config(text="Abono mínimo (30%): $0.00")
            return
        fecha_ini, fecha_fin = fechas
        _placa, tarifa = self.vehiculos_info.get(vehiculo, (None, 0))
        dias = (fecha_fin - fecha_ini).days + 1
        total = dias * tarifa
        self.lbl_total.config(text=f"Total: ${total:.2f}")
        self.lbl_minimo.config(text=f"Abono mínimo (30%): ${total*0.3:.2f}")

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
        restante = total_pago - abono_val
        query_reserva = (
            "INSERT INTO Reserva_alquiler "
            "(fecha_hora, fecha_hora_inicio, fecha_hora_fin, abono, "
            "saldo_pendiente, id_estado_reserva) "
            "VALUES (NOW(), %s, %s, %s, %s, %s)"
        )
        query_abono = (
            "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
            "VALUES (%s, NOW(), LAST_INSERT_ID(), %s)"
        )
        try:
            self.conexion.ejecutar(
                query_reserva,
                (
                    fecha_ini.strftime("%Y-%m-%d %H:%M:%S"),
                    fecha_fin.strftime("%Y-%m-%d %H:%M:%S"),
                    abono_val,
                    restante,
                    1,
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

    def _abrir_historial(self) -> None:
        ventana = tk.Toplevel(self)
        ventana.title("Historial de reservas")
        ventana.geometry("600x300")
        cols = ("id", "fecha", "total", "estado")
        tree = ttk.Treeview(ventana, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.capitalize())
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        query = (
            "SELECT id_reserva, fecha_hora, abono + saldo_pendiente AS total, id_estado_reserva "
            "FROM Reserva_alquiler"
        )
        try:
            filas = self.conexion.ejecutar(query)
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo obtener el historial:\n{exc}")
            filas = []
        for fila in filas:
            tree.insert("", tk.END, values=fila)

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
            "SELECT r.id_reserva, r.abono + r.saldo_pendiente AS total, "
            "COALESCE(SUM(a.valor),0) AS pagado "
            "FROM Reserva_alquiler r "
            "LEFT JOIN Abono_reserva a ON r.id_reserva=a.id_reserva "
            "GROUP BY r.id_reserva, r.abono, r.saldo_pendiente"
        )
        try:
            filas = self.conexion.ejecutar(query)
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
            "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
            "VALUES (%s, NOW(), %s, %s)"
        )
        try:
            self.conexion.ejecutar(query, (monto, id_reserva, self.medios[medio]))
            messagebox.showinfo("Éxito", "Abono registrado")
            self.entry_monto.delete(0, tk.END)
            self._cargar_reservas()
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo registrar el abono:\n{exc}")

