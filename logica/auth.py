from typing import Optional

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash


class Autenticador:
    """Gestor de autenticación y obtención de roles."""

    def __init__(self) -> None:
        self.conexion = ConexionBD()

    def autenticar(self, correo: str, password: str) -> Optional[str]:
        """Return role name if credentials are valid."""
        consulta_cliente = (
            "SELECT 'cliente' FROM clientes WHERE correo=%s AND contrasena=%s"
        )
        consulta_empleado = (
            "SELECT te.nombre FROM empleados e "
            "JOIN tipo_empleado te ON e.tipo_empleado_id=te.id "
            "WHERE e.correo=%s AND e.contrasena=%s"
        )
        hashed = sha256_hash(password)
        if self.conexion.ejecutar(consulta_cliente, (correo, hashed)):
            return 'cliente'
        resultado = self.conexion.ejecutar(consulta_empleado, (correo, hashed))
        if resultado:
            return resultado[0][0]
        return None
