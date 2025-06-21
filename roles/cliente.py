from __future__ import annotations

from conexion.conexion import ConexionBD


def _print_table(headers: list[str], rows: list[tuple]) -> None:
    """Print rows as a simple table."""
    if not rows:
        return
    col_widths = []
    for i, head in enumerate(headers):
        max_len = len(str(head))
        for row in rows:
            val = str(row[i])
            if len(val) > max_len:
                max_len = len(val)
        col_widths.append(max_len)
    header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)
    print(header_line)
    print(separator)
    for row in rows:
        line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(line)


def ver_reservas(id_cliente: int) -> None:
    """Consultar e imprimir las reservas de un cliente."""
    conn = ConexionBD()
    query = (
        "SELECT r.id_reserva, COALESCE(tv.descripcion, 'N/A') AS tipo, "
        "r.fecha_hora_salida, r.fecha_hora_entrada, er.descripcion "
        "FROM Reserva_alquiler r "
        "JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
        "LEFT JOIN Alquiler a ON r.id_alquiler=a.id_alquiler "
        "LEFT JOIN Vehiculo v ON a.id_vehiculo=v.placa "
        "LEFT JOIN Tipo_vehiculo tv ON v.id_tipo_vehiculo=tv.id_tipo "
        "WHERE r.id_cliente=%s "
        "ORDER BY r.fecha_hora_salida"
    )
    try:
        filas = conn.ejecutar(query, (id_cliente,))
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error consultando reservas:", exc)
        return
    if not filas:
        print("No hay reservas registradas para este cliente.")
        return
    headers = ["ID", "Tipo", "Inicio", "Fin", "Estado"]
    _print_table(headers, filas)
