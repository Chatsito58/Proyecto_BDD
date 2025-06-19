import tkinter as tk
from tkinter import messagebox


class ClienteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Cliente')
        self.geometry('320x200')
        tk.Label(self, text='Bienvenido, cliente').pack(pady=10)
        tk.Button(self, text='Reservar vehículo', command=self._reservar).pack(pady=5)
        tk.Button(self, text='Ver historial', command=self._historial).pack(pady=5)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=10)

    def _reservar(self) -> None:
        messagebox.showinfo('Reservar', 'Función de reserva no implementada')

    def _historial(self) -> None:
        messagebox.showinfo('Historial', 'Función de historial no implementada')

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
