import tkinter as tk
from tkinter import messagebox, ttk

from conexion.conexion import ConexionBD


class ClienteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Cliente')
        self.geometry('320x250')
        self.conexion = ConexionBD()

        tk.Label(self, text='Bienvenido, cliente').pack(pady=10)
        tk.Button(self, text='Reservar vehículo', command=self._reservar).pack(pady=5)
        tk.Button(self, text='Ver historial', command=self._historial).pack(pady=5)
        tk.Button(self, text='Vehículos disponibles', command=self._ver_vehiculos).pack(pady=5)
        tk.Button(self, text='Tarifas/promociones', command=self._ver_tarifas).pack(pady=5)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=10)

    def _reservar(self) -> None:
        messagebox.showinfo('Reservar', 'Función de reserva no implementada')

    def _historial(self) -> None:
        messagebox.showinfo('Historial', 'Función de historial no implementada')

    def _ver_vehiculos(self) -> None:
        try:
            filas = self.conexion.ejecutar(
                'SELECT placa, modelo FROM Vehiculo LIMIT 10'
            )
        except Exception as exc:
            messagebox.showerror('Error', f'No se pudieron obtener los vehículos:\n{exc}')
            return

        self._mostrar_resultados('Vehículos disponibles', ['Placa', 'Modelo'], filas)

    def _ver_tarifas(self) -> None:
        try:
            filas = self.conexion.ejecutar(
                'SELECT descripcion, valor FROM Descuento_alquiler'
            )
        except Exception as exc:
            messagebox.showerror('Error', f'No se pudieron obtener las tarifas:\n{exc}')
            return

        self._mostrar_resultados('Tarifas y promociones', ['Descripción', 'Valor'], filas)

    def _mostrar_resultados(self, titulo: str, columnas: list[str], filas: list[tuple]) -> None:
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.geometry('360x240')

        tree = ttk.Treeview(ventana, columns=columnas, show='headings')
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=150)

        for fila in filas:
            tree.insert('', tk.END, values=fila)

        tree.pack(expand=True, fill='both', padx=10, pady=10)

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
