from __future__ import annotations

import tkinter as tk
from datetime import datetime

import customtkinter as ctk
from tkcalendar import Calendar
from interfaces.componentes.ctk_scrollable_combobox import CTkScrollableComboBox


class SelectorFechaHora(ctk.CTkFrame):
    """Componente para seleccionar fecha y hora."""

    def __init__(self, master: tk.Misc | None = None, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))

        self.entry = ctk.CTkEntry(self, textvariable=self.var)
        self.entry.pack(side="left", fill="x", expand=True)

        self.btn_open = ctk.CTkButton(
            self, text="\U0001f4c5", width=40, command=self._abrir
        )
        self.btn_open.pack(side="left", padx=(5, 0))

        self._top: ctk.CTkToplevel | None = None

    # ------------------------------------------------------------------
    def _abrir(self) -> None:
        if self._top and self._top.winfo_exists():
            self._top.focus_set()
            return

        self._top = ctk.CTkToplevel(self)
        self._top.title("Seleccionar fecha y hora")
        self._top.resizable(False, False)

        try:
            current = datetime.strptime(self.var.get(), "%Y-%m-%d %H:%M")
        except ValueError:
            current = datetime.now()

        self.cal = Calendar(self._top, selectmode="day", date_pattern="yyyy-mm-dd")
        self.cal.pack(padx=10, pady=10)
        self.cal.selection_set(current.date())

        # actualizar entrada al seleccionar una fecha
        self.cal.bind("<<CalendarSelected>>", lambda _e: self._actualizar())

        frame_hora = ctk.CTkFrame(self._top, fg_color="transparent")
        frame_hora.pack(pady=(0, 10))

        horas = [f"{h:02d}" for h in range(24)]
        minutos = [f"{m:02d}" for m in range(60)]
        self.combo_hora = CTkScrollableComboBox(frame_hora, values=horas, width=60)
        self.combo_hora.pack(side="left", padx=(0, 5))
        self.combo_hora.set(f"{current.hour:02d}")
        self.combo_hora.bind("<<ComboboxSelected>>", lambda _e: self._actualizar())
        self.combo_minuto = CTkScrollableComboBox(frame_hora, values=minutos, width=60)
        self.combo_minuto.pack(side="left")
        self.combo_minuto.set(f"{current.minute:02d}")
        self.combo_minuto.bind("<<ComboboxSelected>>", lambda _e: self._actualizar())

        ctk.CTkButton(self._top, text="Aceptar", command=self._confirmar).pack(
            pady=(0, 10)
        )

    def _confirmar(self) -> None:
        self._actualizar()
        if self._top:
            self._top.destroy()
            self._top = None

    # ------------------------------------------------------------------
    def _actualizar(self) -> None:
        """Actualizar la variable con la fecha y hora seleccionadas."""
        fecha = self.cal.selection_get()
        hora = int(self.combo_hora.get())
        minuto = int(self.combo_minuto.get())
        seleccionado = datetime(fecha.year, fecha.month, fecha.day, hora, minuto)
        self.var.set(seleccionado.strftime("%Y-%m-%d %H:%M"))

    # ------------------------------------------------------------------
    def obtener_datetime(self) -> datetime:
        try:
            return datetime.strptime(self.var.get(), "%Y-%m-%d %H:%M")
        except ValueError:
            return datetime.now()

    def get(self) -> str:
        """Devolver la fecha y hora seleccionadas como cadena."""
        return self.var.get()

    # Alias para compatibilidad
    def get_date(self) -> datetime:
        """Devolver la fecha y hora seleccionadas."""
        return self.obtener_datetime()
