from __future__ import annotations

import json
import secrets
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash


class Autenticador:
    """Gestor de autenticación y obtención de roles."""

    def __init__(self) -> None:
        self.conexion = ConexionBD()

    def autenticar(self, correo: str, password: str) -> Optional[str]:
        """Return role name if credentials are valid."""
        consulta_cliente = (
            "SELECT 'cliente' FROM cliente WHERE correo=%s AND contrasena=%s"
        )
        consulta_empleado = (
            "SELECT te.nombre FROM empleado e "
            "JOIN tipo_empleado te ON e.id_tipo_empleado=te.id_tipo_empleado "
            "WHERE e.correo=%s AND e.contrasena=%s"
        )
        hashed = sha256_hash(password)
        if self.conexion.ejecutar(consulta_cliente, (correo, hashed)):
            return "cliente"

        resultado = self.conexion.ejecutar(consulta_empleado, (correo, hashed))
        if resultado:
            rol = str(resultado[0][0]).strip().lower()
            return rol

        return None


TOKEN_DURATION = timedelta(hours=1)
TOKENS: Dict[str, Dict[str, Any]] = {}
_CLEANUP_THREAD: threading.Thread | None = None


def _remove_expired_tokens() -> None:
    now = datetime.now()
    expired = [tok for tok, data in list(TOKENS.items()) if data["exp"] <= now]
    for tok in expired:
        TOKENS.pop(tok, None)


def _cleanup_loop(interval: int) -> None:
    while True:
        time.sleep(interval)
        _remove_expired_tokens()


def start_cleanup_task(interval_seconds: int = 600) -> None:
    global _CLEANUP_THREAD
    if _CLEANUP_THREAD is None:
        _CLEANUP_THREAD = threading.Thread(
            target=_cleanup_loop, args=(interval_seconds,), daemon=True
        )
        _CLEANUP_THREAD.start()


def login(correo: str, password: str) -> Optional[str]:
    """Return an auth token if credentials are valid."""
    aut = Autenticador()
    rol = aut.autenticar(correo, password)
    if not rol:
        return None
    token = secrets.token_urlsafe(16)
    TOKENS[token] = {"rol": rol, "exp": datetime.now() + TOKEN_DURATION}
    return token


def check_permission(token: str, permiso: str) -> bool:
    """Return True if the token is valid and has the given permission."""
    _remove_expired_tokens()
    data = TOKENS.get(token)
    if not data:
        return False
    rol = data["rol"]
    if rol == "cliente":
        return False
    conn = ConexionBD()
    res = conn.ejecutar(
        "SELECT permisos FROM tipo_empleado WHERE LOWER(nombre)=%s",
        (rol.lower(),),
    )
    if not res:
        return False
    permisos = json.loads(res[0][0])
    return "*" in permisos or permiso in permisos
