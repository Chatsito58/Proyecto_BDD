import re


def validar_correo(correo: str) -> bool:
    """Return True if correo has a basic valid email format."""
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, correo) is not None
