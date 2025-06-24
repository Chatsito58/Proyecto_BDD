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

        Devuelve el resultado obtenido de la base remota si está
        disponible; de lo contrario se devuelve el de la base local.
        """
        res_local: List[Tuple[Any, ...]] | None = None
        res_remota: List[Tuple[Any, ...]] | None = None
        try:
            res_local = self.local.ejecutar(query, params)
        except Exception:
            # La lógica de ConexionBD ya gestiona el almacenamiento de pendientes
            pass
        try:
            res_remota = self.remota.ejecutar(query, params)
        except Exception:
            pass

        return res_remota if res_remota is not None else (res_local or [])
