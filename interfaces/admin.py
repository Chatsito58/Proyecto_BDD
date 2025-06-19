import tkinter as tk


class AdminApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Administrador')
        self.geometry('300x150')
        tk.Label(self, text='Panel de administrador').pack(pady=10)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=20)

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
