import tkinter as tk


class GerenteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Gerente')
        self.geometry('300x150')
        tk.Label(self, text='Panel de gerente').pack(pady=10)
        tk.Button(self, text='Cerrar sesión', command=self._logout).pack(pady=20)

    def _logout(self) -> None:
        self.destroy()
        from interfaces.login import LoginApp
        LoginApp().mainloop()
