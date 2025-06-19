import tkinter as tk
from tkinter import messagebox


class GerenteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Gerente')
        self.geometry('320x200')
        tk.Label(self, text='Panel de gerente').pack(pady=10)
        tk.Button(self, text='Ver reportes', command=self._reportes).pack(pady=5)
        tk.Button(self, text='Gestionar empleados', command=self._empleados).pack(pady=5)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=10)

    def _reportes(self) -> None:
        messagebox.showinfo('Reportes', 'Función no implementada')

    def _empleados(self) -> None:
        messagebox.showinfo('Empleados', 'Función no implementada')

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
