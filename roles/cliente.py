from __future__ import annotations

from conexion.conexion import ConexionBD


def realizar_abono(id_cliente: int) -> None:
    """Permitir al cliente registrar un abono para una de sus reservas pendientes."""
    conexion = ConexionBD()

    # Obtener identificador de estado "pendiente" (o "reservado" como respaldo)
    id_estado = None
    try:
        res = conexion.ejecutar(
            "SELECT id_estado FROM Estado_reserva WHERE LOWER(descripcion)='pendiente'"
        )
        if res:
            id_estado = int(res[0][0])
        else:
            res = conexion.ejecutar(
                "SELECT id_estado FROM Estado_reserva WHERE LOWER(descripcion)='reservado'"
            )
            id_estado = int(res[0][0]) if res else None
    except Exception as exc:
        print("Error obteniendo estados:", exc)
        return

    # Buscar reservas pendientes del cliente
    query = (
        "SELECT r.id_reserva, (r.abono + r.saldo_pendiente) AS total, "
        "COALESCE(SUM(a.valor),0) AS abonado "
        "FROM Reserva_alquiler r "
        "LEFT JOIN Abono_reserva a ON r.id_reserva=a.id_reserva "
        "WHERE r.id_cliente=%s "
    )
    params = [id_cliente]
    if id_estado is not None:
        query += "AND r.id_estado_reserva=%s "
        params.append(id_estado)
    query += "GROUP BY r.id_reserva, r.abono, r.saldo_pendiente"

    try:
        filas = conexion.ejecutar(query, tuple(params))
    except Exception as exc:
        print("Error consultando reservas:", exc)
        return

    if not filas:
        print("No tiene reservas pendientes.")
        return

    print("Reservas pendientes:")
    for idx, (id_reserva, total, abonado) in enumerate(filas, start=1):
        restante = float(total) - float(abonado)
        print(f"{idx}. Reserva #{id_reserva} - Saldo restante: ${restante:.2f}")

    # Selección
    seleccion = None
    while seleccion is None:
        opcion = input("Seleccione una reserva: ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(filas):
            seleccion = int(opcion) - 1
        else:
            print("Opción inválida")

    id_reserva, total, abonado = filas[seleccion]
    restante = float(total) - float(abonado)
    print(f"Total: ${float(total):.2f}")
    print(f"Abonado: ${float(abonado):.2f}")
    print(f"Saldo restante: ${restante:.2f}")

    monto = None
    while monto is None:
        monto_str = input("Monto a abonar: ").strip()
        try:
            monto_val = float(monto_str)
        except ValueError:
            print("Monto inválido")
            continue
        if monto_val > restante:
            print("El monto no puede superar el saldo restante")
            continue
        if monto_val <= 0:
            print("El monto debe ser positivo")
            continue
        monto = monto_val

    # Registrar abono
    try:
        conexion.ejecutar(
            "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva) VALUES (%s, NOW(), %s)",
            (monto, id_reserva),
        )
        print("Abono registrado correctamente.")
    except Exception as exc:
        print("Error registrando abono:", exc)
