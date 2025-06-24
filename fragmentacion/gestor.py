from __future__ import annotations

from typing import Any, List, Tuple, Optional

from conexion.conexion import ConexionBD


class GestorFragmentacion:
    """Ejecuta operaciones en el fragmento correcto.

    Cada fragmento mantiene su propia cola de pendientes usando los nuevos
    nombres ``queue_file_local`` y ``queue_file_remota`` en lugar del
    argumento obsoleto ``queue_file``.
    """

    def __init__(self) -> None:
        # Un fragmento por cada base
        self.frag1 = ConexionBD(
            active="local",
            queue_file_local="pendientes_frag1.json",
        )
        self.frag2 = ConexionBD(
            active="remote",
            queue_file_remota="pendientes_frag2.json",
        )

    def _seleccionar_fragmento(self, id_val: int) -> ConexionBD:
        """Seleccionar fragmento por un criterio simple de par/impar."""
        return self.frag1 if id_val % 2 == 0 else self.frag2

    def ejecutar(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple[Any, ...]]:
        """Ejecutar la consulta en el fragmento determinado."""
        conn = self.frag1
        if "cliente" in query.lower() and params:
            try:
                id_val = int(params[0])
                conn = self._seleccionar_fragmento(id_val)
            except (ValueError, TypeError):
                conn = self.frag1
        return conn.ejecutar(query, params)
