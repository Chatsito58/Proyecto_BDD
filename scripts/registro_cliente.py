# ¡ATENCIÓN! No colocar claves reales aquí. Usa variables de entorno en producción.
from utils.logger import configurar_logging
from interfaces.registro_cliente import VentanaCrearCliente
import tkinter as tk


def main() -> None:
    configurar_logging()
    root = tk.Tk()
    root.withdraw()
    VentanaCrearCliente(root)
    root.mainloop()


if __name__ == "__main__":
    main()
