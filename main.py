from utils.logger import configurar_logging
from interfaces.login import LoginApp


def main() -> None:
    configurar_logging()
    app = LoginApp()
    app.mainloop()


if __name__ == '__main__':
    main()
