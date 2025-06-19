import tkinter as tk
from ttkthemes import ThemedTk
from conexion.conexion import ConexionBD
from Consulta import MySQLApp


class AdminApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Administrador')
        self.geometry('320x200')
        tk.Label(self, text='Panel de administrador').pack(pady=10)
        tk.Button(self, text='Abrir consultas SQL', command=self._abrir_sql).pack(pady=5)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=10)

    def _abrir_sql(self) -> None:
        root = ThemedTk(theme='arc')
        MySQLApp(root, ConexionBD())
        root.mainloop()

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
