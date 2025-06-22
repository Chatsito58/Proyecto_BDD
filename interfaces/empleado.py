from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ttkthemes import ThemedTk

import logging

from conexion.conexion import ConexionBD
from interfaces.componentes.ctk_scrollable_combobox import CTkScrollableComboBox
from utils import cancel_pending_after, safe_bg_error_handler


class VentanaEmpleado(ThemedTk):
    def __init__(self) -> None:
        super().__init__(theme="arc")
        self.report_callback_exception = safe_bg_error_handler
        self._after_ids: list[str] = []
        self.title("🧑‍🔧 Panel del Empleado")
        self.configure(bg="#2a2a2a")
        self.geometry("340x260")
        self._subventanas: list[tk.Toplevel] = []
        self._configurar_estilo()
        self._build_ui()

    # ------------------------------------------------------------------
    def _registrar(self, win: tk.Toplevel) -> None:
        """Mantener referencia a ventanas hijas y asegurar su cierre."""
        self._subventanas.append(win)

        def _on_close() -> None:
            if win in self._subventanas:
                self._subventanas.remove(win)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("TLabel", font=("Segoe UI", 11))

    def _build_ui(self) -> None:
        marco = ttk.Frame(self, padding=20)
        marco.pack(expand=True)

        ttk.Label(
            marco, text="🧑‍🔧 Panel del Empleado", font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))
        ttk.Button(marco, text="Gestionar Reservas", command=self._abrir_reservas).pack(
            fill="x", pady=5
        )
        ttk.Button(marco, text="Gestionar Vehículos", command=self._vehiculos).pack(
            fill="x", pady=5
        )
        ttk.Button(marco, text="Cerrar sesión", command=self._logout).pack(
            fill="x", pady=(15, 0)
        )

    def _abrir_reservas(self) -> None:
        win = VentanaGestionReservas(self)
        self._registrar(win)

    def _vehiculos(self) -> None:
        win = VentanaVehiculos(self)
        self._registrar(win)

    def _logout(self) -> None:
        for win in list(self._subventanas):
            win.destroy()
        cancel_pending_after(self)
        self.quit()
        self.destroy()
        from interfaces.login import VentanaLogin

        VentanaLogin().mainloop()


class VentanaGestionReservas(tk.Toplevel):
    """Listado de reservas pendientes con acciones."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Reservas pendientes")
        self.geometry("760x400")
        self.conexion = ConexionBD()
        self._build_ui()
        self._cargar()

    def _build_ui(self) -> None:
        cols = ("id", "cliente", "entrada", "salida", "estado")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=10, padx=10)

        btns = ttk.Frame(self)
        btns.pack(pady=5)
        ttk.Button(btns, text="Aprobar", command=self._aprobar).pack(side="left", padx=5)
        ttk.Button(btns, text="Rechazar", command=self._rechazar).pack(side="left", padx=5)
        ttk.Button(btns, text="Abonos", command=self._abrir_abonos).pack(side="left", padx=5)

    def _cargar(self) -> None:
        query = (
            "SELECT r.id_reserva, c.nombre, r.fecha_hora_entrada, r.fecha_hora_salida, er.descripcion "
            "FROM Reserva_alquiler r "
            "JOIN Cliente c ON r.id_cliente=c.id_cliente "
            "JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
            "WHERE LOWER(er.descripcion) IN ('pendiente','reservado') "
            "ORDER BY r.fecha_hora_entrada"
        )
        try:
            filas = self.conexion.ejecutar(query)
        except Exception as exc:  # pragma: no cover - conexion errors vary
            logging.error("Error cargando reservas: %s", exc)
            messagebox.showerror("Error", f"No se pudieron cargar reservas:\n{exc}")
            filas = []
        self.tree.delete(*self.tree.get_children())
        for fila in filas:
            self.tree.insert("", tk.END, values=fila)

    def _aprobar(self) -> None:
        item = self.tree.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione una reserva")
            return
        id_reserva = self.tree.item(item)["values"][0]
        try:
            self.conexion.ejecutar(
                "UPDATE Reserva_alquiler SET id_estado_reserva=1 WHERE id_reserva=%s",
                (id_reserva,),
            )
            messagebox.showinfo("Éxito", "Reserva aprobada")
            self._cargar()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            logging.error("Error aprobando reserva: %s", exc)
            messagebox.showerror("Error", f"No se pudo aprobar:\n{exc}")

    def _rechazar(self) -> None:
        item = self.tree.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione una reserva")
            return
        id_reserva = self.tree.item(item)["values"][0]
        try:
            self.conexion.ejecutar(
                "UPDATE Reserva_alquiler SET id_estado_reserva=2 WHERE id_reserva=%s",
                (id_reserva,),
            )
            messagebox.showinfo("Éxito", "Reserva cancelada")
            self._cargar()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            logging.error("Error cancelando reserva: %s", exc)
            messagebox.showerror("Error", f"No se pudo cancelar:\n{exc}")

    def _abrir_abonos(self) -> None:
        item = self.tree.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione una reserva")
            return
        id_reserva = self.tree.item(item)["values"][0]
        VentanaAbonos(self, id_reserva, self.conexion)


class VentanaAbonos(tk.Toplevel):
    """Permite ver y modificar abonos de una reserva."""

    def __init__(self, master: tk.Misc, id_reserva: int, conexion: ConexionBD) -> None:
        super().__init__(master)
        self.title(f"Abonos reserva #{id_reserva}")
        self.geometry("500x320")
        self.id_reserva = id_reserva
        self.conexion = conexion
        self._build_ui()
        self._cargar()

    def _build_ui(self) -> None:
        self.tree = ttk.Treeview(self, columns=("id", "valor"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("valor", text="Valor")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("valor", anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        frm = ttk.Frame(self)
        frm.pack(pady=5)
        ttk.Label(frm, text="Nuevo valor:").grid(row=0, column=0, padx=5)
        self.entry_valor = ttk.Entry(frm)
        self.entry_valor.grid(row=0, column=1, padx=5)
        ttk.Button(frm, text="Actualizar", command=self._actualizar).grid(row=0, column=2, padx=5)

    def _cargar(self) -> None:
        try:
            filas = self.conexion.ejecutar(
                "SELECT id_abono_reserva, valor FROM Abono_reserva WHERE id_reserva=%s",
                (self.id_reserva,),
            )
        except Exception as exc:  # pragma: no cover - conexion errors vary
            logging.error("Error consultando abonos: %s", exc)
            messagebox.showerror("Error", f"No se pudieron obtener abonos:\n{exc}")
            filas = []
        self.tree.delete(*self.tree.get_children())
        for fila in filas:
            self.tree.insert("", tk.END, values=fila)

    def _actualizar(self) -> None:
        item = self.tree.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un abono")
            return
        abono_id = self.tree.item(item)["values"][0]
        valor_str = self.entry_valor.get().strip()
        try:
            valor = float(valor_str)
        except ValueError:
            messagebox.showerror("Error", "Valor inválido")
            return
        try:
            self.conexion.ejecutar(
                "UPDATE Abono_reserva SET valor=%s WHERE id_abono_reserva=%s",
                (valor, abono_id),
            )
            messagebox.showinfo("Éxito", "Abono actualizado")
            self._cargar()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            logging.error("Error actualizando abono: %s", exc)
            messagebox.showerror("Error", f"No se pudo actualizar:\n{exc}")


class VentanaVehiculos(tk.Toplevel):
    """Permite gestionar vehículos básicos."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Vehículos")
        self.geometry("600x400")
        self.conexion = ConexionBD()
        self._build_ui()
        self._cargar()

    def _build_ui(self) -> None:
        self.tree = ttk.Treeview(self, columns=("placa", "modelo"), show="headings")
        for c in ("placa", "modelo"):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btns = ttk.Frame(self)
        btns.pack(pady=5)
        ttk.Button(btns, text="Agregar", command=self._agregar).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self._eliminar).pack(side="left", padx=5)
        ttk.Button(btns, text="Actualizar", command=self._cargar).pack(side="left", padx=5)

    def _cargar(self) -> None:
        try:
            filas = self.conexion.ejecutar("SELECT placa, modelo FROM Vehiculo")
        except Exception as exc:  # pragma: no cover - conexion errors vary
            logging.error("Error cargando vehículos: %s", exc)
            messagebox.showerror("Error", f"No se pudieron cargar vehículos:\n{exc}")
            filas = []
        self.tree.delete(*self.tree.get_children())
        for fila in filas:
            self.tree.insert("", tk.END, values=fila)

    def _agregar(self) -> None:
        top = tk.Toplevel(self)
        top.title("Nuevo vehículo")
        ttk.Label(top, text="Placa:").grid(row=0, column=0, padx=5, pady=5)
        entry_placa = ttk.Entry(top)
        entry_placa.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(top, text="Modelo:").grid(row=1, column=0, padx=5, pady=5)
        entry_modelo = ttk.Entry(top)
        entry_modelo.grid(row=1, column=1, padx=5, pady=5)

        def guardar() -> None:
            placa = entry_placa.get().strip()
            modelo = entry_modelo.get().strip()
            if not placa or not modelo:
                messagebox.showerror("Error", "Debe ingresar placa y modelo")
                return
            try:
                self.conexion.ejecutar(
                    "INSERT INTO Vehiculo (placa, modelo) VALUES (%s, %s)",
                    (placa, modelo),
                )
                messagebox.showinfo("Éxito", "Vehículo registrado")
                top.destroy()
                self._cargar()
            except Exception as exc:  # pragma: no cover - conexion errors vary
                messagebox.showerror("Error", f"No se pudo registrar:\n{exc}")

        ttk.Button(top, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2, pady=10)

    def _eliminar(self) -> None:
        item = self.tree.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un vehículo")
            return
        placa = self.tree.item(item)["values"][0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar vehículo {placa}?"):
            return
        try:
            self.conexion.ejecutar("DELETE FROM Vehiculo WHERE placa=%s", (placa,))
            messagebox.showinfo("Éxito", "Vehículo eliminado")
            self._cargar()
        except Exception as exc:  # pragma: no cover - conexion errors vary
            messagebox.showerror("Error", f"No se pudo eliminar:\n{exc}")
