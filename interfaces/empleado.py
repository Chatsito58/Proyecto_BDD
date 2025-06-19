import tkinter as tk
from tkinter import messagebox


class EmpleadoApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Empleado')
        self.geometry('320x200')
        tk.Label(self, text='Panel de empleado').pack(pady=10)
        tk.Button(self, text='Registrar alquiler', command=self._registrar).pack(pady=5)
        tk.Button(self, text='Gestionar vehículos', command=self._vehiculos).pack(pady=5)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=10)

    def _registrar(self) -> None:
        messagebox.showinfo('Registrar', 'Función no implementada')

    def _vehiculos(self) -> None:
        messagebox.showinfo('Vehículos', 'Función no implementada')

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
