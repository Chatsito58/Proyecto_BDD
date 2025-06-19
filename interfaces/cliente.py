import tkinter as tk


class ClienteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Cliente')
        self.geometry('300x150')
        tk.Label(self, text='Bienvenido, cliente').pack(pady=10)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=20)

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
