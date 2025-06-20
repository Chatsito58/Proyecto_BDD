from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
import calendar
from ttkthemes import ThemedTk

from conexion.conexion import ConexionBD


class SimpleDateEntry(ttk.Frame):
    """Selector de fecha simple sin dependencias externas"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.date_var = tk.StringVar()
        self.date_var.set(date.today().strftime("%Y-%m-%d"))
        
        # Entry para mostrar la fecha
        self.entry = ttk.Entry(self, textvariable=self.date_var, width=12, font=("Segoe UI", 10))
        self.entry.pack(side="left", padx=(0, 5))
        
        # Botón para abrir calendario
        self.btn_calendar = ttk.Button(self, text="📅", width=3, command=self._open_calendar)
        self.btn_calendar.pack(side="left")
        
    def _open_calendar(self):
        """Abre una ventana simple de calendario"""
        cal_window = tk.Toplevel(self)
        cal_window.title("Seleccionar Fecha")
        cal_window.geometry("300x200")
        cal_window.resizable(False, False)
        cal_window.grab_set()  # Modal
        
        # Variables para el calendario
        today = date.today()
        self.cal_year = tk.IntVar(value=today.year)
        self.cal_month = tk.IntVar(value=today.month)
        
        # Frame para controles
        control_frame = ttk.Frame(cal_window)
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text="◀", command=lambda: self._change_month(-1)).pack(side="left")
        self.month_label = ttk.Label(control_frame, text="", font=("Segoe UI", 12, "bold"))
        self.month_label.pack(side="left", padx=20)
        ttk.Button(control_frame, text="▶", command=lambda: self._change_month(1)).pack(side="left")
        
        # Frame para días
        self.days_frame = ttk.Frame(cal_window)
        self.days_frame.pack(pady=10)
        
        self._update_calendar()
        
        def _change_month(self, delta):
            new_month = self.cal_month.get() + delta
            if new_month > 12:
                new_month = 1
                self.cal_year.set(self.cal_year.get() + 1)
            elif new_month < 1:
                new_month = 12
                self.cal_year.set(self.cal_year.get() - 1)
            self.cal_month.set(new_month)
            self._update_calendar()
        
        self._change_month = _change_month
        
    def _update_calendar(self):
        # Limpiar frame
        for widget in self.days_frame.winfo_children():
            widget.destroy()
            
        year = self.cal_year.get()
        month = self.cal_month.get()
        
        # Actualizar label del mes
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.month_label.config(text=f"{month_names[month]} {year}")
        
        # Crear calendario
        cal = calendar.monthcalendar(year, month)
        
        # Headers de días
        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, day in enumerate(days):
            ttk.Label(self.days_frame, text=day, font=("Segoe UI", 9, "bold")).grid(row=0, column=i, padx=2, pady=2)
        
        # Días del mes
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                btn = ttk.Button(
                    self.days_frame, 
                    text=str(day), 
                    width=3,
                    command=lambda d=day: self._select_date(d)
                )
                btn.grid(row=week_num+1, column=day_num, padx=1, pady=1)
    
    def _select_date(self, day):
        selected_date = date(self.cal_year.get(), self.cal_month.get(), day)
        self.date_var.set(selected_date.strftime("%Y-%m-%d"))
        # Cerrar ventana del calendario
        for widget in self.winfo_toplevel().winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.title() == "Seleccionar Fecha":
                widget.destroy()
                break
    
    def get_date(self):
        """Devuelve la fecha seleccionada como objeto date"""
        try:
            return datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
        except:
            return date.today()


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
        estilo.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
        estilo.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#666666")

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=20)
        marco.pack(expand=True)

        ttk.Label(marco, text="👤 Panel del Cliente", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        ttk.Button(marco, text="🚗 Nueva Reserva", command=self._reservar).pack(fill="x", pady=5)
        ttk.Button(marco, text="🚙 Vehículos disponibles", command=self._ver_vehiculos).pack(fill="x", pady=5)
        ttk.Button(marco, text="💰 Tarifas/promociones", command=self._ver_tarifas).pack(fill="x", pady=5)
        ttk.Button(marco, text="🚪 Cerrar sesión", command=self._logout).pack(fill="x", pady=(15, 0))

    def _crear_selector_tiempo(self, parent, label_text: str, row: int) -> tuple:
        """Crea un selector de fecha y hora más amigable"""
        # Frame contenedor
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Label principal
        ttk.Label(frame, text=label_text, style="Title.TLabel").pack(anchor="w")
        
        # Frame para fecha y hora
        datetime_frame = ttk.Frame(frame)
        datetime_frame.pack(fill="x", pady=(5, 0))
        
        # Selector de fecha
        fecha_frame = ttk.LabelFrame(datetime_frame, text="📅 Fecha", padding=5)
        fecha_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        date_entry = SimpleDateEntry(fecha_frame)
        date_entry.pack(fill="x")
        
        # Selector de hora
        hora_frame = ttk.LabelFrame(datetime_frame, text="🕐 Hora", padding=5)
        hora_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        time_frame = ttk.Frame(hora_frame)
        time_frame.pack(fill="x")
        
        # Spinbox para horas (0-23)
        hour_var = tk.StringVar(value="08")
        hour_spinbox = ttk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            width=3,
            textvariable=hour_var,
            format="%02.0f",
            font=("Segoe UI", 10)
        )
        hour_spinbox.pack(side="left", padx=(0, 2))
        
        ttk.Label(time_frame, text=":").pack(side="left")
        
        # Spinbox para minutos (0-59, incrementos de 15)
        minute_var = tk.StringVar(value="00")
        minute_spinbox = ttk.Spinbox(
            time_frame,
            values=["00", "15", "30", "45"],
            width=3,
            textvariable=minute_var,
            font=("Segoe UI", 10)
        )
        minute_spinbox.pack(side="left", padx=(2, 0))
        
        return date_entry, hour_var, minute_var

    def _crear_campo_numerico(self, parent, label_text: str, placeholder: str, row: int) -> ttk.Entry:
        """Crea un campo numérico con mejor diseño"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Label(frame, text=label_text, style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=placeholder, style="Subtitle.TLabel").pack(anchor="w")
        
        entry = ttk.Entry(frame, font=("Segoe UI", 11))
        entry.pack(fill="x", pady=(5, 0))
        
        # Validación para solo números y punto decimal
        def validar_numero(char):
            return char.isdigit() or char == "." or char == ""
        
        vcmd = (parent.register(validar_numero), '%S')
        entry.config(validate='key', validatecommand=vcmd)
        
        return entry

    def _reservar(self) -> None:
        ventana = tk.Toplevel(self)
        ventana.title("🚗 Nueva Reserva")
        ventana.configure(bg="#f4f6f9")
        ventana.geometry("500x600")
        ventana.resizable(False, False)
        
        # Frame principal con scroll
        main_frame = ttk.Frame(ventana, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(
            titulo_frame, 
            text="🚗 Nueva Reserva", 
            font=("Segoe UI", 16, "bold")
        ).pack()
        
        ttk.Label(
            titulo_frame, 
            text="Complete los siguientes datos para realizar su reserva", 
            style="Subtitle.TLabel"
        ).pack(pady=(5, 0))
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        
        # Selectores de fecha y hora
        date_inicio, hour_inicio, minute_inicio = self._crear_selector_tiempo(
            main_frame, "🚀 Fecha y hora de inicio", 1
        )
        
        date_fin, hour_fin, minute_fin = self._crear_selector_tiempo(
            main_frame, "🏁 Fecha y hora de finalización", 2
        )
        
        # Campos numéricos
        entry_abono = self._crear_campo_numerico(
            main_frame, "💰 Abono inicial", "Ingrese el monto del abono (ej: 50000)", 3
        )
        
        entry_saldo = self._crear_campo_numerico(
            main_frame, "💳 Saldo pendiente", "Ingrese el saldo restante (ej: 150000)", 4
        )
        
        # Información adicional
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información", padding=10)
        info_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=20)
        
        info_text = (
            "• El abono mínimo es del 30% del valor total\n"
            "• La reserva se confirmará automáticamente\n"
            "• Recibirá un correo de confirmación"
        )
        ttk.Label(info_frame, text=info_text, style="Subtitle.TLabel").pack(anchor="w")

        def registrar() -> None:
            # Obtener valores de fecha y hora
            try:
                fecha_inicio_obj = date_inicio.get_date()
                hora_inicio_str = f"{hour_inicio.get().zfill(2)}:{minute_inicio.get().zfill(2)}"
                fecha_ini = datetime.combine(fecha_inicio_obj, datetime.strptime(hora_inicio_str, "%H:%M").time())
                
                fecha_fin_obj = date_fin.get_date()
                hora_fin_str = f"{hour_fin.get().zfill(2)}:{minute_fin.get().zfill(2)}"
                fecha_fin_dt = datetime.combine(fecha_fin_obj, datetime.strptime(hora_fin_str, "%H:%M").time())
            except Exception:
                messagebox.showerror("Error", "Error al procesar las fechas y horas seleccionadas")
                return
            
            # Validar campos numéricos
            abono = entry_abono.get().strip()
            saldo = entry_saldo.get().strip()
            
            if not abono or not saldo:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Validar fechas
            if fecha_fin_dt <= fecha_ini:
                messagebox.showerror(
                    "Error", "La fecha de finalización debe ser posterior a la de inicio"
                )
                return
            
            # Validar que la fecha de inicio no sea en el pasado
            if fecha_ini <= datetime.now():
                messagebox.showerror(
                    "Error", "La fecha de inicio debe ser futura"
                )
                return
            
            try:
                abono_val = float(abono)
                saldo_val = float(saldo)
                
                if abono_val < 0 or saldo_val < 0:
                    raise ValueError("Los valores no pueden ser negativos")
                    
            except ValueError:
                messagebox.showerror("Error", "Los valores monetarios deben ser números válidos y positivos")
                return
            
            # Insertar en base de datos (manteniendo la lógica original)
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
                        fecha_fin_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        abono_val,
                        saldo_val,
                        1,  # Estado 'Reservado'
                    ),
                )
                messagebox.showinfo(
                    "✅ Reserva Exitosa", 
                    f"Reserva registrada correctamente\n\n"
                    f"📅 Desde: {fecha_ini.strftime('%d/%m/%Y %H:%M')}\n"
                    f"📅 Hasta: {fecha_fin_dt.strftime('%d/%m/%Y %H:%M')}\n"
                    f"💰 Abono: ${abono_val:,.0f}\n"
                    f"💳 Saldo: ${saldo_val:,.0f}"
                )
                ventana.destroy()
            except Exception as exc:  # pragma: no cover - depende de la BD
                messagebox.showerror(
                    "Error", f"No se pudo registrar la reserva:\n{exc}"
                )

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame, 
            text="✅ Confirmar Reserva", 
            command=registrar,
            style="TButton"
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="❌ Cancelar", 
            command=ventana.destroy
        ).pack(side="left")

    def _ver_vehiculos(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT placa, modelo FROM Vehiculo")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudieron obtener los vehículos:\n{exc}")
            return
        self._mostrar_resultados("🚗 Vehículos disponibles", ["Placa", "Modelo"], filas)

    def _ver_tarifas(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT descripcion, valor FROM Descuento_alquiler")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudieron obtener las tarifas:\n{exc}")
            return
        self._mostrar_resultados("💰 Tarifas y promociones", ["Descripción", "Valor"], filas)

    def _mostrar_resultados(self, titulo: str, columnas: list[str], filas: list[tuple]) -> None:
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.configure(bg="#f4f6f9")
        ventana.geometry("600x400")
        
        # Frame principal
        main_frame = ttk.Frame(ventana, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(main_frame, text=titulo, font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        
        # Treeview con estilo mejorado
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=15)
        
        # Configurar columnas
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=200)
        
        # Insertar datos
        for i, fila in enumerate(filas):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=fila, tags=(tag,))
        
        # Configurar colores alternos
        tree.tag_configure("even", background="#f8f9fa")
        tree.tag_configure("odd", background="white")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elementos
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=ventana.destroy).pack(pady=(15, 0))

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()