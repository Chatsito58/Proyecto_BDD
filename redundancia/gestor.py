from __future__ import annotations

from typing import Any, List, Tuple, Optional

from conexion.conexion import ConexionBD


class GestorRedundancia:
    """Ejecuta cada operación en la base local y en la remota."""

    def __init__(self) -> None:
        # Conexión dedicada para cada base
        self.local = ConexionBD(active="local", queue_file="pendientes_local.json")
        self.remota = ConexionBD(active="remote", queue_file="pendientes_remota.json")

    def ejecutar(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple[Any, ...]]:
        """Ejecuta una consulta en ambas bases de datos.

        Devuelve el resultado obtenido de la base remota si está disponible;
        de lo contrario devuelve el de la base local.
        """
        res_local: List[Tuple[Any, ...]] | None = None
        res_remota: List[Tuple[Any, ...]] | None = None
        try:
            res_local = self.local.ejecutar(query, params)
        except Exception:
            # ``ConexionBD`` ya maneja la cola de pendientes en caso de error
            pass
        try:
            res_remota = self.remota.ejecutar(query, params)
        except Exception:
            pass

        return res_remota if res_remota is not None else (res_local or [])

    def ejecutar_con_columnas(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Versión con columnas de :meth:`ejecutar`.

        Ejecuta la consulta en ambas bases y prioriza los resultados de la
        remota si están disponibles.
        """
        cols_local: List[str] | None = None
        res_local: List[Tuple[Any, ...]] | None = None
        cols_remote: List[str] | None = None
        res_remote: List[Tuple[Any, ...]] | None = None

        try:
            cols_local, res_local = self.local.ejecutar_con_columnas(query, params)
        except Exception:
            pass
        try:
            cols_remote, res_remote = self.remota.ejecutar_con_columnas(query, params)
        except Exception:
            pass

        if cols_remote is not None:
            return cols_remote, res_remote or []
        return cols_local or [], res_local or []

    def close(self) -> None:
        """Cerrar ambas conexiones."""
        self.local.close()
        self.remota.close()
