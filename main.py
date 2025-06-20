from utils.logger import configurar_logging
from interfaces.login import VentanaLogin


def main() -> None:
    configurar_logging()
    app = VentanaLogin()
    app.mainloop()


if __name__ == '__main__':
    main()
