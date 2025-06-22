from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import customtkinter as ctk

from conexion.conexion import ConexionBD
from interfaces.cliente import SimpleDateEntry
from interfaces.componentes.ctk_scrollable_combobox import CTkScrollableComboBox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VentanaGerente(ctk.CTk):
    """Panel principal para el rol de gerente."""

    def __init__(self) -> None:
        super().__init__()
        self.conexion = ConexionBD()
        self.title("\U0001f454 Panel del Gerente")
        self.geometry("900x600")
        self.configure(fg_color="#f4f6f9")
        self._build_ui()
        self._cargar_reservas()
        self._cargar_alquileres()
        self._cargar_reportes()
        self._cargar_empleados()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_reservas = self.tabview.add("Ver Reservas")
        self.tab_alquileres = self.tabview.add("Ver Alquileres")
        self.tab_reportes = self.tabview.add("Reportes")
        self.tab_empleados = self.tabview.add("Gestión de empleados")

        self._build_tab_reservas()
        self._build_tab_alquileres()
        self._build_tab_reportes()
        self._build_tab_empleados()

        ctk.CTkButton(self, text="\U0001f6aa Cerrar sesión", command=self._logout).pack(
            pady=(0, 10)
        )

    # ------------------------------------------------------------------
    # RESERVAS
    def _build_tab_reservas(self) -> None:
        frame = ctk.CTkFrame(self.tab_reservas, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        filtros = ctk.CTkFrame(frame, fg_color="transparent")
        filtros.pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(filtros, text="Desde:").grid(row=0, column=0, padx=5)
        self.desde_res = SimpleDateEntry(filtros)
        self.desde_res.grid(row=0, column=1)
        ctk.CTkLabel(filtros, text="Hasta:").grid(row=0, column=2, padx=5)
        self.hasta_res = SimpleDateEntry(filtros)
        self.hasta_res.grid(row=0, column=3)
        ctk.CTkButton(filtros, text="Filtrar", command=self._cargar_reservas).grid(
            row=0, column=4, padx=5
        )

        cols = ("id", "cliente", "entrada", "salida", "estado", "abono", "saldo")
        self.tree_res = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tree_res.heading(c, text=c.capitalize())
            self.tree_res.column(c, anchor="center")
        self.tree_res.pack(fill="both", expand=True)

    def _cargar_reservas(self) -> None:
        query = (
            "SELECT r.id_reserva, c.nombre, r.fecha_hora_entrada, r.fecha_hora_salida, "
            "er.descripcion, r.abono, r.saldo_pendiente "
            "FROM Reserva_alquiler r "
            "JOIN Cliente c ON r.id_cliente=c.id_cliente "
            "JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
        )
        params: tuple[str, str] | None = None
        desde = self.desde_res.get_date()
        hasta = self.hasta_res.get_date()
        if isinstance(desde, date) and isinstance(hasta, date):
            query += "WHERE DATE(r.fecha_hora_entrada) BETWEEN %s AND %s "
            params = (desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d"))
        query += "ORDER BY r.fecha_hora_entrada DESC"
        try:
            filas = self.conexion.ejecutar(query, params)
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror(
                "Error", f"No se pudieron obtener las reservas:\n{exc}"
            )
            filas = []
        self.tree_res.delete(*self.tree_res.get_children())
        for fila in filas:
            self.tree_res.insert("", tk.END, values=fila)

    # ------------------------------------------------------------------
    # ALQUILERES
    def _build_tab_alquileres(self) -> None:
        frame = ctk.CTkFrame(self.tab_alquileres, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "cliente", "vehiculo", "salida", "entrada", "valor")
        self.tree_alq = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tree_alq.heading(c, text=c.capitalize())
            self.tree_alq.column(c, anchor="center")
        self.tree_alq.pack(fill="both", expand=True)

        ctk.CTkButton(frame, text="Actualizar", command=self._cargar_alquileres).pack(
            pady=5
        )

    def _cargar_alquileres(self) -> None:
        query = (
            "SELECT a.id_alquiler, c.nombre, a.id_vehiculo, a.fecha_hora_salida, "
            "a.fecha_hora_entrada, a.valor "
            "FROM Alquiler a JOIN Cliente c ON a.id_cliente=c.id_cliente "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        try:
            filas = self.conexion.ejecutar(query)
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror(
                "Error", f"No se pudieron obtener los alquileres:\n{exc}"
            )
            filas = []
        self.tree_alq.delete(*self.tree_alq.get_children())
        for fila in filas:
            self.tree_alq.insert("", tk.END, values=fila)

    # ------------------------------------------------------------------
    # REPORTES
    def _build_tab_reportes(self) -> None:
        frame = ctk.CTkFrame(self.tab_reportes, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        filtros = ctk.CTkFrame(frame, fg_color="transparent")
        filtros.pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(filtros, text="Desde:").grid(row=0, column=0, padx=5)
        self.desde_rep = SimpleDateEntry(filtros)
        self.desde_rep.grid(row=0, column=1)
        ctk.CTkLabel(filtros, text="Hasta:").grid(row=0, column=2, padx=5)
        self.hasta_rep = SimpleDateEntry(filtros)
        self.hasta_rep.grid(row=0, column=3)
        ctk.CTkLabel(filtros, text="Estado:").grid(row=0, column=4, padx=5)
        self.combo_estado = CTkScrollableComboBox(filtros, values=["", "reservado", "cancelado"])
        self.combo_estado.grid(row=0, column=5)
        ctk.CTkButton(filtros, text="Aplicar", command=self._cargar_reportes).grid(row=0, column=6, padx=5)

        self.lbl_ingresos = ctk.CTkLabel(frame, text="Ingresos del mes: $0")
        self.lbl_ingresos.pack(anchor="w")
        self.lbl_reservas = ctk.CTkLabel(frame, text="Reservas este mes: 0")
        self.lbl_reservas.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(frame, text="Vehículos más alquilados:").pack(anchor="w")
        self.tree_veh = ttk.Treeview(
            frame, columns=("vehiculo", "cant"), show="headings", height=5
        )
        self.tree_veh.heading("vehiculo", text="Vehículo")
        self.tree_veh.heading("cant", text="Cantidad")
        self.tree_veh.column("vehiculo", anchor="center")
        self.tree_veh.column("cant", anchor="center", width=80)
        self.tree_veh.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Clientes frecuentes:").pack(anchor="w", pady=(10, 0))
        self.tree_cli = ttk.Treeview(
            frame, columns=("cliente", "cant"), show="headings", height=5
        )
        self.tree_cli.heading("cliente", text="Cliente")
        self.tree_cli.heading("cant", text="Cantidad")
        self.tree_cli.column("cliente", anchor="center")
        self.tree_cli.column("cant", anchor="center", width=80)
        self.tree_cli.pack(fill="x", pady=5)

        ctk.CTkButton(frame, text="Actualizar", command=self._cargar_reportes).pack(
            pady=5
        )

    def _cargar_reportes(self) -> None:
        desde = self.desde_rep.get_date()
        hasta = self.hasta_rep.get_date()
        estado = self.combo_estado.get().strip().lower()

        q_ingresos = (
            "SELECT COALESCE(SUM(valor),0) FROM Alquiler "
            "WHERE DATE(fecha_hora_salida) BETWEEN %s AND %s"
        )
        q_reservas = (
            "SELECT COUNT(*) FROM Reserva_alquiler r "
            "JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
            "WHERE DATE(r.fecha_hora) BETWEEN %s AND %s"
        )
        params_res = [desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d")]
        if estado:
            q_reservas += " AND LOWER(er.descripcion)=%s"
            params_res.append(estado)

        q_veh = (
            "SELECT id_vehiculo, COUNT(*) AS c FROM Alquiler "
            "WHERE DATE(fecha_hora_salida) BETWEEN %s AND %s "
            "GROUP BY id_vehiculo ORDER BY c DESC LIMIT 5"
        )
        q_cli = (
            "SELECT c.nombre, COUNT(*) AS c FROM Reserva_alquiler r "
            "JOIN Cliente c ON r.id_cliente=c.id_cliente "
            "WHERE DATE(r.fecha_hora_salida) BETWEEN %s AND %s "
            "GROUP BY c.id_cliente, c.nombre ORDER BY c DESC LIMIT 5"
        )
        try:
            ingresos = self.conexion.ejecutar(
                q_ingresos, (desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d"))
            )[0][0]
            reservas = self.conexion.ejecutar(q_reservas, tuple(params_res))[0][0]
            vehiculos = self.conexion.ejecutar(
                q_veh,
                (desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d")),
            )
            clientes = self.conexion.ejecutar(
                q_cli,
                (desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d")),
            )
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror(
                "Error", f"No se pudieron generar los reportes:\n{exc}"
            )
            ingresos, reservas, vehiculos, clientes = 0, 0, [], []
        self.lbl_ingresos.configure(text=f"Ingresos del mes: ${float(ingresos):,.2f}")
        self.lbl_reservas.configure(text=f"Reservas este mes: {reservas}")
        self.tree_veh.delete(*self.tree_veh.get_children())
        for v in vehiculos:
            self.tree_veh.insert("", tk.END, values=v)
        self.tree_cli.delete(*self.tree_cli.get_children())
        for c in clientes:
            self.tree_cli.insert("", tk.END, values=c)

    # ------------------------------------------------------------------
    # EMPLEADOS
    def _build_tab_empleados(self) -> None:
        frame = ctk.CTkFrame(self.tab_empleados, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "nombre", "correo", "tipo")
        self.tree_emp = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tree_emp.heading(c, text=c.capitalize())
            self.tree_emp.column(c, anchor="center")
        self.tree_emp.pack(fill="both", expand=True, pady=5)

        controls = ctk.CTkFrame(frame, fg_color="transparent")
        controls.pack(anchor="w", pady=5)
        ctk.CTkLabel(controls, text="Tipo:").grid(row=0, column=0, padx=5)
        self.combo_tipo = CTkScrollableComboBox(controls, values=[])
        self.combo_tipo.grid(row=0, column=1, padx=5)
        ctk.CTkButton(controls, text="Cambiar tipo", command=self._cambiar_tipo).grid(
            row=0, column=2, padx=5
        )
        ctk.CTkButton(controls, text="Eliminar", command=self._eliminar_empleado).grid(
            row=0, column=3, padx=5
        )

    def _cargar_empleados(self) -> None:
        try:
            tipos = self.conexion.ejecutar(
                "SELECT id_tipo_empleado, nombre FROM Tipo_empleado"
            )
            self.tipo_map = {n: i for i, n in tipos}
            self.combo_tipo.configure(values=list(self.tipo_map.keys()))
            filas = self.conexion.ejecutar(
                "SELECT e.id_empleado, e.nombre, e.correo, te.nombre "
                "FROM Empleado e JOIN Tipo_empleado te ON e.id_tipo_empleado=te.id_tipo_empleado"
            )
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror(
                "Error", f"No se pudieron obtener los empleados:\n{exc}"
            )
            filas = []
            self.tipo_map = {}
        self.tree_emp.delete(*self.tree_emp.get_children())
        for fila in filas:
            self.tree_emp.insert("", tk.END, values=fila)

    def _cambiar_tipo(self) -> None:
        item = self.tree_emp.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un empleado")
            return
        id_emp, nombre, correo, tipo_act = self.tree_emp.item(item)["values"]
        if str(tipo_act).lower() == "admin":
            messagebox.showerror("Error", "No se puede modificar un usuario admin")
            return
        tipo_nuevo = self.combo_tipo.get()
        id_tipo = self.tipo_map.get(tipo_nuevo)
        if not id_tipo:
            messagebox.showerror("Error", "Seleccione un tipo válido")
            return
        try:
            self.conexion.ejecutar(
                "UPDATE Empleado SET id_tipo_empleado=%s WHERE id_empleado=%s",
                (id_tipo, id_emp),
            )
            messagebox.showinfo("Éxito", "Tipo actualizado")
            self._cargar_empleados()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror("Error", f"No se pudo actualizar:\n{exc}")

    def _eliminar_empleado(self) -> None:
        item = self.tree_emp.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un empleado")
            return
        id_emp, nombre, correo, tipo_act = self.tree_emp.item(item)["values"]
        if str(tipo_act).lower() == "admin":
            messagebox.showerror("Error", "No se puede eliminar un usuario admin")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar al empleado {nombre}?"):
            return
        try:
            self.conexion.ejecutar(
                "DELETE FROM Empleado WHERE id_empleado=%s", (id_emp,)
            )
            messagebox.showinfo("Éxito", "Empleado eliminado")
            self._cargar_empleados()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror("Error", f"No se pudo eliminar:\n{exc}")

    # ------------------------------------------------------------------
    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()
