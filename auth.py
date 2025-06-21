from __future__ import annotations

from typing import Optional

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash


def hash_password(password: str) -> str:
    """Return the SHA256 hash of the given password."""
    return sha256_hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Return True if the password matches the stored hash."""
    return sha256_hash(password) == hash_guardado


def login(conexion: ConexionBD, correo: str, password: str) -> Optional[str]:
    """Verify credentials and return the user role if valid."""
    hashed = hash_password(password)
    q_cliente = (
        "SELECT 'Cliente' FROM Cliente WHERE correo=%s AND contrasena=%s"
    )
    q_empleado = (
        "SELECT te.nombre FROM Empleado e "
        "JOIN tipo_empleado te ON e.id_tipo_empleado=te.id_tipo_empleado "
        "WHERE e.correo=%s AND e.contrasena=%s"
    )
    if conexion.ejecutar(q_cliente, (correo, hashed)):
        return 'Cliente'
    res = conexion.ejecutar(q_empleado, (correo, hashed))
    if res:
        rol = str(res[0][0]).strip().lower()
        if correo.lower() == 'admin@admin.com':
            return 'admin'
        return rol
    return None


def login_usuario(correo: str, contrasena: str) -> Optional[str]:
    """Connect to the DB and validate the given credentials."""
    conexion = ConexionBD()
    return login(conexion, correo, contrasena)
