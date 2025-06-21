from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
import calendar
import customtkinter as ctk

from interfaces.componentes.selector_fecha_hora import SelectorFechaHora

from conexion.conexion import ConexionBD


class SimpleDateEntry(ttk.Frame):
    """Selector de fecha simple sin dependencias externas"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        self.entry = ttk.Entry(self, textvariable=self.date_var, width=12, font=("Segoe UI", 10))
        self.entry.pack(side="left", padx=(0, 5))

        self.btn_calendar = ttk.Button(self, text="📅", width=3, command=self._open_calendar)
        self.btn_calendar.pack(side="left")

        self.cal_window: tk.Toplevel | None = None

    # ------------------------------------------------------------------
    def _open_calendar(self) -> None:
        if self.cal_window and self.cal_window.winfo_exists():
            self.cal_window.focus_set()
            return

        self.cal_window = tk.Toplevel(self)
        self.cal_window.title("Seleccionar Fecha")
        self.cal_window.resizable(False, False)

        today = date.today()
        self.cal_year = tk.IntVar(value=today.year)
        self.cal_month = tk.IntVar(value=today.month)

        control_frame = ttk.Frame(self.cal_window)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text="◀", command=lambda: self._change_month(-1)).pack(side="left")
        self.month_label = ttk.Label(control_frame, font=("Segoe UI", 12, "bold"))
        self.month_label.pack(side="left", padx=20)
        ttk.Button(control_frame, text="▶", command=lambda: self._change_month(1)).pack(side="left")

        self.days_frame = ttk.Frame(self.cal_window)
        self.days_frame.pack(pady=10)

        self._update_calendar()

        self.cal_window.update_idletasks()
        self.update_idletasks()
        w, h = 320, 250
        x = self.btn_calendar.winfo_rootx() + self.btn_calendar.winfo_width() // 2 - w // 2
        y = self.btn_calendar.winfo_rooty() + self.btn_calendar.winfo_height()
        self.cal_window.geometry(f"{w}x{h}+{x}+{y}")
        self.cal_window.grab_set()

    def _change_month(self, delta: int) -> None:
        new_month = self.cal_month.get() + delta
        if new_month > 12:
            new_month = 1
            self.cal_year.set(self.cal_year.get() + 1)
        elif new_month < 1:
            new_month = 12
            self.cal_year.set(self.cal_year.get() - 1)
        self.cal_month.set(new_month)
        self._update_calendar()

    def _update_calendar(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        year = self.cal_year.get()
        month = self.cal_month.get()

        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.month_label.config(text=f"{month_names[month]} {year}")

        cal = calendar.monthcalendar(year, month)

        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, day in enumerate(days):
            ttk.Label(self.days_frame, text=day, font=("Segoe UI", 9, "bold")).grid(row=0, column=i, padx=2, pady=2)

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                btn = ttk.Button(
                    self.days_frame,
                    text=str(day),
                    width=3,
                    command=lambda d=day: self._select_date(d),
                )
                btn.grid(row=week_num + 1, column=day_num, padx=1, pady=1)

    def _select_date(self, day):
        selected_date = date(self.cal_year.get(), self.cal_month.get(), day)
        self.date_var.set(selected_date.strftime("%Y-%m-%d"))
        if self.cal_window and self.cal_window.winfo_exists():
            self.cal_window.destroy()
            self.cal_window = None

    def get_date(self):
        try:
            return datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
        except Exception:
            return date.today()


class VentanaCliente(ctk.CTk):
    """Panel principal del cliente con pesta\u00f1as."""

    def __init__(self, id_cliente: int) -> None:
        super().__init__()
        self.id_cliente = id_cliente
        self.conexion = ConexionBD()
        self.title("\U0001F464 Panel del Cliente")
        self.geometry("760x560")
        self.configure(fg_color="#f4f6f9")
        self._build_ui()
        self._cargar_datos_reserva()
        self._cargar_descuentos()
        self._cargar_reservas_abono()
        self._cargar_historial_reservas()
        self._cargar_historial_alquileres()
        self._cargar_vehiculos()
        self._cargar_tarifas()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_reserva = self.tabview.add("Nueva reserva")
        self.tab_hist_res = self.tabview.add("Historial reservas")
        self.tab_hist_alq = self.tabview.add("Historial alquileres")
        self.tab_vehiculos = self.tabview.add("Veh\u00edculos disponibles")
        self.tab_tarifas = self.tabview.add("Tarifas")
        self.tab_abonos = self.tabview.add("Abonos")

        self._build_tab_reserva()
        self._build_tab_historial_reservas()
        self._build_tab_historial_alquileres()
        self._build_tab_vehiculos()
        self._build_tab_tarifas()
        self._build_tab_abonos()

        ctk.CTkButton(self, text="\U0001F6AA Cerrar sesi\u00f3n", command=self._logout).pack(pady=(0, 10))

    # ------------------------------------------------------------------
    # NUEVA RESERVA
    def _build_tab_reserva(self) -> None:
        frame = ctk.CTkFrame(self.tab_reserva, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame, text="\U0001F697 Crear nueva reserva", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Veh\u00edculo:").pack(anchor="w")
        self.combo_vehiculo = ctk.CTkComboBox(frame, values=[])
        self.combo_vehiculo.pack(fill="x", pady=5)
        self.combo_vehiculo.bind("<<ComboboxSelected>>", lambda _e: self._calcular_total())

        ctk.CTkLabel(frame, text="Inicio:").pack(anchor="w")
        self.selector_inicio = SelectorFechaHora(frame)
        self.selector_inicio.pack(fill="x", pady=5)
        self.selector_inicio.entry.bind("<FocusOut>", lambda _e: self._calcular_total())

        ctk.CTkLabel(frame, text="Fin:").pack(anchor="w")
        self.selector_fin = SelectorFechaHora(frame)
        self.selector_fin.pack(fill="x", pady=5)
        self.selector_fin.entry.bind("<FocusOut>", lambda _e: self._calcular_total())

        ctk.CTkLabel(frame, text="Medio de pago:").pack(anchor="w")
        self.combo_medio = ctk.CTkComboBox(frame, values=[])
        self.combo_medio.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Abono inicial:").pack(anchor="w")
        self.entry_abono = ctk.CTkEntry(frame)
        self.entry_abono.pack(fill="x", pady=5)

        self.lbl_total = ctk.CTkLabel(frame, text="Total: $0.00")
        self.lbl_total.pack(anchor="w", pady=(5, 0))
        ctk.CTkLabel(frame, text="M\u00ednimo debe abonar 30%").pack(anchor="w")
        self.lbl_minimo = ctk.CTkLabel(frame, text="Abono m\u00ednimo: $0.00")
        self.lbl_minimo.pack(anchor="w")

        ctk.CTkButton(frame, text="\U0001F4DD Reservar", command=self._registrar_reserva).pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="Descuentos disponibles:").pack(anchor="w", pady=(10, 0))
        self.tree_desc = ttk.Treeview(frame, columns=("desc", "valor"), show="headings", height=4)
        self.tree_desc.heading("desc", text="Descripci\u00f3n")
        self.tree_desc.heading("valor", text="Valor")
        self.tree_desc.column("desc", width=200)
        self.tree_desc.column("valor", width=80, anchor="center")
        self.tree_desc.pack(fill="both", expand=False, pady=5)

    def _cargar_datos_reserva(self) -> None:
        consulta = (
            "SELECT v.placa, ma.nombre_marca, v.modelo, tv.tarifa_dia "
            "FROM Vehiculo v "
            "JOIN Marca_vehiculo ma ON v.id_marca=ma.id_marca "
            "JOIN Tipo_vehiculo tv ON v.id_tipo_vehiculo=tv.id_tipo "
            "JOIN Estado_vehiculo ev ON v.id_estado_vehiculo=ev.id_estado "
            "WHERE LOWER(ev.descripcion)='disponible'"
        )
        try:
            filas = self.conexion.ejecutar(consulta)
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar veh\u00edculos:\n{exc}")
            filas = []
        self.vehiculos_info: dict[str, tuple[str, float]] = {}
        opciones = []
        for placa, marca, modelo, tarifa in filas:
            texto = f"{placa} - {marca} {modelo}"
            opciones.append(texto)
            self.vehiculos_info[texto] = (placa, float(tarifa))
        self.combo_vehiculo.configure(values=opciones)

        try:
            medios = self.conexion.ejecutar("SELECT id_medio_pago, descripcion FROM Medio_pago")
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar medios de pago:\n{exc}")
            medios = []
        self.medios_info: dict[str, int] = {}
        self.combo_medio.configure(values=[desc for _id, desc in medios])
        for _id, desc in medios:
            self.medios_info[desc] = int(_id)

    def _cargar_descuentos(self) -> None:
        try:
            descuentos = self.conexion.ejecutar("SELECT descripcion, valor FROM Descuento_alquiler")
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar descuentos:\n{exc}")
            descuentos = []
        self.tree_desc.delete(*self.tree_desc.get_children())
        for desc, val in descuentos:
            self.tree_desc.insert("", tk.END, values=(desc, f"{val}%"))

    def _validar_fechas(self, fecha_ini: datetime, fecha_fin: datetime, mostrar_error: bool = True) -> tuple[datetime, datetime] | None:
        if fecha_fin < fecha_ini:
            if mostrar_error:
                messagebox.showerror("Error", "La fecha de fin debe ser posterior a la de inicio")
            return None
        return fecha_ini, fecha_fin

    def _calcular_total(self) -> None:
        vehiculo = self.combo_vehiculo.get()
        fechas = self._validar_fechas(
            self.selector_inicio.obtener_datetime(),
            self.selector_fin.obtener_datetime(),
            mostrar_error=False,
        )
        if not vehiculo or fechas is None:
            self.lbl_total.configure(text="Total: $0.00")
            self.lbl_minimo.configure(text="Abono m\u00ednimo: $0.00")
            return
        fecha_ini, fecha_fin = fechas
        _placa, tarifa = self.vehiculos_info.get(vehiculo, (None, 0))
        dias = (fecha_fin - fecha_ini).days + 1
        total = dias * tarifa
        self.lbl_total.configure(text=f"Total: ${total:.2f}")
        self.lbl_minimo.configure(text=f"Abono m\u00ednimo: ${total*0.3:.2f}")

    def _registrar_reserva(self) -> None:
        vehiculo = self.combo_vehiculo.get()
        medio = self.combo_medio.get()
        abono = self.entry_abono.get().strip()
        if not vehiculo or not medio or not abono:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        fechas = self._validar_fechas(
            self.selector_inicio.obtener_datetime(),
            self.selector_fin.obtener_datetime(),
        )
        if fechas is None:
            return
        fecha_ini, fecha_fin = fechas
        try:
            abono_val = float(abono)
        except ValueError:
            messagebox.showerror("Error", "El abono debe ser num\u00e9rico")
            return
        placa, tarifa = self.vehiculos_info.get(vehiculo, (None, 0))
        if not placa:
            messagebox.showerror("Error", "Veh\u00edculo inv\u00e1lido")
            return
        dias = (fecha_fin - fecha_ini).days + 1
        total_pago = dias * tarifa
        restante = total_pago
        if abono_val < restante * 0.3:
            messagebox.showerror("Error", "Cada abono debe ser m\u00ednimo el 30% del valor restante")
            return
        restante = total_pago - abono_val
        q1 = (
            "INSERT INTO Reserva_alquiler "
            "(fecha_hora, fecha_hora_entrada, fecha_hora_salida, abono, saldo_pendiente, id_cliente, id_estado_reserva) "
            "VALUES (NOW(), %s, %s, %s, %s, %s, %s)"
        )
        q2 = (
            "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
            "VALUES (%s, NOW(), LAST_INSERT_ID(), %s)"
        )
        try:
            self.conexion.ejecutar(q1, (fecha_ini.strftime("%Y-%m-%d %H:%M:%S"), fecha_fin.strftime("%Y-%m-%d %H:%M:%S"), abono_val, restante, self.id_cliente, 1))
            self.conexion.ejecutar(q2, (abono_val, self.medios_info[medio]))
            messagebox.showinfo("\u00c9xito", "Reserva registrada correctamente")
            self.entry_abono.delete(0, tk.END)
            self._cargar_reservas_abono()
            self._cargar_historial_reservas()
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo registrar la reserva:\n{exc}")

    # ------------------------------------------------------------------
    # ABONOS
    def _build_tab_abonos(self) -> None:
        frame = ctk.CTkFrame(self.tab_abonos, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_abono = ttk.Treeview(frame, columns=("id", "restante"), show="headings")
        self.tree_abono.heading("id", text="Reserva")
        self.tree_abono.heading("restante", text="Saldo restante")
        self.tree_abono.column("id", width=80, anchor="center")
        self.tree_abono.column("restante", width=120, anchor="center")
        self.tree_abono.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(frame, text="Medio de pago:").pack(anchor="w")
        self.combo_abono_medio = ctk.CTkComboBox(frame, values=[])
        self.combo_abono_medio.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Monto a abonar:").pack(anchor="w")
        self.entry_abono_monto = ctk.CTkEntry(frame)
        self.entry_abono_monto.pack(fill="x", pady=5)

        ctk.CTkButton(frame, text="Registrar abono", command=self._registrar_abono).pack(pady=10)

    def _cargar_reservas_abono(self) -> None:
        query = (
            "SELECT r.id_reserva, r.abono + r.saldo_pendiente AS total, "
            "COALESCE(SUM(a.valor),0) AS pagado "
            "FROM Reserva_alquiler r "
            "LEFT JOIN Abono_reserva a ON r.id_reserva=a.id_reserva "
            "WHERE r.id_cliente=%s "
            "GROUP BY r.id_reserva, r.abono, r.saldo_pendiente"
        )
        try:
            filas = self.conexion.ejecutar(query, (self.id_cliente,))
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron cargar reservas:\n{exc}")
            filas = []
        self.reservas_restante: dict[str, float] = {}
        self.tree_abono.delete(*self.tree_abono.get_children())
        for id_reserva, total, pagado in filas:
            restante = float(total) - float(pagado)
            self.tree_abono.insert("", tk.END, values=(id_reserva, f"{restante:.2f}"))
            self.reservas_restante[str(id_reserva)] = restante
        self.combo_abono_medio.configure(values=list(self.medios_info.keys()))

    def _registrar_abono(self) -> None:
        seleccion = self.tree_abono.focus()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione una reserva")
            return
        id_reserva = self.tree_abono.item(seleccion)["values"][0]
        restante = self.reservas_restante.get(str(id_reserva), 0)
        monto_str = self.entry_abono_monto.get().strip()
        medio = self.combo_abono_medio.get()
        if not monto_str or not medio:
            messagebox.showerror("Error", "Debe ingresar el monto y medio de pago")
            return
        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "Monto inv\u00e1lido")
            return
        if monto < restante * 0.3:
            messagebox.showerror("Error", "Cada abono debe ser m\u00ednimo el 30% del saldo restante")
            return
        query = (
            "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
            "VALUES (%s, NOW(), %s, %s)"
        )
        try:
            self.conexion.ejecutar(query, (monto, id_reserva, self.medios_info[medio]))
            messagebox.showinfo("\u00c9xito", "Abono registrado")
            self.entry_abono_monto.delete(0, tk.END)
            self._cargar_reservas_abono()
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo registrar el abono:\n{exc}")

    # ------------------------------------------------------------------
    # HISTORIALES
    def _build_tab_historial_reservas(self) -> None:
        frame = ctk.CTkFrame(self.tab_hist_res, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_reservas = ttk.Treeview(frame, columns=("id", "salida", "total", "estado"), show="headings")
        for c in ("id", "salida", "total", "estado"):
            self.tree_reservas.heading(c, text=c.capitalize())
            self.tree_reservas.column(c, anchor="center")
        self.tree_reservas.pack(fill="both", expand=True, pady=5)

        ctk.CTkButton(frame, text="Cancelar reserva", command=self._cancelar_reserva).pack(pady=5)

    def _cargar_historial_reservas(self) -> None:
        query = (
            "SELECT r.id_reserva, r.fecha_hora_salida, "
            "r.abono + r.saldo_pendiente AS total, er.descripcion "
            "FROM Reserva_alquiler r "
            "JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
            "WHERE r.id_cliente=%s"
        )
        try:
            filas = self.conexion.ejecutar(query, (self.id_cliente,))
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo obtener el historial:\n{exc}")
            filas = []
        self.tree_reservas.delete(*self.tree_reservas.get_children())
        for fila in filas:
            self.tree_reservas.insert("", tk.END, values=fila)

    def _cancelar_reserva(self) -> None:
        item = self.tree_reservas.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione una reserva")
            return
        id_reserva, fecha_salida, *_rest = self.tree_reservas.item(item)["values"]
        fecha_dt = (
            fecha_salida if isinstance(fecha_salida, datetime) else datetime.strptime(str(fecha_salida), "%Y-%m-%d %H:%M:%S")
        )
        if fecha_dt <= datetime.now():
            messagebox.showerror("Error", "La reserva ya sucedi\u00f3 y no puede cancelarse")
            return
        if not messagebox.askyesno("Confirmar", "\u00bfCancelar la reserva seleccionada?"):
            return
        try:
            self.conexion.ejecutar("UPDATE Reserva_alquiler SET id_estado_reserva=2 WHERE id_reserva=%s", (id_reserva,))
            messagebox.showinfo("\u00c9xito", "Reserva cancelada")
            self._cargar_historial_reservas()
            self._cargar_reservas_abono()
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo cancelar:\n{exc}")

    def _build_tab_historial_alquileres(self) -> None:
        frame = ctk.CTkFrame(self.tab_hist_alq, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_alquileres = ttk.Treeview(frame, columns=("id", "salida", "valor", "estado"), show="headings")
        for c in ("id", "salida", "valor", "estado"):
            self.tree_alquileres.heading(c, text=c.capitalize())
            self.tree_alquileres.column(c, anchor="center")
        self.tree_alquileres.pack(fill="both", expand=True, pady=5)

        ctk.CTkButton(frame, text="Cancelar alquiler", command=self._cancelar_alquiler).pack(pady=5)

    def _cargar_historial_alquileres(self) -> None:
        query = (
            "SELECT a.id_alquiler, a.fecha_hora_salida, a.valor, ea.descripcion "
            "FROM Alquiler a "
            "JOIN Estado_alquiler ea ON a.id_estado=ea.id_estado "
            "WHERE a.id_cliente=%s "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        try:
            filas = self.conexion.ejecutar(query, (self.id_cliente,))
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo obtener el historial:\n{exc}")
            filas = []
        self.tree_alquileres.delete(*self.tree_alquileres.get_children())
        for fila in filas:
            self.tree_alquileres.insert("", tk.END, values=fila)

    def _cancelar_alquiler(self) -> None:
        item = self.tree_alquileres.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un alquiler")
            return
        id_alquiler, fecha_salida, *_rest = self.tree_alquileres.item(item)["values"]
        fecha_dt = (
            fecha_salida if isinstance(fecha_salida, datetime) else datetime.strptime(str(fecha_salida), "%Y-%m-%d %H:%M:%S")
        )
        if fecha_dt <= datetime.now():
            messagebox.showerror("Error", "Este alquiler ya inici\u00f3 y no puede cancelarse")
            return
        if not messagebox.askyesno("Confirmar", "\u00bfCancelar el alquiler seleccionado?"):
            return
        try:
            self.conexion.ejecutar("DELETE FROM Alquiler WHERE id_alquiler=%s", (id_alquiler,))
            messagebox.showinfo("\u00c9xito", "Alquiler cancelado")
            self._cargar_historial_alquileres()
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudo cancelar:\n{exc}")

    # ------------------------------------------------------------------
    # VEH\u00cdCULOS Y TARIFAS
    def _build_tab_vehiculos(self) -> None:
        frame = ctk.CTkFrame(self.tab_vehiculos, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_veh = ttk.Treeview(frame, columns=("placa", "modelo"), show="headings")
        for c in ("placa", "modelo"):
            self.tree_veh.heading(c, text=c.capitalize())
            self.tree_veh.column(c, anchor="center", width=200)
        self.tree_veh.pack(fill="both", expand=True, pady=5)

    def _cargar_vehiculos(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT placa, modelo FROM Vehiculo")
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron obtener los veh\u00edculos:\n{exc}")
            filas = []
        self.tree_veh.delete(*self.tree_veh.get_children())
        for fila in filas:
            self.tree_veh.insert("", tk.END, values=fila)

    def _build_tab_tarifas(self) -> None:
        frame = ctk.CTkFrame(self.tab_tarifas, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_tar = ttk.Treeview(frame, columns=("desc", "valor"), show="headings")
        for c in ("desc", "valor"):
            self.tree_tar.heading(c, text="Descripci\u00f3n" if c == "desc" else "Valor")
            self.tree_tar.column(c, anchor="center", width=200)
        self.tree_tar.pack(fill="both", expand=True, pady=5)

    def _cargar_tarifas(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT descripcion, valor FROM Descuento_alquiler")
        except Exception as exc:  # pragma: no cover - depende de la BD
            messagebox.showerror("Error", f"No se pudieron obtener las tarifas:\n{exc}")
            filas = []
        self.tree_tar.delete(*self.tree_tar.get_children())
        for fila in filas:
            self.tree_tar.insert("", tk.END, values=fila)

    # ------------------------------------------------------------------
    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()
