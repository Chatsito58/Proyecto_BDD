from __future__ import annotations

from typing import Optional

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash


def login(conexion: ConexionBD, correo: str, password: str) -> Optional[str]:
    """Verify credentials and return the user role if valid."""
    hashed = sha256_hash(password)
    q_cliente = (
        "SELECT 'cliente' FROM cliente WHERE correo=%s AND contrasena=%s"
    )
    q_empleado = (
        "SELECT te.nombre FROM empleado e "
        "JOIN tipo_empleado te ON e.id_tipo_empleado=te.id_tipo_empleado "
        "WHERE e.correo=%s AND e.contrasena=%s"
    )
    if conexion.ejecutar(q_cliente, (correo, hashed)):
        return 'cliente'
    res = conexion.ejecutar(q_empleado, (correo, hashed))
    if res:
        rol = str(res[0][0]).strip().lower()
        if correo.lower() == 'admin@admin.com':
            return 'admin'
        return rol
    return None
